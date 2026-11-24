"""Crear ligas y nombrar su personal (Sprint 5, RIV-011)."""

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.domain.errors import ConflictError, DomainError, NotFoundError, PermissionDeniedError
from app.domain.identity_rules import validate_place_name
from app.domain.league_rules import StaffRole, check_can_create, validate_league_name, validate_season
from app.domain.roles import UserRole
from app.domain.text_keys import search_key
from app.persistence.models_identity import UserAccount
from app.persistence.models_leagues import League, LeagueStaff
from app.persistence.models_teams import Team, TeamMembership
from app.services.audit_service import record_event
from app.services.context import ServiceContext
from app.services.league_queries import get_league, staff_role
from app.services.league_views import LeagueInput


def create_league(ctx: ServiceContext, actor: UserAccount, data: LeagueInput) -> League:
    has_team = ctx.db.scalar(select(TeamMembership.id).join(Team).where(
        TeamMembership.user_id == actor.id, Team.status == "ACTIVE").limit(1)) is not None
    check_can_create(is_referee=any(r.role == UserRole.REFEREE for r in actor.roles), has_team=has_team)
    if not ctx.catalog.has_modality(data.sport_code, data.modality_code):
        raise DomainError("UNKNOWN_MODALITY", "Esa modalidad no corresponde al deporte elegido.")
    name, city = validate_league_name(data.name), validate_place_name(data.city, "ciudad")
    now = ctx.clock.now()
    league = League(
        name=name, name_key=search_key(name), sport_code=data.sport_code, modality_code=data.modality_code,
        city=city, city_key=search_key(city), season=validate_season(data.season),
        description=(data.description or "").strip()[:300] or None, created_by=actor.id, created_at=now,
    )
    ctx.db.add(league)
    ctx.db.flush()
    ctx.db.add(LeagueStaff(league_id=league.id, user_id=actor.id, role=StaffRole.ORGANIZER.value,
                           added_by=actor.id, added_at=now))
    ctx.db.flush()
    record_event(ctx, action="LEAGUE_CREATED", entity="league", entity_id=league.id, initiated_by=actor.id,
                 after={"name": name, "sport": league.sport_code, "modality": league.modality_code,
                        "city": city, "season": league.season})
    return league


def add_staff(ctx: ServiceContext, actor: UserAccount, league_id: int, user_id: int, role: StaffRole) -> LeagueStaff:
    league = get_league(ctx, league_id, lock=True)
    if staff_role(ctx, league.id, actor.id) != StaffRole.ORGANIZER:
        raise PermissionDeniedError("ORGANIZER_ONLY", "Solo el organizador de la liga puede nombrar personal.")
    if ctx.db.get(UserAccount, user_id) is None:
        raise NotFoundError("USER_NOT_FOUND", "Esa persona no existe en RIVAL.")
    if staff_role(ctx, league.id, user_id) is not None:
        raise ConflictError("ALREADY_STAFF", "Esa persona ya hace parte del personal de la liga.")
    staff = LeagueStaff(league_id=league.id, user_id=user_id, role=role.value, added_by=actor.id,
                        added_at=ctx.clock.now())
    ctx.db.add(staff)
    try:
        ctx.db.flush()
    except IntegrityError as error:
        raise ConflictError("ALREADY_STAFF", "Esa persona ya hace parte del personal de la liga.") from error
    record_event(ctx, action="LEAGUE_STAFF_ADDED", entity="league", entity_id=league.id, initiated_by=actor.id,
                 after={"user_id": user_id, "role": role.value})
    return staff
