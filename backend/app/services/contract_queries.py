"""Lectura del contrato: solo los miembros de los dos equipos lo ven; para el resto no existe."""

from sqlalchemy import or_, select

from app.domain.contract_rules import ContractStatus, ContractTerms, terms_from_dict
from app.domain.errors import ConflictError, NotFoundError
from app.domain.team_rules import resolve_admin
from app.persistence.models_contracts import MatchContract, MatchContractSignature, MatchContractVersion
from app.persistence.models_identity import UserAccount
from app.persistence.models_teams import Team
from app.services.context import ServiceContext
from app.services.contract_views import ContractSummaryView, ContractView, VersionView
from app.services.result_queries import get_result, result_view
from app.services.rival_service import require_member
from app.services.team_service import get_active_team, member_views, summary

HOST, GUEST = "HOST", "GUEST"


def load_contract(ctx: ServiceContext, contract_id: int, lock: bool = False) -> MatchContract:
    contract = ctx.db.get(MatchContract, contract_id, with_for_update=lock)
    if contract is None:
        raise NotFoundError("CONTRACT_NOT_FOUND", "El contrato no existe.")
    return contract


def side_teams(ctx: ServiceContext, contract: MatchContract) -> dict[str, Team]:
    host, guest = ctx.db.get(Team, contract.host_team_id), ctx.db.get(Team, contract.guest_team_id)
    assert host is not None and guest is not None
    return {HOST: host, GUEST: guest}


def member_side(teams: dict[str, Team], actor: UserAccount) -> str:
    for side, team in teams.items():
        if any(m.user_id == actor.id for m in team.memberships):
            return side
    raise NotFoundError("CONTRACT_NOT_FOUND", "El contrato no existe.")


def is_admin_of(team: Team, actor: UserAccount) -> bool:
    return resolve_admin(member_views(team)) == actor.id


def get_version(ctx: ServiceContext, version_id: int | None) -> MatchContractVersion:
    version = ctx.db.get(MatchContractVersion, version_id) if version_id is not None else None
    assert version is not None
    return version


def signed_sides(ctx: ServiceContext, contract: MatchContract, version: MatchContractVersion) -> list[str]:
    teams = set(ctx.db.scalars(select(MatchContractSignature.team_id).where(
        MatchContractSignature.version_id == version.id)))
    return [side for side, team_id in ((HOST, contract.host_team_id), (GUEST, contract.guest_team_id))
            if team_id in teams]


def terms_of(version: MatchContractVersion) -> ContractTerms:
    return terms_from_dict(dict(version.terms))


def version_view(ctx: ServiceContext, contract: MatchContract, version: MatchContractVersion) -> VersionView:
    proposer = None
    if version.proposed_by_team_id is not None:
        proposer = HOST if version.proposed_by_team_id == contract.host_team_id else GUEST
    return VersionView(version=version.version, terms=terms_of(version), proposed_by_side=proposer,
                       note=version.note, created_at=version.created_at,
                       signed_by=signed_sides(ctx, contract, version))


def require_not_started(ctx: ServiceContext, contract: MatchContract) -> None:
    """La hora que cuenta es la de la versión firmada; si no hay, la de la versión en negociación."""
    effective = get_version(ctx, contract.signed_version_id or contract.current_version_id)
    if ctx.clock.now() >= terms_of(effective).kickoff_at:
        raise ConflictError("MATCH_ALREADY_STARTED", "El partido ya empezó; el contrato no se puede cambiar.")


def get_contract(ctx: ServiceContext, actor: UserAccount, contract_id: int) -> ContractView:
    contract = load_contract(ctx, contract_id)
    teams = side_teams(ctx, contract)
    side = member_side(teams, actor)
    versions = list(ctx.db.scalars(select(MatchContractVersion).where(
        MatchContractVersion.contract_id == contract.id).order_by(MatchContractVersion.version)))
    by_id = {v.id: version_view(ctx, contract, v) for v in versions}
    signed = by_id.get(contract.signed_version_id) if contract.signed_version_id is not None else None
    return ContractView(
        id=contract.id, request_id=contract.request_id, host=summary(teams[HOST]), guest=summary(teams[GUEST]),
        status=contract.status, my_side=side, is_admin=is_admin_of(teams[side], actor),
        current=by_id[contract.current_version_id or 0], signed=signed, versions=list(by_id.values()),
        cancel_reason=contract.cancel_reason, result=result_view(ctx, contract),
    )


def contract_id_for_offer(ctx: ServiceContext, offer_id: int) -> int | None:
    return ctx.db.scalar(select(MatchContract.id).where(MatchContract.offer_id == offer_id))


def team_contracts(ctx: ServiceContext, actor: UserAccount, team_id: int) -> list[ContractSummaryView]:
    team = get_active_team(ctx, team_id)
    require_member(team, actor)
    rows = ctx.db.scalars(select(MatchContract).where(
        or_(MatchContract.host_team_id == team.id, MatchContract.guest_team_id == team.id))
        .order_by(MatchContract.id.desc()).limit(50))
    result = []
    for contract in rows:
        teams = side_teams(ctx, contract)
        side = HOST if contract.host_team_id == team.id else GUEST
        current = get_version(ctx, contract.current_version_id)
        effective = get_version(ctx, contract.signed_version_id or contract.current_version_id)
        awaiting = contract.status == ContractStatus.NEGOTIATING and side not in signed_sides(ctx, contract, current)
        outcome = get_result(ctx, contract.id)
        result.append(ContractSummaryView(
            id=contract.id, host=summary(teams[HOST]), guest=summary(teams[GUEST]), status=contract.status,
            kickoff_at=terms_of(effective).kickoff_at, my_side=side, awaiting_my_signature=awaiting,
            result_status=outcome.status if outcome else None, host_score=outcome.host_score if outcome else None,
            guest_score=outcome.guest_score if outcome else None))
    return result
