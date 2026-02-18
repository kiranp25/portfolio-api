import json
import time
from typing import Any, Optional

from app.core.config import settings

try:
    import redis
except ImportError:  # pragma: no cover
    redis = None


_redis_client = None
_memory_cache: dict[str, tuple[float, str]] = {}


def get_redis_client():
    global _redis_client
    if _redis_client is not None:
        return _redis_client
    if redis is None:
        return None
    try:
        _redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
        _redis_client.ping()
        return _redis_client
    except Exception:
        _redis_client = None
        return None


def cache_get_json(key: str) -> Optional[Any]:
    client = get_redis_client()
    if client:
        raw = client.get(key)
        return json.loads(raw) if raw else None

    now = time.time()
    data = _memory_cache.get(key)
    if not data:
        return None
    expires_at, payload = data
    if expires_at < now:
        _memory_cache.pop(key, None)
        return None
    return json.loads(payload)


def cache_set_json(key: str, value: Any, ttl_seconds: int) -> None:
    payload = json.dumps(value, default=str)
    client = get_redis_client()
    if client:
        client.setex(key, ttl_seconds, payload)
        return

    _memory_cache[key] = (time.time() + ttl_seconds, payload)


def cache_delete(key: str) -> None:
    client = get_redis_client()
    if client:
        client.delete(key)
        return
    _memory_cache.pop(key, None)
