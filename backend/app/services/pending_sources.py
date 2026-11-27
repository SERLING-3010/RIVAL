"""Fuentes de pendientes (Sprint 11). Cada función devuelve tuplas (tipo, título, detalle, destino, id, hora)."""

from datetime import datetime

from sqlalchemy import func, or_, select

from app.domain.contract_rules import ContractStatus
from app.domain.matchday_rules import RATING_WINDOW
from app.domain.result_rules import ResultStatus
from app.persistence.models_contracts import MatchContract
from app.persistence.models_identity import UserAccount
from app.persistence.models_league_matches import RefereeAssignment
from app.persistence.models_leagues import League, LeagueReferee, LeagueStaff, LeagueTeam
from app.persistence.models_manager import TransferOffer
from app.persistence.models_matchday import CallUp
from app.persistence.models_teams import JoinRequest, Team
from app.persistence.models_venues import Booking, Court, Slot, Venue
from app.services import player_rating_service
from app.services.context import ServiceContext
from app.services.contract_queries import get_version, signed_sides, terms_of
from app.services.result_queries import get_result, reports_of

Row = tuple[str, str, str, str, int | None, datetime | None]


def _names(ctx: ServiceContext, c: MatchContract) -> str:
    host, guest = ctx.db.get(Team, c.host_team_id), ctx.db.get(Team, c.guest_team_id)
    return f"{host.name if host else ''} vs {guest.name if guest else ''}"


def _kickoff(ctx: ServiceContext, c: MatchContract) -> datetime:
    return terms_of(get_version(ctx, c.signed_version_id or c.current_version_id)).kickoff_at


def contracts(ctx: ServiceContext, admin_teams: list[Team]) -> list[Row]:
    ids, now, rows = [t.id for t in admin_teams], ctx.clock.now(), []
    for c in ctx.db.scalars(select(MatchContract).where(
            MatchContract.status != ContractStatus.CANCELLED,
            or_(MatchContract.host_team_id.in_(ids), MatchContract.guest_team_id.in_(ids)))):
        mine, side = (c.host_team_id, "HOST") if c.host_team_id in ids else (c.guest_team_id, "GUEST")
        kickoff = _kickoff(ctx, c)
        current = get_version(ctx, c.current_version_id)
        if c.status == ContractStatus.NEGOTIATING and kickoff > now and side not in signed_sides(ctx, c, current):
            rows.append(("SIGN_CONTRACT", f"Firmar: {_names(ctx, c)}", "Falta la firma de tu equipo.",
                         "contract", c.id, kickoff))
        if c.signed_version_id is None or kickoff > now:
            continue
        result = get_result(ctx, c.id)
        if result is not None and result.status == ResultStatus.DISPUTED:
            rows.append(("RESULT_DISPUTED", f"Marcador en disputa: {_names(ctx, c)}",
                         "Los marcadores no coinciden; revísalo con el rival.", "contract", c.id, kickoff))
        elif (result is None or result.status == ResultStatus.PENDING) and mine not in {
                r.team_id for r in reports_of(ctx, c.id)}:
            rows.append(("REPORT_RESULT", f"Reportar marcador: {_names(ctx, c)}", "El partido ya se jugó.",
                         "contract", c.id, kickoff))
    return rows


def callups(ctx: ServiceContext, actor: UserAccount) -> list[Row]:
    rows = []
    for entry in ctx.db.scalars(select(CallUp).where(CallUp.user_id == actor.id, CallUp.status == "INVITED")):
        c = ctx.db.get(MatchContract, entry.contract_id)
        if c is None or c.status == ContractStatus.CANCELLED or _kickoff(ctx, c) <= ctx.clock.now():
            continue
        rows.append(("CALLUP", f"¿Vas? {_names(ctx, c)}", "Te convocaron a este partido.", "contract", c.id,
                     _kickoff(ctx, c)))
    return rows


def transfers(ctx: ServiceContext, actor: UserAccount, admin_teams: list[Team]) -> list[Row]:
    mine = [("TRANSFER_PLAYER", "Oferta de traspaso por ti", "Tu DT ya aceptó; tú decides.", o)
            for o in ctx.db.scalars(select(TransferOffer).where(
                TransferOffer.player_id == actor.id, TransferOffer.status == "PENDING_PLAYER"))]
    owner = [("TRANSFER_OWNER", "Oferta por un jugador de tu equipo", "Acepta o rechaza la oferta.", o)
             for o in ctx.db.scalars(select(TransferOffer).where(
                 TransferOffer.from_team_id.in_([t.id for t in admin_teams]), TransferOffer.status == "PENDING_OWNER"))]
    return [(k, t, d, "transfers" if k == "TRANSFER_PLAYER" else "team",
             o.id if k == "TRANSFER_PLAYER" else o.from_team_id, None) for k, t, d, o in mine + owner]


