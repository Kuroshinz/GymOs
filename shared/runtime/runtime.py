from __future__ import annotations

import asyncio
import logging
from typing import Any

from shared.events.event_bus import EventBus, get_event_bus
from shared.runtime.context import ContextCollector, RuntimeContext
from shared.runtime.health import HealthMonitor, HealthReport
from shared.runtime.orchestrator import Orchestrator
from shared.runtime.pipeline import PipelineRegistry, PipelineResult
from shared.runtime.reports import DailyReport, ReportGenerator, WeeklyReport
from shared.runtime.scheduler import CycleResult, RuntimeCycle, Scheduler

logger = logging.getLogger("runtime")


class Runtime:
    def __init__(
        self,
        event_bus: EventBus | None = None,
        services: dict[str, Any] | None = None,
        scheduler: Scheduler | None = None,
        config: Any | None = None,
    ) -> None:
        self._event_bus = event_bus or get_event_bus()
        self._services = services or {}
        self._config = config

        self.scheduler = scheduler or Scheduler()
        self.orchestrator = Orchestrator(self._event_bus)
        self.pipelines = PipelineRegistry()
        self.context = ContextCollector()
        self.health = HealthMonitor()
        self.reports = ReportGenerator()

        self._initialized = False
        self._running = False
        self._loop: asyncio.AbstractEventLoop | None = None

    def initialize(self) -> None:
        self.orchestrator.set_pipeline_registry(self.pipelines)
        logger.info(
            "Runtime initialized: %d pipelines, %d context providers",
            len(self.pipelines.all_pipelines),
            len(self.context.registered_sections),
        )
        self._initialized = True

    async def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._loop = asyncio.get_event_loop()

        await self.orchestrator.subscribe_all()
        self.health.beat()
        logger.info("Runtime started — event orchestrator active")

    async def stop(self) -> None:
        self._running = False
        self.orchestrator.unsubscribe_all()
        logger.info("Runtime stopped")

    async def execute_pipeline(self, pipeline_name: str, event: Any = None) -> PipelineResult | None:
        pipeline = self.pipelines.get(pipeline_name)
        if pipeline is None:
            logger.warning("Pipeline '%s' not found", pipeline_name)
            return None
        from shared.events.event import DomainEvent

        trigger = event if isinstance(event, DomainEvent) else None
        result = await pipeline.execute(trigger or DomainEvent(event_name="manual"))
        self.health.record_pipeline_result(result)
        return result

    async def run_cycle(self, cycle: RuntimeCycle | str) -> CycleResult:
        result = await self.scheduler.run_cycle(cycle)
        self.health.record_cycle()
        return result

    async def collect_context(self) -> RuntimeContext:
        return await self.context.collect()

    def check_health(self, engine_statuses: list | None = None) -> HealthReport:
        return self.health.generate_report(engine_statuses)

    def generate_daily_report(
        self,
        context: RuntimeContext | None = None,
    ) -> DailyReport:
        return self.reports.generate_daily(
            cycles=self.scheduler.recent_results,
            traces=self.orchestrator.traces,
            context=context,
            health=self.health.generate_report(),
        )

    def generate_weekly_report(self) -> WeeklyReport:
        return self.reports.generate_weekly()

    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def is_initialized(self) -> bool:
        return self._initialized

    @property
    def uptime(self) -> float:
        hb = self.health.generate_report().heartbeat
        return hb.uptime_seconds if hb else 0.0

    @property
    def services(self) -> dict[str, Any]:
        return dict(self._services)

    def get_service(self, name: str) -> Any | None:
        return self._services.get(name)

    def register_service(self, name: str, service: Any) -> None:
        self._services[name] = service
