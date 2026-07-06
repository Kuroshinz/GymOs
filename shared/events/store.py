"""Event store — persists events for replay and debugging.

Supports JSON file storage for portability.
Future: swap to database-backed storage for production.
"""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from pathlib import Path

from shared.events.domain_events import DomainEvent, event_from_dict

logger = logging.getLogger("nexus.events.store")


class EventStore:
    """Persists domain events and supports replay."""

    def __init__(self, storage_path: str | Path | None = None) -> None:
        if storage_path is None:
            storage_path = Path(__file__).resolve().parent.parent.parent / "data" / "event_store"
        self._path = Path(storage_path)
        self._path.mkdir(parents=True, exist_ok=True)
        self._session_events: list[DomainEvent] = []

    def append(self, event: DomainEvent) -> None:
        """Record an event to the store and flush to disk."""
        self._session_events.append(event)
        self._flush(event)

    def _flush(self, event: DomainEvent) -> None:
        """Append one event to the daily log file."""
        date_str = datetime.now(UTC).strftime("%Y-%m-%d")
        log_file = self._path / f"events-{date_str}.jsonl"
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(event.to_dict(), default=str) + "\n")
        except OSError as exc:
            logger.error("Failed to write event to store: %s", exc)

    def replay(self, event_name: str | None = None) -> list[DomainEvent]:
        """Replay all stored events, optionally filtered by event name."""
        events: list[DomainEvent] = []
        for log_file in sorted(self._path.glob("events-*.jsonl")):
            try:
                with open(log_file, encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            data = json.loads(line)
                            if event_name and data.get("event_name") != event_name:
                                continue
                            ev = event_from_dict(data)
                            events.append(ev)
                        except (json.JSONDecodeError, ValueError, KeyError) as exc:
                            logger.warning("Skipping malformed event in %s: %s", log_file.name, exc)
            except OSError as exc:
                logger.error("Failed to read event store file %s: %s", log_file.name, exc)
        return events

    def replay_by_source(self, source: str) -> list[DomainEvent]:
        """Replay all events from a specific source module."""
        return [e for e in self.replay() if e.source == source]

    def count_events(self) -> dict[str, int]:
        """Count events by name."""
        counts: dict[str, int] = {}
        for e in self.replay():
            name = e.event_name or e.__class__.__name__
            counts[name] = counts.get(name, 0) + 1
        return counts

    def last_n_events(self, n: int = 10) -> list[DomainEvent]:
        """Return the last N events across all log files."""
        all_events = self.replay()
        return all_events[-n:]

    def clear_session(self) -> None:
        self._session_events.clear()

    def session_events(self) -> list[DomainEvent]:
        return list(self._session_events)
