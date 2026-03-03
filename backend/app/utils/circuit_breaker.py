"""Simple circuit breaker implementation."""
import time
import threading
import logging
from enum import Enum

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    """Circuit breaker to protect against cascading failures.

    States:
      - CLOSED: normal operation, requests pass through
      - OPEN: failures exceeded threshold, requests are blocked
      - HALF_OPEN: after reset_timeout, allow one request to test
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        reset_timeout: int = 30,
        window: int = 60,
    ):
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.window = window

        self._state = CircuitState.CLOSED
        self._failures: list[float] = []
        self._last_failure_time: float = 0
        self._lock = threading.Lock()

    @property
    def state(self) -> CircuitState:
        with self._lock:
            if self._state == CircuitState.OPEN:
                if time.time() - self._last_failure_time >= self.reset_timeout:
                    self._state = CircuitState.HALF_OPEN
                    logger.info("Circuit breaker: OPEN -> HALF_OPEN")
            return self._state

    def is_available(self) -> bool:
        """Check if the circuit allows requests."""
        return self.state != CircuitState.OPEN

    def record_success(self) -> None:
        """Record a successful request."""
        with self._lock:
            if self._state == CircuitState.HALF_OPEN:
                self._state = CircuitState.CLOSED
                self._failures.clear()
                logger.info("Circuit breaker: HALF_OPEN -> CLOSED")

    def record_failure(self) -> None:
        """Record a failed request."""
        with self._lock:
            now = time.time()
            self._failures = [t for t in self._failures if now - t < self.window]
            self._failures.append(now)
            self._last_failure_time = now

            if self._state == CircuitState.HALF_OPEN:
                self._state = CircuitState.OPEN
                logger.warning("Circuit breaker: HALF_OPEN -> OPEN")
            elif len(self._failures) >= self.failure_threshold:
                self._state = CircuitState.OPEN
                logger.warning(
                    f"Circuit breaker: CLOSED -> OPEN (failures={len(self._failures)})"
                )
