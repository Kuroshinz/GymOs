from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any


class AnalysisCache:
    """Simple time-based cache for GymBrain analysis results.

    Prevents repeated analysis of the same data within a configurable TTL.
    Currently a placeholder — uses in-memory dict.

    Future: Redis-backed, or file-based cache.
    """

    def __init__(self, default_ttl_seconds: int = 300) -> None:
        self._cache: dict[str, tuple[Any, datetime]] = {}
        self._default_ttl = timedelta(seconds=default_ttl_seconds)

    def get(self, key: str) -> Any | None:
        if key not in self._cache:
            return None
        value, timestamp = self._cache[key]
        if datetime.now() - timestamp >= self._default_ttl:
            del self._cache[key]
            return None
        return value

    def set(self, key: str, value: Any) -> None:
        self._cache[key] = (value, datetime.now())

    def invalidate(self, key: str) -> None:
        self._cache.pop(key, None)

    def clear(self) -> None:
        self._cache.clear()
