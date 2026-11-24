"""Concurrencia real: solo corre contra PostgreSQL (RIVAL_TEST_DATABASE_URL).

Dos administradores (o dos peticiones del mismo) actúan en el mismo instante; los
bloqueos FOR UPDATE y los índices únicos deben dejar pasar solo una acción.
"""

import threading
from datetime import timedelta

import pytest
from sqlalchemy.orm import Session

from app.domain.errors import DomainError
from app.domain.geo import SearchScope
from app.domain.roles import TeamRole, UserRole
from app.persistence.database import make_engine, make_session_factory
from app.services import audit_service, join_service, match_offer_service, match_request_service
from app.services.context import ServiceContext
from app.services.inputs import JoinRequestInput
from tests.conftest import CATALOG, TEST_DATABASE_URL, reset_schema
from tests.services.match_helpers import offer_input, request_input, setup_city
from tests.services.test_team_service import new_user, team_input

pytestmark = pytest.mark.skipif(TEST_DATABASE_URL.startswith("sqlite"), reason="requiere PostgreSQL")


def make_ctx(session: Session, clock) -> ServiceContext:
    return ServiceContext(db=session, clock=clock, catalog=CATALOG,
                          session_ttl=timedelta(days=7), session_idle=timedelta(hours=72))


def race(factory, clock, actions):
    """Ejecuta cada acción en su propia sesión, todas a la vez. Devuelve los códigos de error."""
    barrier = threading.Barrier(len(actions))
    outcomes: list[str] = []

    def run(action):
        with factory() as session:
            ctx = make_ctx(session, clock)
            barrier.wait()
            try:
                action(ctx)
                session.commit()
                outcomes.append("OK")
            except DomainError as error:
                session.rollback()
                outcomes.append(error.code)

    threads = [threading.Thread(target=run, args=(a,)) for a in actions]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=30)
    return sorted(outcomes)


@pytest.fixture
def factory():
    engine = make_engine(TEST_DATABASE_URL)
    reset_schema(engine)
    yield make_session_factory(engine)
    engine.dispose()


def test_two_offers_accepted_at_once_only_one_wins(factory, clock):
    with factory() as session:
        ctx = make_ctx(session, clock)
        city = setup_city(ctx)
        owner, team = city["uno"]
        request = match_request_service.create_request(ctx, owner, team.id, request_input(ctx, scope=SearchScope.CITY))
        a = match_offer_service.make_offer(ctx, city["dos"][0], city["dos"][1].id, request.id, offer_input(ctx))
        b = match_offer_service.make_offer(ctx, city["tres"][0], city["tres"][1].id, request.id, offer_input(ctx))
        session.commit()
        ids = (owner.id, a.id, b.id)

    def accept(offer_id):
        return lambda ctx: match_offer_service.decide(ctx, ctx.db.get(type(owner), ids[0]), offer_id, accept=True)

    assert race(factory, clock, [accept(ids[1]), accept(ids[2])]) == ["MATCH_REQUEST_CLOSED", "OK"]
    with factory() as session:
        assert audit_service.verify_chain(session) is True


def test_two_coaches_approved_at_once_only_one_joins(factory, clock):
    with factory() as session:
        ctx = make_ctx(session, clock)
        from app.services import team_service

        captain = new_user(ctx, "cap@r.test")
        team = team_service.create_team(ctx, captain, team_input())
        reqs = [join_service.request_join(ctx, new_user(ctx, f"dt{i}@r.test", UserRole.COACH), team.id,
                                          JoinRequestInput(desired_role=TeamRole.COACH)) for i in range(2)]
        session.commit()
        ids = (captain.id, reqs[0].id, reqs[1].id)

    def approve(request_id):
        return lambda ctx: join_service.decide(ctx, ctx.db.get(type(captain), ids[0]), request_id, approve=True)

    outcomes = race(factory, clock, [approve(ids[1]), approve(ids[2])])
    # El segundo falla: o el equipo ya tiene DT, o el capitán dejó de administrar al entrar el primer DT.
    assert outcomes.count("OK") == 1
    assert set(outcomes) - {"OK"} <= {"TEAM_HAS_COACH", "ADMIN_ONLY"}
    with factory() as session:
        from app.services import team_service

        detail = team_service.team_detail(make_ctx(session, clock), team.id)
        assert [m.role for m in detail.members].count(TeamRole.COACH) == 1
        assert audit_service.verify_chain(session) is True


def test_accept_and_withdraw_at_once_stay_consistent(factory, clock):
    with factory() as session:
        ctx = make_ctx(session, clock)
        city = setup_city(ctx)
        owner, team = city["uno"]
        rival_owner, rival = city["dos"]
        request = match_request_service.create_request(ctx, owner, team.id, request_input(ctx, scope=SearchScope.CITY))
        offer = match_offer_service.make_offer(ctx, rival_owner, rival.id, request.id, offer_input(ctx))
        session.commit()
        ids = (owner.id, rival_owner.id, offer.id, request.id)

    user = type(owner)
    accept = lambda ctx: match_offer_service.decide(ctx, ctx.db.get(user, ids[0]), ids[2], accept=True)  # noqa: E731
    withdraw = lambda ctx: match_offer_service.withdraw(ctx, ctx.db.get(user, ids[1]), ids[2])  # noqa: E731
    outcomes = race(factory, clock, [accept, withdraw])
    assert outcomes.count("OK") == 1 and set(outcomes) - {"OK"} == {"OFFER_NOT_PENDING"}
    with factory() as session:
        stored = match_request_service.get_request(make_ctx(session, clock), ids[3])
        offer_now = session.get(type(offer), ids[2])
        assert (stored.status == "MATCHED") == (offer_now.status == "ACCEPTED")
        assert audit_service.verify_chain(session) is True


def test_double_tap_accept_invitation_joins_once(factory, clock):
    from app.services import free_agent_service, invitation_service, team_service

    with factory() as session:
        ctx = make_ctx(session, clock)
        captain, player = new_user(ctx, "cap@r.test"), new_user(ctx, "libre@r.test")
        team = team_service.create_team(ctx, captain, team_input())
        free_agent_service.set_free_agent(ctx, player, "FOOTBALL", active=True, position=None, note=None)
        invitation = invitation_service.invite(ctx, captain, team.id, player.id, None)
        session.commit()
        ids = (player.id, invitation.id)

    tap = lambda ctx: invitation_service.respond(ctx, ctx.db.get(type(player), ids[0]), ids[1], accept=True)  # noqa: E731
    assert race(factory, clock, [tap, tap]) == ["INVITATION_ALREADY_DECIDED", "OK"]
