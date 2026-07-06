from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Optional


class Database(ABC):
    @abstractmethod
    async def connect(self) -> None: ...

    @abstractmethod
    async def disconnect(self) -> None: ...

    @abstractmethod
    async def execute(self, query: str, params: dict | None = None) -> Any: ...

    @abstractmethod
    async def fetch_one(self, query: str, params: dict | None = None) -> dict | None: ...

    @abstractmethod
    async def fetch_all(self, query: str, params: dict | None = None) -> list[dict]: ...
