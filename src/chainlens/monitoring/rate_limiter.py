"""RateLimiter — govern call frequency across collectors."""

from __future__ import annotations

import time
from collections import defaultdict
from threading import Lock


class RateLimiter:
    """Sliding-window rate limiter per API endpoint."""

    def __init__(self) -> None:
        self._windows: dict[str, list[float]] = defaultdict(list)
        self._lock = Lock()

    def check(self, api_name: str, max_per_second: float = 10.0) -> bool:
        """Check if a call is allowed under the rate limit.

        Returns True if allowed, False if rate-limited.
        """
        now = time.monotonic()
        window = 1.0  # 1-second sliding window

        with self._lock:
            timestamps = self._windows[api_name]
            # Prune old entries
            cutoff = now - window
            timestamps[:] = [t for t in timestamps if t > cutoff]

            if len(timestamps) >= max_per_second:
                return False
            timestamps.append(now)
            return True

    def wait_if_needed(self, api_name: str, max_per_second: float = 10.0) -> None:
        """Block until a call is allowed under the rate limit."""
        while not self.check(api_name, max_per_second):
            time.sleep(0.1)

    def reset(self) -> None:
        with self._lock:
            self._windows.clear()
