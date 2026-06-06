"""File-based cache with TTL using orjson for speed."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import orjson


class QueryCache:
    """On-disk, TTL-aware cache keyed by query hash."""

    def __init__(self, cache_dir: str = ".cache", ttl_hours: int = 6) -> None:
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl_seconds = ttl_hours * 3600

    def _path(self, key: str) -> Path:
        return self.cache_dir / f"{key}.json"

    def get(self, key: str) -> dict[str, Any] | None:
        path = self._path(key)
        if not path.exists():
            return None
        age = datetime.now(UTC).timestamp() - path.stat().st_mtime
        if age > self.ttl_seconds:
            path.unlink(missing_ok=True)
            return None
        raw = path.read_bytes()
        return orjson.loads(raw)

    def set(self, key: str, data: dict[str, Any]) -> None:
        path = self._path(key)
        path.write_bytes(orjson.dumps(data, option=orjson.OPT_UTC_Z))

    def invalidate(self, key: str) -> None:
        path = self._path(key)
        path.unlink(missing_ok=True)

    def clear_expired(self) -> int:
        now = datetime.now(UTC).timestamp()
        count = 0
        for p in self.cache_dir.glob("*.json"):
            if now - p.stat().st_mtime > self.ttl_seconds:
                p.unlink()
                count += 1
        return count
