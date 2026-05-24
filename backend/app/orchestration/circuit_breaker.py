from __future__ import annotations

import time


class CircuitBreaker:
    def __init__(self, failure_threshold: int = 3, reset_seconds: float = 5.0) -> None:
        self.failure_threshold = failure_threshold
        self.reset_seconds = reset_seconds
        self.failure_count = 0
        self.opened_at: float | None = None

    @property
    def is_open(self) -> bool:
        if self.opened_at is None:
            return False
        if time.time() - self.opened_at > self.reset_seconds:
            self.failure_count = 0
            self.opened_at = None
            return False
        return True

    def record_success(self) -> None:
        self.failure_count = 0
        self.opened_at = None

    def record_failure(self) -> None:
        self.failure_count += 1
        if self.failure_count >= self.failure_threshold:
            self.opened_at = time.time()
