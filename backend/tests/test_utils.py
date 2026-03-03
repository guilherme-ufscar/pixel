"""Tests for utility modules."""
import time
from app.utils.cache import InMemoryCache
from app.utils.circuit_breaker import CircuitBreaker, CircuitState


class TestInMemoryCache:
    """Test in-memory cache."""

    def test_set_and_get(self):
        cache = InMemoryCache()
        cache.set("key", "value", ttl=60)
        assert cache.get("key") == "value"

    def test_ttl_expiration(self):
        cache = InMemoryCache()
        cache.set("key", "value", ttl=1)
        time.sleep(1.1)
        assert cache.get("key") is None

    def test_max_size_eviction(self):
        cache = InMemoryCache(max_size=2)
        cache.set("a", 1, ttl=60)
        cache.set("b", 2, ttl=60)
        cache.set("c", 3, ttl=60)  # Should evict "a"
        assert cache.get("a") is None
        assert cache.get("b") == 2
        assert cache.get("c") == 3

    def test_delete(self):
        cache = InMemoryCache()
        cache.set("key", "value", ttl=60)
        cache.delete("key")
        assert cache.get("key") is None


class TestCircuitBreaker:
    """Test circuit breaker."""

    def test_starts_closed(self):
        cb = CircuitBreaker()
        assert cb.state == CircuitState.CLOSED
        assert cb.is_available()

    def test_opens_after_threshold(self):
        cb = CircuitBreaker(failure_threshold=3, window=60)
        cb.record_failure()
        cb.record_failure()
        cb.record_failure()
        assert cb.state == CircuitState.OPEN
        assert not cb.is_available()

    def test_half_open_after_timeout(self):
        cb = CircuitBreaker(failure_threshold=2, reset_timeout=1)
        cb.record_failure()
        cb.record_failure()
        assert cb.state == CircuitState.OPEN
        time.sleep(1.1)
        assert cb.state == CircuitState.HALF_OPEN

    def test_success_closes_circuit(self):
        cb = CircuitBreaker(failure_threshold=2, reset_timeout=1)
        cb.record_failure()
        cb.record_failure()
        time.sleep(1.1)
        assert cb.state == CircuitState.HALF_OPEN
        cb.record_success()
        assert cb.state == CircuitState.CLOSED
