"""Cartas especiales al momento (Sprint 26): se recalculan cuando cambia algo que las puede otorgar.

Antes se otorgaban solo al abrir la ficha o la plantilla. Ahora también al confirmarse un resultado,
al guardar la planilla, al confirmarse un gol con tipo, al recibir una valoración y al cerrar la
temporada. Reutiliza el mismo cálculo de la ficha y de la plantilla, así que la regla vive en un solo
lugar. Lo ganado queda en `special_card` / `team_special_card`, y de ahí sale el aviso push.
"""

from sqlalchemy import select

from app.domain.team_rules import resolve_admin
from app.persistence.models_identity import UserAccount
from app.persistence.models_manager import MatchAppearance
from app.persistence.models_teams import Team
from app.services.context import ServiceContext
from app.services.team_service import member_views


def refresh_players(ctx: ServiceContext, user_ids: list[int]) -> None:
    from app.services import manager_queries  # importa este módulo de forma indirecta

    for user_id in sorted(set(user_ids)):
        user = ctx.db.get(UserAccount, user_id)
        if user is not None:
            manager_queries.player_card(ctx, user, user_id)  # otorga lo alcanzado (card_queries.face)


def refresh_teams(ctx: ServiceContext, team_ids: list[int]) -> None:
    from app.services import squad_queries  # importa este módulo de forma indirecta

    for team_id in sorted(set(team_ids)):
        team = ctx.db.get(Team, team_id)
        admin_id = resolve_admin(member_views(team)) if team is not None and team.status == "ACTIVE" else None
        admin = ctx.db.get(UserAccount, admin_id) if admin_id is not None else None
        if team is not None and admin is not None:
            squad_queries.squad(ctx, admin, team.id)  # otorga lo alcanzado (team_card_service.card)


def after_result(ctx: ServiceContext, contract_id: int, host_team_id: int, guest_team_id: int) -> None:
    """Resultado confirmado: cambian el récord de ambos equipos y la ficha de quienes tienen planilla."""
    players = list(ctx.db.scalars(select(MatchAppearance.user_id).where(MatchAppearance.contract_id == contract_id)))
    refresh_players(ctx, players)
    refresh_teams(ctx, [host_team_id, guest_team_id])
