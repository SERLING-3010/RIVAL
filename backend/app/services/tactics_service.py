"""Alineación táctica (Sprint 19): la arma el administrador antes del partido; solo la ve su equipo.

El rival nunca la ve. Quien juega prestado ese partido (Sprint 13) la ve como parte de su equipo.
"""

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import delete, select

from app.domain import tactics_rules
from app.domain.contract_rules import ContractStatus
from app.domain.errors import ConflictError, NotFoundError
from app.domain.matchday_rules import CallUpStatus, check_before_kickoff
from app.domain.team_rules import is_matchday_staff
from app.persistence.models_contracts import MatchContract
from app.persistence.models_identity import UserAccount
from app.persistence.models_matchday import CallUp
from app.persistence.models_tactics import MatchTactic, MatchTacticSlot
from app.persistence.models_teams import Team
from app.services import loan_service
from app.services.audit_service import record_event
from app.services.context import ServiceContext
from app.services.contract_queries import load_contract, side_teams
from app.services.matchday_staff import staff_side
from app.services.team_service import member_views


@dataclass(frozen=True)
class SlotView:
    user_id: int
    display_name: str
    position: str | None
    still_going: bool  # False si después dijo que no va


@dataclass(frozen=True)
class TacticView:
    contract_id: int
    team_id: int
    players_per_side: int
    uses_formation: bool
    suggested_formations: list[str]
    formation: str | None
    starters: list[SlotView]
    subs: list[SlotView]
    eligible: list[SlotView]  # convocados que van y aún no están en la alineación
    can_edit: bool


def _my_team(ctx: ServiceContext, contract: MatchContract, actor: UserAccount) -> Team:
    for team in side_teams(ctx, contract).values():
        if any(m.user_id == actor.id for m in team.memberships) or \
                actor.id in loan_service.active_players(ctx, contract.id, team.id):
            return team
    raise NotFoundError("CONTRACT_NOT_FOUND", "El contrato no existe.")


def _going(ctx: ServiceContext, contract_id: int, team_id: int) -> dict[int, str]:
    rows = ctx.db.execute(select(CallUp.user_id, UserAccount.display_name)
                          .join(UserAccount, UserAccount.id == CallUp.user_id)
                          .where(CallUp.contract_id == contract_id, CallUp.team_id == team_id,
                                 CallUp.status == CallUpStatus.GOING))
    return {u: name for u, name in rows}


def _per_side(ctx: ServiceContext, contract: MatchContract) -> int:
    per_side = ctx.catalog.players_per_side(contract.sport_code, contract.modality_code)
    assert per_side is not None
    return per_side


def view(ctx: ServiceContext, actor: UserAccount, contract_id: int) -> TacticView:
    contract = load_contract(ctx, contract_id)
    team = _my_team(ctx, contract, actor)
    going = _going(ctx, contract.id, team.id)
    tactic = ctx.db.scalar(select(MatchTactic).where(MatchTactic.contract_id == contract.id,
                                                     MatchTactic.team_id == team.id))
    slots = list(ctx.db.scalars(select(MatchTacticSlot).where(MatchTacticSlot.tactic_id == tactic.id)
                                .order_by(MatchTacticSlot.sort_order))) if tactic else []
    names = {u.id: u.display_name for u in ctx.db.scalars(select(UserAccount).where(
        UserAccount.id.in_([s.user_id for s in slots])))}

    def slot(s: MatchTacticSlot) -> SlotView:
        return SlotView(s.user_id, names.get(s.user_id, ""), s.position, s.user_id in going)

    placed = {s.user_id for s in slots}
    return TacticView(
        contract_id=contract.id, team_id=team.id, players_per_side=_per_side(ctx, contract),
        uses_formation=contract.sport_code in tactics_rules.FORMATION_SPORTS,
        suggested_formations=tactics_rules.suggested_formations(contract.modality_code),
        formation=tactic.formation if tactic else None,
        starters=[slot(s) for s in slots if s.starter], subs=[slot(s) for s in slots if not s.starter],
        eligible=[SlotView(u, n, None, True) for u, n in sorted(going.items(), key=lambda x: x[1]) if u not in placed],
        can_edit=is_matchday_staff(member_views(team), actor.id) and contract.status != ContractStatus.CANCELLED)


def save(ctx: ServiceContext, actor: UserAccount, contract_id: int, formation: str | None,
         starters: list[tuple[int, str]], subs: list[int]) -> TacticView:
    contract = load_contract(ctx, contract_id, lock=True)
    _side, team = staff_side(ctx, contract, actor)
    if contract.status == ContractStatus.CANCELLED:
        raise ConflictError("CONTRACT_CANCELLED", "Este partido fue cancelado.")
    check_before_kickoff(loan_service.kickoff_of(ctx, contract), ctx.clock.now())
    per_side = _per_side(ctx, contract)
    clean_formation = tactics_rules.validate_formation(contract.sport_code, per_side, formation)
    clean = tactics_rules.validate_slots(starters, subs, per_side, set(_going(ctx, contract.id, team.id)))
    tactic = ctx.db.scalar(select(MatchTactic).where(MatchTactic.contract_id == contract.id,
                                                     MatchTactic.team_id == team.id))
    now: datetime = ctx.clock.now()
    if tactic is None:
        tactic = MatchTactic(contract_id=contract.id, team_id=team.id, updated_by=actor.id, updated_at=now)
        ctx.db.add(tactic)
        ctx.db.flush()
    tactic.formation, tactic.updated_by, tactic.updated_at = clean_formation, actor.id, now
    ctx.db.execute(delete(MatchTacticSlot).where(MatchTacticSlot.tactic_id == tactic.id))
    order = 0
    for user_id, position in clean:
        ctx.db.add(MatchTacticSlot(tactic_id=tactic.id, user_id=user_id, starter=True, sort_order=order,
                                   position=position))
        order += 1
    for user_id in subs:
        ctx.db.add(MatchTacticSlot(tactic_id=tactic.id, user_id=user_id, starter=False, sort_order=order))
        order += 1
    ctx.db.flush()
    record_event(ctx, action="TACTICS_SET", entity="match_contract", entity_id=contract.id, initiated_by=actor.id,
                 after={"team_id": team.id, "starters": len(clean), "subs": len(subs)})  # sin la formación:
    # la actividad del contrato la ven los dos equipos y el rival no debe conocer la táctica
    return view(ctx, actor, contract.id)
