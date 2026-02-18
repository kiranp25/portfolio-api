import time

from fastapi import HTTPException, Request, status

from app.core.config import settings
from app.core.redis_client import get_redis_client

_memory_counters: dict[str, tuple[int, float]] = {}


def _hit_with_memory(key: str, window_seconds: int) -> tuple[int, int]:
    now = time.time()
    count, reset_at = _memory_counters.get(key, (0, now + window_seconds))
    if now >= reset_at:
        count = 0
        reset_at = now + window_seconds
    count += 1
    _memory_counters[key] = (count, reset_at)
    retry_after = max(1, int(reset_at - now))
    return count, retry_after


def _hit_with_redis(key: str, window_seconds: int) -> tuple[int, int]:
    client = get_redis_client()
    if not client:
        return _hit_with_memory(key, window_seconds)

    count = client.incr(key)
    if count == 1:
        client.expire(key, window_seconds)
    ttl = client.ttl(key)
    retry_after = ttl if ttl and ttl > 0 else window_seconds
    return count, retry_after


def rate_limit(scope: str, max_requests: int, window_seconds: int):
    def dependency(request: Request) -> None:
        ip = request.client.host if request.client else "unknown"
        key = f"rl:{scope}:{ip}"
        count, retry_after = _hit_with_redis(key, window_seconds)
        if count > max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded for {scope}",
                headers={"Retry-After": str(retry_after)},
            )

    return dependency


limit_login = rate_limit(
    "auth_login",
    settings.RATE_LIMIT_LOGIN_REQUESTS,
    settings.RATE_LIMIT_LOGIN_WINDOW_SECONDS,
)

limit_public = rate_limit(
    "public_profile",
    settings.RATE_LIMIT_PUBLIC_REQUESTS,
    settings.RATE_LIMIT_PUBLIC_WINDOW_SECONDS,
)
