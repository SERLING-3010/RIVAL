"""Quién maneja el día del partido de su equipo (Sprint 21): el administrador y, si hay DT, el capitán.

Convocatoria, alineación táctica, planilla y resultado. Lo que compromete al equipo frente a otros
(retos, firmas, cancha, mercado, traspasos, préstamos) sigue siendo solo del administrador
(`contract_queries.admin_side`), para que la auditoría siempre nombre a un único responsable.
"""

from app.domain.errors import ConflictError, PermissionDeniedError
from app.domain.team_rules import is_matchday_staff
from app.persistence.models_contracts import MatchContract
from app.persistence.models_identity import UserAccount
from app.persistence.models_teams import Team
from app.services.context import ServiceContext
from app.services.contract_queries import member_side, side_teams
from app.services.team_service import member_views


def staff_side(ctx: ServiceContext, contract: MatchContract, actor: UserAccount) -> tuple[str, Team]:
    teams = side_teams(ctx, contract)
    member_side(teams, actor)  # 404 si no pertenece a ninguno de los dos equipos
    sides = [side for side, team in teams.items() if is_matchday_staff(member_views(team), actor.id)]
    if len(sides) == 2:
        raise ConflictError("SAME_ADMIN_BOTH_TEAMS", "No puedes manejar a los dos equipos del mismo partido.")
    if not sides:
        raise PermissionDeniedError("STAFF_ONLY", "Solo el DT o el capitán del equipo puede hacer esto.")
    return sides[0], teams[sides[0]]
