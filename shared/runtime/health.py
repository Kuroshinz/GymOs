from __future__ import annotations

import logging
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime

from shared.runtime.pipeline import PipelineResult

logger = logging.getLogger("runtime.health")


@dataclass
class Heartbeat:
    tick: int = 0
    started_at: str = ""
    last_beat_at: str = ""
    uptime_seconds: float = 0.0
    cycles_completed: int = 0
    pipelines_executed: int = 0

    @property
    def is_alive(self) -> bool:
        return self.tick > 0


@dataclass
class EngineStatus:
    name: str
    available: bool = False
    last_seen: str = ""
    response_time_ms: float = 0.0
    stale: bool = False
    error: str | None = None


@dataclass
class PipelineMetrics:
    pipeline_name: str
    total_runs: int = 0
    successful_runs: int = 0
    failed_runs: int = 0
    avg_duration_ms: float = 0.0
    max_duration_ms: float = 0.0
    min_duration_ms: float = 0.0
    last_run_at: str = ""
    last_error: str | None = None

    @property
    def success_rate(self) -> float:
        if self.total_runs == 0:
            return 1.0
        return self.successful_runs / self.total_runs


@dataclass
class HealthReport:
    collected_at: str = ""
    heartbeat: Heartbeat | None = None
    pipelines: list[PipelineMetrics] = field(default_factory=list)
    engines: list[EngineStatus] = field(default_factory=list)
    pending_events: int = 0
    failed_events: int = 0
    stale_engines: list[str] = field(default_factory=list)
    overall_health: float = 1.0

    @property
    def is_healthy(self) -> bool:
        return self.overall_health >= 0.7

    @property
    def pipeline_success_rate(self) -> float:
        if not self.pipelines:
            return 1.0
        total = sum(p.total_runs for p in self.pipelines)
        successful = sum(p.successful_runs for p in self.pipelines)
        return successful / total if total > 0 else 1.0


HealthCheckFn = Callable[[], bool | tuple[bool, float]]


class HealthMonitor:
    def __init__(self) -> None:
        self._started_at = datetime.now(UTC).isoformat()
        self._tick = 0
        self._last_beat = time.monotonic()
        self._pipeline_metrics: dict[str, PipelineMetrics] = {}
        self._engine_checks: dict[str, HealthCheckFn] = {}
        self._engine_statuses: dict[str, EngineStatus] = {}
        self._pending_count = 0
        self._failed_count = 0
        self._cycles_completed = 0
        self._pipelines_executed = 0

    def beat(self) -> Heartbeat:
        self._tick += 1
        now = time.monotonic()
        uptime = now - self._last_beat
        self._last_beat = now
        return Heartbeat(
            tick=self._tick,
            started_at=self._started_at,
            last_beat_at=datetime.now(UTC).isoformat(),
            uptime_seconds=uptime,
            cycles_completed=self._cycles_completed,
            pipelines_executed=self._pipelines_executed,
        )

    def record_pipeline_result(self, result: PipelineResult) -> None:
        self._pipelines_executed += 1
        metrics = self._pipeline_metrics.setdefault(
            result.pipeline_name,
            PipelineMetrics(pipeline_name=result.pipeline_name),
        )
        metrics.total_runs += 1
        if result.success:
            metrics.successful_runs += 1
        else:
            metrics.failed_runs += 1
            self._failed_count += 1

        metrics.avg_duration_ms = (
            (metrics.avg_duration_ms * (metrics.total_runs - 1) + result.total_duration_ms)
            / metrics.total_runs
        )
        metrics.max_duration_ms = max(metrics.max_duration_ms, result.total_duration_ms)
        if metrics.min_duration_ms == 0 or result.total_duration_ms < metrics.min_duration_ms:
            metrics.min_duration_ms = result.total_duration_ms
        metrics.last_run_at = result.completed_at
        if not result.success and result.error:
            metrics.last_error = result.error

    def register_engine_check(self, name: str, check_fn: HealthCheckFn) -> None:
        self._engine_checks[name] = check_fn
        self._engine_statuses[name] = EngineStatus(name=name)

    def unregister_engine_check(self, name: str) -> None:
        self._engine_checks.pop(name, None)
        self._engine_statuses.pop(name, None)

    def increment_pending(self) -> None:
        self._pending_count += 1

    def increment_failed(self) -> None:
        self._failed_count += 1

    def record_cycle(self) -> None:
        self._cycles_completed += 1

    async def check_engines(self) -> list[EngineStatus]:
        now = datetime.now(UTC).isoformat()
        statuses: list[EngineStatus] = []
        stale_timeout = 300.0

        for name, check_fn in self._engine_checks.items():
            status = self._engine_statuses.setdefault(name, EngineStatus(name=name))
            try:
                result = check_fn()
                if hasattr(result, "__await__"):
                    result = await result
                if isinstance(result, tuple):
                    available, response_time = result
                    status.response_time_ms = response_time
                else:
                    available = bool(result)
                status.available = available
                status.last_seen = now
                status.error = None
            except Exception as exc:
                status.available = False
                status.error = str(exc)
                logger.warning("Engine check '%s' failed: %s", name, exc)
            statuses.append(status)
            self._engine_statuses[name] = status

        for status in statuses:
            if status.last_seen:
                try:
                    last = datetime.fromisoformat(status.last_seen)
                    elapsed = (datetime.now(UTC) - last).total_seconds()
                    status.stale = elapsed > stale_timeout
                except Exception:
                    status.stale = False

        return statuses

    def generate_report(self, engine_statuses: list[EngineStatus] | None = None) -> HealthReport:
        pipelines = list(self._pipeline_metrics.values())
        engines = engine_statuses or list(self._engine_statuses.values())

        stale = [e.name for e in engines if e.stale]
        total_pipelines = sum(p.total_runs for p in pipelines)
        failed_pipelines = sum(p.failed_runs for p in pipelines)

        health_score = 1.0
        if total_pipelines > 0:
            health_score -= (failed_pipelines / total_pipelines) * 0.3
        if engines:
            available_count = sum(1 for e in engines if e.available)
            health_score -= (1 - available_count / len(engines)) * 0.3
        if stale:
            health_score -= len(stale) * 0.1
        health_score = max(0.0, min(1.0, health_score))

        return HealthReport(
            collected_at=datetime.now(UTC).isoformat(),
            heartbeat=Heartbeat(
                tick=self._tick,
                started_at=self._started_at,
                last_beat_at=datetime.now(UTC).isoformat(),
                uptime_seconds=time.monotonic() - self._last_beat,
                cycles_completed=self._cycles_completed,
                pipelines_executed=self._pipelines_executed,
            ),
            pipelines=pipelines,
            engines=engines,
            pending_events=self._pending_count,
            failed_events=self._failed_count,
            stale_engines=stale,
            overall_health=health_score,
        )

    @property
    def pipeline_metrics(self) -> list[PipelineMetrics]:
        return list(self._pipeline_metrics.values())

    def get_pipeline_metrics(self, name: str) -> PipelineMetrics | None:
        return self._pipeline_metrics.get(name)

    def reset(self) -> None:
        self._pipeline_metrics.clear()
        self._engine_statuses.clear()
        self._pending_count = 0
        self._failed_count = 0
        self._cycles_completed = 0
        self._pipelines_executed = 0
        self._tick = 0
        self._started_at = datetime.now(UTC).isoformat()
        self._last_beat = time.monotonic()
