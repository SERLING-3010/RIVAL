"""Contrato del partido: nace al aceptar una oferta; se firma cuando ambos firman la misma versión.

Toda acción bloquea la fila del contrato (FOR UPDATE). Proponer crea una versión nueva firmada por
quien propone; la versión firmada sigue vigente hasta que el rival firme el cambio.
"""

from sqlalchemy import func, select

from app.domain.contract_rules import (
    ContractStatus, ContractTerms, default_terms, diff_terms, terms_to_dict, validate_terms,
)
from app.domain.errors import ConflictError, DomainError, PermissionDeniedError
from app.domain.match_rules import PlaceKind, RefereeMode
from app.persistence.models_contracts import MatchContract, MatchContractSignature, MatchContractVersion
from app.persistence.models_identity import UserAccount
from app.persistence.models_matches import MatchOffer, MatchRequest
from app.persistence.models_teams import Team
from app.services.audit_service import record_event
from app.services.context import ServiceContext
from app.services.contract_queries import (
    get_version, is_admin_of, load_contract, member_side, require_not_started, side_teams, signed_sides, terms_of,
)

_ENTITY = "match_contract"


def create_from_offer(ctx: ServiceContext, request: MatchRequest, offer: MatchOffer, actor_id: int) -> MatchContract:
    now = ctx.clock.now()
    contract = MatchContract(
        request_id=request.id, offer_id=offer.id, host_team_id=request.team_id, guest_team_id=offer.team_id,
        sport_code=request.sport_code, modality_code=request.modality_code,
        status=ContractStatus.NEGOTIATING.value, created_at=now, updated_at=now,
    )
    ctx.db.add(contract)
    ctx.db.flush()
    terms = default_terms(offer.proposed_start, RefereeMode(offer.referee_mode), PlaceKind(offer.place_kind),
                          offer.place_note)
    version = _insert_version(ctx, contract, terms, team_id=None, actor_id=None, note=None)
    contract.current_version_id = version.id
    ctx.db.flush()
    record_event(ctx, action="CONTRACT_CREATED", entity=_ENTITY, entity_id=contract.id, initiated_by=actor_id,
                 actor_type="SYSTEM_RULE", after={"offer_id": offer.id, "terms": terms_to_dict(terms)})
    return contract


def _insert_version(ctx: ServiceContext, contract: MatchContract, terms: ContractTerms,
                    team_id: int | None, actor_id: int | None, note: str | None) -> MatchContractVersion:
    last = ctx.db.scalar(select(func.max(MatchContractVersion.version)).where(
        MatchContractVersion.contract_id == contract.id)) or 0
    version = MatchContractVersion(contract_id=contract.id, version=last + 1, terms=terms_to_dict(terms),
                                   proposed_by_team_id=team_id, proposed_by=actor_id,
                                   note=(note or "").strip()[:200] or None, created_at=ctx.clock.now())
    ctx.db.add(version)
    ctx.db.flush()
    return version


def _admin_side(ctx: ServiceContext, contract: MatchContract, actor: UserAccount) -> tuple[str, Team]:
    teams = side_teams(ctx, contract)
    member_side(teams, actor)  # 404 si no pertenece a ninguno de los dos equipos
    sides = [side for side, team in teams.items() if is_admin_of(team, actor)]
    if len(sides) == 2:
        raise ConflictError("SAME_ADMIN_BOTH_TEAMS", "No puedes firmar por los dos equipos del mismo partido.")
    if not sides:
        raise PermissionDeniedError("ADMIN_ONLY", "Solo el administrador del equipo (DT o capitán) puede hacer esto.")
    return sides[0], teams[sides[0]]


def _open_for_changes(
    ctx: ServiceContext, contract_id: int, actor: UserAccount, version: int | None
) -> tuple[MatchContract, str, Team, MatchContractVersion]:
    contract = load_contract(ctx, contract_id, lock=True)
    side, team = _admin_side(ctx, contract, actor)
    if contract.status == ContractStatus.CANCELLED:
        raise ConflictError("CONTRACT_CANCELLED", "Este partido fue cancelado.")
    current = get_version(ctx, contract.current_version_id)
    if version is not None and current.version != version:
        raise ConflictError("CONTRACT_VERSION_CHANGED", "El contrato cambió mientras lo revisabas. Revisa la versión nueva.")
    return contract, side, team, current


