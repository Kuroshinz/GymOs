"""DeveloperController — orchestrates devtools lifecycle and UI binding."""

from __future__ import annotations

from typing import Any

from modules.devtools.models.settings import DeveloperSettings
from modules.devtools.services.devtool_service import DevToolsService
from shared.observability import (
    DeveloperConsole,
    InspectedEvent,
    ReplayMode,
    SubscriberInfo,
)


class DeveloperController:
    """Controller for the developer tools workspace.

    Handles user actions from devtools UI and delegates to services.
    """

    def __init__(self, service: DevToolsService | None = None) -> None:
        self._service = service or DevToolsService()

    @property
    def service(self) -> DevToolsService:
        return self._service

    # ─── Lifecycle ────────────────────────────────────────

    def enable(self) -> None:
        self._service.set_enabled(True)

    def disable(self) -> None:
        self._service.set_enabled(False)

    def toggle(self) -> bool:
        return self._service.toggle()

    def get_state(self) -> dict[str, Any]:
        return self._service.get_state().to_dict()

    def get_summary(self) -> dict[str, Any]:
        return self._service.get_summary()

    # ─── Event Inspector ──────────────────────────────────

    def get_inspected_events(self, n: int = 100) -> list[InspectedEvent]:
        return self._service.inspector.last_n(n)

    def search_events(self, query: str) -> list[InspectedEvent]:
        return self._service.inspector.search(query)

    def pause_inspector(self) -> None:
        self._service.inspector.pause()

    def resume_inspector(self) -> None:
        self._service.inspector.resume()

    def clear_inspector(self) -> None:
        self._service.inspector.clear()

    def export_events_json(self) -> str:
        return self._service.inspector.export_json()

    # ─── Timeline ─────────────────────────────────────────

    def get_timeline(self, correlation_id: str) -> dict[str, Any] | None:
        entry = self._service.timeline.get_timeline(correlation_id)
        if entry:
            return {
                "correlation_id": entry.correlation_id,
                "nodes": [
                    {
                        "event_name": n.event_name,
                        "source": n.source,
                        "duration_ms": round(n.duration_ms, 2),
                        "subscriber_count": n.subscriber_count,
                    }
                    for n in entry.nodes
                ],
                "total_duration_ms": round(entry.total_duration_ms(), 2),
                "node_count": entry.node_count(),
            }
        return None

    def get_recent_timelines(self, n: int = 10) -> list[dict[str, Any]]:
        entries = self._service.timeline.get_recent(n)
        return [
            {
                "correlation_id": e.correlation_id,
                "node_count": e.node_count(),
                "total_duration_ms": round(e.total_duration_ms(), 2),
            }
            for e in entries
        ]

    # ─── Subscriber Explorer ──────────────────────────────

    def get_subscribers(self) -> list[SubscriberInfo]:
        return self._service.subscriber_monitor.get_all()

    def mute_subscriber(self, name: str) -> None:
        self._service.subscriber_monitor.mute(name)

    def unmute_subscriber(self, name: str) -> None:
        self._service.subscriber_monitor.unmute(name)

    def toggle_subscriber(self, name: str) -> bool:
        return self._service.subscriber_monitor.toggle_mute(name)

    def get_slow_subscribers(self, threshold_ms: float = 100.0) -> list[SubscriberInfo]:
        return self._service.subscriber_monitor.find_slow_subscribers(threshold_ms)

    def get_failing_subscribers(self) -> list[SubscriberInfo]:
        return self._service.subscriber_monitor.find_failing_subscribers()

    # ─── Performance ──────────────────────────────────────

    def get_slow_operations(self) -> list[Any]:
        return self._service.get_slow_operations()

    def get_most_expensive(self, n: int = 10) -> list[Any]:
        return self._service.get_most_expensive(n)

    def get_perf_stats(self, operation: str) -> dict[str, float]:
        return self._service.perf_monitor.get_stats(operation)

    # ─── Health ───────────────────────────────────────────

    def run_health_checks(self) -> dict[str, Any]:
        results = self._service.run_health_checks()
        return {name: hc.to_dict() for name, hc in results.items()}

    # ─── Replay ───────────────────────────────────────────

    def load_replay_workout(self, correlation_id: str) -> int:
        return self._service.replay_workout(correlation_id)

    def load_replay_all(self) -> int:
        return self._service.replay.load_all()

    def replay_step(self) -> Any:
        return self._service.replay_step()

    def replay_step_back(self) -> Any:
        return self._service.replay.step_back()

    def set_replay_mode(self, mode: str) -> None:
        self._service.replay.set_mode(ReplayMode(mode))

    def set_replay_speed(self, speed: float) -> None:
        self._service.replay.set_speed(speed)

    def get_replay_progress(self) -> Any:
        return self._service.replay.progress()

    # ─── Logs ─────────────────────────────────────────────

    def get_logs(self, n: int = 100) -> list[Any]:
        return self._service.logger.get_recent(n)

    def search_logs(self, query: str) -> list[Any]:
        return self._service.search_logs(query)

    def export_logs(self) -> list[dict[str, Any]]:
        return self._service.logger.export()
