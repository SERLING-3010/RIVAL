"""Escudo y diseño del equipo (Sprint 23). Solo el administrador del equipo (DT, o capitán sin DT).

Cada cambio queda en la auditoría encadenada con antes y después.
"""

from sqlalchemy import select

from app.domain import team_look_rules
from app.domain.special_cards import CODES
from app.domain.errors import PermissionDeniedError
from app.persistence.models_cards import TeamSpecialCard
from app.persistence.models_identity import UserAccount
from app.persistence.models_teams import Team
from app.services.audit_service import record_event
from app.services.context import ServiceContext
from app.services.contract_queries import is_admin_of
from app.services.team_service import get_active_team


def _admin_team(ctx: ServiceContext, actor: UserAccount, team_id: int) -> Team:
    team = get_active_team(ctx, team_id)
    if not is_admin_of(team, actor):
        raise PermissionDeniedError("ADMIN_ONLY",
                                    "Solo el DT (o el capitán si no hay DT) cambia la imagen del equipo.")
    return team


def owned_codes(ctx: ServiceContext, team_id: int) -> list[str]:
    have = set(ctx.db.scalars(select(TeamSpecialCard.code).where(TeamSpecialCard.team_id == team_id)))
    return [code for code in CODES if code in have]


def set_card_choice(ctx: ServiceContext, actor: UserAccount, team_id: int, choice: str | None) -> Team:
    team = _admin_team(ctx, actor, team_id)
    team_look_rules.check_choice(choice, owned_codes(ctx, team.id))
    before = team.card_choice
    team.card_choice = choice
    ctx.db.flush()
    record_event(ctx, action="TEAM_DESIGN_CHOSEN", entity="team", entity_id=team.id, initiated_by=actor.id,
                 before={"card_choice": before}, after={"card_choice": choice})
    return team


def set_crest(ctx: ServiceContext, actor: UserAccount, team_id: int, crest: str | None) -> Team:
    team = _admin_team(ctx, actor, team_id)
    encoded = team_look_rules.parse_crest(crest).encode() if crest is not None else None
    before = team.crest
    team.crest = encoded
    ctx.db.flush()
    record_event(ctx, action="TEAM_CREST_CHANGED", entity="team", entity_id=team.id, initiated_by=actor.id,
                 before={"crest": before}, after={"crest": encoded})
    return team
