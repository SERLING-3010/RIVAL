"""Convocatoria del partido (Sprint 10): el administrador convoca y cada jugador responde si va.

Se cierra a la hora del partido (la firmada; si aún no hay, la de la versión en negociación).
"""

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select

from app.domain.contract_rules import ContractStatus
from app.domain.errors import ConflictError, DomainError, NotFoundError
from app.domain.matchday_rules import CallUpStatus, check_before_kickoff
from app.persistence.models_contracts import MatchContract
from app.persistence.models_identity import UserAccount
from app.persistence.models_matchday import CallUp
from app.persistence.models_teams import Team
from app.services import loan_service
from app.services.audit_service import record_event
from app.services.context import ServiceContext
from app.services.contract_queries import get_version, load_contract, member_side, side_teams, terms_of
from app.services.matchday_staff import staff_side


@dataclass(frozen=True)
class CallUpItem:
    user_id: int
    display_name: str
    status: str


@dataclass(frozen=True)
class TeamCallUpView:
    contract_id: int
    items: list[CallUpItem]
    going: int
    not_going: int
    pending: int


@dataclass(frozen=True)
class MyCallUpView:
    contract_id: int
    my_team: str
    opponent: str
    kickoff_at: datetime
    status: str


def _kickoff(ctx: ServiceContext, contract: MatchContract) -> datetime:
    return terms_of(get_version(ctx, contract.signed_version_id or contract.current_version_id)).kickoff_at


def call_up(ctx: ServiceContext, actor: UserAccount, contract_id: int, user_ids: list[int]) -> None:
    contract = load_contract(ctx, contract_id, lock=True)
    _side, team = staff_side(ctx, contract, actor)
    if contract.status == ContractStatus.CANCELLED:
        raise ConflictError("CONTRACT_CANCELLED", "Este partido fue cancelado.")
    check_before_kickoff(_kickoff(ctx, contract), ctx.clock.now())
    members = {m.user_id for m in team.memberships} | loan_service.active_players(ctx, contract.id, team.id)
    if not user_ids or not set(user_ids) <= members:
        raise DomainError("NOT_A_TEAM_MEMBER", "Solo puedes convocar a jugadores de tu equipo.")
    called = set(ctx.db.scalars(select(CallUp.user_id).where(CallUp.contract_id == contract.id)))
    for user_id in sorted(set(user_ids) - called):
        ctx.db.add(CallUp(contract_id=contract.id, team_id=team.id, user_id=user_id, status=CallUpStatus.INVITED,
                          invited_by=actor.id, invited_at=ctx.clock.now()))
    ctx.db.flush()
    record_event(ctx, action="CALLUP_SENT", entity="match_contract", entity_id=contract.id, initiated_by=actor.id,
                 after={"team_id": team.id, "user_ids": sorted(set(user_ids) - called)})


def respond(ctx: ServiceContext, actor: UserAccount, contract_id: int, going: bool) -> CallUp:
    contract = load_contract(ctx, contract_id, lock=True)
    entry = ctx.db.scalar(select(CallUp).where(CallUp.contract_id == contract.id, CallUp.user_id == actor.id))
    if entry is None:
        raise NotFoundError("CALLUP_NOT_FOUND", "No estás convocado a este partido.")
    check_before_kickoff(_kickoff(ctx, contract), ctx.clock.now())
    before = entry.status
    entry.status = (CallUpStatus.GOING if going else CallUpStatus.NOT_GOING).value
    entry.responded_at = ctx.clock.now()
    ctx.db.flush()
    record_event(ctx, action="CALLUP_RESPONDED", entity="match_contract", entity_id=contract.id,
                 initiated_by=actor.id, before={"status": before}, after={"status": entry.status})
    return entry


def team_callup(ctx: ServiceContext, actor: UserAccount, contract_id: int) -> TeamCallUpView:
    contract = load_contract(ctx, contract_id)
    teams = side_teams(ctx, contract)
    team = teams[member_side(teams, actor)]
    rows = ctx.db.execute(select(CallUp, UserAccount).join(UserAccount, UserAccount.id == CallUp.user_id)
                          .where(CallUp.contract_id == contract.id, CallUp.team_id == team.id)
                          .order_by(UserAccount.display_name)).all()
    items = [CallUpItem(user_id=u.id, display_name=u.display_name, status=c.status) for c, u in rows]
    count = lambda status: sum(1 for i in items if i.status == status)  # noqa: E731
    return TeamCallUpView(contract_id=contract.id, items=items, going=count("GOING"), not_going=count("NOT_GOING"),
                          pending=count("INVITED"))


def my_callups(ctx: ServiceContext, actor: UserAccount) -> list[MyCallUpView]:
    views = []
    for entry in ctx.db.scalars(select(CallUp).where(CallUp.user_id == actor.id).order_by(CallUp.id.desc())):
        contract = load_contract(ctx, entry.contract_id)
        kickoff = _kickoff(ctx, contract)
        if contract.status == ContractStatus.CANCELLED or kickoff <= ctx.clock.now():
            continue
        mine, other = ctx.db.get(Team, entry.team_id), ctx.db.get(Team, contract.host_team_id
                                                                   if entry.team_id == contract.guest_team_id
                                                                   else contract.guest_team_id)
        views.append(MyCallUpView(contract_id=contract.id, my_team=mine.name if mine else "",
                                  opponent=other.name if other else "", kickoff_at=kickoff, status=entry.status))
    return views
