from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class MealItem:
    name: str
    calories: float
    protein_g: float
    carbs_g: float
    fat_g: float
    quantity: float = 1.0
    unit: str = "serving"


@dataclass
class Meal:
    id: Optional[str] = None
    name: str = ""
    items: list[MealItem] = field(default_factory=list)
    eaten_at: Optional[datetime] = None
    notes: str = ""

    @property
    def total_calories(self) -> float:
        return sum(item.calories * item.quantity for item in self.items)

    @property
    def total_protein(self) -> float:
        return sum(item.protein_g * item.quantity for item in self.items)


@dataclass
class NutritionDay:
    date: str
    meals: list[Meal] = field(default_factory=list)
    water_ml: float = 0.0

    @property
    def total_calories(self) -> float:
        return sum(meal.total_calories for meal in self.meals)

    @property
    def total_protein(self) -> float:
        return sum(meal.total_protein for meal in self.meals)
