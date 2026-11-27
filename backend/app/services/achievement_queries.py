"""Insignias de jugadores y equipos (Sprint 17), calculadas en cada consulta a partir de datos reales.

No hay tabla de insignias: así nunca quedan desactualizadas ni se pueden "otorgar" a mano.
"""

from datetime import datetime

from sqlalchemy import select

from app.domain.achievement_rules import Badge, PlayedMatch, outcome, player_badges, team_badges
from app.domain.errors import NotFoundError
from app.domain.result_rules import ResultStatus
from app.persistence.models_contracts import MatchContract
from app.persistence.models_cup import CupMatch, LeagueCup
from app.persistence.models_identity import UserAccount
from app.persistence.models_manager import MatchAppearance
from app.persistence.models_matchday import MatchCheckIn
from app.persistence.models_results import MatchResult
from app.persistence.models_teams import Team
from app.services.context import ServiceContext

_CONFIRMED = MatchResult.status == ResultStatus.CONFIRMED


def _when(result: MatchResult) -> datetime:
    return result.confirmed_at or result.updated_at


def _side_score(result: MatchResult, contract: MatchContract, team_id: int) -> tuple[int, int]:
    host, guest = result.host_score or 0, result.guest_score or 0
    return (host, guest) if team_id == contract.host_team_id else (guest, host)


def _finals_won(ctx: ServiceContext, team_id: int) -> list[tuple[int, datetime]]:
    """(contrato de la final, cuándo se confirmó) de cada copa que ganó el equipo."""
    rows = ctx.db.execute(select(CupMatch.contract_id, MatchResult)
                          .join(LeagueCup, LeagueCup.id == CupMatch.cup_id)
                          .join(MatchResult, MatchResult.contract_id == CupMatch.contract_id)
                          .where(LeagueCup.champion_team_id == team_id, CupMatch.round == LeagueCup.rounds,
                                 CupMatch.winner_team_id == team_id, _CONFIRMED))
    return [(contract_id, _when(result)) for contract_id, result in rows if contract_id is not None]


def for_player(ctx: ServiceContext, user_id: int) -> list[Badge]:
    if ctx.db.get(UserAccount, user_id) is None:
        raise NotFoundError("PLAYER_NOT_FOUND", "Ese jugador no existe.")
    rows = ctx.db.execute(select(MatchAppearance, MatchContract, MatchResult)
                          .join(MatchContract, MatchContract.id == MatchAppearance.contract_id)
                          .join(MatchResult, MatchResult.contract_id == MatchContract.id)
                          .where(MatchAppearance.user_id == user_id, _CONFIRMED)).all()
    matches = [PlayedMatch(at=_when(r), outcome=outcome(*_side_score(r, c, a.team_id)), goals=a.goals)
               for a, c, r in rows]
    check_ins = list(ctx.db.scalars(select(MatchCheckIn.checked_in_at).where(MatchCheckIn.user_id == user_id)))
    finals = {team_id: _finals_won(ctx, team_id) for team_id in {a.team_id for a, _c, _r in rows}}
    titles = [when for a, _c, _r in rows for contract_id, when in finals[a.team_id] if contract_id == a.contract_id]
    return player_badges(matches, check_ins, titles)


def for_team(ctx: ServiceContext, team_id: int) -> list[Badge]:
    if ctx.db.get(Team, team_id) is None:
        raise NotFoundError("TEAM_NOT_FOUND", "El equipo no existe.")
    rows = ctx.db.execute(select(MatchContract, MatchResult)
                          .join(MatchResult, MatchResult.contract_id == MatchContract.id)
                          .where((MatchContract.host_team_id == team_id) | (MatchContract.guest_team_id == team_id),
                                 _CONFIRMED)).all()
    matches = [PlayedMatch(at=_when(r), outcome=outcome(*_side_score(r, c, team_id))) for c, r in rows]
    return team_badges(matches, [when for _contract, when in _finals_won(ctx, team_id)])
