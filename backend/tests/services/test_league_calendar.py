from datetime import timedelta

import pytest

from app.domain.errors import ConflictError, DomainError, PermissionDeniedError
from app.persistence.models_contracts import MatchContract
from app.services import contract_queries, fixture_service, standings_queries
from tests.services.league_match_helpers import first_kickoff, league_with_teams, play


@pytest.fixture
def s(ctx):
    return league_with_teams(ctx)


def owner_of(s, team_id):
    return next(o for o, t in s["teams"].values() if t.id == team_id)


def test_organizer_generates_round_robin_contracts(ctx, s):
    with pytest.raises(PermissionDeniedError):
        fixture_service.generate(ctx, s["teams"]["b"][0], s["league"].id, first_kickoff(ctx), 7)
    fixtures = fixture_service.generate(ctx, s["organizer"], s["league"].id, first_kickoff(ctx), 7)
    assert sorted(f.round for f in fixtures) == [1, 2, 3]  # 3 equipos: 3 fechas, uno descansa cada vez
    contract = ctx.db.get(MatchContract, fixtures[0].contract_id)
    assert (contract.league_id, contract.offer_id, contract.status) == (s["league"].id, None, "NEGOTIATING")
    view = contract_queries.get_contract(ctx, owner_of(s, contract.host_team_id), contract.id)
    assert (view.current.terms.referee_mode, view.current.terms.place_kind) == ("WITH", "TO_AGREE")
    assert view.league_id == s["league"].id
    with pytest.raises(ConflictError) as twice:
        fixture_service.generate(ctx, s["organizer"], s["league"].id, first_kickoff(ctx), 7)
    assert twice.value.code == "FIXTURE_ALREADY_EXISTS"


def test_calendar_view_and_too_long_season(ctx, s):
    with pytest.raises(DomainError) as long:
        fixture_service.generate(ctx, s["organizer"], s["league"].id, first_kickoff(ctx) + timedelta(days=50), 14)
    assert long.value.code == "FIXTURE_TOO_LONG"
    fixture_service.generate(ctx, s["organizer"], s["league"].id, first_kickoff(ctx), 7)
    calendar = standings_queries.calendar(ctx, s["league"].id)
    assert [m.round for m in calendar] == [1, 2, 3]
    assert {frozenset((m.host.name, m.guest.name)) for m in calendar} == {
        frozenset(("Águilas", "Bravos")), frozenset(("Águilas", "Cóndores")), frozenset(("Bravos", "Cóndores"))}


def test_table_counts_only_confirmed_results(ctx, s, clock):
    fixtures = fixture_service.generate(ctx, s["organizer"], s["league"].id, first_kickoff(ctx), 7)
    first = ctx.db.get(MatchContract, fixtures[0].contract_id)
    play(ctx, clock, first, [owner_of(s, first.host_team_id), owner_of(s, first.guest_team_id)], 2, 1)
    table = standings_queries.table(ctx, s["league"].id)
    top = table[0]
    assert (top.team_id, top.points, top.played, top.goal_difference) == (first.host_team_id, 3, 1, 1)
    assert sum(r.played for r in table) == 2 and len(table) == 3
    assert standings_queries.calendar(ctx, s["league"].id)[0].result == "2 – 1"
