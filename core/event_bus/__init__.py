from __future__ import annotations

import asyncio
import logging
import uuid
from collections import defaultdict
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime
from fnmatch import fnmatch

logger = logging.getLogger("nexus.event_bus")

Handler = Callable[..., Awaitable[None] | None]
Middleware = Callable[["Event", "EventBus"], Awaitable[None]]


class Event:
    def __init__(
        self,
        name: str,
        data: dict | None = None,
        *,
        source: str = "",
        correlation_id: str = "",
    ) -> None:
        self.id: str = uuid.uuid4().hex[:12]
        self.name: str = name
        self.data: dict = data or {}
        self.timestamp: datetime = datetime.now(UTC)
        self.source: str = source
        self.correlation_id: str = correlation_id or self.id
        self._stopped: bool = False

    def stop_propagation(self) -> None:
        self._stopped = True

    @property
    def is_stopped(self) -> bool:
        return self._stopped


class EventBus:
    def __init__(self) -> None:
        self._handlers: dict[str, list[Handler]] = defaultdict(list)
        self._once_handlers: dict[str, list[Handler]] = defaultdict(list)
        self._middleware: list[Middleware] = []
        self._wildcard_cache: dict[str, list[str]] = {}

    def use(self, middleware: Middleware) -> None:
        self._middleware.append(middleware)

    def on(self, event_name: str, handler: Handler | None = None) -> Handler | None:
        if handler is not None:
            self._handlers[event_name].append(handler)
            self._wildcard_cache.clear()
            return None

        def decorator(fn: Handler) -> Handler:
            self._handlers[event_name].append(fn)
            self._wildcard_cache.clear()
            return fn

        return decorator

    def once(self, event_name: str, handler: Handler) -> None:
        self._once_handlers[event_name].append(handler)
        self._wildcard_cache.clear()

    def off(self, event_name: str, handler: Handler | None = None) -> None:
        self._wildcard_cache.clear()
        if handler is None:
            self._handlers.pop(event_name, None)
            self._once_handlers.pop(event_name, None)
        else:
            for store in (self._handlers, self._once_handlers):
                handlers = store.get(event_name, [])
                if handler in handlers:
                    handlers.remove(handler)

    def _matching_patterns(self, event_name: str) -> list[str]:
        if event_name in self._wildcard_cache:
            return self._wildcard_cache[event_name]

        all_patterns = set(self._handlers.keys()) | set(self._once_handlers.keys())
        matches = [p for p in all_patterns if fnmatch(event_name, p)]
        self._wildcard_cache[event_name] = matches
        return matches

    async def emit(
        self,
        event_name: str,
        data: dict | None = None,
        *,
        source: str = "",
        correlation_id: str = "",
    ) -> Event:
        event = Event(event_name, data, source=source, correlation_id=correlation_id)

        for middleware in self._middleware:
            try:
                await middleware(event, self)
            except Exception:
                logger.exception("Middleware failed for event %s", event_name)
            if event.is_stopped:
                return event

        patterns = self._matching_patterns(event_name)

        for pattern in patterns:
            handlers = list(self._handlers.get(pattern, []))
            once = self._once_handlers.pop(pattern, [])

            for handler in handlers + once:
                if event.is_stopped:
                    return event
                try:
                    result = handler(event)
                    if asyncio.iscoroutine(result):
                        await result
                except Exception:
                    logger.exception(
                        "Handler %s failed for event %s",
                        getattr(handler, "__name__", "unknown"),
                        event_name,
                    )

        return event

    def clear(self) -> None:
        self._handlers.clear()
        self._once_handlers.clear()
        self._wildcard_cache.clear()
        self._middleware.clear()

    @property
    def handler_count(self) -> int:
        return sum(len(v) for v in self._handlers.values()) + sum(
            len(v) for v in self._once_handlers.values()
        )
