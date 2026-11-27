"""Ventanas de traspasos por liga (Sprint 13).

El organizador o un coorganizador la fija. Si cualquiera de los dos equipos de un traspaso está
aprobado en una liga cuya ventana está cerrada, el traspaso no se puede ofertar ni completar.
"""

from datetime import datetime

from sqlalchemy import select

from app.domain.errors import PermissionDeniedError
from app.domain.league_rules import StaffRole
from app.domain.loan_rules import check_window, validate_window, window_open
from app.persistence.models_identity import UserAccount
from app.persistence.models_leagues import League, LeagueTeam
from app.services.audit_service import record_event
from app.services.context import ServiceContext
from app.services.league_queries import get_league, staff_role


def set_window(ctx: ServiceContext, actor: UserAccount, league_id: int, starts_at: datetime | None,
               ends_at: datetime | None) -> League:
    league = get_league(ctx, league_id, lock=True)
    if staff_role(ctx, league.id, actor.id) not in (StaffRole.ORGANIZER, StaffRole.CO_ORGANIZER):
        raise PermissionDeniedError("ORGANIZER_ONLY", "Solo el organizador o un coorganizador fija la ventana.")
    if starts_at is not None and ends_at is not None:
        validate_window(starts_at, ends_at)
    else:
        starts_at = ends_at = None  # quitar la ventana: traspasos abiertos
    before = {"start": league.transfer_window_start, "end": league.transfer_window_end}
    league.transfer_window_start, league.transfer_window_end = starts_at, ends_at
    ctx.db.flush()
    record_event(ctx, action="TRANSFER_WINDOW_SET", entity="league", entity_id=league.id, initiated_by=actor.id,
                 before=before, after={"start": starts_at, "end": ends_at})
    return league


def check_teams(ctx: ServiceContext, team_ids: list[int]) -> None:
    """Falla con TRANSFER_WINDOW_CLOSED si alguna liga de estos equipos tiene la ventana cerrada."""
    leagues = ctx.db.scalars(select(League).join(LeagueTeam, LeagueTeam.league_id == League.id).where(
        LeagueTeam.team_id.in_(team_ids), LeagueTeam.status == "APPROVED", League.status == "ACTIVE"))
    now = ctx.clock.now()
    for league in leagues:
        check_window(window_open(league.transfer_window_start, league.transfer_window_end, now))
