"""Inscripción de equipos y cuerpo arbitral de una liga (Sprint 5, RIV-010 y RIV-011).

Pedir y decidir bloquean la fila de la liga (FOR UPDATE); el índice único parcial impide
dos solicitudes activas del mismo equipo o árbitro en la misma liga.
"""

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.domain.errors import ConflictError, DomainError, NotFoundError, PermissionDeniedError
from app.domain.league_rules import ACTIVE_STATUSES, EnrollmentKind, EnrollmentStatus, check_can_decide
from app.domain.roles import UserRole
from app.persistence.models_identity import UserAccount
from app.persistence.models_leagues import LeagueReferee, LeagueTeam
from app.services.audit_service import record_event
from app.services.context import ServiceContext
from app.services.league_queries import get_league, staff_role
from app.services.team_service import get_active_team, require_admin, resolve_admin_id

_PENDING, _APPROVED = EnrollmentStatus.PENDING.value, EnrollmentStatus.APPROVED.value
Entry = LeagueTeam | LeagueReferee


def _insert(ctx: ServiceContext, entry: Entry, kind: EnrollmentKind, actor_id: int, after: dict[str, object]) -> None:
    model = type(entry)
    owner = model.team_id == entry.team_id if isinstance(entry, LeagueTeam) else LeagueReferee.user_id == entry.user_id
    if ctx.db.scalar(select(model.id).where(model.league_id == entry.league_id, owner,
                                            model.status.in_(ACTIVE_STATUSES))) is not None:
        raise ConflictError("ALREADY_REQUESTED", "Ya hay una solicitud pendiente o aprobada en esta liga.")
    ctx.db.add(entry)
    try:  # el índice único cubre la carrera entre dos peticiones simultáneas
        ctx.db.flush()
    except IntegrityError as error:
        raise ConflictError("ALREADY_REQUESTED", "Ya hay una solicitud pendiente o aprobada en esta liga.") from error
    record_event(ctx, action=f"LEAGUE_{kind.upper()}_REQUESTED", entity=f"league_{kind}", entity_id=entry.id,
                 initiated_by=actor_id, after={"league_id": entry.league_id, **after})


def request_team(ctx: ServiceContext, actor: UserAccount, league_id: int, team_id: int) -> LeagueTeam:
    league = get_league(ctx, league_id, lock=True)
    team = get_active_team(ctx, team_id)
    require_admin(team, actor)
    if (team.sport_code, team.modality_code, team.city_key) != (league.sport_code, league.modality_code, league.city_key):
        raise DomainError("TEAM_NOT_ELIGIBLE", "Tu equipo debe ser del mismo deporte, modalidad y ciudad de la liga.")
    entry = LeagueTeam(league_id=league.id, team_id=team.id, status=_PENDING, requested_by=actor.id,
                       requested_at=ctx.clock.now())
    _insert(ctx, entry, "team", actor.id, {"team_id": team.id})
    return entry


def request_referee(ctx: ServiceContext, actor: UserAccount, league_id: int) -> LeagueReferee:
    league = get_league(ctx, league_id, lock=True)
    if not any(r.role == UserRole.REFEREE for r in actor.roles):
        raise PermissionDeniedError("REFEREE_ROLE_REQUIRED", "Agrega el rol de árbitro para unirte al cuerpo arbitral.")
    if league.sport_code not in {s.sport_code for s in actor.sports}:
        raise DomainError("SPORT_NOT_IN_PROFILE", "Agrega el deporte de la liga a tu perfil de árbitro.")
    entry = LeagueReferee(league_id=league.id, user_id=actor.id, status=_PENDING, requested_at=ctx.clock.now())
    _insert(ctx, entry, "referee", actor.id, {"user_id": actor.id})
    return entry


def _get_entry(ctx: ServiceContext, kind: EnrollmentKind, entry_id: int) -> Entry:
    model: type[Entry] = LeagueTeam if kind == "team" else LeagueReferee
    entry = ctx.db.get(model, entry_id)
    if entry is None:
        raise NotFoundError("LEAGUE_REQUEST_NOT_FOUND", "La solicitud no existe.")
    get_league(ctx, entry.league_id, lock=True)  # mismo orden de bloqueo en todas las acciones
    ctx.db.refresh(entry)
    return entry


def _requester_id(ctx: ServiceContext, entry: Entry) -> int | None:
    return resolve_admin_id(ctx, entry.team_id) if isinstance(entry, LeagueTeam) else entry.user_id


def decide(ctx: ServiceContext, actor: UserAccount, kind: EnrollmentKind, entry_id: int, approve: bool) -> Entry:
    entry = _get_entry(ctx, kind, entry_id)
    check_can_decide(staff_role(ctx, entry.league_id, actor.id), kind)
    if entry.status != _PENDING:
        raise ConflictError("LEAGUE_REQUEST_NOT_PENDING", "Esta solicitud ya fue decidida.")
    entry.status = _APPROVED if approve else EnrollmentStatus.REJECTED.value
    entry.decided_by, entry.decided_at = actor.id, ctx.clock.now()
    ctx.db.flush()
    record_event(ctx, action=f"LEAGUE_{kind.upper()}_{'APPROVED' if approve else 'REJECTED'}",
                 entity=f"league_{kind}", entity_id=entry.id, initiated_by=_requester_id(ctx, entry),
                 approved_by=actor.id, before={"status": _PENDING}, after={"status": entry.status})
    return entry


def withdraw(ctx: ServiceContext, actor: UserAccount, kind: EnrollmentKind, entry_id: int) -> Entry:
    """Quien pidió retira la solicitud pendiente, o sale de la liga si ya estaba aprobado."""
    entry = _get_entry(ctx, kind, entry_id)
    if _requester_id(ctx, entry) != actor.id:
        raise PermissionDeniedError("REQUESTER_ONLY", "Solo quien pidió (o el administrador del equipo) puede retirarla.")
    if entry.status not in (_PENDING, _APPROVED):
        raise ConflictError("LEAGUE_REQUEST_CLOSED", "Esta solicitud ya está cerrada.")
    before = entry.status
    entry.status, entry.decided_by, entry.decided_at = EnrollmentStatus.WITHDRAWN.value, actor.id, ctx.clock.now()
    ctx.db.flush()
    record_event(ctx, action=f"LEAGUE_{kind.upper()}_WITHDRAWN", entity=f"league_{kind}", entity_id=entry.id,
                 initiated_by=actor.id, before={"status": before}, after={"status": entry.status})
    return entry
