from datetime import timedelta

import pytest

from app.domain.errors import ConflictError, DomainError, NotFoundError, PermissionDeniedError
from app.persistence.models_contracts import MatchContract
from app.services import contract_service, cup_queries, cup_service, fixture_service, referee_service, standings_queries
from tests.services.league_match_helpers import first_kickoff, league_with_teams, play


@pytest.fixture
def s(ctx):
    return league_with_teams(ctx)  # Águilas (organiza), Bravos y Cóndores, todos con nivel 1500


def cup(ctx, s):
    return cup_queries.bracket(ctx, s["organizer"], s["league"].id)


def test_only_organizers_create_one_cup_per_league(ctx, s):
    _owner_b, _team_b = s["teams"]["b"]
    with pytest.raises(PermissionDeniedError):
        cup_service.create(ctx, _owner_b, s["league"].id, first_kickoff(ctx), 7)
    with pytest.raises(NotFoundError):
        cup(ctx, s)
    cup_service.create(ctx, s["organizer"], s["league"].id, first_kickoff(ctx), 7)
    with pytest.raises(ConflictError):
        cup_service.create(ctx, s["organizer"], s["league"].id, first_kickoff(ctx), 7)


def test_bye_then_winner_advances_to_final_and_becomes_champion(ctx, s, clock):
    cup_service.create(ctx, s["organizer"], s["league"].id, first_kickoff(ctx), 7)
    view = cup(ctx, s)
    assert [r.name for r in view.rounds] == ["Semifinal", "Final"]
    bye, semi = view.rounds[0].matches
    assert (bye.host_name, bye.guest_name, bye.winner_name) == ("Águilas", None, "Águilas")  # pase directo
    assert (semi.host_name, semi.guest_name, semi.contract_id is not None) == ("Bravos", "Cóndores", True)
    final = view.rounds[1].matches[0]
    assert (final.host_name, final.guest_name, final.contract_id) == ("Águilas", None, None)
    owners_bc = [s["teams"]["b"][0], s["teams"]["c"][0]]
    play(ctx, clock, ctx.db.get(MatchContract, semi.contract_id), owners_bc, 0, 2)
    final = cup(ctx, s).rounds[1].matches[0]
    assert (final.host_name, final.guest_name, final.contract_id is not None) == ("Águilas", "Cóndores", True)
    contract = ctx.db.get(MatchContract, final.contract_id)
    assert contract.league_id == s["league"].id  # el árbitro de la liga se puede asignar
    clock.advance(timedelta(days=4))  # la final es una semana después de la semifinal
    play(ctx, clock, contract, [s["teams"]["a"][0], s["teams"]["c"][0]], 3, 1)
    assert cup(ctx, s).champion_name == "Águilas"


def test_tie_waits_for_penalties_set_by_organizer(ctx, s, clock):
    cup_service.create(ctx, s["organizer"], s["league"].id, first_kickoff(ctx), 7)
    semi = cup(ctx, s).rounds[0].matches[1]
    with pytest.raises(ConflictError):  # sin resultado no hay penales
        cup_service.set_tiebreak(ctx, s["organizer"], semi.id, s["teams"]["b"][1].id)
    play(ctx, clock, ctx.db.get(MatchContract, semi.contract_id), [s["teams"]["b"][0], s["teams"]["c"][0]], 1, 1)
    view = cup(ctx, s)
    assert view.rounds[0].matches[1].needs_tiebreak and view.rounds[1].matches[0].guest_name is None
    with pytest.raises(PermissionDeniedError):
        cup_service.set_tiebreak(ctx, s["teams"]["b"][0], semi.id, s["teams"]["b"][1].id)
    with pytest.raises(DomainError):  # Águilas no jugó ese cruce
        cup_service.set_tiebreak(ctx, s["organizer"], semi.id, s["teams"]["a"][1].id)
    cup_service.set_tiebreak(ctx, s["organizer"], semi.id, s["teams"]["b"][1].id)
    view = cup(ctx, s)
    assert view.rounds[0].matches[1].winner_name == "Bravos" and view.rounds[1].matches[0].guest_name == "Bravos"
    with pytest.raises(ConflictError):  # ya tiene ganador
        cup_service.set_tiebreak(ctx, s["organizer"], semi.id, s["teams"]["c"][1].id)


def test_cup_matches_do_not_count_in_the_league_table(ctx, s, clock):
    fixture_service.generate(ctx, s["organizer"], s["league"].id, first_kickoff(ctx), 7)
    cup_service.create(ctx, s["organizer"], s["league"].id, first_kickoff(ctx) + timedelta(hours=3), 7)
    semi = cup(ctx, s).rounds[0].matches[1]
    play(ctx, clock, ctx.db.get(MatchContract, semi.contract_id), [s["teams"]["b"][0], s["teams"]["c"][0]], 4, 0)
    assert all(row.played == 0 for row in standings_queries.table(ctx, s["league"].id))


def test_referee_result_also_advances_the_cup(ctx, s, clock):
    cup_service.create(ctx, s["organizer"], s["league"].id, first_kickoff(ctx), 7)
    semi = cup(ctx, s).rounds[0].matches[1]
    assignment = referee_service.assign(ctx, s["organizer"], semi.contract_id, s["referee"].id)
    referee_service.respond(ctx, s["referee"], assignment.id, accept=True)
    for owner in (s["teams"]["b"][0], s["teams"]["c"][0]):
        contract_service.sign(ctx, owner, semi.contract_id, version=1)
    clock.advance(timedelta(days=3))
    referee_service.report_result(ctx, s["referee"], semi.contract_id, 2, 1)
    assert cup(ctx, s).rounds[1].matches[0].guest_name == "Bravos"
