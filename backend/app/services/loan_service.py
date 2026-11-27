"""Préstamo de un jugador para un solo partido (Sprint 13).

El administrador del equipo que juega lo pide; acepta el administrador del equipo dueño y después el
jugador (nadie acepta por él). Con el préstamo activo, el jugador puede ser convocado y estar en la
planilla de ese partido; no cambia de equipo ni se mueven monedas.
"""

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select

from app.domain.contract_rules import ContractStatus
from app.domain.errors import ConflictError, DomainError, NotFoundError, PermissionDeniedError
from app.domain.loan_rules import OPEN_LOANS, LoanStatus
from app.domain.matchday_rules import check_before_kickoff
from app.domain.roles import TeamRole
from app.domain.team_rules import resolve_admin
from app.persistence.models_contracts import MatchContract
from app.persistence.models_identity import UserAccount
from app.persistence.models_manager import PlayerLoan
from app.persistence.models_teams import Team
from app.services.audit_service import record_event
from app.services.context import ServiceContext
from app.services.contract_queries import admin_side, get_version, load_contract, terms_of
from app.services.team_service import get_active_team, member_views, require_admin


@dataclass(frozen=True)
class LoanView:
    id: int
    contract_id: int
    player_id: int
    player_name: str
    from_team: str
    to_team: str
    status: str
    kickoff_at: datetime


def kickoff_of(ctx: ServiceContext, contract: MatchContract) -> datetime:
    return terms_of(get_version(ctx, contract.signed_version_id or contract.current_version_id)).kickoff_at


def request(ctx: ServiceContext, actor: UserAccount, contract_id: int, player_id: int, from_team_id: int) -> PlayerLoan:
    contract = load_contract(ctx, contract_id, lock=True)
    _side, team = admin_side(ctx, contract, actor)
    if contract.status == ContractStatus.CANCELLED:
        raise ConflictError("CONTRACT_CANCELLED", "Este partido fue cancelado.")
    check_before_kickoff(kickoff_of(ctx, contract), ctx.clock.now())
    owner = get_active_team(ctx, from_team_id)
    member = next((m for m in owner.memberships if m.user_id == player_id), None)
    if owner.id in (contract.host_team_id, contract.guest_team_id) or owner.sport_code != contract.sport_code:
        raise DomainError("LOAN_NOT_ALLOWED", "Solo se pide prestado a un equipo del mismo deporte que no juega este partido.")
    if member is None or member.role != TeamRole.PLAYER or any(m.user_id == player_id for m in team.memberships):
        raise DomainError("LOAN_NOT_ALLOWED", "Solo se presta a un jugador (no DT ni capitán) que no esté en tu equipo.")
    if ctx.db.scalar(select(PlayerLoan.id).where(PlayerLoan.contract_id == contract.id, PlayerLoan.player_id == player_id,
                                                 PlayerLoan.status.in_(OPEN_LOANS))) is not None:
        raise ConflictError("LOAN_ALREADY_OPEN", "Ya hay un préstamo de ese jugador para este partido.")
    loan = PlayerLoan(contract_id=contract.id, player_id=player_id, from_team_id=owner.id, to_team_id=team.id,
                      status=LoanStatus.PENDING_OWNER.value, requested_by=actor.id, created_at=ctx.clock.now())
    ctx.db.add(loan)
    ctx.db.flush()
    record_event(ctx, action="LOAN_REQUESTED", entity="match_contract", entity_id=contract.id, initiated_by=actor.id,
                 after={"loan_id": loan.id, "player_id": player_id, "from_team_id": owner.id})
    return loan


def _loan(ctx: ServiceContext, loan_id: int) -> tuple[PlayerLoan, MatchContract]:
    loan = ctx.db.get(PlayerLoan, loan_id, with_for_update=True)
    if loan is None:
        raise NotFoundError("LOAN_NOT_FOUND", "El préstamo no existe.")
    return loan, load_contract(ctx, loan.contract_id)


def _set(ctx: ServiceContext, loan: PlayerLoan, status: LoanStatus, action: str, actor_id: int) -> PlayerLoan:
    before, loan.status, loan.decided_at = loan.status, status.value, ctx.clock.now()
    ctx.db.flush()
    record_event(ctx, action=action, entity="match_contract", entity_id=loan.contract_id, initiated_by=actor_id,
                 before={"status": before}, after={"loan_id": loan.id, "status": loan.status})
    return loan


def decide_owner(ctx: ServiceContext, actor: UserAccount, loan_id: int, accept: bool) -> PlayerLoan:
    loan, contract = _loan(ctx, loan_id)
    require_admin(get_active_team(ctx, loan.from_team_id), actor)
    if loan.status != LoanStatus.PENDING_OWNER:
        raise ConflictError("LOAN_NOT_PENDING", "Este préstamo ya no espera tu decisión.")
    check_before_kickoff(kickoff_of(ctx, contract), ctx.clock.now())
    status = LoanStatus.PENDING_PLAYER if accept else LoanStatus.REJECTED
    return _set(ctx, loan, status, "LOAN_OWNER_ACCEPTED" if accept else "LOAN_OWNER_REJECTED", actor.id)


def decide_player(ctx: ServiceContext, actor: UserAccount, loan_id: int, accept: bool) -> PlayerLoan:
    loan, contract = _loan(ctx, loan_id)
    if actor.id != loan.player_id:
        raise PermissionDeniedError("PLAYER_ONLY", "Solo el jugador decide si juega prestado.")
    if loan.status != LoanStatus.PENDING_PLAYER:
        raise PermissionDeniedError("OWNER_FIRST", "Primero debe aceptar el administrador de tu equipo.")
    check_before_kickoff(kickoff_of(ctx, contract), ctx.clock.now())
    status = LoanStatus.ACTIVE if accept else LoanStatus.REJECTED
    return _set(ctx, loan, status, "LOAN_ACTIVE" if accept else "LOAN_PLAYER_REJECTED", actor.id)


def cancel(ctx: ServiceContext, actor: UserAccount, loan_id: int) -> PlayerLoan:
    loan, contract = _loan(ctx, loan_id)
    teams = [t for t in (ctx.db.get(Team, loan.to_team_id), ctx.db.get(Team, loan.from_team_id)) if t]
    involved = actor.id == loan.player_id or any(resolve_admin(member_views(t)) == actor.id for t in teams)
    if not involved:
        raise PermissionDeniedError("LOAN_PARTIES_ONLY", "Solo los administradores o el jugador cancelan el préstamo.")
    if loan.status not in OPEN_LOANS:
        raise ConflictError("LOAN_CLOSED", "Este préstamo ya está cerrado.")
    check_before_kickoff(kickoff_of(ctx, contract), ctx.clock.now())
    return _set(ctx, loan, LoanStatus.CANCELLED, "LOAN_CANCELLED", actor.id)


def active_players(ctx: ServiceContext, contract_id: int, team_id: int) -> set[int]:
    return set(ctx.db.scalars(select(PlayerLoan.player_id).where(
        PlayerLoan.contract_id == contract_id, PlayerLoan.to_team_id == team_id, PlayerLoan.status == LoanStatus.ACTIVE)))
