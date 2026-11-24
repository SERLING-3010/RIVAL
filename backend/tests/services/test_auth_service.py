from datetime import date, timedelta

import pytest

from app.domain.errors import AuthenticationError, ConflictError, DomainError, RateLimitedError
from app.domain.roles import UserRole
from app.services import auth_service
from app.services.rate_limiter import LoginRateLimiter
from tests.conftest import register_input


def test_register_stores_hash_not_password(ctx):
    user = auth_service.register_user(ctx, register_input())
    assert user.password_hash.startswith("$argon2id$")
    assert "sábados" not in user.password_hash
    assert [r.role for r in user.roles] == ["PLAYER"]


def test_register_rejects_minor(ctx):
    with pytest.raises(DomainError) as error:
        auth_service.register_user(ctx, register_input(birth_date=date(2010, 1, 1)))
    assert error.value.code == "UNDERAGE"


def test_register_rejects_duplicate_email_case_insensitive(ctx):
    auth_service.register_user(ctx, register_input(email="dt@rival.test"))
    with pytest.raises(ConflictError) as error:
        auth_service.register_user(ctx, register_input(email="DT@Rival.test"))
    assert error.value.code == "EMAIL_TAKEN"


def test_register_rejects_unknown_sport(ctx):
    data = register_input()
    data.sports = ["QUIDDITCH"]
    with pytest.raises(DomainError) as error:
        auth_service.register_user(ctx, data)
    assert error.value.code == "UNKNOWN_SPORT"


def test_login_and_authenticate(ctx):
    auth_service.register_user(ctx, register_input())
    token, user = auth_service.login(ctx, LoginRateLimiter(), "jugador@rival.test", "mi equipo juega los sábados", "ip")
    assert auth_service.authenticate(ctx, token).id == user.id


def test_wrong_password_message_does_not_reveal_user(ctx):
    limiter = LoginRateLimiter()
    with pytest.raises(AuthenticationError) as unknown:
        auth_service.login(ctx, limiter, "nadie@rival.test", "cualquier cosa larga", "ip")
    auth_service.register_user(ctx, register_input())
    with pytest.raises(AuthenticationError) as wrong:
        auth_service.login(ctx, limiter, "jugador@rival.test", "otra clave larga", "ip")
    assert unknown.value.message == wrong.value.message


def test_five_failures_lock_login(ctx):
    auth_service.register_user(ctx, register_input())
    limiter = LoginRateLimiter()
    for _ in range(5):
        with pytest.raises(AuthenticationError):
            auth_service.login(ctx, limiter, "jugador@rival.test", "clave equivocada", "ip")
    with pytest.raises(RateLimitedError) as error:
        auth_service.login(ctx, limiter, "jugador@rival.test", "mi equipo juega los sábados", "ip")
    assert error.value.retry_after_seconds > 0


def test_session_expires_after_idle(ctx, clock):
    auth_service.register_user(ctx, register_input())
    token, _ = auth_service.login(ctx, LoginRateLimiter(), "jugador@rival.test", "mi equipo juega los sábados", "ip")
    clock.advance(timedelta(hours=73))
    with pytest.raises(AuthenticationError):
        auth_service.authenticate(ctx, token)


def test_logout_invalidates_token(ctx):
    auth_service.register_user(ctx, register_input())
    token, _ = auth_service.login(ctx, LoginRateLimiter(), "jugador@rival.test", "mi equipo juega los sábados", "ip")
    auth_service.logout(ctx, token)
    with pytest.raises(AuthenticationError):
        auth_service.authenticate(ctx, token)


def test_add_second_role(ctx):
    user = auth_service.register_user(ctx, register_input())
    auth_service.add_role(ctx, user, UserRole.REFEREE, ["FOOTBALL", "BASKETBALL"])
    assert sorted(r.role for r in user.roles) == ["PLAYER", "REFEREE"]
    assert sorted(s.sport_code for s in user.sports) == ["BASKETBALL", "FOOTBALL"]
