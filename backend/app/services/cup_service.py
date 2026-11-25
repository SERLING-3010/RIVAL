"""Copa eliminatoria de una liga (Sprint 16): la arma el organizador y define los empates por penales.

El cuadro completo se guarda al crearla; los cruces sin rival (pases directos) avanzan de inmediato.
La siembra sigue el nivel Glicko-2 de cada equipo (sin partidos, 1500), y a igual nivel, el más antiguo.
"""

from datetime import datetime

from sqlalchemy import select

from app.domain import cup_rules
from app.domain.errors import ConflictError, DomainError, NotFoundError, PermissionDeniedError
from app.domain.fixture_rules import round_dates
from app.domain.league_rules import EnrollmentStatus, StaffRole
from app.domain.result_rules import ResultStatus
from app.persistence.models_cup import CupMatch, LeagueCup
from app.persistence.models_identity import UserAccount
from app.persistence.models_leagues import LeagueTeam
from app.persistence.models_matchday import TeamRating
from app.persistence.models_results import MatchResult
from app.services.audit_service import record_event
from app.services.context import ServiceContext
from app.services.cup_advance import advance, open_match
from app.services.league_queries import get_league, staff_role

_ORGANIZERS = (StaffRole.ORGANIZER, StaffRole.CO_ORGANIZER)


def _require_organizer(ctx: ServiceContext, league_id: int, actor: UserAccount) -> None:
    if staff_role(ctx, league_id, actor.id) not in _ORGANIZERS:
        raise PermissionDeniedError("ORGANIZER_ONLY", "Solo el organizador o un coorganizador maneja la copa.")


def _seeded(ctx: ServiceContext, league_id: int) -> list[int]:
    teams = list(ctx.db.scalars(select(LeagueTeam.team_id).where(
        LeagueTeam.league_id == league_id, LeagueTeam.status == EnrollmentStatus.APPROVED).order_by(LeagueTeam.id)))
    ratings = {r.team_id: r.rating for r in ctx.db.scalars(select(TeamRating).where(TeamRating.team_id.in_(teams)))}
    return sorted(teams, key=lambda t: -ratings.get(t, 1500.0))  # orden estable: a igual nivel, el más antiguo


def create(ctx: ServiceContext, actor: UserAccount, league_id: int, first_kickoff: datetime,
           days_between: int) -> LeagueCup:
    league = get_league(ctx, league_id, lock=True)
    _require_organizer(ctx, league.id, actor)
    if ctx.db.scalar(select(LeagueCup.id).where(LeagueCup.league_id == league.id)) is not None:
        raise ConflictError("CUP_ALREADY_EXISTS", "Esta liga ya tiene copa.")
    seeded = _seeded(ctx, league.id)
    pairs = cup_rules.first_round(seeded)
    rounds = cup_rules.rounds_for(len(pairs) * 2)
    round_dates(first_kickoff, days_between, rounds, ctx.clock.now())  # misma regla de fechas que el calendario
    cup = LeagueCup(league_id=league.id, first_kickoff=first_kickoff, days_between=days_between, rounds=rounds,
                    created_by=actor.id, created_at=ctx.clock.now())
    ctx.db.add(cup)
    ctx.db.flush()
    matches = {(r, p): CupMatch(cup_id=cup.id, round=r, position=p)
               for r in range(1, rounds + 1) for p in range(len(pairs) >> (r - 1))}
    for p, (host, guest) in enumerate(pairs):
        matches[(1, p)].host_team_id, matches[(1, p)].guest_team_id = host, guest
    ctx.db.add_all(matches.values())
    ctx.db.flush()
    record_event(ctx, action="CUP_CREATED", entity="league", entity_id=league.id, initiated_by=actor.id,
                 after={"cup_id": cup.id, "teams": len(seeded), "rounds": rounds, "seeds": seeded})
    for p, (host, guest) in enumerate(pairs):
        assert host is not None  # el mejor sembrado de cada cruce siempre es un equipo real
        if guest is None:  # pase directo
            advance(ctx, cup, matches[(1, p)], host, actor.id)
        else:
            open_match(ctx, cup, matches[(1, p)], actor.id)
    return cup


def set_tiebreak(ctx: ServiceContext, actor: UserAccount, cup_match_id: int, winner_team_id: int) -> CupMatch:
    match = ctx.db.get(CupMatch, cup_match_id, with_for_update=True)
    cup = ctx.db.get(LeagueCup, match.cup_id, with_for_update=True) if match else None
    if match is None or cup is None:
        raise NotFoundError("CUP_MATCH_NOT_FOUND", "El cruce no existe.")
    _require_organizer(ctx, cup.league_id, actor)
    result = ctx.db.scalar(select(MatchResult).where(MatchResult.contract_id == match.contract_id))
    tied = result is not None and result.status == ResultStatus.CONFIRMED and result.host_score == result.guest_score
    if not tied or match.winner_team_id is not None:
        raise ConflictError("NO_TIE_TO_BREAK", "Solo se definen por penales los cruces empatados y sin ganador.")
    if winner_team_id not in (match.host_team_id, match.guest_team_id):
        raise DomainError("NOT_IN_MATCH", "El ganador debe ser uno de los dos equipos del cruce.")
    match.tiebreak_winner_id = winner_team_id
    record_event(ctx, action="CUP_TIEBREAK_SET", entity="league", entity_id=cup.league_id, initiated_by=actor.id,
                 after={"cup_match_id": match.id, "winner_team_id": winner_team_id})
    advance(ctx, cup, match, winner_team_id, actor.id)
    return match
