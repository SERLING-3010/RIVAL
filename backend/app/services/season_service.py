"""Cierre de temporada (Sprint 23): el organizador la cierra y gana el primero de la tabla.

Solo se cierra cuando todos los partidos del calendario tienen resultado confirmado o están
cancelados, y al menos uno se jugó. Queda en la auditoría encadenada y no se puede reabrir.
"""

from sqlalchemy import select

from app.domain.contract_rules import ContractStatus
from app.domain.errors import ConflictError, PermissionDeniedError
from app.domain.league_rules import StaffRole
from app.domain.result_rules import ResultStatus
from app.persistence.models_contracts import MatchContract
from app.persistence.models_identity import UserAccount
from app.persistence.models_league_matches import LeagueFixture
from app.persistence.models_leagues import League
from app.persistence.models_results import MatchResult
from app.services import standings_queries
from app.services.audit_service import record_event
from app.services.context import ServiceContext
from app.services.league_queries import get_league, staff_role


def close(ctx: ServiceContext, actor: UserAccount, league_id: int) -> League:
    league = get_league(ctx, league_id, lock=True)
    if staff_role(ctx, league.id, actor.id) != StaffRole.ORGANIZER:
        raise PermissionDeniedError("ORGANIZER_ONLY", "Solo el organizador puede cerrar la temporada.")
    if league.closed_at is not None:
        raise ConflictError("SEASON_ALREADY_CLOSED", "Esta temporada ya está cerrada.")
    confirmed = select(MatchResult.contract_id).where(MatchResult.status == ResultStatus.CONFIRMED)
    open_matches = ctx.db.scalar(select(LeagueFixture.id).join(MatchContract, MatchContract.id ==
                                                                LeagueFixture.contract_id)
                                 .where(LeagueFixture.league_id == league.id,
                                        MatchContract.status != ContractStatus.CANCELLED,
                                        MatchContract.id.not_in(confirmed)).limit(1))
    if open_matches is not None:
        raise ConflictError("SEASON_NOT_FINISHED",
                            "Aún hay partidos del calendario sin resultado confirmado o sin cancelar.")
    table = [row for row in standings_queries.table(ctx, league.id) if row.played > 0]
    if not table:
        raise ConflictError("NO_MATCHES_PLAYED", "No se puede cerrar una temporada sin partidos jugados.")
    champion = table[0]
    league.champion_team_id, league.closed_at = champion.team_id, ctx.clock.now()
    ctx.db.flush()
    record_event(ctx, action="LEAGUE_SEASON_CLOSED", entity="league", entity_id=league.id, initiated_by=actor.id,
                 after={"champion_team_id": champion.team_id, "points": champion.points,
                        "season": league.season})
    return league
