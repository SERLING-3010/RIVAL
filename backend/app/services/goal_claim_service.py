"""Goles con tipo (Sprint 23): el DT o el capitán rival confirma o rechaza cada uno.

Un gol rechazado sigue contando como gol normal; solo pierde el tipo. Si el rival no responde en 72
horas, el tipo no cuenta y ya no se puede confirmar. Cada decisión queda en la auditoría con su nombre.
"""

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import func, or_, select

from app.domain.errors import ConflictError, NotFoundError, PermissionDeniedError
from app.domain.special_cards import CLAIM_WINDOW
from app.persistence.models_cards import GoalClaim
from app.persistence.models_contracts import MatchContract
from app.persistence.models_identity import UserAccount
from app.services import card_awards
from app.services.audit_service import record_event
from app.services.context import ServiceContext
from app.services.contract_queries import load_contract, member_side, side_teams
from app.services.matchday_staff import staff_side

PENDING, CONFIRMED, REJECTED, EXPIRED = "PENDING", "CONFIRMED", "REJECTED", "EXPIRED"


@dataclass(frozen=True)
class GoalClaimView:
    id: int
    team_id: int
    user_id: int
    display_name: str
    kind: str
    status: str  # PENDING, CONFIRMED, REJECTED o EXPIRED
    claimed_at: datetime
    can_decide: bool  # el actor es DT o capitán del rival y aún está a tiempo


def _status(claim: GoalClaim, now: datetime) -> str:
    if claim.status == PENDING and claim.claimed_at + CLAIM_WINDOW <= now:
        return EXPIRED
    return claim.status


def _rival_staff_team(ctx: ServiceContext, contract_id: int, actor: UserAccount) -> int | None:
    """El equipo que el actor maneja en ese partido, o None si no es DT ni capitán."""
    try:
        return staff_side(ctx, load_contract(ctx, contract_id), actor)[1].id
    except (PermissionDeniedError, ConflictError):
        return None


def claims(ctx: ServiceContext, actor: UserAccount, contract_id: int) -> list[GoalClaimView]:
    contract = load_contract(ctx, contract_id)
    member_side(side_teams(ctx, contract), actor)  # 404 si no es de ninguno de los dos equipos
    mine = _rival_staff_team(ctx, contract_id, actor)
    now = ctx.clock.now()
    rows = ctx.db.execute(select(GoalClaim, UserAccount.display_name)
                          .join(UserAccount, UserAccount.id == GoalClaim.user_id)
                          .where(GoalClaim.contract_id == contract_id).order_by(GoalClaim.id)).all()
    return [GoalClaimView(c.id, c.team_id, c.user_id, name, c.kind, _status(c, now), c.claimed_at,
                          can_decide=mine is not None and mine != c.team_id and _status(c, now) == PENDING)
            for c, name in rows]


def decide(ctx: ServiceContext, actor: UserAccount, claim_id: int, accept: bool) -> GoalClaim:
    found = ctx.db.get(GoalClaim, claim_id)
    if found is None:
        raise NotFoundError("GOAL_CLAIM_NOT_FOUND", "Ese gol no existe.")
    # Primero el contrato y luego el gol, en el mismo orden que la planilla (evita interbloqueos).
    contract = load_contract(ctx, found.contract_id, lock=True)
    claim = ctx.db.get(GoalClaim, claim_id, with_for_update=True, populate_existing=True)
    if claim is None:  # la planilla se corrigió mientras tanto
        raise NotFoundError("GOAL_CLAIM_NOT_FOUND", "Ese gol no existe.")
    member_side(side_teams(ctx, contract), actor)
    _side, team = staff_side(ctx, contract, actor)
    if team.id == claim.team_id:
        raise PermissionDeniedError("RIVAL_ONLY", "El tipo de gol lo confirma el equipo rival.")
    status = _status(claim, ctx.clock.now())
    if status == EXPIRED:
        raise ConflictError("GOAL_CLAIM_EXPIRED", "Pasaron las 72 horas: este gol ya no se puede confirmar.")
    if status != PENDING:
        raise ConflictError("GOAL_CLAIM_DECIDED", "Este gol ya fue confirmado o rechazado.")
    claim.status = CONFIRMED if accept else REJECTED
    claim.decided_by, claim.decided_at = actor.id, ctx.clock.now()
    ctx.db.flush()
    record_event(ctx, action="GOAL_KIND_CONFIRMED" if accept else "GOAL_KIND_REJECTED", entity="match_contract",
                 entity_id=claim.contract_id, initiated_by=claim.claimed_by, approved_by=actor.id,
                 before={"status": PENDING},
                 after={"claim_id": claim.id, "user_id": claim.user_id, "kind": claim.kind, "status": claim.status})
    if accept:
        card_awards.refresh_players(ctx, [claim.user_id])  # Sprint 26: puede completar una hazaña
    return claim


def confirmed_kinds(ctx: ServiceContext, user_id: int) -> dict[str, int]:
    """Goles con tipo que el rival confirmó, por tipo."""
    rows = ctx.db.execute(select(GoalClaim.kind, func.count()).where(
        GoalClaim.user_id == user_id, GoalClaim.status == CONFIRMED).group_by(GoalClaim.kind))
    return {kind: int(n) for kind, n in rows}


Row = tuple[str, str, str, str, int | None, datetime | None]


def awaiting(ctx: ServiceContext, staff_team_ids: list[int]) -> list[Row]:
    """Pendientes: partidos donde el rival marcó goles con tipo que este equipo aún no responde."""
    if not staff_team_ids:
        return []
    now, per_contract = ctx.clock.now(), dict[int, tuple[int, datetime]]()
    rows = ctx.db.execute(select(GoalClaim, MatchContract)
                          .join(MatchContract, MatchContract.id == GoalClaim.contract_id)
                          .where(GoalClaim.status == PENDING, GoalClaim.claimed_at > now - CLAIM_WINDOW,
                                 or_(MatchContract.host_team_id.in_(staff_team_ids),
                                     MatchContract.guest_team_id.in_(staff_team_ids))))
    for claim, contract in rows:
        mine = contract.host_team_id if contract.host_team_id in staff_team_ids else contract.guest_team_id
        if claim.team_id != mine:
            count, due = per_contract.get(contract.id, (0, claim.claimed_at + CLAIM_WINDOW))
            per_contract[contract.id] = (count + 1, min(due, claim.claimed_at + CLAIM_WINDOW))
    return [("CONFIRM_GOAL_KINDS", "Confirmar goles especiales",
             f"El rival marcó {n} {'gol' if n == 1 else 'goles'} con tipo; confírmalos o recházalos.",
             "contract", contract_id, due) for contract_id, (n, due) in per_contract.items()]
