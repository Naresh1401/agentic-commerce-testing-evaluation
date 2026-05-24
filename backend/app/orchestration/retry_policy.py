from __future__ import annotations

import time
from typing import Callable, TypeVar


T = TypeVar("T")


def retry(operation: Callable[[], T], attempts: int = 3, backoff_seconds: float = 0.05) -> T:
    last_error: Exception | None = None
    for attempt in range(attempts):
        try:
            return operation()
        except Exception as exc:
            last_error = exc
            if attempt < attempts - 1:
                time.sleep(backoff_seconds * (attempt + 1))
    assert last_error is not None
    raise last_error
