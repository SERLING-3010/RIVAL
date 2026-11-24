"""Lectura de ligas: buscar, detalle y mis ligas. Cualquiera ve lo aprobado; solo el personal ve lo pendiente."""

from sqlalchemy import func, select

from app.domain.errors import NotFoundError
from app.domain.league_rules import ACTIVE_STATUSES, EnrollmentStatus, StaffRole
from app.domain.team_rules import resolve_admin
from app.domain.text_keys import search_key
from app.persistence.models_identity import UserAccount
from app.persistence.models_leagues import League, LeagueReferee, LeagueStaff, LeagueTeam
from app.persistence.models_teams import Team
from app.services.context import ServiceContext
from app.services.league_views import (
    LeagueDetailView, LeaguePage, LeagueSearchInput, LeagueSummaryView, MyLeagueView, RefereeEntryView, StaffView,
    TeamEntryView,
)
from app.services.team_service import member_views, summary

MAX_PAGE_SIZE = 50
_APPROVED = EnrollmentStatus.APPROVED.value


def get_league(ctx: ServiceContext, league_id: int, lock: bool = False) -> League:
    league = ctx.db.get(League, league_id, with_for_update=lock)
    if league is None or league.status != "ACTIVE":
        raise NotFoundError("LEAGUE_NOT_FOUND", "La liga no existe o ya no está activa.")
    return league


def staff_role(ctx: ServiceContext, league_id: int, user_id: int) -> StaffRole | None:
    role = ctx.db.scalar(select(LeagueStaff.role).where(LeagueStaff.league_id == league_id,
                                                        LeagueStaff.user_id == user_id))
    return StaffRole(role) if role else None


def league_summary(ctx: ServiceContext, league: League) -> LeagueSummaryView:
    def count(model: type[LeagueTeam] | type[LeagueReferee]) -> int:
        return ctx.db.scalar(select(func.count()).select_from(model).where(
            model.league_id == league.id, model.status == _APPROVED)) or 0
    return LeagueSummaryView(id=league.id, name=league.name, sport_code=league.sport_code,
                             modality_code=league.modality_code, city=league.city, season=league.season,
                             team_count=count(LeagueTeam), referee_count=count(LeagueReferee))


def search_leagues(ctx: ServiceContext, query: LeagueSearchInput) -> LeaguePage:
    page_size, page = max(1, min(query.page_size, MAX_PAGE_SIZE)), max(1, query.page)
    stmt = select(League).where(League.status == "ACTIVE")
    if query.sport_code:
        stmt = stmt.where(League.sport_code == query.sport_code)
    if query.city:
        stmt = stmt.where(League.city_key == search_key(query.city))
    if query.query:
        stmt = stmt.where(League.name_key.contains(search_key(query.query), autoescape=True))
    total = ctx.db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    rows = ctx.db.scalars(stmt.order_by(League.name_key, League.id).offset((page - 1) * page_size).limit(page_size))
    return LeaguePage(items=[league_summary(ctx, l) for l in rows], page=page, page_size=page_size, total=total)


def _team_entries(ctx: ServiceContext, league_id: int, statuses: tuple[str, ...]) -> list[TeamEntryView]:
    rows = ctx.db.execute(select(LeagueTeam, Team).join(Team, Team.id == LeagueTeam.team_id).where(
        LeagueTeam.league_id == league_id, LeagueTeam.status.in_(statuses)).order_by(LeagueTeam.id)).all()
    return [TeamEntryView(id=e.id, team=summary(t), status=e.status) for e, t in rows]


def _referee_entries(ctx: ServiceContext, league_id: int, statuses: tuple[str, ...]) -> list[RefereeEntryView]:
    rows = ctx.db.execute(select(LeagueReferee, UserAccount).join(UserAccount, UserAccount.id == LeagueReferee.user_id)
                          .where(LeagueReferee.league_id == league_id, LeagueReferee.status.in_(statuses))
                          .order_by(LeagueReferee.id)).all()
    return [RefereeEntryView(id=e.id, user_id=u.id, display_name=u.display_name, status=e.status) for e, u in rows]


def league_detail(ctx: ServiceContext, actor: UserAccount, league_id: int) -> LeagueDetailView:
    league = get_league(ctx, league_id)
    role = staff_role(ctx, league.id, actor.id)
    staff = [StaffView(user_id=u.id, display_name=u.display_name, role=s.role) for s, u in ctx.db.execute(
        select(LeagueStaff, UserAccount).join(UserAccount, UserAccount.id == LeagueStaff.user_id)
        .where(LeagueStaff.league_id == league.id).order_by(LeagueStaff.id)).all()]
    pending = (EnrollmentStatus.PENDING.value,)
    active_teams = _team_entries(ctx, league.id, ACTIVE_STATUSES)
    mine = [e for e in active_teams if _admin_of(ctx, e.team.id) == actor.id]
    my_ref = next((r for r in _referee_entries(ctx, league.id, ACTIVE_STATUSES) if r.user_id == actor.id), None)
    return LeagueDetailView(
        league=league_summary(ctx, league), description=league.description, my_role=role.value if role else None,
        staff=staff, teams=_team_entries(ctx, league.id, (_APPROVED,)),
        referees=_referee_entries(ctx, league.id, (_APPROVED,)),
        pending_teams=_team_entries(ctx, league.id, pending) if role else [],
        pending_referees=_referee_entries(ctx, league.id, pending) if role else [],
        my_team_requests=mine, my_referee_request=my_ref,
    )


def _admin_of(ctx: ServiceContext, team_id: int) -> int | None:
    team = ctx.db.get(Team, team_id)
    return resolve_admin(member_views(team)) if team else None


def my_leagues(ctx: ServiceContext, actor: UserAccount) -> list[MyLeagueView]:
    relations: dict[int, str] = {}
    for league_id, role in ctx.db.execute(select(LeagueStaff.league_id, LeagueStaff.role).where(
            LeagueStaff.user_id == actor.id)):
        relations[league_id] = role
    for (league_id,) in ctx.db.execute(select(LeagueReferee.league_id).where(
            LeagueReferee.user_id == actor.id, LeagueReferee.status == _APPROVED)):
        relations.setdefault(league_id, "REFEREE")
    for (league_id,) in ctx.db.execute(select(LeagueTeam.league_id).join(Team, Team.id == LeagueTeam.team_id).where(
            LeagueTeam.status == _APPROVED, Team.memberships.any(user_id=actor.id))):
        relations.setdefault(league_id, "TEAM")
    leagues = ctx.db.scalars(select(League).where(League.id.in_(relations), League.status == "ACTIVE")
                             .order_by(League.name_key))
    return [MyLeagueView(league=league_summary(ctx, l), relation=relations[l.id]) for l in leagues]
