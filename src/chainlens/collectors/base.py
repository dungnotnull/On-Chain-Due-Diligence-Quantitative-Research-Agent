"""Async HTTP base client with retry/backoff + file-based caching."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx
import orjson
from tenacity import retry, stop_after_attempt, wait_exponential

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent


class AsyncCollectorBase:
    """Base class for all data collectors. Provides caching + retry."""

    def __init__(self, cache_dir: str = ".cache", ttl_hours: int = 6) -> None:
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl_hours = ttl_hours
        self._client: httpx.AsyncClient | None = None

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client

    def _cache_key(self, data: dict[str, Any]) -> str:
        raw = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(raw.encode()).hexdigest()

    def _cache_path(self, key: str) -> Path:
        return self.cache_dir / f"{key}.json"

    def _cache_get(self, key: str) -> dict[str, Any] | None:
        path = self._cache_path(key)
        if not path.exists():
            return None
        age = datetime.now(UTC).timestamp() - path.stat().st_mtime
        if age > self.ttl_hours * 3600:
            path.unlink(missing_ok=True)
            return None
        raw = path.read_bytes()
        return orjson.loads(raw)

    def _cache_set(self, key: str, data: dict[str, Any]) -> None:
        path = self._cache_path(key)
        path.write_bytes(orjson.dumps(data, option=orjson.OPT_UTC_Z))

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
    )
    async def _request(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        client = self._get_client()
        resp = await client.request(method, url, **kwargs)
        resp.raise_for_status()
        return resp

    async def _cached_request(
        self, cache_key_data: dict[str, Any], fetcher
    ) -> dict[str, Any]:
        key = self._cache_key(cache_key_data)
        cached = self._cache_get(key)
        if cached is not None:
            cached["_cached"] = True
            return cached
        result = await fetcher()
        result["_cached"] = False
        self._cache_set(key, result)
        return result

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None
