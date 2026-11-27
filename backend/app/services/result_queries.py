"""Lectura del resultado y de los reportes de cada equipo (Sprint 4)."""

from sqlalchemy import select

from app.persistence.models_contracts import MatchContract
from app.persistence.models_results import MatchResult, MatchResultReport
from app.services.context import ServiceContext
from app.services.contract_views import ResultReportView, ResultView


def get_result(ctx: ServiceContext, contract_id: int) -> MatchResult | None:
    return ctx.db.scalar(select(MatchResult).where(MatchResult.contract_id == contract_id))


def reports_of(ctx: ServiceContext, contract_id: int) -> list[MatchResultReport]:
    return list(ctx.db.scalars(select(MatchResultReport).where(
        MatchResultReport.contract_id == contract_id).order_by(MatchResultReport.reported_at, MatchResultReport.id)))


def result_view(ctx: ServiceContext, contract: MatchContract) -> ResultView | None:
    result = get_result(ctx, contract.id)
    if result is None:
        return None
    reports = [
        ResultReportView(side="HOST" if r.team_id == contract.host_team_id else "GUEST", host_score=r.host_score,
                         guest_score=r.guest_score, reported_at=r.reported_at)
        for r in reports_of(ctx, contract.id)
    ]
    return ResultView(status=result.status, host_score=result.host_score, guest_score=result.guest_score,
                      reports=reports, by_referee=result.referee_id is not None)
