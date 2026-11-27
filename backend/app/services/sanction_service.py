"""Moderación (Sprint 12): moderadores, cola de reportes y sanciones con motivo. Apelaciones: appeal_service."""

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import or_, select

from app.domain.errors import ConflictError, NotFoundError, PermissionDeniedError
from app.domain.identity_rules import normalize_email
from app.domain.moderation_rules import SanctionKind, suspension_end, validate_text
from app.domain.team_rules import resolve_admin
from app.persistence.models_identity import UserAccount
from app.persistence.models_moderation import Moderator, Report, Sanction
from app.persistence.models_teams import Team
from app.services.audit_service import record_event
from app.services.context import ServiceContext
from app.services.team_service import member_views


@dataclass(frozen=True)
class ReportView:
    id: int
    category: str
    description: str
    target: str  # nombre de la persona o del equipo reportado
    created_at: datetime


def grant_moderator(ctx: ServiceContext, email: str) -> UserAccount:
    user = ctx.db.scalar(select(UserAccount).where(UserAccount.email == normalize_email(email)))
    if user is None:
        raise NotFoundError("USER_NOT_FOUND", "No hay una cuenta con ese correo.")
    if ctx.db.get(Moderator, user.id) is None:
        ctx.db.add(Moderator(user_id=user.id, granted_at=ctx.clock.now()))
        ctx.db.flush()
        record_event(ctx, action="MODERATOR_GRANTED", entity="user_account", entity_id=user.id, initiated_by=None,
                     actor_type="AUTOMATION")
    return user


def is_moderator(ctx: ServiceContext, user_id: int) -> bool:
    return ctx.db.get(Moderator, user_id) is not None


def require_moderator(ctx: ServiceContext, actor: UserAccount) -> None:
    if not is_moderator(ctx, actor.id):
        raise PermissionDeniedError("MODERATORS_ONLY", "Solo las personas moderadoras pueden hacer esto.")


def involved(ctx: ServiceContext, report: Report, user_id: int) -> bool:
    team = ctx.db.get(Team, report.target_team_id) if report.target_team_id else None
    return user_id in {report.reporter_id, report.target_user_id} or bool(
        team and any(m.user_id == user_id for m in team.memberships))


def _open_report(ctx: ServiceContext, actor: UserAccount, report_id: int) -> Report:
    require_moderator(ctx, actor)
    report = ctx.db.get(Report, report_id, with_for_update=True)
    if report is None:
        raise NotFoundError("REPORT_NOT_FOUND", "El reporte no existe.")
    if involved(ctx, report, actor.id):
        raise PermissionDeniedError("CONFLICT_OF_INTEREST", "No puedes decidir un reporte en el que estás involucrado.")
    if report.status != "OPEN":
        raise ConflictError("REPORT_ALREADY_DECIDED", "Este reporte ya fue decidido.")
    return report


def queue(ctx: ServiceContext, actor: UserAccount) -> list[ReportView]:
    require_moderator(ctx, actor)
    views = []
    for r in ctx.db.scalars(select(Report).where(Report.status == "OPEN").order_by(Report.created_at)):
        if involved(ctx, r, actor.id):
            continue
        user = ctx.db.get(UserAccount, r.target_user_id) if r.target_user_id else None
        team = ctx.db.get(Team, r.target_team_id) if r.target_team_id else None
        target = user.display_name if user else f"Equipo {team.name}" if team else ""
        views.append(ReportView(id=r.id, category=r.category, description=r.description, target=target,
                                created_at=r.created_at))
    return views


def _close(ctx: ServiceContext, report: Report, actor: UserAccount, status: str, note: str) -> None:
    report.status, report.decided_by, report.decided_at = status, actor.id, ctx.clock.now()
    report.decision_note = validate_text(note, 5, 300, "El motivo")
    ctx.db.flush()


def dismiss(ctx: ServiceContext, actor: UserAccount, report_id: int, note: str) -> Report:
    report = _open_report(ctx, actor, report_id)
    _close(ctx, report, actor, "DISMISSED", note)
    record_event(ctx, action="REPORT_DISMISSED", entity="report", entity_id=report.id, initiated_by=report.reporter_id,
                 approved_by=actor.id, after={"note": report.decision_note})
    return report


def sanction(ctx: ServiceContext, actor: UserAccount, report_id: int, kind: SanctionKind, days: int | None,
             reason: str) -> Sanction:
    report = _open_report(ctx, actor, report_id)
    target = report.target_user_id
    if target is None:  # [SUPUESTO] reporte contra un equipo: se sanciona a su administrador actual
        team = ctx.db.get(Team, report.target_team_id)
        target = resolve_admin(member_views(team)) if team else None
    if target is None:
        raise ConflictError("NO_SANCTION_TARGET", "El equipo no tiene administrador a quien sancionar.")
    ends_at = suspension_end(kind, days, ctx.clock.now())
    _close(ctx, report, actor, "ACTIONED", reason)
    item = Sanction(user_id=target, report_id=report.id, kind=kind.value, reason=report.decision_note or "",
                    ends_at=ends_at, status="ACTIVE", decided_by=actor.id, created_at=ctx.clock.now())
    ctx.db.add(item)
    ctx.db.flush()
    record_event(ctx, action="USER_SANCTIONED", entity="sanction", entity_id=item.id, initiated_by=report.reporter_id,
                 approved_by=actor.id, after={"user_id": target, "kind": item.kind,
                                              "ends_at": ends_at.isoformat() if ends_at else None})
    return item


def active_suspension(ctx: ServiceContext, user_id: int) -> Sanction | None:
    return ctx.db.scalar(select(Sanction).where(
        Sanction.user_id == user_id, Sanction.kind == SanctionKind.SUSPENSION, Sanction.status == "ACTIVE",
        or_(Sanction.ends_at.is_(None), Sanction.ends_at > ctx.clock.now())))


def my_sanctions(ctx: ServiceContext, actor: UserAccount) -> list[Sanction]:
    return list(ctx.db.scalars(select(Sanction).where(Sanction.user_id == actor.id).order_by(Sanction.id.desc())))
