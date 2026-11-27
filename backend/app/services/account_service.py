"""Términos aceptados y eliminación de la cuenta (Sprint 27, Ley 1581).

Eliminar = anonimizar (decisión del dueño, 25/11/2026). Se borran correo, nombre, fecha de nacimiento,
barrio, posición, sesiones, teléfonos, perfiles de agente libre y el texto de sus mensajes; la persona
queda como «Jugador eliminado». Partidos, resultados y la auditoría se conservan sin esos datos. Antes
debe salir de sus equipos y dejar sus ligas y canchas, para que nadie quede sin responsable.
"""

import secrets

from sqlalchemy import delete, select, update

from app.domain import legal_rules
from app.domain.errors import ConflictError, DomainError
from app.domain.league_rules import StaffRole
from app.persistence.models_chat import MatchChatMessage
from app.persistence.models_identity import AuthSession, UserAccount
from app.persistence.models_leagues import League, LeagueStaff
from app.persistence.models_push import PushDevice
from app.persistence.models_scouting import FreeAgentProfile
from app.persistence.models_teams import Team, TeamMembership
from app.persistence.models_venues import Venue
from app.services.audit_service import record_event
from app.services.context import ServiceContext
from app.services.passwords import hash_password, verify_password


def accept_terms(ctx: ServiceContext, user: UserAccount, version: str) -> UserAccount:
    legal_rules.check_version(version)
    before = user.terms_version
    user.terms_version, user.terms_accepted_at = version, ctx.clock.now()
    ctx.db.flush()
    record_event(ctx, action="TERMS_ACCEPTED", entity="user_account", entity_id=user.id, initiated_by=user.id,
                 before={"terms_version": before}, after={"terms_version": version})
    return user


def _blockers(ctx: ServiceContext, user: UserAccount) -> None:
    in_team = ctx.db.scalar(select(TeamMembership.id).join(Team, Team.id == TeamMembership.team_id)
                            .where(TeamMembership.user_id == user.id, Team.status == "ACTIVE").limit(1))
    if in_team is not None:
        raise ConflictError("LEAVE_TEAMS_FIRST", "Antes de eliminar tu cuenta, sal de tus equipos.")
    organizer = ctx.db.scalar(select(LeagueStaff.id).join(League, League.id == LeagueStaff.league_id)
                              .where(LeagueStaff.user_id == user.id, League.status == "ACTIVE",
                                     LeagueStaff.role == StaffRole.ORGANIZER.value).limit(1))
    if organizer is not None:
        raise ConflictError("LEAGUE_ORGANIZER_FIRST", "Organizas una liga: pásala a otra persona antes.")
    if ctx.db.scalar(select(Venue.id).where(Venue.owner_id == user.id).limit(1)) is not None:
        raise ConflictError("VENUES_FIRST", "Tienes canchas registradas: escríbenos para cerrarlas antes.")


def delete_account(ctx: ServiceContext, user: UserAccount, password: str) -> None:
    if not verify_password(user.password_hash, password):
        # 422 y no 401: con 401 la app cerraría la sesión en vez de dejar reintentar.
        raise DomainError("WRONG_PASSWORD", "La contraseña no coincide.")
    _blockers(ctx, user)
    now = ctx.clock.now()
    user.email = legal_rules.deleted_email(user.id)
    user.password_hash = hash_password(secrets.token_urlsafe(32))  # nadie conoce esta contraseña
    user.display_name, user.birth_date = legal_rules.DELETED_NAME, legal_rules.DELETED_BIRTH_DATE
    user.city = user.city_key = user.neighborhood = user.neighborhood_key = legal_rules.DELETED_PLACE
    user.position, user.deleted_at = None, now
    for table in (AuthSession, PushDevice, FreeAgentProfile):
        ctx.db.execute(delete(table).where(table.user_id == user.id))
    ctx.db.execute(update(MatchChatMessage).where(MatchChatMessage.author_id == user.id,
                                                  MatchChatMessage.deleted_at.is_(None))
                   .values(body="", deleted_at=now))
    ctx.db.flush()
    record_event(ctx, action="ACCOUNT_DELETED", entity="user_account", entity_id=user.id, initiated_by=user.id,
                 after={"anonymized": True})
