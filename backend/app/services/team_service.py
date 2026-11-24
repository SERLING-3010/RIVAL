"""Casos de uso de equipos: crear, buscar, ver detalle y Mis equipos."""

from sqlalchemy import func, select

from app.domain.errors import DomainError, NotFoundError, PermissionDeniedError
from app.domain.identity_rules import validate_place_name
from app.domain.roles import ROLES_THAT_CAN_CREATE_TEAMS, TeamRole, UserRole
from app.domain.team_rules import MemberView, initial_team_role, resolve_admin
from app.domain.text_keys import search_key
from app.persistence.models_identity import UserAccount
from app.persistence.models_teams import JoinRequest, Team, TeamMembership
from app.services.audit_service import record_event
from app.services.context import ServiceContext
from app.services.inputs import CreateTeamInput, TeamSearchInput
from app.services.team_views import MemberItem, MyTeamView, TeamDetailView, TeamPage, TeamSummaryView

MAX_PAGE_SIZE = 50


def get_active_team(ctx: ServiceContext, team_id: int, lock: bool = False) -> Team:
    """Con lock=True bloquea la fila del equipo (FOR UPDATE) para cambios de plantilla en serie."""
    team = ctx.db.get(Team, team_id, with_for_update=lock)
    if team is None or team.status != "ACTIVE":
        raise NotFoundError("TEAM_NOT_FOUND", "El equipo no existe o ya no está activo.")
    return team


def member_views(team: Team) -> list[MemberView]:
    return [MemberView(user_id=m.user_id, role=TeamRole(m.role)) for m in team.memberships]


def require_admin(team: Team, actor: UserAccount) -> None:
    if resolve_admin(member_views(team)) != actor.id:
        raise PermissionDeniedError(
            "ADMIN_ONLY", "Solo el administrador del equipo (DT o capitán) puede hacer esto."
        )


def resolve_admin_id(ctx: ServiceContext, team_id: int) -> int | None:
    team = ctx.db.get(Team, team_id)
    return resolve_admin(member_views(team)) if team else None


def record_admin_change(ctx: ServiceContext, team: Team, admin_before: int | None, actor_id: int) -> None:
    """El administrador se calcula; si una acción lo cambia, queda un evento propio en la auditoría."""
    admin_after = resolve_admin(member_views(team))
    if admin_after != admin_before and admin_after is not None:
        record_event(
            ctx, action="TEAM_ADMIN_CHANGED", entity="team", entity_id=team.id, initiated_by=actor_id,
            actor_type="SYSTEM_RULE", before={"admin": admin_before}, after={"admin": admin_after},
        )


def summary(team: Team) -> TeamSummaryView:
    return TeamSummaryView(
        id=team.id, name=team.name, sport_code=team.sport_code, modality_code=team.modality_code,
        city=team.city, neighborhood=team.neighborhood, member_count=len(team.memberships),
        has_coach=any(m.role == TeamRole.COACH for m in team.memberships),
    )


def create_team(ctx: ServiceContext, actor: UserAccount, data: CreateTeamInput) -> Team:
    roles = {UserRole(r.role) for r in actor.roles}
    if not roles & ROLES_THAT_CAN_CREATE_TEAMS:
        raise PermissionDeniedError("ROLE_CANNOT_CREATE_TEAM", "Agrega el rol de jugador o DT para crear un equipo.")
    if data.as_coach and UserRole.COACH not in roles:
        raise PermissionDeniedError("COACH_ROLE_REQUIRED", "Para entrar como DT agrega el rol de director técnico.")
    if not ctx.catalog.has_modality(data.sport_code, data.modality_code):
        raise DomainError("UNKNOWN_MODALITY", "Esa modalidad no corresponde al deporte elegido.")
    name = data.name.strip()
    if not 2 <= len(name) <= 60:
        raise DomainError("INVALID_TEAM_NAME", "El nombre del equipo debe tener entre 2 y 60 caracteres.")
    city = validate_place_name(data.city, "ciudad")
    neighborhood = validate_place_name(data.neighborhood, "barrio")
    now = ctx.clock.now()
    role = initial_team_role(UserRole.COACH if data.as_coach else UserRole.PLAYER)
    team = Team(
        name=name, name_key=search_key(name), sport_code=data.sport_code, modality_code=data.modality_code,
        city=city, city_key=search_key(city), neighborhood=neighborhood, neighborhood_key=search_key(neighborhood),
        created_by=actor.id, created_at=now,
        memberships=[TeamMembership(user_id=actor.id, role=role.value, joined_at=now)],
    )
    ctx.db.add(team)
    ctx.db.flush()
    record_event(
        ctx, action="TEAM_CREATED", entity="team", entity_id=team.id, initiated_by=actor.id,
        after={"name": team.name, "sport": team.sport_code, "modality": team.modality_code, "creator_role": role.value},
    )
    return team


def search_teams(ctx: ServiceContext, query: TeamSearchInput) -> TeamPage:
    page_size = max(1, min(query.page_size, MAX_PAGE_SIZE))
    page = max(1, query.page)
    stmt = select(Team).where(Team.status == "ACTIVE")
    if query.sport_code:
        stmt = stmt.where(Team.sport_code == query.sport_code)
    if query.modality_code:
        stmt = stmt.where(Team.modality_code == query.modality_code)
    if query.city:
        stmt = stmt.where(Team.city_key == search_key(query.city))
    if query.query:
        stmt = stmt.where(Team.name_key.contains(search_key(query.query), autoescape=True))
    total = ctx.db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    rows = ctx.db.scalars(stmt.order_by(Team.name_key, Team.id).offset((page - 1) * page_size).limit(page_size))
    return TeamPage(items=[summary(t) for t in rows], page=page, page_size=page_size, total=total)


def team_detail(ctx: ServiceContext, team_id: int) -> TeamDetailView:
    team = get_active_team(ctx, team_id)
    users = {u.id: u for u in ctx.db.scalars(
        select(UserAccount).where(UserAccount.id.in_([m.user_id for m in team.memberships]))
    )}
    members = [
        MemberItem(user_id=m.user_id, display_name=users[m.user_id].display_name,
                   role=TeamRole(m.role), position=users[m.user_id].position)
        for m in sorted(team.memberships, key=lambda m: (m.joined_at, m.id))
    ]
    return TeamDetailView(team=summary(team), admin_user_id=resolve_admin(member_views(team)), members=members)


def my_teams(ctx: ServiceContext, actor: UserAccount) -> list[MyTeamView]:
    memberships = ctx.db.scalars(
        select(TeamMembership).join(Team).where(TeamMembership.user_id == actor.id, Team.status == "ACTIVE")
    ).all()
    result: list[MyTeamView] = []
    for membership in memberships:
        team = membership.team
        is_admin = resolve_admin(member_views(team)) == actor.id
        pending = 0
        if is_admin:
            pending = ctx.db.scalar(select(func.count()).select_from(JoinRequest).where(
                JoinRequest.team_id == team.id, JoinRequest.status == "PENDING",
                JoinRequest.direction == "REQUEST")) or 0
        result.append(MyTeamView(team=summary(team), my_role=TeamRole(membership.role),
                                 is_admin=is_admin, pending_requests=pending))
    return result
