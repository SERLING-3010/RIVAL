"""Centro de salud del sistema: invariantes deterministas (Sprint 0, sección 7.6).

Cada chequeo busca un estado que nunca debería existir. Severidad: S0 crítico, S1 alto, S3 bajo.
Incluye reservas de cancha (Sprint 6) y modo manager (Sprint 7): saldo negativo, traspaso sin el jugador.
"""

from dataclasses import dataclass
from datetime import timedelta

from sqlalchemy import func, select

from app.domain.contract_rules import ContractStatus
from app.domain.manager_rules import TransferStatus
from app.domain.match_rules import RequestStatus
from app.domain.result_rules import ResultStatus
from app.domain.team_rules import resolve_admin
from app.domain.venue_rules import BookingStatus
from app.persistence.models_contracts import MatchContract, MatchContractSignature
from app.persistence.models_manager import CoinEntry, TransferOffer
from app.persistence.models_matches import MatchRequest
from app.persistence.models_results import MatchResult
from app.persistence.models_teams import Team
from app.persistence.models_venues import Booking, Slot
from app.services import security_service
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


def _bookings(ctx: ServiceContext) -> list[HealthFinding]:
    confirmed = BookingStatus.CONFIRMED.value
    doubles = ctx.db.scalars(select(Booking.slot_id).where(Booking.status == confirmed)
                             .group_by(Booking.slot_id).having(func.count() > 1))
    findings = [HealthFinding("S0", "SLOT_DOUBLE_BOOKED", "slot", sid, "Franja con dos reservas confirmadas.")
                for sid in doubles]
    for booking, slot in ctx.db.execute(select(Booking, Slot).join(Slot, Slot.id == Booking.slot_id)
                                        .where(Booking.status == confirmed)):
        contract = ctx.db.get(MatchContract, booking.contract_id)
        if contract is None or contract.signed_version_id is None or contract.status == ContractStatus.CANCELLED:
            covered = False
        else:
            terms = terms_of(get_version(ctx, contract.signed_version_id))
            covered = slot.starts_at <= terms.kickoff_at and                 terms.kickoff_at + timedelta(minutes=terms.duration_minutes) <= slot.ends_at
        if not covered:
            findings.append(HealthFinding("S1", "BOOKING_OUT_OF_SYNC", "booking", booking.id,
                                          "Reserva confirmada que ya no corresponde al partido firmado."))
    return findings


def _manager(ctx: ServiceContext) -> list[HealthFinding]:
    negative = ctx.db.scalars(select(CoinEntry.team_id).group_by(CoinEntry.team_id)
                              .having(func.sum(CoinEntry.amount) < 0))
    findings = [HealthFinding("S0", "NEGATIVE_COIN_BALANCE", "team", tid, "Equipo con saldo de monedas negativo.")
                for tid in negative]
    unconsented = ctx.db.scalars(select(TransferOffer.id).where(
        TransferOffer.status == TransferStatus.COMPLETED, TransferOffer.player_decided_at.is_(None)))
    findings += [HealthFinding("S0", "TRANSFER_WITHOUT_PLAYER_CONSENT", "transfer_offer", oid,
                               "Traspaso completado sin la aceptación del jugador.") for oid in unconsented]
    return findings


def _security(ctx: ServiceContext) -> list[HealthFinding]:
    return [HealthFinding("S1", "LOGIN_FAILURE_SPIKE", "auth", None,
                          f"Muchos inicios de sesión fallidos en la última hora (clave {key[:8]}…).")
            for key in security_service.failure_spikes(ctx)]


def run_checks(ctx: ServiceContext) -> list[HealthFinding]:
    findings = _audit(ctx) + _teams(ctx) + _contracts(ctx) + _requests(ctx) + _bookings(ctx) + _manager(ctx)
    findings += _security(ctx)
    return sorted(findings, key=lambda f: (f.severity, f.code, f.entity_id or 0))
