"""Nutrition module publisher — publishes nutrition events."""

from shared.events.domain_events import MealLogged
from shared.events.publisher import Publisher


class NutritionPublisher(Publisher):
    """Publishes events from the nutrition module."""

    def publish_meal_logged(
        self,
        meal_name: str = "",
        calories: float = 0.0,
        protein_g: float = 0.0,
        carbs_g: float = 0.0,
        fat_g: float = 0.0,
        date: str = "",
    ) -> MealLogged:
        return self.publish(MealLogged(
            meal_name=meal_name,
            calories=calories,
            protein_g=protein_g,
            carbs_g=carbs_g,
            fat_g=carbs_g,
            date=date,
        ))
