"""Event timeline — visualizes event sequences with duration, publisher, and subscriber info."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class TimelineNode:
    event_name: str
    source: str
    duration_ms: float = 0.0
    subscriber_count: int = 0
    subscribers: list[str] = field(default_factory=list)
    correlation_id: str = ""


@dataclass
class TimelineEntry:
    correlation_id: str
    nodes: list[TimelineNode] = field(default_factory=list)
    started_at: str = ""
    completed_at: str = ""

    def total_duration_ms(self) -> float:
        return sum(n.duration_ms for n in self.nodes)

    def node_count(self) -> int:
        return len(self.nodes)


class EventTimeline:
    """Tracks event sequences grouped by correlation_id.

    Builds a directed graph of event flow showing publisher → subscriber chains.
    """

    def __init__(self) -> None:
        self._entries: dict[str, TimelineEntry] = {}

    def record(
        self,
        correlation_id: str,
        event_name: str,
        source: str,
        duration_ms: float = 0.0,
        subscriber_count: int = 0,
        subscribers: list[str] | None = None,
        timestamp: str = "",
    ) -> None:
        if correlation_id not in self._entries:
            self._entries[correlation_id] = TimelineEntry(
                correlation_id=correlation_id,
                started_at=timestamp,
            )
        entry = self._entries[correlation_id]
        entry.nodes.append(TimelineNode(
            event_name=event_name,
            source=source,
            duration_ms=duration_ms,
            subscriber_count=subscriber_count,
            subscribers=subscribers or [],
            correlation_id=correlation_id,
        ))
        if timestamp:
            entry.completed_at = timestamp

    def get_timeline(self, correlation_id: str) -> TimelineEntry | None:
        return self._entries.get(correlation_id)

    def get_all_timelines(self) -> list[TimelineEntry]:
        return list(self._entries.values())

    def get_recent(self, n: int = 10) -> list[TimelineEntry]:
        return list(self._entries.values())[-n:]

    def get_by_source(self, source: str) -> list[TimelineEntry]:
        return [
            e for e in self._entries.values()
            if any(n.source == source for n in e.nodes)
        ]

    def get_by_event_name(self, event_name: str) -> list[TimelineEntry]:
        return [
            e for e in self._entries.values()
            if any(n.event_name == event_name for n in e.nodes)
        ]

    def clear(self) -> None:
        self._entries.clear()

    @property
    def count(self) -> int:
        return len(self._entries)

    def to_text(self, correlation_id: str) -> str:
        entry = self._entries.get(correlation_id)
        if not entry:
            return f"Timeline not found: {correlation_id}"
        lines = [f"Timeline: {correlation_id}", ""]
        for i, node in enumerate(entry.nodes):
            prefix = "↓ " if i > 0 else "  "
            subs = f" [{node.subscriber_count} subs]" if node.subscriber_count else ""
            dur = f" ({node.duration_ms:.1f}ms)" if node.duration_ms else ""
            lines.append(f"{prefix}{node.event_name} ({node.source}){dur}{subs}")
        lines.append("")
        lines.append(f"Total: {entry.total_duration_ms():.1f}ms, {entry.node_count()} events")
        return "\n".join(lines)
