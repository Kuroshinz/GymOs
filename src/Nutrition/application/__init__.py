from typing import Optional

from core.event_bus import EventBus
from src.Nutrition.domain import NutritionDay, Meal


class NutritionService:
    def __init__(self, repository, event_bus: EventBus) -> None:
        self._repository = repository
        self._event_bus = event_bus

    async def log_meal(self, date: str, meal: Meal) -> NutritionDay:
        day = await self._repository.get_day(date) or NutritionDay(date=date)
        day.meals.append(meal)
        await self._repository.save_day(day)
        await self._event_bus.emit("nutrition.meal_logged", {
            "date": date,
            "calories": meal.total_calories,
            "protein": meal.total_protein,
        })
        return day

    async def get_day(self, date: str) -> Optional[NutritionDay]:
        return await self._repository.get_day(date)
