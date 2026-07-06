"""Developer console — top-level facade that wires all observability components."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from shared.events.event_bus import EventBus, get_event_bus
from shared.events.store import EventStore
from shared.observability.health import ComponentHealth, HealthDashboard, HealthStatus
from shared.observability.inspector import EventInspector
from shared.observability.logger import get_logger
from shared.observability.metrics import get_metrics
from shared.observability.perf_monitor import PerformanceMonitor
from shared.observability.replay import ReplayCenter
from shared.observability.subscriber_monitor import SubscriberMonitor
from shared.observability.timeline import EventTimeline


@dataclass
class DeveloperState:
    enabled: bool = True
    event_count: int = 0
    subscriber_count: int = 0
    log_count: int = 0
    error_count: int = 0
    health_status: str = "unknown"
    inspector_paused: bool = False
    replay_status: str = "idle"
    uptime_seconds: float = 0.0
    events_per_sec: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "enabled": self.enabled,
            "event_count": self.event_count,
            "subscriber_count": self.subscriber_count,
            "log_count": self.log_count,
            "error_count": self.error_count,
            "health_status": self.health_status,
            "inspector_paused": self.inspector_paused,
            "replay_status": self.replay_status,
            "uptime_seconds": round(self.uptime_seconds, 1),
            "events_per_sec": round(self.events_per_sec, 2),
        }


DeveloperPlugin = Callable[["DeveloperConsole"], None]


class DeveloperConsole:
    """Top-level developer console.

    Wires together all observability components:
    - Event inspector
    - Event timeline
    - Subscriber monitor
    - Performance monitor
    - Health dashboard
    - Replay center
    - Structured logger
    - Metrics collector

    Supports plugin registration for future modules.
    """

    def __init__(
        self,
        bus: EventBus | None = None,
        store: EventStore | None = None,
        enabled: bool = True,
    ) -> None:
        self._bus = bus or get_event_bus()
        self._store = store or EventStore()
        self._enabled = enabled
        self._start_time = datetime.now(UTC)
        self._plugins: dict[str, DeveloperPlugin] = {}

        self.inspector = EventInspector(self._bus)
        self.timeline = EventTimeline()
        self.subscriber_monitor = SubscriberMonitor(self._bus)
        self.perf_monitor = PerformanceMonitor()
        self.health = HealthDashboard()
        self.replay = ReplayCenter(self._store, self._bus)
        self.logger = get_logger()
        self.metrics = get_metrics()

        if enabled:
            self._wire()

    def _wire(self) -> None:
        self.inspector.attach(self._bus)
        self._register_default_health_checks()

    def _header_timing(self) -> dict[str, float]:
        return {
            "event_count": self.inspector.count(),
            "performance_samples": len(self.perf_monitor._samples),
            "timeline_entries": self.timeline.count,
            "health_components": self.health.component_count,
            "slow_operations": len(self.perf_monitor.get_slow_operations()),
        }

    def disable(self) -> None:
        self._enabled = False
        self.inspector.pause()

    def enable(self) -> None:
        self._enabled = True
        self.inspector.resume()

    @property
    def enabled(self) -> bool:
        return self._enabled

    def state(self) -> DeveloperState:
        overall = self.health.overall_status()
        return DeveloperState(
            enabled=self._enabled,
            event_count=self.inspector.count(),
            subscriber_count=len(self.subscriber_monitor.get_all()),
            log_count=self.logger.count,
            error_count=self.logger.error_count(),
            health_status=overall.value,
            inspector_paused=self.inspector.is_paused,
            replay_status=self.replay.progress().status,
            uptime_seconds=(datetime.now(UTC) - self._start_time).total_seconds(),
            events_per_sec=self.metrics.events_per_sec(),
        )

    def summary(self) -> dict[str, Any]:
        return {
            "state": self.state().to_dict(),
            "inspector": {
                "total_events": self.inspector.count(),
                "paused": self.inspector.is_paused,
            },
            "health": {
                c.name: c.status.value
                for c in self.health.get_all_health().values()
            },
            "metrics": {
                "counters": self.metrics.get_all_counters(),
                "timers": self.metrics.get_all_timers(),
            },
            "logs": {
                "total": self.logger.count,
                "errors": self.logger.error_count(),
                "warnings": self.logger.warning_count(),
            },
            "performance": self._header_timing(),
        }

    # ─── Health check registration ────────────────────────

    def _register_default_health_checks(self) -> None:
        def check_event_bus() -> ComponentHealth:
            count = self._bus.handler_count
            return ComponentHealth(
                name="Event Bus",
                status=HealthStatus.HEALTHY,
                message=f"{count} handlers registered",
            )

        def check_event_store() -> ComponentHealth:
            try:
                event_count = len(self._store.session_events())
                return ComponentHealth(
                    name="Event Store",
                    status=HealthStatus.HEALTHY,
                    message=f"{event_count} session events",
                )
            except Exception as exc:
                return ComponentHealth(
                    name="Event Store",
                    status=HealthStatus.ERROR,
                    message=str(exc),
                )

        def check_logger() -> ComponentHealth:
            return ComponentHealth(
                name="Logger",
                status=HealthStatus.HEALTHY,
                message=f"{self.logger.count} entries",
            )

        self.health.register("Event Bus", check_event_bus)
        self.health.register("Event Store", check_event_store)
        self.health.register("Logger", check_logger)

    def register_health_check(self, name: str, checker: Callable[[], ComponentHealth]) -> None:
        self.health.register(name, checker)

    # ─── Plugin system ─────────────────────────────────────

    def register_plugin(self, name: str, plugin: DeveloperPlugin) -> None:
        self._plugins[name] = plugin
        plugin(self)

    def get_plugins(self) -> dict[str, DeveloperPlugin]:
        return dict(self._plugins)

    # ─── Convenience ──────────────────────────────────────

    def log_event_timing(self, event_name: str, source: str, duration_ms: float, subscriber_count: int = 0, correlation_id: str = "") -> None:
        self.metrics.timer("event.dispatch", duration_ms, {"event": event_name})
        self.timeline.record(
            correlation_id=correlation_id or event_name,
            event_name=event_name,
            source=source,
            duration_ms=duration_ms,
            subscriber_count=subscriber_count,
        )
        if duration_ms > 100:
            self.logger.warning(
                f"Slow event dispatch: {event_name} ({duration_ms:.1f}ms)",
                module="devconsole",
                correlation_id=correlation_id,
            )