def join_requests(ctx: ServiceContext, admin_teams: list[Team]) -> list[Row]:
    rows = []
    for team in admin_teams:
        count = ctx.db.scalar(select(func.count()).select_from(JoinRequest).where(
            JoinRequest.team_id == team.id, JoinRequest.status == "PENDING", JoinRequest.direction == "REQUEST")) or 0
        if count:
            rows.append(("JOIN_REQUESTS", f"{count} solicitud(es) para {team.name}", "Aprueba o rechaza.",
                         "team", team.id, None))
    return rows


def referee(ctx: ServiceContext, actor: UserAccount) -> list[Row]:
    rows, now = [], ctx.clock.now()
    for a in ctx.db.scalars(select(RefereeAssignment).where(RefereeAssignment.referee_id == actor.id,
                                                            RefereeAssignment.status.in_(("PENDING", "ACCEPTED")))):
        c = ctx.db.get(MatchContract, a.contract_id)
        if c is None or c.status == ContractStatus.CANCELLED:
            continue
        kickoff, result = _kickoff(ctx, c), get_result(ctx, c.id)
        if a.status == "PENDING" and kickoff > now:
            rows.append(("REFEREE_ASSIGNMENT", f"Arbitrar: {_names(ctx, c)}", "Acepta o rechaza el partido.",
                         "referee", c.id, kickoff))
        elif a.status == "ACCEPTED" and kickoff <= now and (result is None or result.status != "CONFIRMED"):
            rows.append(("REFEREE_RESULT", f"Fijar resultado: {_names(ctx, c)}", "Ya se jugó el partido.",
                         "referee", c.id, kickoff))
    return rows


def bookings(ctx: ServiceContext, actor: UserAccount) -> list[Row]:
    rows = ctx.db.execute(select(Booking, Slot, Venue).join(Slot, Slot.id == Booking.slot_id)
                          .join(Court, Court.id == Slot.court_id).join(Venue, Venue.id == Court.venue_id)
                          .where(Venue.owner_id == actor.id, Booking.status == "PENDING",
                                 Slot.starts_at > ctx.clock.now())).all()
    return [("CONFIRM_BOOKING", f"Confirmar reserva en {v.name}", "Un equipo pidió una franja para su partido.",
             "venue", v.id, s.starts_at) for _b, s, v in rows]


def leagues(ctx: ServiceContext, actor: UserAccount) -> list[Row]:
    rows = []
    for staff, league in ctx.db.execute(select(LeagueStaff, League).join(League, League.id == LeagueStaff.league_id)
                                        .where(LeagueStaff.user_id == actor.id, League.status == "ACTIVE")).all():
        teams = 0 if staff.role == "REFEREE_COORDINATOR" else ctx.db.scalar(select(func.count()).select_from(
            LeagueTeam).where(LeagueTeam.league_id == league.id, LeagueTeam.status == "PENDING")) or 0
        refs = ctx.db.scalar(select(func.count()).select_from(LeagueReferee).where(
            LeagueReferee.league_id == league.id, LeagueReferee.status == "PENDING")) or 0
        if teams + refs:
            rows.append(("LEAGUE_REQUESTS", f"{teams + refs} solicitud(es) en {league.name}", "Revísalas en la liga.",
                         "league", league.id, None))
    return rows


def ratings(ctx: ServiceContext, actor: UserAccount, member_teams: list[Team]) -> list[Row]:
    ids, since, rows = [t.id for t in member_teams], ctx.clock.now() - RATING_WINDOW, []
    for c in ctx.db.scalars(select(MatchContract).where(
            MatchContract.signed_version_id.is_not(None),
            or_(MatchContract.host_team_id.in_(ids), MatchContract.guest_team_id.in_(ids)))):
        result = get_result(ctx, c.id)
        if result is None or result.status != ResultStatus.CONFIRMED or _kickoff(ctx, c) < since:
            continue
        if player_rating_service.to_rate(ctx, actor, c.id):
            rows.append(("RATE_TEAMMATES", f"Valora a tus compañeros: {_names(ctx, c)}", "Tienes 7 días.",
                         "contract", c.id, _kickoff(ctx, c) + RATING_WINDOW))
    return rows