def _sign(ctx: ServiceContext, contract: MatchContract, version: MatchContractVersion, team: Team, actor_id: int) -> None:
    ctx.db.add(MatchContractSignature(version_id=version.id, team_id=team.id, signed_by=actor_id,
                                      signed_at=ctx.clock.now()))
    ctx.db.flush()
    if len(signed_sides(ctx, contract, version)) == 2:
        contract.status, contract.signed_version_id = ContractStatus.SIGNED.value, version.id
    contract.updated_at = ctx.clock.now()
    ctx.db.flush()
    record_event(ctx, action="CONTRACT_SIGNED", entity=_ENTITY, entity_id=contract.id, initiated_by=actor_id,
                 after={"version": version.version, "team_id": team.id, "status": contract.status})


def propose(ctx: ServiceContext, actor: UserAccount, contract_id: int, base_version: int,
            terms: ContractTerms, note: str | None = None) -> MatchContract:
    contract, side, team, current = _open_for_changes(ctx, contract_id, actor, base_version)
    require_not_started(ctx, contract)
    validate_terms(terms, ctx.clock.now())
    diff = diff_terms(terms_of(current), terms)
    if not diff["after"]:
        raise DomainError("NO_CHANGES", "La propuesta es igual al contrato actual. Cambia al menos una condición.")
    version = _insert_version(ctx, contract, terms, team_id=team.id, actor_id=actor.id, note=note)
    contract.current_version_id, contract.status = version.id, ContractStatus.NEGOTIATING.value
    ctx.db.flush()
    record_event(ctx, action="CONTRACT_VERSION_PROPOSED", entity=_ENTITY, entity_id=contract.id,
                 initiated_by=actor.id, before=diff["before"], after={**diff["after"], "version": version.version})
    _sign(ctx, contract, version, team, actor.id)
    return contract


def sign(ctx: ServiceContext, actor: UserAccount, contract_id: int, version: int) -> MatchContract:
    contract, side, team, current = _open_for_changes(ctx, contract_id, actor, version)
    if contract.status != ContractStatus.NEGOTIATING:
        raise ConflictError("CONTRACT_NOT_NEGOTIATING", "Este contrato ya está firmado por ambos equipos.")
    if side in signed_sides(ctx, contract, current):
        raise ConflictError("ALREADY_SIGNED", "Tu equipo ya firmó esta versión. Falta la firma del rival.")
    validate_terms(terms_of(current), ctx.clock.now())
    _sign(ctx, contract, current, team, actor.id)
    return contract


def reject_amendment(ctx: ServiceContext, actor: UserAccount, contract_id: int, version: int) -> MatchContract:
    """El rival rechaza (o quien propuso retira) un cambio a un contrato ya firmado: vuelve la versión firmada."""
    contract, side, team, current = _open_for_changes(ctx, contract_id, actor, version)
    if contract.status != ContractStatus.NEGOTIATING or contract.signed_version_id is None:
        raise ConflictError("NO_AMENDMENT", "No hay un cambio pendiente sobre un contrato firmado.")
    withdrawn = current.proposed_by_team_id == team.id
    contract.current_version_id, contract.status = contract.signed_version_id, ContractStatus.SIGNED.value
    contract.updated_at = ctx.clock.now()
    ctx.db.flush()
    record_event(ctx, action="CONTRACT_AMENDMENT_WITHDRAWN" if withdrawn else "CONTRACT_AMENDMENT_REJECTED",
                 entity=_ENTITY, entity_id=contract.id, initiated_by=actor.id,
                 before={"version": current.version}, after={"version": get_version(ctx, contract.signed_version_id).version})
    return contract


def cancel(ctx: ServiceContext, actor: UserAccount, contract_id: int, reason: str) -> MatchContract:
    contract, _side, _team, _current = _open_for_changes(ctx, contract_id, actor, None)
    clean = reason.strip()
    if not 5 <= len(clean) <= 200:
        raise DomainError("CANCEL_REASON_REQUIRED", "Escribe el motivo de la cancelación (5 a 200 caracteres).")
    require_not_started(ctx, contract)
    before = contract.status
    contract.status, contract.cancel_reason, contract.cancelled_by = ContractStatus.CANCELLED.value, clean, actor.id
    contract.updated_at = ctx.clock.now()
    ctx.db.flush()
    record_event(ctx, action="CONTRACT_CANCELLED", entity=_ENTITY, entity_id=contract.id, initiated_by=actor.id,
                 before={"status": before}, after={"status": contract.status, "reason": clean})
    return contract
