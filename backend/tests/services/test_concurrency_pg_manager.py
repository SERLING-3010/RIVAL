"""Concurrencia real del modo manager y del árbitro (Sprints 7 y 8): solo corre contra PostgreSQL."""

from datetime import timedelta

import pytest
from sqlalchemy import func, select

from app.persistence.models_contracts import MatchContract
from app.persistence.models_identity import UserAccount
from app.persistence.models_manager import CoinEntry
from app.persistence.models_results import MatchResult
from app.services import (
    audit_service, coin_service, contract_service, fixture_service, health_service, referee_service,
    result_service, transfer_listing_service, transfer_service,
)
from tests.conftest import TEST_DATABASE_URL
from tests.services.league_match_helpers import first_kickoff, league_with_teams
from tests.services.manager_helpers import add_player
from tests.services.test_concurrency_pg import factory, make_ctx, race  # noqa: F401  (fixture reutilizada)
from tests.services.test_rival_service import make_team

pytestmark = pytest.mark.skipif(TEST_DATABASE_URL.startswith("sqlite"), reason="requiere PostgreSQL")


def user(ctx, user_id):
    return ctx.db.get(UserAccount, user_id)


def test_two_players_accept_at_once_buyer_never_goes_negative(factory, clock):  # noqa: F811
    with factory() as session:
        ctx = make_ctx(session, clock)
        seller_owner, seller = make_team(ctx, "v@r.test", "Águilas", "Barrio Uno")
        buyer_owner, buyer = make_team(ctx, "c@r.test", "Bravos", "Barrio Dos")
        players = [add_player(ctx, seller, f"p{i}@r.test") for i in range(2)]
        offers = []
        for p in players:
            transfer_listing_service.set_listed(ctx, seller_owner, seller.id, p.id, listed=True)
            offer = transfer_service.make_offer(ctx, buyer_owner, buyer.id, p.id, 600)  # 600 + 600 > 1.000
            transfer_service.decide_owner(ctx, seller_owner, offer.id, accept=True)
            offers.append((p.id, offer.id))
        session.commit()
        buyer_id = buyer.id
    accept = [lambda ctx, p=p, o=o: transfer_service.decide_player(ctx, user(ctx, p), o, accept=True)
              for p, o in offers]
    assert race(factory, clock, accept) == ["INSUFFICIENT_COINS", "OK"]
    with factory() as session:
        ctx = make_ctx(session, clock)
        assert coin_service.balance(ctx, buyer_id) == 400
        assert health_service.run_checks(ctx) == []
        assert audit_service.verify_chain(session) is True


def test_referee_and_team_confirm_at_once_result_and_rewards_once(factory, clock):  # noqa: F811
    with factory() as session:
        ctx = make_ctx(session, clock)
        s = league_with_teams(ctx)
        fixture = fixture_service.generate(ctx, s["organizer"], s["league"].id, first_kickoff(ctx), 7)[0]
        contract = ctx.db.get(MatchContract, fixture.contract_id)
        owners = {t.id: o for o, t in s["teams"].values()}
        host_owner, guest_owner = owners[contract.host_team_id], owners[contract.guest_team_id]
        assignment = referee_service.assign(ctx, s["organizer"], contract.id, s["referee"].id)
        referee_service.respond(ctx, s["referee"], assignment.id, accept=True)
        for owner in (host_owner, guest_owner):
            contract_service.sign(ctx, owner, contract.id, version=1)
        clock.advance(timedelta(days=3))
        result_service.report(ctx, host_owner, contract.id, 1, 0)
        session.commit()
        ids = (guest_owner.id, s["referee"].id, contract.id, contract.host_team_id)
    team = lambda ctx: result_service.report(ctx, user(ctx, ids[0]), ids[2], 1, 0)  # noqa: E731
    referee = lambda ctx: referee_service.report_result(ctx, user(ctx, ids[1]), ids[2], 3, 3)  # noqa: E731
    outcomes = race(factory, clock, [team, referee])
    assert outcomes.count("OK") == 1 and set(outcomes) - {"OK"} == {"RESULT_ALREADY_CONFIRMED"}
    with factory() as session:
        result = session.scalar(select(MatchResult).where(MatchResult.contract_id == ids[2]))
        assert result is not None and result.status == "CONFIRMED"
        rewards = session.scalar(select(func.count()).select_from(CoinEntry).where(
            CoinEntry.team_id == ids[3], CoinEntry.reason == "MATCH_REWARD"))
        assert rewards == 1
