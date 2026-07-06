from __future__ import annotations

import time
from collections import OrderedDict
from threading import Lock
from typing import Any, Optional


class Cache:
    _instance: Cache | None = None

    def __new__(cls) -> Cache:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._store: dict = {}
            cls._instance._ttl: dict = {}
            cls._instance._lock = Lock()
            cls._instance._max_size = 1000
        return cls._instance

    def configure(self, max_size: int = 1000) -> None:
        self._max_size = max_size

    def get(self, key: str, default: Any = None) -> Any:
        with self._lock:
            if key in self._store:
                expiry = self._ttl.get(key)
                if expiry is None or time.time() < expiry:
                    return self._store[key]
                self._evict(key)
            return default

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        with self._lock:
            if len(self._store) >= self._max_size:
                self._evict_lru()
            self._store[key] = value
            self._ttl[key] = (time.time() + ttl) if ttl else None

    def delete(self, key: str) -> None:
        with self._lock:
            self._evict(key)

    def clear(self) -> None:
        with self._lock:
            self._store.clear()
            self._ttl.clear()

    def _evict(self, key: str) -> None:
        self._store.pop(key, None)
        self._ttl.pop(key, None)

    def _evict_lru(self) -> None:
        if self._store:
            self._evict(next(iter(self._store)))
