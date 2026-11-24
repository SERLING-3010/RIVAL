"""Central de actividad (RIV-014): quién hizo cada cambio, con antes y después.

Lee la bitácora de auditoría filtrada por lo que el usuario puede ver. Nunca incluye eventos
de cuentas (registro, sesiones): esos datos son de la persona, no del equipo.
"""

import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from sqlalchemy import and_, or_, select

from app.persistence.models_audit import AuditEvent
from app.persistence.models_contracts import MatchContract
from app.persistence.models_identity import UserAccount
from app.persistence.models_leagues import LeagueTeam
from app.persistence.models_manager import TransferOffer
from app.persistence.models_matches import MatchOffer, MatchRequest
from app.persistence.models_teams import JoinRequest
from app.services.context import ServiceContext
from app.services.contract_queries import load_contract, member_side, side_teams
from app.services.rival_service import require_member
from app.services.team_service import get_active_team

MAX_ITEMS = 100


@dataclass(frozen=True)
class ActivityView:
    occurred_at: datetime
    action: str
    entity: str
    entity_id: str
    actor_type: str
    actor_name: str | None
    approver_name: str | None
    before: dict[str, Any] | None
    after: dict[str, Any] | None


def _ids(ctx: ServiceContext, stmt: Any) -> list[str]:
    return [str(i) for i in ctx.db.scalars(stmt)]


def _load(ctx: ServiceContext, scopes: dict[str, list[str]]) -> list[ActivityView]:
    conditions = [and_(AuditEvent.entity == entity, AuditEvent.entity_id.in_(ids)) for entity, ids in scopes.items() if ids]
    events = list(ctx.db.scalars(select(AuditEvent).where(or_(*conditions))
                                 .order_by(AuditEvent.chain_position.desc()).limit(MAX_ITEMS)))
    people = {e for ev in events for e in (ev.initiated_by, ev.approved_by) if e is not None}
    names = {u.id: u.display_name for u in ctx.db.scalars(select(UserAccount).where(UserAccount.id.in_(people)))}
    return [
        ActivityView(occurred_at=ev.occurred_at, action=ev.action, entity=ev.entity, entity_id=ev.entity_id,
                     actor_type=ev.actor_type, actor_name=names.get(ev.initiated_by or 0),
                     approver_name=names.get(ev.approved_by or 0),
                     before=json.loads(ev.before_json) if ev.before_json else None,
                     after=json.loads(ev.after_json) if ev.after_json else None)
        for ev in events
    ]


def team_activity(ctx: ServiceContext, actor: UserAccount, team_id: int) -> list[ActivityView]:
    team = get_active_team(ctx, team_id)
    require_member(team, actor)
    requests = _ids(ctx, select(MatchRequest.id).where(MatchRequest.team_id == team.id))
    offers = _ids(ctx, select(MatchOffer.id).join(MatchRequest, MatchRequest.id == MatchOffer.request_id).where(
        or_(MatchOffer.team_id == team.id, MatchRequest.team_id == team.id)))
    return _load(ctx, {
        "team": [str(team.id)],
        "join_request": _ids(ctx, select(JoinRequest.id).where(JoinRequest.team_id == team.id)),
        "match_request": requests,
        "match_offer": offers,
        "league_team": _ids(ctx, select(LeagueTeam.id).where(LeagueTeam.team_id == team.id)),
        "transfer_offer": _ids(ctx, select(TransferOffer.id).where(
            or_(TransferOffer.from_team_id == team.id, TransferOffer.to_team_id == team.id))),
        "match_contract": _ids(ctx, select(MatchContract.id).where(
            or_(MatchContract.host_team_id == team.id, MatchContract.guest_team_id == team.id))),
    })


def contract_activity(ctx: ServiceContext, actor: UserAccount, contract_id: int) -> list[ActivityView]:
    contract = load_contract(ctx, contract_id)
    member_side(side_teams(ctx, contract), actor)  # 404 si no pertenece a ninguno de los dos equipos
    return _load(ctx, {
        "match_contract": [str(contract.id)],
        "match_offer": [str(contract.offer_id)],
        "match_request": [str(contract.request_id)],
    })
