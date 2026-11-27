import pytest

from app.domain.errors import ConflictError, DomainError, NotFoundError, PermissionDeniedError
from app.persistence.models_manager import CoinEntry
from app.services import coin_service, lineup_service, manager_queries
from tests.services.manager_helpers import add_player, confirmed_match


def test_new_team_starts_with_budget_and_confirmed_result_pays(ctx, clock):
    s = confirmed_match(ctx, clock, 2, 1)
    assert coin_service.balance(ctx, s["host"].id) == 1000 + 150
    assert coin_service.balance(ctx, s["guest"].id) == 1000 + 50
    reasons = [e.reason for e in coin_service.history(ctx, s["host"].id)]
    assert reasons == ["MATCH_REWARD", "STARTING_BUDGET"]


def test_coins_never_go_negative(ctx, clock):
    s = confirmed_match(ctx, clock)
    with pytest.raises(ConflictError) as poor:
        coin_service.move(ctx, s["guest"].id, -5000, "TEST", None, None)
    assert poor.value.code == "INSUFFICIENT_COINS"
    assert ctx.db.query(CoinEntry).filter(CoinEntry.reason == "TEST").count() == 0


def test_lineup_builds_player_card(ctx, clock):
    s = confirmed_match(ctx, clock, 2, 1)
    striker = add_player(ctx, s["host"], "nueve@r.test")
    lineup_service.record(ctx, s["host_owner"], s["contract_id"], [(striker.id, 2), (s["host_owner"].id, 0)])
    card = manager_queries.player_card(ctx, s["guest_owner"], striker.id)
    assert (card.matches, card.goals, card.wins, card.draws, card.losses) == (1, 2, 1, 0, 0)
    loser = manager_queries.player_card(ctx, s["guest_owner"], s["guest_owner"].id)
    assert loser.matches == 0  # sin planilla no hay partidos en la ficha
    lineup_service.record(ctx, s["guest_owner"], s["contract_id"], [(s["guest_owner"].id, 1)])
    loser = manager_queries.player_card(ctx, s["host_owner"], s["guest_owner"].id)
    assert (loser.matches, loser.goals, loser.losses) == (1, 1, 1)


def test_lineup_rules_and_corrections(ctx, clock):
    s = confirmed_match(ctx, clock, 2, 1)
    with pytest.raises(DomainError) as too_many:
        lineup_service.record(ctx, s["host_owner"], s["contract_id"], [(s["host_owner"].id, 3)])
    assert too_many.value.code == "GOALS_EXCEED_SCORE"
    with pytest.raises(DomainError):  # un jugador del rival no va en mi planilla
        lineup_service.record(ctx, s["host_owner"], s["contract_id"], [(s["guest_owner"].id, 0)])
    lineup_service.record(ctx, s["host_owner"], s["contract_id"], [(s["host_owner"].id, 2)])
    lineup_service.record(ctx, s["host_owner"], s["contract_id"], [(s["host_owner"].id, 1)])  # corrige
    assert manager_queries.player_card(ctx, s["host_owner"], s["host_owner"].id).goals == 1
    with pytest.raises(NotFoundError):
        lineup_service.record(ctx, s["city"]["tres"][0], s["contract_id"], [(s["host_owner"].id, 0)])


def test_lineup_requires_confirmed_result(ctx, clock):
    from tests.services.contract_helpers import matched_scene
    s = matched_scene(ctx)
    with pytest.raises(ConflictError) as early:
        lineup_service.record(ctx, s["host_owner"], s["contract_id"], [(s["host_owner"].id, 0)])
    assert early.value.code == "RESULT_NOT_CONFIRMED"


def test_only_admin_records_lineup(ctx, clock):
    s = confirmed_match(ctx, clock)
    player = add_player(ctx, s["host"], "raso@r.test")
    with pytest.raises(PermissionDeniedError):
        lineup_service.record(ctx, player, s["contract_id"], [(player.id, 0)])
