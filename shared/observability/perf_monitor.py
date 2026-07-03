"""Performance monitor — measures dispatch latency, subscriber latency, and system-wide timing."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable


@dataclass
class PerfSample:
    operation: str
    duration_ms: float
    component: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    tags: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "operation": self.operation,
            "duration_ms": round(self.duration_ms, 3),
            "component": self.component,
            "timestamp": self.timestamp,
            "tags": self.tags,
        }


class PerformanceMonitor:
    """Collects and reports performance samples across all system components.

    Highlights slow operations automatically.
    """

    def __init__(self, slow_threshold_ms: float = 100.0) -> None:
        self._samples: list[PerfSample] = []
        self._max_samples = 10000
        self._slow_threshold_ms = slow_threshold_ms

    def record(
        self,
        operation: str,
        duration_ms: float,
        component: str = "",
        tags: dict[str, str] | None = None,
    ) -> PerfSample:
        sample = PerfSample(
            operation=operation,
            duration_ms=duration_ms,
            component=component,
            tags=tags or {},
        )
        self._samples.append(sample)
        if len(self._samples) > self._max_samples:
            self._samples.pop(0)
        return sample

    def time(self, operation: str, component: str = "", tags: dict[str, str] | None = None) -> _PerfTimer:
        return _PerfTimer(self, operation, component, tags or {})

    def get_samples(
        self,
        operation: str | None = None,
        component: str | None = None,
        limit: int = 100,
    ) -> list[PerfSample]:
        results = list(self._samples)
        if operation:
            results = [s for s in results if s.operation == operation]
        if component:
            results = [s for s in results if s.component == component]
        return results[-limit:]

    def get_slow_operations(self, threshold_ms: float | None = None) -> list[PerfSample]:
        threshold = threshold_ms or self._slow_threshold_ms
        return [s for s in self._samples if s.duration_ms > threshold]

    def get_stats(self, operation: str) -> dict[str, float]:
        samples = [s for s in self._samples if s.operation == operation]
        if not samples:
            return {"count": 0, "min": 0, "max": 0, "avg": 0}
        durations = [s.duration_ms for s in samples]
        return {
            "count": len(durations),
            "min": min(durations),
            "max": max(durations),
            "avg": sum(durations) / len(durations),
        }

    def get_component_stats(self, component: str) -> dict[str, Any]:
        samples = [s for s in self._samples if s.component == component]
        if not samples:
            return {"count": 0, "operations": {}}
        ops: dict[str, list[float]] = {}
        for s in samples:
            ops.setdefault(s.operation, []).append(s.duration_ms)
        stats = {}
        for op, durations in ops.items():
            stats[op] = {
                "count": len(durations),
                "min": min(durations),
                "max": max(durations),
                "avg": sum(durations) / len(durations),
            }
        return {"count": len(samples), "operations": stats}

    def get_most_expensive_operations(self, n: int = 10) -> list[PerfSample]:
        sorted_samples = sorted(self._samples, key=lambda s: s.duration_ms, reverse=True)
        return sorted_samples[:n]

    def clear(self) -> None:
        self._samples.clear()


class _PerfTimer:
    def __init__(self, monitor: PerformanceMonitor, operation: str, component: str, tags: dict[str, str]) -> None:
        self._monitor = monitor
        self._operation = operation
        self._component = component
        self._tags = tags
        self._start: float = 0.0

    def __enter__(self) -> "_PerfTimer":
        self._start = time.perf_counter()
        return self

    def __exit__(self, *args: Any) -> None:
        duration_ms = (time.perf_counter() - self._start) * 1000
        self._monitor.record(self._operation, duration_ms, self._component, self._tags)
