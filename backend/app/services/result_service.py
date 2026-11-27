"""Reporte del resultado: cada administrador reporta el marcador; vale cuando ambos coinciden.

Bloquea la fila del contrato (FOR UPDATE), así dos reportes simultáneos se resuelven en serie.
El partido que cuenta es el de la versión firmada, aunque haya un cambio pendiente sin aceptar.
"""

from app.domain.contract_rules import ContractStatus
from app.domain.errors import ConflictError
from app.domain.result_rules import ResultStatus, check_can_report, resolve_result, validate_score
from app.persistence.models_contracts import MatchContract
from app.persistence.models_identity import UserAccount
from app.persistence.models_results import MatchResult, MatchResultReport
from app.services import card_awards, cup_advance, settlement_service
from app.services.audit_service import record_event
from app.services.context import ServiceContext
from app.services.contract_queries import get_version, load_contract, terms_of
from app.services.matchday_staff import staff_side
from app.services.result_queries import get_result, reports_of

_ACTION = {
    ResultStatus.PENDING: "RESULT_REPORTED",
    ResultStatus.CONFIRMED: "RESULT_CONFIRMED",
    ResultStatus.DISPUTED: "RESULT_DISPUTED",
}


def _require_played(ctx: ServiceContext, contract: MatchContract) -> None:
    if contract.status == ContractStatus.CANCELLED:
        raise ConflictError("CONTRACT_CANCELLED", "Este partido fue cancelado.")
    if contract.signed_version_id is None:
        raise ConflictError("CONTRACT_NOT_SIGNED", "El resultado se reporta solo en partidos firmados por ambos.")
    check_can_report(terms_of(get_version(ctx, contract.signed_version_id)).kickoff_at, ctx.clock.now())


def report(ctx: ServiceContext, actor: UserAccount, contract_id: int, host_score: int, guest_score: int) -> MatchResult:
    contract = load_contract(ctx, contract_id, lock=True)
    _side, team = staff_side(ctx, contract, actor)
    _require_played(ctx, contract)
    validate_score(host_score, guest_score)
    now = ctx.clock.now()
    result = get_result(ctx, contract.id)
    if result is None:
        result = MatchResult(contract_id=contract.id, status=ResultStatus.PENDING.value, updated_at=now)
        ctx.db.add(result)
    elif result.status == ResultStatus.CONFIRMED:
        raise ConflictError("RESULT_ALREADY_CONFIRMED", "El resultado ya fue confirmado por ambos equipos.")
    mine = next((r for r in reports_of(ctx, contract.id) if r.team_id == team.id), None)
    before = None if mine is None else {"host_score": mine.host_score, "guest_score": mine.guest_score}
    if mine is None:
        mine = MatchResultReport(contract_id=contract.id, team_id=team.id, host_score=host_score,
                                 guest_score=guest_score, reported_by=actor.id, reported_at=now)
        ctx.db.add(mine)
    else:
        mine.host_score, mine.guest_score, mine.reported_by, mine.reported_at = host_score, guest_score, actor.id, now
    ctx.db.flush()
    status, score = resolve_result([(r.host_score, r.guest_score) for r in reports_of(ctx, contract.id)])
    result.status, result.updated_at = status.value, now
    result.host_score, result.guest_score = score if score else (None, None)
    result.confirmed_at = now if status == ResultStatus.CONFIRMED else None
    ctx.db.flush()
    if status == ResultStatus.CONFIRMED and score:
        settlement_service.settle(ctx, contract.id, contract.host_team_id, contract.guest_team_id, *score)
    record_event(ctx, action=_ACTION[status], entity="match_contract", entity_id=contract.id, initiated_by=actor.id,
                 before=before, after={"team_id": team.id, "host_score": host_score, "guest_score": guest_score,
                                       "result_status": status.value})
    if status == ResultStatus.CONFIRMED and score:
        cup_advance.on_result(ctx, contract.id, *score)  # si es de copa, avanza el ganador
        card_awards.after_result(ctx, contract.id, contract.host_team_id, contract.guest_team_id)  # Sprint 26
    return result
