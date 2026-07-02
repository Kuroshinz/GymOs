from __future__ import annotations

from typing import Optional

from core.event_bus import EventBus, Event


class WorkoutEngine:
    _instance: Optional["WorkoutEngine"] = None

    def __new__(cls) -> "WorkoutEngine":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        self._event_bus = EventBus()

    async def initialize(self) -> None:
        self._event_bus.on("workout.created", self._on_workout_created)
        self._event_bus.on("workout.completed", self._on_workout_completed)

    async def _on_workout_created(self, event: Event) -> None: ...
    async def _on_workout_completed(self, event: Event) -> None: ...
