from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable, Coroutine
from dataclasses import dataclass, field
from typing import Any, Optional

TaskFunc = Callable[..., Coroutine[Any, Any, None] | None]

@dataclass
class ScheduledTask:
    name: str
    func: TaskFunc
    interval: float
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)
    _task: asyncio.Task | None = None


class Scheduler:
    _instance: Scheduler | None = None

    def __new__(cls) -> Scheduler:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._tasks: dict[str, ScheduledTask] = {}
        return cls._instance

    def add(
        self,
        name: str,
        func: TaskFunc,
        interval: float,
        *args: Any,
        **kwargs: Any,
    ) -> ScheduledTask:
        task = ScheduledTask(name=name, func=func, interval=interval, args=args, kwargs=kwargs)
        self._tasks[name] = task
        return task

    def remove(self, name: str) -> None:
        task = self._tasks.pop(name, None)
        if task and task._task and not task._task.done():
            task._task.cancel()

    async def _run_loop(self, task: ScheduledTask) -> None:
        while True:
            try:
                result = task.func(*task.args, **task.kwargs)
                if asyncio.iscoroutine(result):
                    await result
            except asyncio.CancelledError:
                break
            except Exception:
                logging.exception(f"Task {task.name} failed")
            await asyncio.sleep(task.interval)

    async def start_all(self) -> None:
        for task in self._tasks.values():
            task._task = asyncio.create_task(self._run_loop(task))

    async def stop_all(self) -> None:
        for task in self._tasks.values():
            if task._task and not task._task.done():
                task._task.cancel()
        self._tasks.clear()
