from typing import Optional

from core.event_bus import EventBus, Event


class NutritionEngine:
    _instance: Optional["NutritionEngine"] = None

    def __new__(cls) -> "NutritionEngine":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        self._event_bus = EventBus()

    async def initialize(self) -> None:
        self._event_bus.on("nutrition.meal_logged", self._on_meal_logged)

    async def _on_meal_logged(self, event: Event) -> None: ...
