from __future__ import annotations

import logging
import time
import uuid
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import UTC, datetime

from shared.events.event import DomainEvent
from shared.events.event_bus import EventBus, get_event_bus
from shared.runtime.pipeline import PipelineRegistry, PipelineResult

logger = logging.getLogger("runtime.orchestrator")


@dataclass
class EventBinding:
    event_name: str
    pipeline_name: str
    description: str = ""
    enabled: bool = True
    priority: int = 0


@dataclass
class PipelineTrace:
    trace_id: str
    event_name: str
    pipeline_name: str
    correlation_id: str = ""
    started_at: str = ""
    completed_at: str = ""
    duration_ms: float = 0.0
    success: bool = True
    result: PipelineResult | None = None


EventHandler = Callable[[DomainEvent], Awaitable[None] | None]


class Orchestrator:
    def __init__(self, event_bus: EventBus | None = None) -> None:
        self._event_bus = event_bus or get_event_bus()
        self._bindings: dict[str, list[EventBinding]] = {}
        self._pipelines: PipelineRegistry | None = None
        self._traces: list[PipelineTrace] = []
        self._max_traces = 1000
        self._handlers: dict[str, EventHandler] = {}
        self._subscribed = False

    def set_pipeline_registry(self, registry: PipelineRegistry) -> None:
        self._pipelines = registry

    def bind(self, event_name: str, pipeline_name: str, description: str = "", priority: int = 0) -> EventBinding:
        binding = EventBinding(
            event_name=event_name,
            pipeline_name=pipeline_name,
            description=description or f"{event_name} -> {pipeline_name}",
            priority=priority,
        )
        self._bindings.setdefault(event_name, []).append(binding)
        self._bindings[event_name].sort(key=lambda b: b.priority)
        return binding

    def bind_many(self, bindings: list[EventBinding]) -> None:
        for b in bindings:
            self._bindings.setdefault(b.event_name, []).append(b)
        for event_name in self._bindings:
            self._bindings[event_name].sort(key=lambda b: b.priority)

    def unbind(self, event_name: str, pipeline_name: str) -> None:
        bindings = self._bindings.get(event_name, [])
        self._bindings[event_name] = [b for b in bindings if b.pipeline_name != pipeline_name]

    async def subscribe_all(self) -> None:
        if self._subscribed:
            return
        for event_name, bindings in self._bindings.items():
            handler = self._create_handler(event_name)
            self._handlers[event_name] = handler
            self._event_bus.subscribe(event_name, handler)
        self._subscribed = True
        logger.info("Orchestrator subscribed to %d event types", len(self._bindings))

    def unsubscribe_all(self) -> None:
        if not self._subscribed:
            return
        for event_name, handler in self._handlers.items():
            self._event_bus.off(event_name, handler)
        self._handlers.clear()
        self._subscribed = False
        logger.info("Orchestrator unsubscribed from all events")

    def _create_handler(self, event_name: str) -> EventHandler:
        bindings = self._bindings.get(event_name, [])
        pipeline_registry = self._pipelines

        async def handler(event: DomainEvent) -> None:
            trace_id = uuid.uuid4().hex[:12]
            started_at = datetime.now(UTC).isoformat()
            start_time = time.monotonic()

            for binding in bindings:
                if not binding.enabled:
                    continue
                if pipeline_registry is None:
                    continue
                pipeline = pipeline_registry.get(binding.pipeline_name)
                if pipeline is None:
                    logger.warning("Pipeline '%s' not found for event '%s'", binding.pipeline_name, event_name)
                    continue

                try:
                    result = await pipeline.execute(event)
                    elapsed = (time.monotonic() - start_time) * 1000
                    trace = PipelineTrace(
                        trace_id=trace_id,
                        event_name=event_name,
                        pipeline_name=binding.pipeline_name,
                        correlation_id=event.correlation_id,
                        started_at=started_at,
                        completed_at=datetime.now(UTC).isoformat(),
                        duration_ms=elapsed,
                        success=result.success,
                        result=result,
                    )
                    self._traces.append(trace)
                    if len(self._traces) > self._max_traces:
                        self._traces.pop(0)
                except Exception as exc:
                    elapsed = (time.monotonic() - start_time) * 1000
                    trace = PipelineTrace(
                        trace_id=trace_id,
                        event_name=event_name,
                        pipeline_name=binding.pipeline_name,
                        correlation_id=event.correlation_id,
                        started_at=started_at,
                        completed_at=datetime.now(UTC).isoformat(),
                        duration_ms=elapsed,
                        success=False,
                    )
                    self._traces.append(trace)
                    logger.error("Pipeline '%s' failed for event '%s': %s", binding.pipeline_name, event_name, exc)

            if len(self._traces) > self._max_traces:
                self._traces = self._traces[-self._max_traces:]

        return handler

    @property
    def traces(self) -> list[PipelineTrace]:
        return list(self._traces)

    @property
    def recent_traces(self, count: int = 10) -> list[PipelineTrace]:
        return self._traces[-count:]

    @property
    def bindings(self) -> dict[str, list[EventBinding]]:
        return {k: list(v) for k, v in self._bindings.items()}

    @property
    def is_subscribed(self) -> bool:
        return self._subscribed

    def clear_traces(self) -> None:
        self._traces.clear()
