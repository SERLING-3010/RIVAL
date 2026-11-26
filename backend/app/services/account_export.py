"""Descargar mis datos (Sprint 27, derecho a conocer de la Ley 1581). Solo los datos de quien la pide.

Incluye lo que RIVAL guarda de la persona: perfil, equipos, partidos, valoraciones recibidas (sin
quién las dio), mensajes que escribió, check-ins (solo la hora: nunca se guarda la posición), perfiles
de agente libre, teléfonos con avisos y la aceptación de términos. No incluye datos de otras personas.
"""

from sqlalchemy import func, select

from app.persistence.models_chat import MatchChatMessage
from app.persistence.models_identity import UserAccount
from app.persistence.models_manager import MatchAppearance
from app.persistence.models_matchday import MatchCheckIn, PlayerRating
from app.persistence.models_push import PushDevice
from app.persistence.models_scouting import FreeAgentProfile
from app.persistence.models_teams import Team, TeamMembership
from app.services.context import ServiceContext

Data = dict[str, object]


def _iso(value: object) -> object:
    return value.isoformat() if hasattr(value, "isoformat") else value


def export(ctx: ServiceContext, user: UserAccount) -> Data:
    teams = ctx.db.execute(select(TeamMembership, Team).join(Team, Team.id == TeamMembership.team_id)
                           .where(TeamMembership.user_id == user.id)).all()
    matches = ctx.db.scalars(select(MatchAppearance).where(MatchAppearance.user_id == user.id)
                             .order_by(MatchAppearance.recorded_at)).all()
    average, votes = ctx.db.execute(select(func.avg(PlayerRating.score), func.count(PlayerRating.id))
                                    .where(PlayerRating.rated_id == user.id)).one()
    messages = ctx.db.scalars(select(MatchChatMessage).where(MatchChatMessage.author_id == user.id,
                                                             MatchChatMessage.deleted_at.is_(None))
                              .order_by(MatchChatMessage.id)).all()
    check_ins = ctx.db.scalars(select(MatchCheckIn.checked_in_at).where(MatchCheckIn.user_id == user.id)).all()
    agents = ctx.db.scalars(select(FreeAgentProfile).where(FreeAgentProfile.user_id == user.id)).all()
    devices = ctx.db.scalar(select(func.count()).select_from(PushDevice).where(PushDevice.user_id == user.id))
    return {
        "perfil": {
            "correo": user.email, "nombre": user.display_name, "fecha_nacimiento": _iso(user.birth_date),
            "ciudad": user.city, "barrio": user.neighborhood, "posicion": user.position,
            "roles": sorted(r.role for r in user.roles), "deportes": sorted(s.sport_code for s in user.sports),
            "creada": _iso(user.created_at),
        },
        "aceptacion_terminos": {"version": user.terms_version, "fecha": _iso(user.terms_accepted_at)},
        "equipos": [{"equipo": t.name, "rol": m.role, "desde": _iso(m.joined_at)} for m, t in teams],
        "partidos": [{"contrato": a.contract_id, "goles": a.goals, "registrado": _iso(a.recorded_at)}
                     for a in matches],
        "valoraciones_recibidas": {"cantidad": int(votes),
                                   "promedio": round(float(average), 1) if average is not None else None},
        "mensajes_de_chat": [{"contrato": m.contract_id, "texto": m.body, "fecha": _iso(m.created_at)}
                             for m in messages],
        "check_ins": [_iso(c) for c in check_ins],
        "agente_libre": [{"deporte": a.sport_code, "posicion": a.position, "nota": a.note, "activo": a.active}
                         for a in agents],
        "telefonos_con_avisos": int(devices or 0),
    }
