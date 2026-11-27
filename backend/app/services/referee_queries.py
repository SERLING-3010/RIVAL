"""Lectura de árbitros asignados a partidos de liga (Sprint 8)."""

from sqlalchemy import select

from app.persistence.models_identity import UserAccount
from app.persistence.models_league_matches import RefereeAssignment
from app.services.context import ServiceContext
from app.services.contract_views import RefereeView

ACTIVE = ("PENDING", "ACCEPTED")


def active_assignment(ctx: ServiceContext, contract_id: int) -> RefereeAssignment | None:
    return ctx.db.scalar(select(RefereeAssignment).where(RefereeAssignment.contract_id == contract_id,
                                                         RefereeAssignment.status.in_(ACTIVE)))


def referee_view(ctx: ServiceContext, contract_id: int) -> RefereeView | None:
    assignment = active_assignment(ctx, contract_id)
    referee = ctx.db.get(UserAccount, assignment.referee_id) if assignment else None
    if assignment is None or referee is None:
        return None
    return RefereeView(assignment_id=assignment.id, referee_id=referee.id, display_name=referee.display_name,
                       status=assignment.status)
