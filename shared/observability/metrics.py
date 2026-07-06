"""Metrics platform — internal system metrics collection."""

from __future__ import annotations

import threading
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any


class MetricType(Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    TIMER = "timer"
    HISTOGRAM = "histogram"


@dataclass
class MetricSample:
    name: str
    metric_type: str
    value: float
    tags: dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "metric_type": self.metric_type,
            "value": self.value,
            "tags": self.tags,
            "timestamp": self.timestamp.isoformat(),
        }


class MetricsCollector:
    """Collects internal system metrics.

    Supports counters, gauges, timers, and histograms.
    Thread-safe. Exportable for dashboards.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._counters: dict[str, float] = defaultdict(float)
        self._gauges: dict[str, float] = {}
        self._timers: dict[str, list[float]] = defaultdict(list)
        self._histograms: dict[str, list[float]] = defaultdict(list)
        self._samples: list[MetricSample] = []
        self._max_samples = 10000

    # ─── Counters ────────────────────────────────────────

    def increment(self, name: str, value: float = 1.0, tags: dict[str, str] | None = None) -> None:
        with self._lock:
            self._counters[name] += value
            self._record(MetricType.COUNTER, name, self._counters[name], tags)

    def counter(self, name: str) -> float:
        with self._lock:
            return self._counters.get(name, 0.0)

    # ─── Gauges ──────────────────────────────────────────

    def gauge(self, name: str, value: float, tags: dict[str, str] | None = None) -> None:
        with self._lock:
            self._gauges[name] = value
            self._record(MetricType.GAUGE, name, value, tags)

    def get_gauge(self, name: str) -> float | None:
        with self._lock:
            return self._gauges.get(name)

    # ─── Timers ──────────────────────────────────────────

    def timer(self, name: str, duration_ms: float, tags: dict[str, str] | None = None) -> None:
        with self._lock:
            self._timers[name].append(duration_ms)
            self._record(MetricType.TIMER, name, duration_ms, tags)

    def time(self, name: str, tags: dict[str, str] | None = None) -> _TimerContext:
        return _TimerContext(self, name, tags or {})

    def timer_stats(self, name: str) -> dict[str, float]:
        with self._lock:
            vals = self._timers.get(name, [])
            if not vals:
                return {"count": 0, "min": 0, "max": 0, "avg": 0, "total": 0}
            return {
                "count": len(vals),
                "min": min(vals),
                "max": max(vals),
                "avg": sum(vals) / len(vals),
                "total": sum(vals),
            }

    # ─── Histograms ──────────────────────────────────────

    def histogram(self, name: str, value: float, tags: dict[str, str] | None = None) -> None:
        with self._lock:
            self._histograms[name].append(value)
            self._record(MetricType.HISTOGRAM, name, value, tags)

    def histogram_stats(self, name: str) -> dict[str, float]:
        with self._lock:
            vals = self._histograms.get(name, [])
            if not vals:
                return {"count": 0, "min": 0, "max": 0, "avg": 0, "p50": 0, "p95": 0, "p99": 0}
            sorted_vals = sorted(vals)
            n = len(sorted_vals)
            def percentile(p: float) -> float:
                idx = max(0, min(n - 1, int(n * p / 100.0) - 1))
                return sorted_vals[idx]
            return {
                "count": n,
                "min": sorted_vals[0],
                "max": sorted_vals[-1],
                "avg": sum(sorted_vals) / n,
                "p50": percentile(50),
                "p95": percentile(95),
                "p99": percentile(99),
            }

    # ─── Internal ─────────────────────────────────────────

    def _record(self, mtype: MetricType, name: str, value: float, tags: dict[str, str] | None) -> None:
        sample = MetricSample(name=name, metric_type=mtype.value, value=value, tags=tags or {})
        self._samples.append(sample)
        if len(self._samples) > self._max_samples:
            self._samples.pop(0)

    def get_samples(self, metric_type: str | None = None) -> list[MetricSample]:
        if metric_type:
            return [s for s in self._samples if s.metric_type == metric_type]
        return list(self._samples)

    def get_all_counters(self) -> dict[str, float]:
        with self._lock:
            return dict(self._counters)

    def get_all_timers(self) -> dict[str, dict[str, float]]:
        return {name: self.timer_stats(name) for name in list(self._timers.keys())}

    def clear(self) -> None:
        with self._lock:
            self._counters.clear()
            self._gauges.clear()
            self._timers.clear()
            self._histograms.clear()
            self._samples.clear()

    def events_per_sec(self) -> float:
        samples = [s for s in self._samples if s.name == "event.published"]
        if len(samples) < 2:
            return 0.0
        duration = (samples[-1].timestamp - samples[0].timestamp).total_seconds()
        if duration <= 0:
            return 0.0
        return len(samples) / duration


class _TimerContext:
    def __init__(self, collector: MetricsCollector, name: str, tags: dict[str, str]) -> None:
        self._collector = collector
        self._name = name
        self._tags = tags
        self._start: float = 0.0

    def __enter__(self) -> _TimerContext:
        self._start = time.perf_counter()
        return self

    def __exit__(self, *args: Any) -> None:
        duration_ms = (time.perf_counter() - self._start) * 1000
        self._collector.timer(self._name, duration_ms, self._tags)


_metrics_instance: MetricsCollector | None = None


def get_metrics() -> MetricsCollector:
    global _metrics_instance
    if _metrics_instance is None:
        _metrics_instance = MetricsCollector()
    return _metrics_instance
