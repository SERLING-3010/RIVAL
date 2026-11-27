"""Lectura de préstamos (Sprint 13): los del partido para su equipo y los que esperan mi decisión."""

from sqlalchemy import or_, select

from app.domain.loan_rules import LoanStatus
from app.domain.team_rules import resolve_admin
from app.persistence.models_identity import UserAccount
from app.persistence.models_manager import PlayerLoan
from app.persistence.models_teams import Team, TeamMembership
from app.services.context import ServiceContext
from app.services.contract_queries import load_contract, member_side, side_teams
from app.services.loan_service import LoanView, kickoff_of
from app.services.team_service import member_views


def _view(ctx: ServiceContext, loan: PlayerLoan) -> LoanView:
    player = ctx.db.get(UserAccount, loan.player_id)
    src, dst = ctx.db.get(Team, loan.from_team_id), ctx.db.get(Team, loan.to_team_id)
    return LoanView(id=loan.id, contract_id=loan.contract_id, player_id=loan.player_id,
                    player_name=player.display_name if player else "", from_team=src.name if src else "",
                    to_team=dst.name if dst else "", status=loan.status,
                    kickoff_at=kickoff_of(ctx, load_contract(ctx, loan.contract_id)))


def for_contract(ctx: ServiceContext, actor: UserAccount, contract_id: int) -> list[LoanView]:
    """Préstamos que pidió mi equipo para este partido."""
    contract = load_contract(ctx, contract_id)
    teams = side_teams(ctx, contract)
    team = teams[member_side(teams, actor)]
    return [_view(ctx, l) for l in ctx.db.scalars(select(PlayerLoan).where(
        PlayerLoan.contract_id == contract.id, PlayerLoan.to_team_id == team.id).order_by(PlayerLoan.id))]


def awaiting_me(ctx: ServiceContext, actor: UserAccount) -> list[LoanView]:
    """Préstamos que esperan mi decisión: como jugador prestado o como administrador del equipo dueño."""
    admin_of = [t.id for t in ctx.db.scalars(select(Team).join(TeamMembership).where(
        TeamMembership.user_id == actor.id, Team.status == "ACTIVE")) if resolve_admin(member_views(t)) == actor.id]
    rows = ctx.db.scalars(select(PlayerLoan).where(or_(
        (PlayerLoan.player_id == actor.id) & (PlayerLoan.status == LoanStatus.PENDING_PLAYER),
        PlayerLoan.from_team_id.in_(admin_of) & (PlayerLoan.status == LoanStatus.PENDING_OWNER))))
    now = ctx.clock.now()
    return [v for v in (_view(ctx, l) for l in rows) if v.kickoff_at > now]
