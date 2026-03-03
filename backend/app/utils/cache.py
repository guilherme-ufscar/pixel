"""TTL Cache with LRU eviction. Supports Redis and in-memory backends."""
import time
import threading
import logging
import json
from collections import OrderedDict
from typing import Optional, Any

logger = logging.getLogger(__name__)


class InMemoryCache:
    """Thread-safe in-memory TTL cache with LRU eviction."""

    def __init__(self, max_size: int = 1000):
        self._cache: OrderedDict[str, tuple[Any, float]] = OrderedDict()
        self._lock = threading.Lock()
        self._max_size = max_size

    def get(self, key: str) -> Optional[Any]:
        """Get value by key. Returns None if expired or missing."""
        with self._lock:
            if key not in self._cache:
                return None
            value, expires_at = self._cache[key]
            if time.time() > expires_at:
                del self._cache[key]
                return None
            self._cache.move_to_end(key)
            return value

    def set(self, key: str, value: Any, ttl: int = 300) -> None:
        """Set value with TTL in seconds."""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
            elif len(self._cache) >= self._max_size:
                self._cache.popitem(last=False)
            self._cache[key] = (value, time.time() + ttl)

    def delete(self, key: str) -> None:
        """Delete a cached value."""
        with self._lock:
            self._cache.pop(key, None)

    def clear(self) -> None:
        """Clear all cached values."""
        with self._lock:
            self._cache.clear()


class RedisCache:
    """Redis-backed cache."""

    def __init__(self, redis_client):
        self._redis = redis_client

    def get(self, key: str) -> Optional[Any]:
        """Get value by key."""
        try:
            value = self._redis.get(key)
            if value is None:
                return None
            return json.loads(value)
        except Exception as e:
            logger.warning(f"Redis get error: {e}")
            return None

    def set(self, key: str, value: Any, ttl: int = 300) -> None:
        """Set value with TTL in seconds."""
        try:
            self._redis.setex(key, ttl, json.dumps(value))
        except Exception as e:
            logger.warning(f"Redis set error: {e}")

    def delete(self, key: str) -> None:
        """Delete a cached value."""
        try:
            self._redis.delete(key)
        except Exception as e:
            logger.warning(f"Redis delete error: {e}")

    def clear(self) -> None:
        """Flush all keys (careful in production!)."""
        try:
            self._redis.flushdb()
        except Exception as e:
            logger.warning(f"Redis clear error: {e}")


def create_cache(redis_url: str = "") -> InMemoryCache | RedisCache:
    """Create cache instance. Uses Redis if URL provided, else in-memory."""
    if redis_url and redis_url != "memory://":
        try:
            import redis
            client = redis.from_url(redis_url, decode_responses=True)
            client.ping()
            logger.info("Using Redis cache")
            return RedisCache(client)
        except Exception as e:
            logger.warning(f"Redis unavailable, falling back to in-memory cache: {e}")
    logger.info("Using in-memory cache")
    return InMemoryCache()
