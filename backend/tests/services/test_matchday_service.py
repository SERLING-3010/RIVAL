from datetime import timedelta

import pytest

from app.domain.errors import ConflictError, DomainError, NotFoundError, PermissionDeniedError
from app.persistence.models_audit import AuditEvent
from app.services import callup_service, contract_service, lineup_service, manager_queries, player_rating_service
from app.services import result_service, settlement_service
from tests.services.contract_helpers import matched_scene
from tests.services.manager_helpers import add_player, confirmed_match


def test_confirmed_result_moves_glicko_levels(ctx, clock):
    s = confirmed_match(ctx, clock, 3, 0)
    host, host_n = settlement_service.current_rating(ctx, s["host"].id)
    guest, _ = settlement_service.current_rating(ctx, s["guest"].id)
    assert host.rating > 1600 > 1400 > guest.rating and host_n == 1 and host.rd < 350


def test_callup_and_responses(ctx, clock):
    s = matched_scene(ctx)
    player = add_player(ctx, s["host"], "nueve@r.test")
    with pytest.raises(PermissionDeniedError):
        callup_service.call_up(ctx, player, s["contract_id"], [player.id])
    with pytest.raises(DomainError) as outsider:
        callup_service.call_up(ctx, s["host_owner"], s["contract_id"], [s["guest_owner"].id])
    assert outsider.value.code == "NOT_A_TEAM_MEMBER"
    callup_service.call_up(ctx, s["host_owner"], s["contract_id"], [player.id, s["host_owner"].id])
    callup_service.respond(ctx, player, s["contract_id"], going=True)
    view = callup_service.team_callup(ctx, s["host_owner"], s["contract_id"])
    assert (view.going, view.not_going, view.pending) == (1, 0, 1)
    assert [c.status for c in callup_service.my_callups(ctx, player)] == ["GOING"]
    with pytest.raises(NotFoundError):  # al rival no lo convocaron
        callup_service.respond(ctx, s["guest_owner"], s["contract_id"], going=True)
    clock.advance(timedelta(hours=31))
    with pytest.raises(ConflictError) as late:
        callup_service.respond(ctx, player, s["contract_id"], going=False)
    assert late.value.code == "MATCH_ALREADY_STARTED"


def test_teammates_rate_players_who_played(ctx, clock):
    s = confirmed_match(ctx, clock, 2, 1)
    striker, keeper = add_player(ctx, s["host"], "nueve@r.test"), add_player(ctx, s["host"], "portero@r.test")
    lineup_service.record(ctx, s["host_owner"], s["contract_id"], [(striker.id, 2), (keeper.id, 0)])
    assert [p.user_id for p in player_rating_service.to_rate(ctx, keeper, s["contract_id"])] == [striker.id]
    player_rating_service.rate(ctx, keeper, s["contract_id"], striker.id, 9)
    player_rating_service.rate(ctx, s["host_owner"], s["contract_id"], striker.id, 7)
    card = manager_queries.player_card(ctx, s["guest_owner"], striker.id)
    assert (card.rating_average, card.rating_votes) == (8.0, 2)
    with pytest.raises(ConflictError) as twice:
        player_rating_service.rate(ctx, keeper, s["contract_id"], striker.id, 10)
    assert twice.value.code == "ALREADY_RATED"
    with pytest.raises(DomainError):
        player_rating_service.rate(ctx, striker, s["contract_id"], striker.id, 10)
    with pytest.raises(NotFoundError):  # el rival no valora a mi equipo
        player_rating_service.rate(ctx, s["city"]["tres"][0], s["contract_id"], striker.id, 1)
    rated = [e for e in ctx.db.query(AuditEvent).filter(AuditEvent.action == "PLAYER_RATED")]
    assert len(rated) == 2 and all("score" not in (e.after_json or "") for e in rated)  # la nota es privada


def test_rating_needs_confirmed_result(ctx, clock):
    s = matched_scene(ctx)
    for owner in (s["host_owner"], s["guest_owner"]):
        contract_service.sign(ctx, owner, s["contract_id"], version=1)
    clock.advance(timedelta(hours=31))
    result_service.report(ctx, s["host_owner"], s["contract_id"], 1, 0)
    with pytest.raises(ConflictError) as error:
        player_rating_service.rate(ctx, s["host_owner"], s["contract_id"], s["host_owner"].id, 5)
    assert error.value.code == "RESULT_NOT_CONFIRMED"
