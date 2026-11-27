"""Avance en el cuadro de la copa (Sprint 16): el ganador pasa al siguiente cruce y, cuando ese cruce
tiene sus dos equipos, nace su contrato (árbitro y lugar por acordar, como el calendario de la liga).

Lo llama la liquidación del resultado confirmado (admins o árbitro) y el desempate por penales.
"""

from datetime import datetime, timedelta

from sqlalchemy import select

from app.domain import launch_rules
from app.domain import cup_rules
from app.domain.contract_rules import default_terms
from app.domain.match_rules import PlaceKind
from app.persistence.models_contracts import MatchContract
from app.persistence.models_cup import CupMatch, LeagueCup
from app.persistence.models_leagues import League
from app.services import contract_service
from app.services.audit_service import record_event
from app.services.context import ServiceContext


def round_kickoff(ctx: ServiceContext, cup: LeagueCup, round_number: int) -> datetime:
    """Fecha de la ronda; si ya pasó (resultados tardíos), el día siguiente a la misma hora."""
    kickoff = cup.first_kickoff + timedelta(days=cup.days_between * (round_number - 1))
    while kickoff <= ctx.clock.now():
        kickoff += timedelta(days=1)
    return kickoff


def open_match(ctx: ServiceContext, cup: LeagueCup, match: CupMatch, actor_id: int | None) -> None:
    """Crea el contrato del cruce cuando ya tiene sus dos equipos."""
    if match.contract_id is not None or match.host_team_id is None or match.guest_team_id is None:
        return
    league = ctx.db.get(League, cup.league_id)
    assert league is not None
    contract = contract_service.create_contract(ctx, MatchContract(
        league_id=league.id, host_team_id=match.host_team_id, guest_team_id=match.guest_team_id,
        sport_code=league.sport_code, modality_code=league.modality_code),
        default_terms(round_kickoff(ctx, cup, match.round), launch_rules.default_referee(ctx.features),
                      PlaceKind.TO_AGREE, None), actor_id)
    match.contract_id = contract.id
    ctx.db.flush()


def advance(ctx: ServiceContext, cup: LeagueCup, match: CupMatch, winner_id: int, actor_id: int | None) -> None:
    match.winner_team_id = winner_id
    if match.round == cup.rounds:
        cup.champion_team_id = winner_id
        ctx.db.flush()
        record_event(ctx, action="CUP_CHAMPION", entity="league", entity_id=cup.league_id, initiated_by=actor_id,
                     actor_type="SYSTEM_RULE", after={"cup_id": cup.id, "team_id": winner_id})
        return
    parent = ctx.db.scalar(select(CupMatch).where(CupMatch.cup_id == cup.id, CupMatch.round == match.round + 1,
                                                  CupMatch.position == match.position // 2))
    assert parent is not None
    if match.position % 2 == 0:
        parent.host_team_id = winner_id
    else:
        parent.guest_team_id = winner_id
    ctx.db.flush()
    record_event(ctx, action="CUP_TEAM_ADVANCED", entity="league", entity_id=cup.league_id, initiated_by=actor_id,
                 actor_type="SYSTEM_RULE", after={"cup_id": cup.id, "team_id": winner_id, "to_round": parent.round})
    open_match(ctx, cup, parent, actor_id)


def on_result(ctx: ServiceContext, contract_id: int, host_goals: int, guest_goals: int) -> None:
    """Resultado confirmado: si el partido es de copa y hay ganador, avanza. Con empate espera los penales."""
    match = ctx.db.scalar(select(CupMatch).where(CupMatch.contract_id == contract_id).with_for_update())
    if match is None or match.winner_team_id is not None:
        return
    cup = ctx.db.get(LeagueCup, match.cup_id, with_for_update=True)
    assert cup is not None and match.host_team_id is not None and match.guest_team_id is not None
    winner = cup_rules.match_winner(match.host_team_id, match.guest_team_id, host_goals, guest_goals, None)
    if winner is not None:
        advance(ctx, cup, match, winner, None)
