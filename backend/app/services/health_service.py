"""Centro de salud del sistema: invariantes deterministas (Sprint 0, sección 7.6).

Cada chequeo busca un estado que nunca debería existir. Severidad: S0 crítico, S1 alto, S3 bajo.
"""

from dataclasses import dataclass
from datetime import timedelta

from sqlalchemy import func, select

from app.domain.contract_rules import ContractStatus
from app.domain.match_rules import RequestStatus
from app.domain.result_rules import ResultStatus
from app.domain.team_rules import resolve_admin
from app.persistence.models_contracts import MatchContract, MatchContractSignature
from app.persistence.models_matches import MatchRequest
from app.persistence.models_results import MatchResult
from app.persistence.models_teams import Team
from app.services.audit_service import verify_chain
from app.services.context import ServiceContext
from app.services.contract_queries import get_version, terms_of
from app.services.team_service import member_views

RESULT_GRACE = timedelta(hours=48)


@dataclass(frozen=True)
class HealthFinding:
    severity: str
    code: str
    entity: str
    entity_id: int | None
    message: str


def _audit(ctx: ServiceContext) -> list[HealthFinding]:
    if verify_chain(ctx.db):
        return []
    return [HealthFinding("S0", "AUDIT_CHAIN_BROKEN", "audit_event", None,
                          "La cadena de auditoría no coincide: alguien alteró eventos.")]


def _teams(ctx: ServiceContext) -> list[HealthFinding]:
    return [
        HealthFinding("S1", "TEAM_WITHOUT_ADMIN", "team", team.id, "Equipo activo sin administrador.")
        for team in ctx.db.scalars(select(Team).where(Team.status == "ACTIVE"))
        if resolve_admin(member_views(team)) is None
    ]


def _contracts(ctx: ServiceContext) -> list[HealthFinding]:
    findings = []
    for contract in ctx.db.scalars(select(MatchContract).where(MatchContract.signed_version_id.is_not(None))):
        signatures = ctx.db.scalar(select(func.count(func.distinct(MatchContractSignature.team_id))).where(
            MatchContractSignature.version_id == contract.signed_version_id)) or 0
        if signatures < 2:
            findings.append(HealthFinding("S0", "SIGNED_WITHOUT_TWO_SIGNATURES", "match_contract", contract.id,
                                          "Contrato firmado sin la firma de ambos equipos en esa versión."))
        if contract.status == ContractStatus.CANCELLED:
            continue
        kickoff = terms_of(get_version(ctx, contract.signed_version_id)).kickoff_at
        result = ctx.db.scalar(select(MatchResult.status).where(MatchResult.contract_id == contract.id))
        if result != ResultStatus.CONFIRMED and ctx.clock.now() > kickoff + RESULT_GRACE:
            findings.append(HealthFinding("S3", "RESULT_OVERDUE", "match_contract", contract.id,
                                          "Partido jugado sin resultado confirmado 48 h después."))
    return findings


def _requests(ctx: ServiceContext) -> list[HealthFinding]:
    orphans = ctx.db.scalars(select(MatchRequest.id).where(
        MatchRequest.status == RequestStatus.MATCHED,
        ~select(MatchContract.id).where(MatchContract.request_id == MatchRequest.id).exists()))
    return [HealthFinding("S1", "MATCHED_WITHOUT_CONTRACT", "match_request", rid,
                          "Búsqueda con rival aceptado pero sin contrato.") for rid in orphans]


def run_checks(ctx: ServiceContext) -> list[HealthFinding]:
    findings = _audit(ctx) + _teams(ctx) + _contracts(ctx) + _requests(ctx)
    return sorted(findings, key=lambda f: (f.severity, f.code, f.entity_id or 0))
