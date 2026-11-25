from datetime import timedelta

import pytest

from app.domain.errors import NotFoundError
from app.persistence.models_contracts import MatchContract
from app.services import achievement_queries, cup_queries, cup_service, lineup_service
from tests.services.league_match_helpers import first_kickoff, league_with_teams, play


def by_code(badges):
    return {b.code: b for b in badges}


def test_cup_final_with_hat_trick_gives_player_and_team_badges(ctx, s_cup, clock):
    s = s_cup
    a_owner, a_team = s["teams"]["a"]
    c_owner, _c_team = s["teams"]["c"]
    semi = cup_queries.bracket(ctx, a_owner, s["league"].id).rounds[0].matches[1]
    play(ctx, clock, ctx.db.get(MatchContract, semi.contract_id), [s["teams"]["b"][0], c_owner], 0, 1)
    final = cup_queries.bracket(ctx, a_owner, s["league"].id).rounds[1].matches[0]
    clock.advance(timedelta(days=4))
    play(ctx, clock, ctx.db.get(MatchContract, final.contract_id), [a_owner, c_owner], 3, 1)
    lineup_service.record(ctx, a_owner, final.contract_id, [(a_owner.id, 3)])
    player = by_code(achievement_queries.for_player(ctx, a_owner.id))
    assert all(player[c].earned_at is not None for c in ("DEBUT", "HAT_TRICK", "CUP_CHAMPION"))
    assert player["GOALS_10"].progress == "3/10"
    team = by_code(achievement_queries.for_team(ctx, a_team.id))
    assert team["FIRST_WIN"].earned_at is not None and team["CUP_CHAMPION"].earned_at is not None
    runner_up = by_code(achievement_queries.for_player(ctx, c_owner.id))
    assert runner_up["CUP_CHAMPION"].earned_at is None  # no estuvo en la planilla del campeón


def test_unknown_player_or_team(ctx):
    with pytest.raises(NotFoundError):
        achievement_queries.for_player(ctx, 9999)
    with pytest.raises(NotFoundError):
        achievement_queries.for_team(ctx, 9999)


@pytest.fixture
def s_cup(ctx):
    s = league_with_teams(ctx)
    cup_service.create(ctx, s["organizer"], s["league"].id, first_kickoff(ctx), 7)
    return s
