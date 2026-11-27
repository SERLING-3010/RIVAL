from datetime import timedelta

from app.persistence.models_contracts import MatchContract
from app.services import cup_queries, cup_service, lineup_service, manager_queries
from tests.services.league_match_helpers import first_kickoff, league_with_teams, play


def test_card_face_comes_from_real_matches(ctx, clock):
    s = league_with_teams(ctx)
    cup_service.create(ctx, s["organizer"], s["league"].id, first_kickoff(ctx), 7)
    a_owner, _a = s["teams"]["a"]
    c_owner, _c = s["teams"]["c"]
    semi = cup_queries.bracket(ctx, a_owner, s["league"].id).rounds[0].matches[1]
    play(ctx, clock, ctx.db.get(MatchContract, semi.contract_id), [s["teams"]["b"][0], c_owner], 0, 1)
    final = cup_queries.bracket(ctx, a_owner, s["league"].id).rounds[1].matches[0]
    clock.advance(timedelta(days=4))
    play(ctx, clock, ctx.db.get(MatchContract, final.contract_id), [a_owner, c_owner], 3, 1)
    lineup_service.record(ctx, a_owner, final.contract_id, [(a_owner.id, 3)])
    card = manager_queries.player_card(ctx, c_owner, a_owner.id).card
    assert (card.media, card.tier, card.next_tier, card.media_to_next, card.display_tier) ==         (71, "PLATA", "ORO", 4, "PLATA")
    assert card.market_value == 390  # 71 × 5 + 25 por Plata + 10 por la victoria = 390
    assert len(card.specials) == 15 and all(sp.earned_at is None for sp in card.specials)
    assert [(g.current, g.target) for g in card.specials[0].goals] == [(3, 10)]  # Rubí: 3 de 10 goles
    assert (card.hat_tricks, card.recent) == (1, ["W"])
    assert {"Debut", "Triplete", "Campeón de copa"} <= set(card.badges)
    empty = manager_queries.player_card(ctx, a_owner, s["referee"].id).card
    assert (empty.media, empty.recent, empty.badges) == (57, [], [])
