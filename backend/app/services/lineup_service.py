"""Planilla del partido: quién jugó y cuántos goles hizo cada uno (Sprint 7, RIV-016).

Solo con resultado confirmado. Cada equipo registra la suya; corregirla reemplaza la anterior y
queda en la auditoría con antes y después. De aquí salen las estadísticas reales de la ficha.
"""

from sqlalchemy import delete, select

from app.domain.errors import ConflictError
from app.domain.manager_rules import validate_lineup
from app.domain.result_rules import ResultStatus
from app.persistence.models_identity import UserAccount
from app.persistence.models_manager import MatchAppearance
from app.services import loan_service
from app.services.audit_service import record_event
from app.services.context import ServiceContext
from app.services.contract_queries import load_contract
from app.services.matchday_staff import staff_side
from app.services.result_queries import get_result


def record(ctx: ServiceContext, actor: UserAccount, contract_id: int, entries: list[tuple[int, int]]) -> None:
    contract = load_contract(ctx, contract_id, lock=True)
    side, team = staff_side(ctx, contract, actor)
    result = get_result(ctx, contract.id)
    if result is None or result.status != ResultStatus.CONFIRMED or result.host_score is None:
        raise ConflictError("RESULT_NOT_CONFIRMED", "La planilla se registra cuando el resultado está confirmado.")
    score = result.host_score if side == "HOST" else result.guest_score
    members = {m.user_id for m in team.memberships} | loan_service.active_players(ctx, contract.id, team.id)
    validate_lineup(entries, team_score=score or 0, members=members)  # con préstamos activos (Sprint 13)
    previous = list(ctx.db.scalars(select(MatchAppearance).where(
        MatchAppearance.contract_id == contract.id, MatchAppearance.team_id == team.id)))
    before = {str(a.user_id): a.goals for a in previous} or None
    ctx.db.execute(delete(MatchAppearance).where(MatchAppearance.contract_id == contract.id,
                                                 MatchAppearance.team_id == team.id))
    now = ctx.clock.now()
    for user_id, goals in entries:
        ctx.db.add(MatchAppearance(contract_id=contract.id, team_id=team.id, user_id=user_id, goals=goals,
                                   recorded_by=actor.id, recorded_at=now))
    ctx.db.flush()
    record_event(ctx, action="LINEUP_RECORDED", entity="match_contract", entity_id=contract.id,
                 initiated_by=actor.id, before=before,
                 after={"team_id": team.id, "players": {str(u): g for u, g in entries}})
