from typing import Optional

from core.event_bus import EventBus, Event


class RecoveryEngine:
    _instance: Optional["RecoveryEngine"] = None

    def __new__(cls) -> "RecoveryEngine":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        self._event_bus = EventBus()

    async def initialize(self) -> None:
        self._event_bus.on("workout.completed", self._on_workout_completed)
        self._event_bus.on("sleep.logged", self._on_sleep_logged)

    async def _on_workout_completed(self, event: Event) -> None: ...
    async def _on_sleep_logged(self, event: Event) -> None: ...
