"""Pendientes del usuario (Sprint 11): todo lo que espera su acción, calculado en cada consulta.

No guarda copias: cada fuente consulta el estado actual, así nada queda desactualizado. El orden
pone primero lo que tiene hora más cercana.
"""

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select

from app.domain.team_rules import resolve_admin
from app.persistence.models_identity import UserAccount
from app.persistence.models_teams import Team, TeamMembership
from app.services import loan_queries
from app.services import pending_sources as sources
from app.services.context import ServiceContext
from app.services.team_service import member_views


@dataclass(frozen=True)
class PendingItem:
    kind: str  # SIGN_CONTRACT, REPORT_RESULT, RESULT_DISPUTED, CALLUP, TRANSFER_PLAYER, TRANSFER_OWNER, ...
    title: str
    detail: str
    target: str  # contract, team, league, venue, transfers, referee, loans
    target_id: int | None
    due_at: datetime | None


def _my_teams(ctx: ServiceContext, actor: UserAccount) -> tuple[list[Team], list[Team]]:
    teams = list(ctx.db.scalars(select(Team).join(TeamMembership).where(
        TeamMembership.user_id == actor.id, Team.status == "ACTIVE")))
    return teams, [t for t in teams if resolve_admin(member_views(t)) == actor.id]


def pending(ctx: ServiceContext, actor: UserAccount) -> list[PendingItem]:
    member_teams, admin_teams = _my_teams(ctx, actor)
    raw = (
        sources.contracts(ctx, admin_teams)
        + sources.callups(ctx, actor)
        + sources.transfers(ctx, actor, admin_teams)
        + sources.join_requests(ctx, admin_teams)
        + sources.referee(ctx, actor)
        + sources.bookings(ctx, actor)
        + sources.leagues(ctx, actor)
        + sources.ratings(ctx, actor, member_teams)
        + [("LOAN_PLAYER" if loan.status == "PENDING_PLAYER" else "LOAN_OWNER",
            f"Préstamo: {loan.player_name} para {loan.to_team}", "Acepta o rechaza el préstamo para un partido.",
            "loans", loan.id, loan.kickoff_at) for loan in loan_queries.awaiting_me(ctx, actor)]
    )
    items = [PendingItem(*r) for r in raw]
    far = datetime.max.replace(tzinfo=ctx.clock.now().tzinfo)
    return sorted(items, key=lambda i: (i.due_at or far, i.kind, i.target_id or 0))
