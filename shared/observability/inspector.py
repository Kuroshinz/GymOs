"""Live event inspector — captures, inspects, filters, and exports domain events."""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from shared.events.event_bus import EventBus


@dataclass
class InspectedEvent:
    event_name: str
    source: str
    timestamp: str
    correlation_id: str
    event_id: str
    event_version: str
    payload: dict[str, Any]
    subscriber_count: int = 0
    execution_duration_ms: float = 0.0
    status: str = "delivered"


class EventInspector:
    """Captures and inspects all events flowing through the event bus.

    Supports pause/resume, search, filter, clear, and export.
    """

    def __init__(self, bus: EventBus | None = None, max_events: int = 5000) -> None:
        self._bus = bus
        self._events: list[InspectedEvent] = []
        self._max_events = max_events
        self._paused = False
        self._handler: Callable | None = None
        self._filter_fn: Callable[[InspectedEvent], bool] | None = None

    def attach(self, bus: EventBus) -> None:
        """Attach to an event bus and start capturing."""
        self._bus = bus
        bus._core.on("*", self._core_handler)

    def _core_handler(self, core_event: Any) -> None:
        if self._paused:
            return
        data = core_event.data or {}
        payload = data.get("payload", {})
        ie = InspectedEvent(
            event_name=data.get("event_name", core_event.name),
            source=data.get("source", core_event.source),
            timestamp=data.get("timestamp", core_event.timestamp.isoformat() if hasattr(core_event, "timestamp") else ""),
            correlation_id=data.get("correlation_id", core_event.correlation_id),
            event_id=data.get("event_id", core_event.id),
            event_version=data.get("event_version", "1.0"),
            payload=payload,
            status="delivered",
        )
        if self._filter_fn and not self._filter_fn(ie):
            return
        self._events.append(ie)
        if len(self._events) > self._max_events:
            self._events.pop(0)

    # ─── Controls ─────────────────────────────────────────

    def pause(self) -> None:
        self._paused = True

    def resume(self) -> None:
        self._paused = False

    @property
    def is_paused(self) -> bool:
        return self._paused

    def clear(self) -> None:
        self._events.clear()

    # ─── Query ────────────────────────────────────────────

    def all_events(self) -> list[InspectedEvent]:
        return list(self._events)

    def last_n(self, n: int = 10) -> list[InspectedEvent]:
        return self._events[-n:]

    def count(self) -> int:
        return len(self._events)

    # ─── Search / Filter ──────────────────────────────────

    def search(self, query: str) -> list[InspectedEvent]:
        q = query.lower()
        return [
            e for e in self._events
            if q in e.event_name.lower()
            or q in e.source.lower()
            or q in e.correlation_id.lower()
            or q in e.event_id.lower()
        ]

    def filter_by_source(self, source: str) -> list[InspectedEvent]:
        return [e for e in self._events if e.source == source]

    def filter_by_event_name(self, event_name: str) -> list[InspectedEvent]:
        return [e for e in self._events if e.event_name == event_name]

    def filter_by_correlation_id(self, correlation_id: str) -> list[InspectedEvent]:
        return [e for e in self._events if e.correlation_id == correlation_id]

    def filter_by_status(self, status: str) -> list[InspectedEvent]:
        return [e for e in self._events if e.status == status]

    def set_filter(self, filter_fn: Callable[[InspectedEvent], bool] | None) -> None:
        self._filter_fn = filter_fn

    # ─── Export ───────────────────────────────────────────

    def export_json(self, events: list[InspectedEvent] | None = None) -> str:
        target = events or self._events
        return json.dumps([self._to_dict(e) for e in target], indent=2, default=str)

    def export_csv(self, events: list[InspectedEvent] | None = None) -> str:
        target = events or self._events
        lines = ["event_name,source,timestamp,correlation_id,status"]
        for e in target:
            lines.append(f"{e.event_name},{e.source},{e.timestamp},{e.correlation_id},{e.status}")
        return "\n".join(lines)

    def copy_payload(self, event: InspectedEvent) -> str:
        return json.dumps(event.payload, indent=2, default=str)

    def copy_json(self, event: InspectedEvent) -> str:
        return json.dumps(self._to_dict(event), indent=2, default=str)

    @staticmethod
    def _to_dict(e: InspectedEvent) -> dict[str, Any]:
        return {
            "event_name": e.event_name,
            "source": e.source,
            "timestamp": e.timestamp,
            "correlation_id": e.correlation_id,
            "event_id": e.event_id,
            "event_version": e.event_version,
            "payload": e.payload,
            "subscriber_count": e.subscriber_count,
            "execution_duration_ms": e.execution_duration_ms,
            "status": e.status,
        }
