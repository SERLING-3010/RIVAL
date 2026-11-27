from datetime import timedelta

import pytest
from sqlalchemy import select

from app.domain.errors import ConflictError, DomainError, PermissionDeniedError
from app.persistence.models_audit import AuditEvent
from app.persistence.models_cards import SpecialCard
from app.services import goal_claim_service, lineup_service, manager_queries, pending_service, special_card_service
from tests.services.manager_helpers import confirmed_match


def _with_chilena(ctx, clock):
    s = confirmed_match(ctx, clock, 2, 1)
    lineup_service.record(ctx, s["host_owner"], s["contract_id"], [(s["host_owner"].id, 2)],
                          {s["host_owner"].id: ["CHILENA"]})
    return s


def test_rival_confirms_a_goal_kind_and_it_counts(ctx, clock):
    s = _with_chilena(ctx, clock)
    [mine] = goal_claim_service.claims(ctx, s["host_owner"], s["contract_id"])
    assert (mine.kind, mine.status, mine.can_decide) == ("CHILENA", "PENDING", False)
    [theirs] = goal_claim_service.claims(ctx, s["guest_owner"], s["contract_id"])
    assert theirs.can_decide
    waiting = [p for p in pending_service.pending(ctx, s["guest_owner"]) if p.kind == "CONFIRM_GOAL_KINDS"]
    assert [(p.target, p.target_id) for p in waiting] == [("contract", s["contract_id"])]
    assert not [p for p in pending_service.pending(ctx, s["host_owner"]) if p.kind == "CONFIRM_GOAL_KINDS"]
    with pytest.raises(PermissionDeniedError) as own:
        goal_claim_service.decide(ctx, s["host_owner"], mine.id, accept=True)
    assert own.value.code == "RIVAL_ONLY"
    assert goal_claim_service.confirmed_kinds(ctx, s["host_owner"].id) == {}
    goal_claim_service.decide(ctx, s["guest_owner"], mine.id, accept=True)
    assert goal_claim_service.confirmed_kinds(ctx, s["host_owner"].id) == {"CHILENA": 1}
    assert not [p for p in pending_service.pending(ctx, s["guest_owner"]) if p.kind == "CONFIRM_GOAL_KINDS"]
    with pytest.raises(ConflictError) as twice:
        goal_claim_service.decide(ctx, s["guest_owner"], mine.id, accept=False)
    assert twice.value.code == "GOAL_CLAIM_DECIDED"
    event = ctx.db.scalars(select(AuditEvent).where(AuditEvent.action == "GOAL_KIND_CONFIRMED")).one()
    assert (event.initiated_by, event.approved_by) == (s["host_owner"].id, s["guest_owner"].id)


def test_rejected_or_expired_kinds_do_not_count(ctx, clock):
    s = _with_chilena(ctx, clock)
    [claim] = goal_claim_service.claims(ctx, s["guest_owner"], s["contract_id"])
    goal_claim_service.decide(ctx, s["guest_owner"], claim.id, accept=False)
    assert goal_claim_service.confirmed_kinds(ctx, s["host_owner"].id) == {}
    card = manager_queries.player_card(ctx, s["guest_owner"], s["host_owner"].id)
    assert card.goals == 2  # el gol rechazado sigue contando como gol normal
    lineup_service.record(ctx, s["host_owner"], s["contract_id"], [(s["host_owner"].id, 2)],
                          {s["host_owner"].id: ["OLIMPICO"]})  # corregir la planilla deja el tipo pendiente
    [fresh] = goal_claim_service.claims(ctx, s["guest_owner"], s["contract_id"])
    assert (fresh.kind, fresh.status) == ("OLIMPICO", "PENDING")
    clock.advance(timedelta(hours=73))
    [late] = goal_claim_service.claims(ctx, s["guest_owner"], s["contract_id"])
    assert (late.status, late.can_decide) == ("EXPIRED", False)
    with pytest.raises(ConflictError) as expired:
        goal_claim_service.decide(ctx, s["guest_owner"], fresh.id, accept=True)
    assert expired.value.code == "GOAL_CLAIM_EXPIRED"


def test_more_kinds_than_goals_is_refused(ctx, clock):
    s = confirmed_match(ctx, clock, 2, 1)
    with pytest.raises(DomainError) as error:
        lineup_service.record(ctx, s["host_owner"], s["contract_id"], [(s["host_owner"].id, 1)],
                              {s["host_owner"].id: ["CHILENA", "PENAL"]})
    assert error.value.code == "GOAL_KINDS_EXCEED_GOALS"


def test_special_cards_are_awarded_once_and_kept(ctx, clock):
    s = confirmed_match(ctx, clock, 2, 1)
    user_id = s["host_owner"].id
    first = special_card_service.award(ctx, user_id, ["RUBI"])
    clock.advance(timedelta(days=1))
    again = special_card_service.award(ctx, user_id, ["RUBI", "ESMERALDA"])
    assert again["RUBI"] == first["RUBI"] and set(again) == {"RUBI", "ESMERALDA"}
    assert len(list(ctx.db.scalars(select(SpecialCard).where(SpecialCard.user_id == user_id)))) == 2
    later = special_card_service.award(ctx, user_id, [])  # ya no cumple: se queda con las suyas
    assert set(later) == {"RUBI", "ESMERALDA"}
    card = manager_queries.player_card(ctx, s["guest_owner"], user_id).card
    assert (card.tier, card.display_tier) == ("BRONCE", "ESMERALDA")
    assert [sp.code for sp in card.specials if sp.earned_at] == ["RUBI", "ESMERALDA"]
