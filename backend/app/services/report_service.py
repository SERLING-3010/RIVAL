"""Reportes de usuarios (Sprint 12): agresión, inasistencia, perfil falso u otro motivo.

Un reporte no sanciona a nadie por sí solo: lo revisa una persona moderadora.
"""

from datetime import timedelta

from sqlalchemy import func, select

from app.domain.errors import DomainError, NotFoundError
from app.domain.moderation_rules import ReportCategory, check_report_quota, validate_text
from app.persistence.models_identity import UserAccount
from app.persistence.models_moderation import Report
from app.persistence.models_teams import Team
from app.services.audit_service import record_event
from app.services.context import ServiceContext


def create_report(ctx: ServiceContext, actor: UserAccount, *, category: ReportCategory, description: str,
                  target_user_id: int | None = None, target_team_id: int | None = None,
                  contract_id: int | None = None) -> Report:
    if (target_user_id is None) == (target_team_id is None) or target_user_id == actor.id:
        raise DomainError("INVALID_REPORT_TARGET", "Reporta a una persona o a un equipo (que no seas tú).")
    if target_user_id is not None and ctx.db.get(UserAccount, target_user_id) is None:
        raise NotFoundError("USER_NOT_FOUND", "Esa persona no existe en RIVAL.")
    if target_team_id is not None:
        team = ctx.db.get(Team, target_team_id)
        if team is None:
            raise NotFoundError("TEAM_NOT_FOUND", "El equipo no existe.")
        if any(m.user_id == actor.id for m in team.memberships):
            raise DomainError("INVALID_REPORT_TARGET", "No puedes reportar a tu propio equipo.")
    since = ctx.clock.now() - timedelta(days=1)
    check_report_quota(ctx.db.scalar(select(func.count()).select_from(Report).where(
        Report.reporter_id == actor.id, Report.created_at >= since)) or 0)
    report = Report(reporter_id=actor.id, target_user_id=target_user_id, target_team_id=target_team_id,
                    contract_id=contract_id, category=category.value,
                    description=validate_text(description, 10, 500, "La descripción"), status="OPEN",
                    created_at=ctx.clock.now())
    ctx.db.add(report)
    ctx.db.flush()
    record_event(ctx, action="REPORT_CREATED", entity="report", entity_id=report.id, initiated_by=actor.id,
                 after={"category": report.category, "target_user_id": target_user_id,
                        "target_team_id": target_team_id})
    return report
