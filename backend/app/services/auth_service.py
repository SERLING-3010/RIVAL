"""Casos de uso de identidad: registro por rol, inicio y cierre de sesión, agregar rol."""

import hashlib
import secrets

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.domain.age_policy import is_adult
from app.domain.errors import AuthenticationError, ConflictError, DomainError
from app.domain.identity_rules import (
    normalize_email,
    validate_display_name,
    validate_password,
    validate_place_name,
)
from app.domain.roles import UserRole
from app.domain.text_keys import search_key
from app.persistence.models_identity import AuthSession, UserAccount, UserRoleRow, UserSport
from app.services.audit_service import record_event
from app.services.clock import local_today
from app.services.context import ServiceContext
from app.services.inputs import RegisterInput
from app.services.passwords import hash_password, verify_password
from app.services.rate_limiter import LoginRateLimiter

_INVALID_LOGIN = "Correo o contraseña incorrectos."
_INVALID_SESSION = "Tu sesión terminó. Inicia sesión de nuevo."


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _check_sports(ctx: ServiceContext, sports: list[str]) -> list[str]:
    unique = sorted(set(sports))
    if not unique:
        raise DomainError("SPORTS_REQUIRED", "Elige al menos un deporte.")
    for code in unique:
        if not ctx.catalog.has_sport(code):
            raise DomainError("UNKNOWN_SPORT", f"El deporte {code} no está en el catálogo.")
    return unique


def register_user(ctx: ServiceContext, data: RegisterInput) -> UserAccount:
    email = normalize_email(data.email)
    validate_password(data.password)
    if not is_adult(data.birth_date, local_today(ctx.clock)):
        raise DomainError("UNDERAGE", "Por ahora RIVAL es solo para mayores de 18 años.")
    sports = _check_sports(ctx, data.sports)
    if ctx.db.scalar(select(UserAccount.id).where(UserAccount.email == email)):
        raise ConflictError("EMAIL_TAKEN", "Ya existe una cuenta con ese correo.")
    now = ctx.clock.now()
    city = validate_place_name(data.city, "ciudad")
    neighborhood = validate_place_name(data.neighborhood, "barrio")
    user = UserAccount(
        email=email,
        password_hash=hash_password(data.password),
        display_name=validate_display_name(data.display_name),
        birth_date=data.birth_date,
        city=city,
        city_key=search_key(city),
        neighborhood=neighborhood,
        neighborhood_key=search_key(neighborhood),
        position=(data.position or "").strip()[:40] or None,
        created_at=now,
        roles=[UserRoleRow(role=data.role.value, created_at=now)],
        sports=[UserSport(sport_code=code) for code in sports],
    )
    ctx.db.add(user)
    try:
        ctx.db.flush()
    except IntegrityError as error:  # dos registros simultáneos con el mismo correo
        raise ConflictError("EMAIL_TAKEN", "Ya existe una cuenta con ese correo.") from error
    record_event(
        ctx,
        action="USER_REGISTERED",
        entity="user_account",
        entity_id=user.id,
        initiated_by=user.id,
        after={"display_name": user.display_name, "role": data.role.value, "sports": sports},
    )
    return user


def login(
    ctx: ServiceContext, limiter: LoginRateLimiter, email: str, password: str, client_key: str
) -> tuple[str, UserAccount]:
    key = f"{email.strip().lower()}|{client_key}"
    now = ctx.clock.now()
    limiter.check(key, now)
    user = ctx.db.scalar(select(UserAccount).where(UserAccount.email == email.strip().lower()))
    if not verify_password(user.password_hash if user else None, password) or user is None:
        limiter.register_failure(key, now)
        raise AuthenticationError("INVALID_CREDENTIALS", _INVALID_LOGIN)
    limiter.register_success(key)
    token = secrets.token_urlsafe(32)
    ctx.db.add(
        AuthSession(
            user_id=user.id,
            token_hash=_hash_token(token),
            created_at=now,
            last_seen_at=now,
            expires_at=now + ctx.session_ttl,
        )
    )
    record_event(ctx, action="USER_LOGGED_IN", entity="user_account", entity_id=user.id, initiated_by=user.id)
    return token, user


def authenticate(ctx: ServiceContext, token: str) -> UserAccount:
    session = ctx.db.scalar(select(AuthSession).where(AuthSession.token_hash == _hash_token(token)))
    now = ctx.clock.now()
    if session is None or session.expires_at <= now or now - session.last_seen_at > ctx.session_idle:
        if session is not None:
            ctx.db.delete(session)
            ctx.db.flush()
        raise AuthenticationError("SESSION_EXPIRED", _INVALID_SESSION)
    session.last_seen_at = now
    user = ctx.db.get(UserAccount, session.user_id)
    if user is None:
        raise AuthenticationError("SESSION_EXPIRED", _INVALID_SESSION)
    return user


def logout(ctx: ServiceContext, token: str) -> None:
    session = ctx.db.scalar(select(AuthSession).where(AuthSession.token_hash == _hash_token(token)))
    if session is not None:
        record_event(
            ctx, action="USER_LOGGED_OUT", entity="user_account", entity_id=session.user_id,
            initiated_by=session.user_id,
        )
        ctx.db.delete(session)
        ctx.db.flush()


def add_role(ctx: ServiceContext, user: UserAccount, role: UserRole, sports: list[str]) -> UserAccount:
    codes = _check_sports(ctx, sports)
    before = {"roles": sorted(r.role for r in user.roles)}
    if role.value not in before["roles"]:
        user.roles.append(UserRoleRow(role=role.value, created_at=ctx.clock.now()))
    known = {s.sport_code for s in user.sports}
    user.sports.extend(UserSport(sport_code=c) for c in codes if c not in known)
    ctx.db.flush()
    record_event(
        ctx, action="USER_ROLE_ADDED", entity="user_account", entity_id=user.id, initiated_by=user.id,
        before=before, after={"roles": sorted(r.role for r in user.roles)},
    )
    return user
