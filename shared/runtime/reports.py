from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from shared.runtime.context import RuntimeContext
from shared.runtime.health import HealthReport
from shared.runtime.orchestrator import PipelineTrace
from shared.runtime.pipeline import PipelineResult
from shared.runtime.scheduler import CycleResult

logger = logging.getLogger("runtime.reports")


@dataclass
class DailyReport:
    date: str = ""
    generated_at: str = ""
    cycles_run: list[CycleResult] = field(default_factory=list)
    pipelines_executed: int = 0
    pipelines_succeeded: int = 0
    pipelines_failed: int = 0
    events_processed: int = 0
    errors: list[str] = field(default_factory=list)
    context: RuntimeContext | None = None
    health: HealthReport | None = None

    @property
    def success_rate(self) -> float:
        total = self.pipelines_executed
        if total == 0:
            return 1.0
        return self.pipelines_succeeded / total


@dataclass
class WeeklyReport:
    week_start: str = ""
    week_end: str = ""
    generated_at: str = ""
    daily_reports: list[DailyReport] = field(default_factory=list)
    total_pipelines: int = 0
    total_events: int = 0
    total_errors: int = 0
    avg_success_rate: float = 1.0
    top_errors: list[str] = field(default_factory=list)


class ReportGenerator:
    def __init__(self) -> None:
        self._daily_reports: list[DailyReport] = []
        self._max_daily_reports = 90

    def generate_daily(
        self,
        cycles: list[CycleResult],
        traces: list[PipelineTrace],
        context: RuntimeContext | None = None,
        health: HealthReport | None = None,
    ) -> DailyReport:
        today = datetime.now(UTC).strftime("%Y-%m-%d")
        total = len(traces)
        succeeded = sum(1 for t in traces if t.success)
        failed = total - succeeded
        errors = [t.result.error for t in traces if t.result and t.result.error] if traces else []

        report = DailyReport(
            date=today,
            generated_at=datetime.now(UTC).isoformat(),
            cycles_run=cycles,
            pipelines_executed=total,
            pipelines_succeeded=succeeded,
            pipelines_failed=failed,
            events_processed=total,
            errors=errors[:10],
            context=context,
            health=health,
        )
        self._daily_reports.append(report)
        if len(self._daily_reports) > self._max_daily_reports:
            self._daily_reports.pop(0)
        return report

    def generate_weekly(self, reports: list[DailyReport] | None = None) -> WeeklyReport:
        source = reports or self._daily_reports
        now = datetime.now(UTC)
        week_start = now.strftime("%Y-%m-%d")
        week_end = now.strftime("%Y-%m-%d")
        recent = source[-7:] if len(source) >= 7 else source

        total_pipelines = sum(r.pipelines_executed for r in recent)
        total_events = sum(r.events_processed for r in recent)
        avg_rate = (
            sum(r.success_rate for r in recent) / len(recent)
            if recent
            else 1.0
        )
        all_errors: list[str] = []
        for r in recent:
            all_errors.extend(r.errors)
        top_errors = sorted(set(all_errors), key=lambda e: all_errors.count(e), reverse=True)[:5]

        return WeeklyReport(
            week_start=week_start,
            week_end=week_end,
            generated_at=datetime.now(UTC).isoformat(),
            daily_reports=recent,
            total_pipelines=total_pipelines,
            total_events=total_events,
            total_errors=len(all_errors),
            avg_success_rate=avg_rate,
            top_errors=top_errors,
        )

    def generate_pipeline_trace_report(self, trace: PipelineTrace) -> dict[str, Any]:
        return {
            "trace_id": trace.trace_id,
            "event": trace.event_name,
            "pipeline": trace.pipeline_name,
            "correlation_id": trace.correlation_id,
            "started_at": trace.started_at,
            "completed_at": trace.completed_at,
            "duration_ms": trace.duration_ms,
            "success": trace.success,
            "steps": self._format_steps(trace.result) if trace.result else [],
        }

    def generate_event_trace(self, traces: list[PipelineTrace]) -> dict[str, Any]:
        by_event: dict[str, list[PipelineTrace]] = {}
        for t in traces:
            by_event.setdefault(t.event_name, []).append(t)

        return {
            "generated_at": datetime.now(UTC).isoformat(),
            "total_traces": len(traces),
            "events": {
                event: {
                    "count": len(event_traces),
                    "success_rate": sum(1 for t in event_traces if t.success) / len(event_traces) if event_traces else 1.0,
                    "pipelines": list({t.pipeline_name for t in event_traces}),
                }
                for event, event_traces in by_event.items()
            },
        }

    def generate_health_report(self, health: HealthReport) -> dict[str, Any]:
        return {
            "generated_at": health.collected_at,
            "overall_health": health.overall_health,
            "healthy": health.is_healthy,
            "heartbeat": {
                "tick": health.heartbeat.tick if health.heartbeat else 0,
                "uptime_seconds": health.heartbeat.uptime_seconds if health.heartbeat else 0,
                "cycles_completed": health.heartbeat.cycles_completed if health.heartbeat else 0,
            } if health.heartbeat else {},
            "pipelines": [
                {
                    "name": p.pipeline_name,
                    "total_runs": p.total_runs,
                    "success_rate": p.success_rate,
                    "avg_duration_ms": round(p.avg_duration_ms, 1),
                }
                for p in health.pipelines
            ],
            "engines": [
                {
                    "name": e.name,
                    "available": e.available,
                    "stale": e.stale,
                    "error": e.error,
                }
                for e in health.engines
            ],
            "pending_events": health.pending_events,
            "failed_events": health.failed_events,
            "stale_engines": health.stale_engines,
        }

    def generate_cycle_summary(self, results: list[CycleResult]) -> dict[str, Any]:
        by_cycle: dict[str, list[CycleResult]] = {}
        for r in results:
            key = r.cycle.value if hasattr(r.cycle, "value") else str(r.cycle)
            by_cycle.setdefault(key, []).append(r)

        return {
            "generated_at": datetime.now(UTC).isoformat(),
            "total_cycles": len(results),
            "cycles": {
                cycle: {
                    "count": len(cycle_results),
                    "success_rate": sum(1 for r in cycle_results if r.success) / len(cycle_results) if cycle_results else 1.0,
                    "avg_duration_ms": sum(r.duration_ms for r in cycle_results) / len(cycle_results) if cycle_results else 0,
                }
                for cycle, cycle_results in by_cycle.items()
            },
        }

    @property
    def daily_reports(self) -> list[DailyReport]:
        return list(self._daily_reports)

    def _format_steps(self, result: PipelineResult) -> list[dict[str, Any]]:
        return [
            {
                "step_id": s.step_id,
                "name": s.name,
                "status": s.status.value,
                "duration_ms": s.duration_ms,
                "error": s.error,
            }
            for s in result.steps
        ]
