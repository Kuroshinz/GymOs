"""Replay center — replays events from EventStore with step/continuous modes and speed control."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable

from shared.events.domain_events import DomainEvent, event_from_dict
from shared.events.event_bus import EventBus
from shared.events.store import EventStore


class ReplayMode(Enum):
    STEP = "step"
    CONTINUOUS = "continuous"
    BURST = "burst"


@dataclass
class ReplayProgress:
    total: int = 0
    replayed: int = 0
    elapsed_seconds: float = 0.0
    paused: bool = False
    mode: str = "step"
    speed_multiplier: float = 1.0
    current_event: str = ""
    status: str = "idle"


EventHandler = Callable[[DomainEvent], None]


class ReplayCenter:
    """Replays events from the EventStore.

    Supports step mode (one event at a time), continuous mode (auto-play),
    speed multiplier, pause/resume, and event filtering.
    """

    def __init__(self, store: EventStore | None = None, bus: EventBus | None = None) -> None:
        self._store = store or EventStore()
        self._bus = bus
        self._mode: ReplayMode = ReplayMode.STEP
        self._speed: float = 1.0
        self._paused = False
        self._events: list[DomainEvent] = []
        self._index: int = 0
        self._start_time: float = 0.0
        self._replayed_count: int = 0
        self._status: str = "idle"
        self._on_event: EventHandler | None = None

    def load_workout(self, correlation_id: str) -> int:
        """Load all events for a workout (by correlation_id)."""
        if self._store:
            events = self._store.replay()
            self._events = [e for e in events if e.correlation_id == correlation_id]
        else:
            self._events = []
        self._index = 0
        self._replayed_count = 0
        return len(self._events)

    def load_by_source(self, source: str) -> int:
        """Load all events from a specific source module."""
        if self._store:
            events = self._store.replay()
            self._events = [e for e in events if e.source == source]
        else:
            self._events = []
        self._index = 0
        self._replayed_count = 0
        return len(self._events)

    def load_by_event_name(self, event_name: str) -> int:
        """Load all events of a specific type."""
        if self._store:
            self._events = self._store.replay(event_name=event_name)
        else:
            self._events = []
        self._index = 0
        self._replayed_count = 0
        return len(self._events)

    def load_range(self, start_index: int, count: int) -> int:
        """Load a range of events from the store."""
        if self._store:
            all_events = self._store.replay()
            self._events = all_events[start_index:start_index + count]
        else:
            self._events = []
        self._index = 0
        self._replayed_count = 0
        return len(self._events)

    def load_all(self) -> int:
        """Load all events from the store."""
        if self._store:
            self._events = self._store.replay()
        else:
            self._events = []
        self._index = 0
        self._replayed_count = 0
        return len(self._events)

    # ─── Controls ─────────────────────────────────────────

    def set_mode(self, mode: ReplayMode) -> None:
        self._mode = mode

    def set_speed(self, multiplier: float) -> None:
        self._speed = max(0.1, min(multiplier, 100.0))

    def pause(self) -> None:
        self._paused = True

    def resume(self) -> None:
        self._paused = False

    @property
    def is_paused(self) -> bool:
        return self._paused

    # ─── Playback ─────────────────────────────────────────

    def step(self) -> DomainEvent | None:
        """Replay the next single event."""
        if self._paused or self._index >= len(self._events):
            self._status = "completed" if self._index >= len(self._events) else "paused"
            return None
        event = self._events[self._index]
        self._index += 1
        self._replayed_count += 1
        self._status = "playing"
        if self._bus:
            self._bus.publish(event)
        if self._on_event:
            self._on_event(event)
        return event

    def step_back(self) -> DomainEvent | None:
        """Go back one event."""
        if self._index <= 0:
            return None
        self._index -= 1
        self._replayed_count = max(0, self._replayed_count - 1)
        return self._events[self._index] if self._index < len(self._events) else None

    def play_continuous(self, on_event: EventHandler | None = None) -> None:
        """Replay all loaded events continuously."""
        self._paused = False
        self._status = "playing"
        self._start_time = time.time()
        while self._index < len(self._events):
            if self._paused:
                self._status = "paused"
                return
            event = self._events[self._index]
            if self._bus:
                self._bus.publish(event)
            if on_event:
                on_event(event)
            if self._on_event:
                self._on_event(event)
            self._index += 1
            self._replayed_count += 1
            delay = 0.05 / self._speed
            time.sleep(delay)
        self._status = "completed"

    def set_event_handler(self, handler: EventHandler | None) -> None:
        self._on_event = handler

    # ─── Status ───────────────────────────────────────────

    def progress(self) -> ReplayProgress:
        now = time.time()
        elapsed = (now - self._start_time) if self._start_time else 0.0
        return ReplayProgress(
            total=len(self._events),
            replayed=self._replayed_count,
            elapsed_seconds=elapsed,
            paused=self._paused,
            mode=self._mode.value,
            speed_multiplier=self._speed,
            current_event=self._events[self._index - 1].event_name if self._events and self._index > 0 else "",
            status=self._status,
        )

    def remaining(self) -> int:
        return max(0, len(self._events) - self._index)

    def reset(self) -> None:
        self._index = 0
        self._replayed_count = 0
        self._paused = False
        self._status = "idle"
