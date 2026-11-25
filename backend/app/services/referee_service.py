"""Árbitros en partidos de liga (Sprint 8): asignar, aceptar y fijar el resultado.

Asignan el organizador, un coorganizador o el coordinador arbitral, solo árbitros aprobados del
cuerpo arbitral. El resultado del árbitro con asignación aceptada vale por sí solo (RIV-013).
"""

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select

from app.domain.contract_rules import ContractStatus
from app.domain.errors import ConflictError, DomainError, NotFoundError, PermissionDeniedError
from app.domain.result_rules import ResultStatus, check_can_report, validate_score
from app.persistence.models_identity import UserAccount
from app.persistence.models_league_matches import RefereeAssignment
from app.persistence.models_leagues import League, LeagueReferee
from app.persistence.models_results import MatchResult
from app.persistence.models_teams import Team
from app.services import cup_advance, settlement_service
from app.services.audit_service import record_event
from app.services.context import ServiceContext
from app.services.contract_queries import get_version, load_contract, terms_of
from app.services.league_queries import staff_role
from app.services.referee_queries import active_assignment
from app.services.result_queries import get_result


@dataclass(frozen=True)
class RefereeMatchView:
    assignment_id: int
    contract_id: int
    status: str
    league_name: str
    host_name: str
    guest_name: str
    kickoff_at: datetime
    place_kind: str
    place_note: str | None
    result_status: str | None
    host_score: int | None
    guest_score: int | None


def assign(ctx: ServiceContext, actor: UserAccount, contract_id: int, referee_id: int) -> RefereeAssignment:
    contract = load_contract(ctx, contract_id, lock=True)
    if contract.league_id is None:
        raise ConflictError("NOT_A_LEAGUE_MATCH", "Solo se asignan árbitros a partidos de una liga.")
    if staff_role(ctx, contract.league_id, actor.id) is None:
        raise PermissionDeniedError("LEAGUE_STAFF_ONLY", "Solo el personal de la liga asigna árbitros.")
    if ctx.db.scalar(select(LeagueReferee.id).where(LeagueReferee.league_id == contract.league_id,
                                                    LeagueReferee.user_id == referee_id,
                                                    LeagueReferee.status == "APPROVED")) is None:
        raise DomainError("NOT_LEAGUE_REFEREE", "Esa persona no está aprobada en el cuerpo arbitral de la liga.")
    if contract.status == ContractStatus.CANCELLED:
        raise ConflictError("CONTRACT_CANCELLED", "Este partido fue cancelado.")
    if active_assignment(ctx, contract.id) is not None:
        raise ConflictError("REFEREE_ALREADY_ASSIGNED", "Este partido ya tiene un árbitro asignado o pendiente.")
    assignment = RefereeAssignment(contract_id=contract.id, referee_id=referee_id, status="PENDING",
                                   assigned_by=actor.id, assigned_at=ctx.clock.now())
    ctx.db.add(assignment)
    ctx.db.flush()
    record_event(ctx, action="REFEREE_ASSIGNED", entity="match_contract", entity_id=contract.id,
                 initiated_by=actor.id, after={"referee_id": referee_id, "assignment_id": assignment.id})
    return assignment


def respond(ctx: ServiceContext, actor: UserAccount, assignment_id: int, accept: bool) -> RefereeAssignment:
    assignment = ctx.db.get(RefereeAssignment, assignment_id, with_for_update=True)
    if assignment is None:
        raise NotFoundError("ASSIGNMENT_NOT_FOUND", "La asignación no existe.")
    if assignment.referee_id != actor.id:
        raise PermissionDeniedError("REFEREE_ONLY", "Solo el árbitro asignado puede responder.")
    if assignment.status != "PENDING":
        raise ConflictError("ASSIGNMENT_NOT_PENDING", "Ya respondiste esta asignación.")
    assignment.status, assignment.decided_at = ("ACCEPTED" if accept else "DECLINED"), ctx.clock.now()
    ctx.db.flush()
    record_event(ctx, action="REFEREE_ACCEPTED" if accept else "REFEREE_DECLINED", entity="match_contract",
                 entity_id=assignment.contract_id, initiated_by=actor.id, after={"assignment_id": assignment.id})
    return assignment


def report_result(ctx: ServiceContext, actor: UserAccount, contract_id: int, host_score: int,
                  guest_score: int) -> MatchResult:
    contract = load_contract(ctx, contract_id, lock=True)
    assignment = active_assignment(ctx, contract.id)
    if assignment is None or assignment.referee_id != actor.id or assignment.status != "ACCEPTED":
        raise PermissionDeniedError("ASSIGNED_REFEREE_ONLY", "Solo el árbitro asignado (y que aceptó) fija el resultado.")
    if contract.status == ContractStatus.CANCELLED or contract.signed_version_id is None:
        raise ConflictError("CONTRACT_NOT_SIGNED", "El resultado se fija en partidos firmados por ambos.")
    check_can_report(terms_of(get_version(ctx, contract.signed_version_id)).kickoff_at, ctx.clock.now())
    validate_score(host_score, guest_score)
    result, now = get_result(ctx, contract.id), ctx.clock.now()
    if result is not None and result.status == ResultStatus.CONFIRMED:
        raise ConflictError("RESULT_ALREADY_CONFIRMED", "El resultado ya estaba confirmado.")
    before = result.status if result else None
    if result is None:
        result = MatchResult(contract_id=contract.id, status=ResultStatus.PENDING.value, updated_at=now)
        ctx.db.add(result)
    result.status, result.host_score, result.guest_score = ResultStatus.CONFIRMED.value, host_score, guest_score
    result.referee_id, result.confirmed_at, result.updated_at = actor.id, now, now
    ctx.db.flush()
    settlement_service.settle(ctx, contract.id, contract.host_team_id, contract.guest_team_id, host_score, guest_score)
    record_event(ctx, action="RESULT_SET_BY_REFEREE", entity="match_contract", entity_id=contract.id,
                 initiated_by=actor.id, before={"result_status": before},
                 after={"host_score": host_score, "guest_score": guest_score, "result_status": result.status})
    cup_advance.on_result(ctx, contract.id, host_score, guest_score)  # si es de copa, avanza el ganador
    return result


def my_matches(ctx: ServiceContext, actor: UserAccount) -> list[RefereeMatchView]:
    rows = ctx.db.scalars(select(RefereeAssignment).where(RefereeAssignment.referee_id == actor.id,
                                                          RefereeAssignment.status.in_(("PENDING", "ACCEPTED")))
                          .order_by(RefereeAssignment.id.desc()))
    views = []
    for a in rows:
        contract = load_contract(ctx, a.contract_id)
        terms = terms_of(get_version(ctx, contract.signed_version_id or contract.current_version_id))
        league, host, guest = (ctx.db.get(League, contract.league_id or 0), ctx.db.get(Team, contract.host_team_id),
                               ctx.db.get(Team, contract.guest_team_id))
        result = get_result(ctx, contract.id)
        views.append(RefereeMatchView(
            assignment_id=a.id, contract_id=contract.id, status=a.status, league_name=league.name if league else "",
            host_name=host.name if host else "", guest_name=guest.name if guest else "", kickoff_at=terms.kickoff_at,
            place_kind=terms.place_kind.value, place_note=terms.place_note,
            result_status=result.status if result else None, host_score=result.host_score if result else None,
            guest_score=result.guest_score if result else None))
    return views
