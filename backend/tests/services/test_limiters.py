from datetime import UTC, datetime, timedelta

import pytest

from app.domain.errors import RateLimitedError
from app.services.ip_limiter import SlidingWindowLimiter
from app.services.rate_limiter import MAX_TRACKED_KEYS, LoginRateLimiter

NOW = datetime(2026, 11, 23, 15, 0, tzinfo=UTC)


def test_window_blocks_after_max_and_recovers():
    limiter = SlidingWindowLimiter(max_events=2, window=timedelta(minutes=1))
    limiter.hit("ip", NOW)
    limiter.hit("ip", NOW)
    with pytest.raises(RateLimitedError) as error:
        limiter.hit("ip", NOW)
    assert error.value.retry_after_seconds > 0
    limiter.hit("ip", NOW + timedelta(minutes=2))


def test_login_limiter_memory_is_bounded():
    limiter = LoginRateLimiter()
    for i in range(MAX_TRACKED_KEYS + 50):
        limiter.register_failure(f"correo{i}@x.test|ip", NOW)
    later = NOW + timedelta(hours=1)
    limiter.register_failure("otro@x.test|ip", later)
    assert limiter.tracked_keys() < 100
