"""DevTools service — bridges the DeveloperConsole with the UI layer."""

from __future__ import annotations

from typing import Any

from modules.devtools.models.settings import DeveloperSettings, DevToolsState
from shared.observability import (
    DeveloperConsole,
    EventInspector,
    EventTimeline,
    HealthDashboard,
    MetricsCollector,
    PerformanceMonitor,
    ReplayCenter,
    StructuredLogger,
    SubscriberMonitor,
)
from shared.observability.health import ComponentHealth


class DevToolsService:
    """Application service wrapping DeveloperConsole for UI consumption.

    Provides convenience methods for the view layer.
    """

    def __init__(self, console: DeveloperConsole | None = None) -> None:
        from shared.observability.devconsole import DeveloperConsole
        self._console = console or DeveloperConsole()
        self._settings = DeveloperSettings()

    @property
    def console(self) -> DeveloperConsole:
        return self._console

    @property
    def inspector(self) -> EventInspector:
        return self._console.inspector

    @property
    def timeline(self) -> EventTimeline:
        return self._console.timeline

    @property
    def health(self) -> HealthDashboard:
        return self._console.health

    @property
    def replay(self) -> ReplayCenter:
        return self._console.replay

    @property
    def subscriber_monitor(self) -> SubscriberMonitor:
        return self._console.subscriber_monitor

    @property
    def perf_monitor(self) -> PerformanceMonitor:
        return self._console.perf_monitor

    @property
    def metrics(self) -> MetricsCollector:
        return self._console.metrics

    @property
    def logger(self) -> StructuredLogger:
        return self._console.logger

    def get_state(self) -> DevToolsState:
        state = self._console.state()
        return DevToolsState(
            settings=self._settings,
            event_count=state.event_count,
            subscriber_count=state.subscriber_count,
            log_count=state.log_count,
            error_count=state.error_count,
            health_status=state.health_status,
            uptime_seconds=state.uptime_seconds,
            events_per_sec=state.events_per_sec,
        )

    def toggle(self) -> bool:
        if self._settings.enabled:
            self._console.disable()
            self._settings.enabled = False
        else:
            self._console.enable()
            self._settings.enabled = True
        return self._settings.enabled

    def set_enabled(self, enabled: bool) -> None:
        self._settings.enabled = enabled
        if enabled:
            self._console.enable()
        else:
            self._console.disable()

    def update_settings(self, **kwargs: Any) -> None:
        for key, value in kwargs.items():
            if hasattr(self._settings, key):
                setattr(self._settings, key, value)

    def get_summary(self) -> dict[str, Any]:
        return self._console.summary()

    def run_health_checks(self) -> dict[str, ComponentHealth]:
        return self._console.health.check_all()

    def search_logs(self, query: str) -> list[Any]:
        return self._console.logger.search(query)

    def get_slow_operations(self) -> list[Any]:
        return self._console.perf_monitor.get_slow_operations()

    def get_most_expensive(self, n: int = 10) -> list[Any]:
        return self._console.perf_monitor.get_most_expensive_operations(n)

    def replay_workout(self, correlation_id: str) -> int:
        count = self._console.replay.load_workout(correlation_id)
        return count

    def replay_step(self) -> Any:
        return self._console.replay.step()
