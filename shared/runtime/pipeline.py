from __future__ import annotations

import logging
import time
import uuid
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from shared.events.event import DomainEvent

logger = logging.getLogger("runtime.pipeline")


class PipelineStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"


@dataclass
class PipelineStep:
    step_id: str
    name: str
    processor: str = ""
    duration_ms: float = 0.0
    status: PipelineStatus = PipelineStatus.PENDING
    error: str | None = None
    output: dict | None = None
    started_at: str | None = None
    completed_at: str | None = None


@dataclass
class PipelineResult:
    pipeline_id: str
    pipeline_name: str
    trigger_event: str = ""
    correlation_id: str = ""
    status: PipelineStatus = PipelineStatus.PENDING
    steps: list[PipelineStep] = field(default_factory=list)
    started_at: str = ""
    completed_at: str = ""
    total_duration_ms: float = 0.0
    error: str | None = None

    @property
    def success(self) -> bool:
        return self.status in (PipelineStatus.COMPLETED, PipelineStatus.PARTIAL)

    @property
    def step_count(self) -> int:
        return len(self.steps)

    @property
    def failed_steps(self) -> list[PipelineStep]:
        return [s for s in self.steps if s.status == PipelineStatus.FAILED]

    @property
    def duration_s(self) -> float:
        return self.total_duration_ms / 1000.0


StepHandler = Callable[[DomainEvent, dict[str, Any]], Awaitable[dict[str, Any] | None]]


@dataclass
class PipelineDef:
    name: str
    steps: list[tuple[str, StepHandler]]
    description: str = ""
    timeout_ms: float = 30000.0


StepHandlerSync = Callable[[DomainEvent, dict[str, Any]], dict[str, Any] | None]


class Pipeline:
    def __init__(self, pipeline_def: PipelineDef) -> None:
        self._def = pipeline_def

    @property
    def name(self) -> str:
        return self._def.name

    @property
    def definition(self) -> PipelineDef:
        return self._def

    async def execute(
        self,
        event: DomainEvent,
        initial_context: dict[str, Any] | None = None,
    ) -> PipelineResult:
        pipeline_id = uuid.uuid4().hex[:12]
        started_at = datetime.now(UTC).isoformat()
        context: dict[str, Any] = dict(initial_context or {})
        context["event"] = event
        context["pipeline_id"] = pipeline_id

        result = PipelineResult(
            pipeline_id=pipeline_id,
            pipeline_name=self._def.name,
            trigger_event=event.event_name or event.__class__.__name__,
            correlation_id=event.correlation_id,
            status=PipelineStatus.RUNNING,
            started_at=started_at,
        )

        start_time = time.monotonic()

        for step_name, handler in self._def.steps:
            step_start = time.monotonic()
            step = PipelineStep(
                step_id=f"{pipeline_id}_{step_name}",
                name=step_name,
                processor=handler.__name__ if hasattr(handler, "__name__") else handler.__class__.__name__,
                status=PipelineStatus.RUNNING,
                started_at=datetime.now(UTC).isoformat(),
            )

            try:
                step_output = await self._run_step(handler, event, context)
                step.status = PipelineStatus.COMPLETED
                step.output = step_output or {}
                step.completed_at = datetime.now(UTC).isoformat()
                step.duration_ms = (time.monotonic() - step_start) * 1000
                result.steps.append(step)

                if step_output is not None:
                    context[step_name] = step_output
            except Exception as exc:
                elapsed = (time.monotonic() - step_start) * 1000
                step.status = PipelineStatus.FAILED
                step.error = str(exc)
                step.duration_ms = elapsed
                step.completed_at = datetime.now(UTC).isoformat()
                result.steps.append(step)
                logger.warning("Pipeline '%s' step '%s' failed: %s", self._def.name, step_name, exc)

        total_elapsed = (time.monotonic() - start_time) * 1000
        result.total_duration_ms = total_elapsed
        result.completed_at = datetime.now(UTC).isoformat()

        failed = result.failed_steps
        if not failed:
            result.status = PipelineStatus.COMPLETED
        elif len(failed) < len(self._def.steps):
            result.status = PipelineStatus.PARTIAL
        else:
            result.status = PipelineStatus.FAILED

        return result

    async def _run_step(
        self,
        handler: StepHandler | StepHandlerSync,
        event: DomainEvent,
        context: dict[str, Any],
    ) -> dict[str, Any] | None:
        result = handler(event, context)
        if hasattr(result, "__await__"):
            result = await result
        return result


class PipelineRegistry:
    def __init__(self) -> None:
        self._pipelines: dict[str, Pipeline] = {}

    def register(self, pipeline: Pipeline) -> None:
        self._pipelines[pipeline.name] = pipeline

    def register_def(self, pipeline_def: PipelineDef) -> Pipeline:
        pipeline = Pipeline(pipeline_def)
        self._pipelines[pipeline_def.name] = pipeline
        return pipeline

    def unregister(self, name: str) -> None:
        self._pipelines.pop(name, None)

    def get(self, name: str) -> Pipeline | None:
        return self._pipelines.get(name)

    @property
    def all_pipelines(self) -> list[Pipeline]:
        return list(self._pipelines.values())

    @property
    def pipeline_names(self) -> list[str]:
        return list(self._pipelines.keys())

    def clear(self) -> None:
        self._pipelines.clear()
