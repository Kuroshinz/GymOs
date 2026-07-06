from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum

from shared.events.event import DomainEvent

logger = logging.getLogger("runtime.scheduler")


class RuntimeCycle(Enum):
    MORNING = "morning"
    WORKOUT = "workout"
    MEAL = "meal"
    RECOVERY = "recovery"
    NIGHT = "night"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


@dataclass
class CycleResult:
    cycle: RuntimeCycle
    started_at: str = ""
    completed_at: str = ""
    duration_ms: float = 0.0
    success: bool = True
    error: str | None = None
    pipelines_run: list[str] = field(default_factory=list)


CycleHandler = Callable[[], Awaitable[CycleResult] | CycleResult]


class Scheduler:
    def __init__(self) -> None:
        self._handlers: dict[str, list[CycleHandler]] = {}
        self._tasks: dict[str, asyncio.Task] = {}
        self._running = False
        self._results: list[CycleResult] = []

    def register_cycle_handler(self, cycle: RuntimeCycle | str, handler: CycleHandler) -> None:
        key = cycle.value if isinstance(cycle, RuntimeCycle) else cycle
        self._handlers.setdefault(key, []).append(handler)

    def unregister_cycle_handler(self, cycle: RuntimeCycle | str, handler: CycleHandler) -> None:
        key = cycle.value if isinstance(cycle, RuntimeCycle) else cycle
        handlers = self._handlers.get(key, [])
        if handler in handlers:
            handlers.remove(handler)

    async def run_cycle(self, cycle: RuntimeCycle | str, trigger_event: DomainEvent | None = None) -> CycleResult:
        key = cycle.value if isinstance(cycle, RuntimeCycle) else cycle
        started_at = datetime.now(UTC).isoformat()
        start_time = __import__("time").monotonic()

        result = CycleResult(
            cycle=cycle if isinstance(cycle, RuntimeCycle) else RuntimeCycle.MORNING,
            started_at=started_at,
        )

        handlers = self._handlers.get(key, [])
        if not handlers:
            logger.debug("No handlers for cycle '%s'", key)
            result.completed_at = datetime.now(UTC).isoformat()
            self._results.append(result)
            return result

        all_success = True
        for handler in handlers:
            try:
                cycle_result = handler()
                if hasattr(cycle_result, "__await__"):
                    cycle_result = await cycle_result
                if isinstance(cycle_result, CycleResult):
                    result.pipelines_run.extend(cycle_result.pipelines_run)
                    if not cycle_result.success:
                        all_success = False
                result.pipelines_run.append(handler.__name__ if hasattr(handler, "__name__") else str(handler))
            except Exception as exc:
                all_success = False
                logger.warning("Cycle '%s' handler failed: %s", key, exc)
                result.error = str(exc)

        elapsed = (__import__("time").monotonic() - start_time) * 1000
        result.duration_ms = elapsed
        result.completed_at = datetime.now(UTC).isoformat()
        result.success = all_success
        self._results.append(result)
        return result

    async def run_morning(self) -> CycleResult:
        return await self.run_cycle(RuntimeCycle.MORNING)

    async def run_workout(self) -> CycleResult:
        return await self.run_cycle(RuntimeCycle.WORKOUT)

    async def run_meal(self) -> CycleResult:
        return await self.run_cycle(RuntimeCycle.MEAL)

    async def run_recovery(self) -> CycleResult:
        return await self.run_cycle(RuntimeCycle.RECOVERY)

    async def run_night(self) -> CycleResult:
        return await self.run_cycle(RuntimeCycle.NIGHT)

    async def run_weekly(self) -> CycleResult:
        return await self.run_cycle(RuntimeCycle.WEEKLY)

    async def run_monthly(self) -> CycleResult:
        return await self.run_cycle(RuntimeCycle.MONTHLY)

    async def start_auto_scheduler(self, interval_seconds: float = 60.0) -> None:
        self._running = True
        while self._running:
            await asyncio.sleep(interval_seconds)

    def stop_auto_scheduler(self) -> None:
        self._running = False
        for task in self._tasks.values():
            task.cancel()
        self._tasks.clear()

    @property
    def recent_results(self) -> list[CycleResult]:
        return list(self._results)

    @property
    def last_result(self) -> CycleResult | None:
        return self._results[-1] if self._results else None

    def clear_results(self) -> None:
        self._results.clear()
