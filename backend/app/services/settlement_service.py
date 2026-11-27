"""Liquidación de un resultado confirmado (Sprint 10): monedas RIVAL y nivel Glicko-2 de ambos equipos.

La llaman el reporte de los equipos y el del árbitro, una sola vez por partido. Bloquea los dos
equipos en orden de id (igual que un traspaso) para que dos operaciones no se bloqueen entre sí.
"""

from sqlalchemy import select

from app.domain.glicko2 import GameResult, Rating, update
from app.persistence.models_matchday import TeamRating
from app.persistence.models_teams import Team
from app.services import coin_service
from app.services.audit_service import record_event
from app.services.context import ServiceContext


def current_rating(ctx: ServiceContext, team_id: int) -> tuple[Rating, int]:
    row = ctx.db.get(TeamRating, team_id)
    return (Rating(row.rating, row.rd, row.volatility), row.matches) if row else (Rating(), 0)


def settle(ctx: ServiceContext, contract_id: int, host_id: int, guest_id: int, host_goals: int,
           guest_goals: int) -> None:
    for team_id in sorted((host_id, guest_id)):
        ctx.db.get(Team, team_id, with_for_update=True)
    coin_service.reward_result(ctx, contract_id, host_id, guest_id, host_goals, guest_goals)
    host_score = 1.0 if host_goals > guest_goals else 0.5 if host_goals == guest_goals else 0.0
    (host, host_n), (guest, guest_n) = current_rating(ctx, host_id), current_rating(ctx, guest_id)
    new_host = update(host, [GameResult(guest, host_score)])
    new_guest = update(guest, [GameResult(host, 1.0 - host_score)])
    for team_id, rating, played in ((host_id, new_host, host_n), (guest_id, new_guest, guest_n)):
        row = ctx.db.get(TeamRating, team_id)
        if row is None:
            row = TeamRating(team_id=team_id, rating=0.0, rd=0.0, volatility=0.0, matches=0, updated_at=ctx.clock.now())
            ctx.db.add(row)
        row.rating, row.rd, row.volatility = rating.rating, rating.rd, rating.volatility
        row.matches, row.updated_at = played + 1, ctx.clock.now()
    ctx.db.flush()
    record_event(ctx, action="TEAM_RATINGS_UPDATED", entity="match_contract", entity_id=contract_id,
                 initiated_by=None, actor_type="SYSTEM_RULE",
                 before={"host": round(host.rating, 1), "guest": round(guest.rating, 1)},
                 after={"host": round(new_host.rating, 1), "guest": round(new_guest.rating, 1)})


def ratings_for(ctx: ServiceContext, team_ids: list[int]) -> dict[int, TeamRating]:
    return {r.team_id: r for r in ctx.db.scalars(select(TeamRating).where(TeamRating.team_id.in_(team_ids)))}
