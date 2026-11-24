"""Valoraciones entre compañeros después del partido (Sprint 10).

Con resultado confirmado y planilla, cada miembro del equipo valora de 1 a 10 a los compañeros que
jugaron. La nota individual es privada: la auditoría guarda que se valoró, no cuánto; la ficha solo
muestra el promedio y el número de votos.
"""

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import func, select

from app.domain.errors import ConflictError
from app.domain.matchday_rules import check_can_rate, validate_score
from app.domain.result_rules import ResultStatus
from app.persistence.models_contracts import MatchContract
from app.persistence.models_identity import UserAccount
from app.persistence.models_manager import MatchAppearance
from app.persistence.models_matchday import PlayerRating
from app.persistence.models_teams import Team
from app.services.audit_service import record_event
from app.services.context import ServiceContext
from app.services.contract_queries import get_version, load_contract, member_side, side_teams, terms_of
from app.services.result_queries import get_result


@dataclass(frozen=True)
class RateableView:
    user_id: int
    display_name: str


def _context(
    ctx: ServiceContext, actor: UserAccount, contract_id: int, lock: bool = False
) -> tuple[MatchContract, set[int], datetime]:
    contract = load_contract(ctx, contract_id, lock=lock)
    teams = side_teams(ctx, contract)
    team: Team = teams[member_side(teams, actor)]
    result = get_result(ctx, contract.id)
    if result is None or result.status != ResultStatus.CONFIRMED or contract.signed_version_id is None:
        raise ConflictError("RESULT_NOT_CONFIRMED", "Se valora cuando el resultado está confirmado.")
    played = set(ctx.db.scalars(select(MatchAppearance.user_id).where(
        MatchAppearance.contract_id == contract.id, MatchAppearance.team_id == team.id)))
    return contract, played, terms_of(get_version(ctx, contract.signed_version_id)).kickoff_at


def rate(ctx: ServiceContext, actor: UserAccount, contract_id: int, rated_id: int, score: int) -> PlayerRating:
    contract, played, kickoff = _context(ctx, actor, contract_id, lock=True)
    check_can_rate(actor.id, rated_id, played, kickoff, ctx.clock.now())
    validate_score(score)
    exists = ctx.db.scalar(select(PlayerRating.id).where(PlayerRating.contract_id == contract.id,
                                                         PlayerRating.rater_id == actor.id,
                                                         PlayerRating.rated_id == rated_id))
    if exists is not None:
        raise ConflictError("ALREADY_RATED", "Ya valoraste a este compañero en este partido.")
    rating = PlayerRating(contract_id=contract.id, rater_id=actor.id, rated_id=rated_id, score=score,
                          created_at=ctx.clock.now())
    ctx.db.add(rating)
    ctx.db.flush()
    record_event(ctx, action="PLAYER_RATED", entity="match_contract", entity_id=contract.id, initiated_by=actor.id,
                 after={"rated_id": rated_id})
    return rating


def to_rate(ctx: ServiceContext, actor: UserAccount, contract_id: int) -> list[RateableView]:
    contract, played, _kickoff = _context(ctx, actor, contract_id)
    done = set(ctx.db.scalars(select(PlayerRating.rated_id).where(PlayerRating.contract_id == contract.id,
                                                                 PlayerRating.rater_id == actor.id)))
    pending = sorted(played - done - {actor.id})
    users = ctx.db.scalars(select(UserAccount).where(UserAccount.id.in_(pending)).order_by(UserAccount.display_name))
    return [RateableView(user_id=u.id, display_name=u.display_name) for u in users]


def summary(ctx: ServiceContext, user_id: int) -> tuple[float | None, int]:
    average, votes = ctx.db.execute(select(func.avg(PlayerRating.score), func.count(PlayerRating.id)).where(
        PlayerRating.rated_id == user_id)).one()
    return (round(float(average), 1) if average is not None else None), int(votes)
