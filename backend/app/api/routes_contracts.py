"""Rutas del contrato de partido: ver, proponer cambios, firmar, rechazar un cambio y cancelar."""

from dataclasses import asdict

from fastapi import APIRouter

from app.api.dependencies import CtxDep, UserDep
from app.api.schemas_contracts import CancelBody, ContractOut, ContractSummaryOut, ProposalBody, VersionBody
from app.domain.contract_rules import ContractTerms
from app.persistence.models_identity import UserAccount
from app.services import contract_queries, contract_service
from app.services.context import ServiceContext

router = APIRouter(prefix="/api/v1")


def _out(ctx: ServiceContext, user: UserAccount, contract_id: int) -> ContractOut:
    return ContractOut.model_validate(asdict(contract_queries.get_contract(ctx, user, contract_id)))


@router.get("/teams/{team_id}/contracts")
def team_contracts(team_id: int, ctx: CtxDep, user: UserDep) -> list[ContractSummaryOut]:
    return [ContractSummaryOut.model_validate(asdict(v)) for v in contract_queries.team_contracts(ctx, user, team_id)]


@router.get("/contracts/{contract_id}")
def get_contract(contract_id: int, ctx: CtxDep, user: UserDep) -> ContractOut:
    return _out(ctx, user, contract_id)


@router.post("/contracts/{contract_id}/proposals", status_code=201)
def propose(contract_id: int, body: ProposalBody, ctx: CtxDep, user: UserDep) -> ContractOut:
    terms = ContractTerms(**body.terms.model_dump())
    contract_service.propose(ctx, user, contract_id, body.base_version, terms, body.note)
    return _out(ctx, user, contract_id)


@router.post("/contracts/{contract_id}/sign")
def sign(contract_id: int, body: VersionBody, ctx: CtxDep, user: UserDep) -> ContractOut:
    contract_service.sign(ctx, user, contract_id, body.version)
    return _out(ctx, user, contract_id)


@router.post("/contracts/{contract_id}/reject-amendment")
def reject_amendment(contract_id: int, body: VersionBody, ctx: CtxDep, user: UserDep) -> ContractOut:
    contract_service.reject_amendment(ctx, user, contract_id, body.version)
    return _out(ctx, user, contract_id)


@router.post("/contracts/{contract_id}/cancel")
def cancel(contract_id: int, body: CancelBody, ctx: CtxDep, user: UserDep) -> ContractOut:
    contract_service.cancel(ctx, user, contract_id, body.reason)
    return _out(ctx, user, contract_id)
