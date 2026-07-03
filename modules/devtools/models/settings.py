"""Developer settings and state models."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class DeveloperSettings:
    enabled: bool = False
    show_overlay: bool = False
    inspector_paused: bool = False
    replay_speed: float = 1.0
    max_log_entries: int = 1000
    max_inspected_events: int = 5000
    slow_threshold_ms: float = 100.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "enabled": self.enabled,
            "show_overlay": self.show_overlay,
            "inspector_paused": self.inspector_paused,
            "replay_speed": self.replay_speed,
            "max_log_entries": self.max_log_entries,
            "max_inspected_events": self.max_inspected_events,
            "slow_threshold_ms": self.slow_threshold_ms,
        }


@dataclass
class DevToolsState:
    settings: DeveloperSettings = field(default_factory=DeveloperSettings)
    event_count: int = 0
    subscriber_count: int = 0
    log_count: int = 0
    error_count: int = 0
    health_status: str = "unknown"
    uptime_seconds: float = 0.0
    events_per_sec: float = 0.0
    last_refresh: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return {
            "settings": self.settings.to_dict(),
            "event_count": self.event_count,
            "subscriber_count": self.subscriber_count,
            "log_count": self.log_count,
            "error_count": self.error_count,
            "health_status": self.health_status,
            "uptime_seconds": round(self.uptime_seconds, 1),
            "events_per_sec": round(self.events_per_sec, 2),
            "last_refresh": self.last_refresh,
        }
