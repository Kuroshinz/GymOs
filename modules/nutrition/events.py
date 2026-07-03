"""Nutrition Domain Events — event-driven integration with GymOS event platform.

Events published:
  - NutritionUpdated — broad signal that nutrition data has changed
  - MealLogged — specific meal was logged
  - MacroTargetChanged — macro targets were updated

Event consumers:
  - Dashboard (auto-refresh nutrition widget)
  - GymBrain (re-evaluate nutrition-based rules)
  - AnalysisCache (invalidate cached nutrition analysis)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from shared.events.event import DomainEvent


@dataclass
class NutritionUpdated(DomainEvent):
    """Published when any nutrition data changes."""
    date: str = ""
    update_type: str = ""  # "meal", "hydration", "import", "all"
    entries_count: int = 0
    source: str = "nutrition"


@dataclass
class MealLogged(DomainEvent):
    """Published when a meal is logged."""
    date: str = ""
    meal_name: str = ""
    calories: float = 0.0
    protein_g: float = 0.0
    source: str = "nutrition"


@dataclass
class MacroTargetChanged(DomainEvent):
    """Published when macro targets are updated."""
    calories: float = 0.0
    protein_g: float = 0.0
    carbs_g: float = 0.0
    fat_g: float = 0.0
    goal_type: str = ""
    source: str = "nutrition"


# Register events for deserialization
NUTRITION_EVENT_REGISTRY: dict[str, type[DomainEvent]] = {
    "NutritionUpdated": NutritionUpdated,
    "MealLogged": MealLogged,
    "MacroTargetChanged": MacroTargetChanged,
}
