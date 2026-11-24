"""Agentes libres: jugadores sin equipo que quieren ser encontrados, por deporte, barrio y ciudad."""

from dataclasses import dataclass

from sqlalchemy import func, select

from app.domain.errors import DomainError, PermissionDeniedError
from app.domain.roles import ROLES_THAT_CAN_CREATE_TEAMS, UserRole
from app.domain.text_keys import search_key
from app.persistence.models_identity import UserAccount
from app.persistence.models_scouting import FreeAgentProfile
from app.services.audit_service import record_event
from app.services.context import ServiceContext
from app.services.team_service import MAX_PAGE_SIZE


@dataclass(frozen=True)
class FreeAgentView:
    user_id: int
    display_name: str
    sport_code: str
    position: str | None
    note: str | None
    neighborhood: str
    city: str


@dataclass(frozen=True)
class FreeAgentPage:
    items: list[FreeAgentView]
    page: int
    page_size: int
    total: int


def set_free_agent(
    ctx: ServiceContext, actor: UserAccount, sport_code: str, active: bool, position: str | None, note: str | None
) -> FreeAgentProfile:
    if not {UserRole(r.role) for r in actor.roles} & ROLES_THAT_CAN_CREATE_TEAMS:
        raise PermissionDeniedError("ROLE_CANNOT_BE_FREE_AGENT", "Agrega el rol de jugador para aparecer como agente libre.")
    if not ctx.catalog.has_sport(sport_code):
        raise DomainError("UNKNOWN_SPORT", f"El deporte {sport_code} no está en el catálogo.")
    profile = ctx.db.scalar(select(FreeAgentProfile).where(
        FreeAgentProfile.user_id == actor.id, FreeAgentProfile.sport_code == sport_code))
    before = {"active": profile.active} if profile else None
    if profile is None:
        profile = FreeAgentProfile(user_id=actor.id, sport_code=sport_code)
        ctx.db.add(profile)
    profile.active = active
    profile.position = (position or "").strip()[:40] or None
    profile.note = (note or "").strip()[:200] or None
    profile.updated_at = ctx.clock.now()
    ctx.db.flush()
    record_event(ctx, action="FREE_AGENT_UPDATED", entity="free_agent_profile", entity_id=profile.id,
                 initiated_by=actor.id, before=before, after={"active": active, "sport": sport_code})
    return profile


def search(
    ctx: ServiceContext,
    actor: UserAccount,
    sport_code: str,
    city: str,
    neighborhood: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> FreeAgentPage:
    page, page_size = max(1, page), max(1, min(page_size, MAX_PAGE_SIZE))
    stmt = (
        select(FreeAgentProfile, UserAccount)
        .join(UserAccount, UserAccount.id == FreeAgentProfile.user_id)
        .where(FreeAgentProfile.active.is_(True), FreeAgentProfile.sport_code == sport_code,
               UserAccount.city_key == search_key(city))
    )
    if neighborhood:
        stmt = stmt.where(UserAccount.neighborhood_key == search_key(neighborhood))
    total = ctx.db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    rows = ctx.db.execute(
        stmt.order_by(FreeAgentProfile.updated_at.desc(), FreeAgentProfile.id).offset((page - 1) * page_size).limit(page_size)
    ).all()
    items = [
        FreeAgentView(user_id=u.id, display_name=u.display_name, sport_code=p.sport_code,
                      position=p.position or u.position, note=p.note, neighborhood=u.neighborhood, city=u.city)
        for p, u in rows
    ]
    return FreeAgentPage(items=items, page=page, page_size=page_size, total=total)


def deactivate(ctx: ServiceContext, user_id: int, sport_code: str) -> None:
    profile = ctx.db.scalar(select(FreeAgentProfile).where(
        FreeAgentProfile.user_id == user_id, FreeAgentProfile.sport_code == sport_code))
    if profile is not None and profile.active:
        profile.active = False
        profile.updated_at = ctx.clock.now()


def my_profiles(ctx: ServiceContext, actor: UserAccount) -> list[FreeAgentProfile]:
    return list(ctx.db.scalars(select(FreeAgentProfile).where(FreeAgentProfile.user_id == actor.id)
                               .order_by(FreeAgentProfile.sport_code)))
