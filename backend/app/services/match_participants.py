"""Quiénes participan de un partido (chat del Sprint 14 y check-in del Sprint 15).

Miembros de los dos equipos, jugadores prestados activos para el partido y el árbitro asignado
(pendiente o aceptado).
"""

from sqlalchemy import select

from app.domain.errors import NotFoundError
from app.persistence.models_contracts import MatchContract
from app.persistence.models_identity import UserAccount
from app.persistence.models_league_matches import RefereeAssignment
from app.services import loan_service
from app.services.context import ServiceContext
from app.services.contract_queries import load_contract, side_teams


def participants(ctx: ServiceContext, contract: MatchContract) -> set[int]:
    ids: set[int] = set()
    for team in side_teams(ctx, contract).values():
        ids |= {m.user_id for m in team.memberships}
        ids |= loan_service.active_players(ctx, contract.id, team.id)
    referee = ctx.db.scalar(select(RefereeAssignment.referee_id).where(
        RefereeAssignment.contract_id == contract.id, RefereeAssignment.status.in_(("PENDING", "ACCEPTED"))))
    if referee is not None:
        ids.add(referee)
    return ids


def participant_contract(ctx: ServiceContext, actor: UserAccount, contract_id: int,
                         lock: bool = False) -> MatchContract:
    """El contrato, o 404 si quien pregunta no participa del partido."""
    contract = load_contract(ctx, contract_id, lock=lock)
    if actor.id not in participants(ctx, contract):
        raise NotFoundError("CONTRACT_NOT_FOUND", "El contrato no existe.")
    return contract
