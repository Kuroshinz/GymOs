from typing import Optional

from core.event_bus import EventBus, Event


class PredictionEngine:
    _instance: Optional["PredictionEngine"] = None

    def __new__(cls) -> "PredictionEngine":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        self._event_bus = EventBus()

    async def initialize(self) -> None:
        self._event_bus.on("analytics.updated", self._on_analytics_updated)

    async def _on_analytics_updated(self, event: Event) -> None: ...

    async def predict_performance(self, user_id: str) -> dict: ...
    async def predict_recovery_time(self, workout_id: str) -> float: ...
