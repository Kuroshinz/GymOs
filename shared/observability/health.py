"""Health dashboard — monitors component health across the system."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any


class HealthStatus(Enum):
    HEALTHY = "healthy"
    WARNING = "warning"
    ERROR = "error"
    UNKNOWN = "unknown"
    DISABLED = "disabled"


@dataclass
class ComponentHealth:
    name: str
    status: HealthStatus = HealthStatus.UNKNOWN
    message: str = ""
    last_checked: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    response_time_ms: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "status": self.status.value,
            "message": self.message,
            "last_checked": self.last_checked,
            "response_time_ms": round(self.response_time_ms, 2),
            "metadata": self.metadata,
        }


HealthChecker = Callable[[], ComponentHealth]


class HealthDashboard:
    """Monitors the health of all system components.

    Components register a health check function.
    The dashboard aggregates results and reports overall system health.
    """

    def __init__(self) -> None:
        self._checkers: dict[str, HealthChecker] = {}
        self._results: dict[str, ComponentHealth] = {}

    def register(self, name: str, checker: HealthChecker) -> None:
        """Register a health check function for a component."""
        self._checkers[name] = checker

    def check(self, name: str) -> ComponentHealth:
        """Run a single component health check."""
        checker = self._checkers.get(name)
        if not checker:
            return ComponentHealth(name=name, status=HealthStatus.UNKNOWN, message="No checker registered")
        try:
            result = checker()
            self._results[name] = result
            return result
        except Exception as exc:
            result = ComponentHealth(
                name=name,
                status=HealthStatus.ERROR,
                message=str(exc),
            )
            self._results[name] = result
            return result

    def check_all(self) -> dict[str, ComponentHealth]:
        """Run all registered health checks."""
        results = {}
        for name in self._checkers:
            results[name] = self.check(name)
        return results

    def get_health(self, name: str) -> ComponentHealth | None:
        return self._results.get(name)

    def get_all_health(self) -> dict[str, ComponentHealth]:
        return dict(self._results)

    def overall_status(self) -> HealthStatus:
        if not self._results:
            return HealthStatus.UNKNOWN
        statuses = [r.status for r in self._results.values()]
        if any(s == HealthStatus.ERROR for s in statuses):
            return HealthStatus.ERROR
        if any(s == HealthStatus.WARNING for s in statuses):
            return HealthStatus.WARNING
        if any(s == HealthStatus.UNKNOWN for s in statuses):
            return HealthStatus.UNKNOWN
        return HealthStatus.HEALTHY

    def healthy_count(self) -> int:
        return sum(1 for r in self._results.values() if r.status == HealthStatus.HEALTHY)

    def warning_count(self) -> int:
        return sum(1 for r in self._results.values() if r.status == HealthStatus.WARNING)

    def error_count(self) -> int:
        return sum(1 for r in self._results.values() if r.status == HealthStatus.ERROR)

    def clear(self) -> None:
        self._checkers.clear()
        self._results.clear()

    @property
    def component_count(self) -> int:
        return len(self._checkers)
