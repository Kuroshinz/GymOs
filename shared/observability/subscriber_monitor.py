"""Subscriber monitor — tracks execution, latency, errors, and supports disable/enable."""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from shared.events.domain_events import DomainEvent
from shared.events.event_bus import EventBus


@dataclass
class SubscriberInfo:
    name: str
    module: str = ""
    status: str = "active"
    handled_events: list[str] = field(default_factory=list)
    execution_count: int = 0
    average_latency_ms: float = 0.0
    max_latency_ms: float = 0.0
    error_count: int = 0
    last_execution: str = ""
    muted: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "module": self.module,
            "status": self.status,
            "handled_events": self.handled_events,
            "execution_count": self.execution_count,
            "average_latency_ms": round(self.average_latency_ms, 2),
            "max_latency_ms": round(self.max_latency_ms, 2),
            "error_count": self.error_count,
            "last_execution": self.last_execution,
            "muted": self.muted,
        }


SubscriberHandler = Callable[[DomainEvent], None]


class SubscriberMonitor:
    """Wraps handlers to measure execution time, count calls, track failures.

    Supports temporarily disabling (muting) subscribers without removing them.
    """

    def __init__(self, bus: EventBus | None = None) -> None:
        self._bus = bus
        self._subscribers: dict[str, SubscriberInfo] = {}
        self._handlers: dict[str, SubscriberHandler] = {}

    def register(
        self,
        name: str,
        handler: SubscriberHandler,
        module: str = "",
        handled_events: list[str] | None = None,
    ) -> SubscriberHandler:
        """Register a handler for monitoring. Returns a wrapped handler."""
        info = SubscriberInfo(
            name=name,
            module=module,
            handled_events=handled_events or [],
        )
        self._subscribers[name] = info

        def wrapped(event: DomainEvent) -> None:
            if info.muted:
                return
            start = time.perf_counter()
            try:
                handler(event)
                elapsed = (time.perf_counter() - start) * 1000
                info.execution_count += 1
                info.average_latency_ms = (
                    (info.average_latency_ms * (info.execution_count - 1) + elapsed)
                    / info.execution_count
                )
                info.max_latency_ms = max(info.max_latency_ms, elapsed)
                info.last_execution = event.timestamp.isoformat() if hasattr(event, "timestamp") else ""
            except Exception:
                elapsed = (time.perf_counter() - start) * 1000
                info.error_count += 1
                info.execution_count += 1
                raise

        self._handlers[name] = wrapped
        return wrapped

    def get_info(self, name: str) -> SubscriberInfo | None:
        return self._subscribers.get(name)

    def get_all(self) -> list[SubscriberInfo]:
        return list(self._subscribers.values())

    def mute(self, name: str) -> None:
        if name in self._subscribers:
            self._subscribers[name].muted = True
            self._subscribers[name].status = "muted"

    def unmute(self, name: str) -> None:
        if name in self._subscribers:
            self._subscribers[name].muted = False
            self._subscribers[name].status = "active"

    def toggle_mute(self, name: str) -> bool:
        if name in self._subscribers:
            if self._subscribers[name].muted:
                self.unmute(name)
                return False
            else:
                self.mute(name)
                return True
        return False

    def is_muted(self, name: str) -> bool:
        info = self._subscribers.get(name)
        return info.muted if info else False

    def get_wrapped_handler(self, name: str) -> SubscriberHandler | None:
        return self._handlers.get(name)

    def find_slow_subscribers(self, threshold_ms: float = 100.0) -> list[SubscriberInfo]:
        return [
            s for s in self._subscribers.values()
            if s.average_latency_ms > threshold_ms and s.execution_count > 0
        ]

    def find_failing_subscribers(self) -> list[SubscriberInfo]:
        return [
            s for s in self._subscribers.values()
            if s.error_count > 0
        ]

    def clear(self) -> None:
        self._subscribers.clear()
        self._handlers.clear()
