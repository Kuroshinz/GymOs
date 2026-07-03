"""Nutrition Provider — abstraction for GymBrain to consume nutrition data.

Design:
  - NutritionProvider is an interface that GymBrain consumes
  - ProductionNutritionProvider is the SQLite-backed implementation
  - Providers are replaceable (test with MockNutritionProvider)
  - GymBrain never accesses NutritionRepository directly
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any, Optional

from modules.nutrition.domain import (
    DailyNutrition, LeanBulkAnalysis, MacroAnalysis,
    MacroStatusResult, MacroStatus, MacroTarget, NutritionSummary,
)
from modules.nutrition.infrastructure.repository import NutritionRepository


class NutritionProvider(ABC):
    """Abstract interface for nutrition data access.

    GymBrain consumes nutrition data exclusively through this interface.
    Never couples GymBrain to a specific repository or database.
    """

    @abstractmethod
    def get_today(self) -> Optional[DailyNutrition]:
        ...

    @abstractmethod
    def get_day(self, date: str) -> Optional[DailyNutrition]:
        ...

    @abstractmethod
    def get_recent_days(self, days: int = 7) -> list[DailyNutrition]:
        ...

    @abstractmethod
    def get_default_target(self) -> MacroTarget:
        ...

    @abstractmethod
    def get_average_calories(self, days: int = 7) -> float:
        ...

    @abstractmethod
    def get_average_protein(self, days: int = 7) -> float:
        ...

    @abstractmethod
    def has_data(self) -> bool:
        ...

    @abstractmethod
    def get_body_weight_history(self, days: int = 90) -> list[Any]:
        ...

    @abstractmethod
    def get_latest_body_weight(self) -> Optional[Any]:
        ...

    @abstractmethod
    def get_summary(self) -> NutritionSummary:
        ...


class ProductionNutritionProvider(NutritionProvider):
    """SQLite-backed NutritionProvider for production use.

    Wraps NutritionRepository and also accesses body weight data
    through the shared GymDatabase.
    """

    def __init__(
        self,
        repository: NutritionRepository,
        db: Any = None,
    ) -> None:
        self._repo = repository
        self._db = db

    def get_today(self) -> Optional[DailyNutrition]:
        today = datetime.now().strftime("%Y-%m-%d")
        return self._repo.get_day(today)

    def get_day(self, date: str) -> Optional[DailyNutrition]:
        return self._repo.get_day(date)

    def get_recent_days(self, days: int = 7) -> list[DailyNutrition]:
        return self._repo.get_recent_days(days)

    def get_default_target(self) -> MacroTarget:
        return self._repo.get_default_target()

    def get_average_calories(self, days: int = 7) -> float:
        return self._repo.get_average_calories(days)

    def get_average_protein(self, days: int = 7) -> float:
        return self._repo.get_average_protein(days)

    def has_data(self) -> bool:
        return self._repo.has_data()

    def get_body_weight_history(self, days: int = 90) -> list[Any]:
        if self._db:
            try:
                return self._db.get_body_weight_history(days=days)
            except Exception:
                pass
        return []

    def get_latest_body_weight(self) -> Optional[Any]:
        if self._db:
            try:
                return self._db.get_latest_body_weight()
            except Exception:
                pass
        return None

    def get_summary(self) -> NutritionSummary:
        """Build a NutritionSummary for the Dashboard."""
        today_str = datetime.now().strftime("%Y-%m-%d")
        target = self.get_default_target()

        # Today's nutrition
        today_day = self.get_today()
        if today_day and today_day.has_data:
            cals = today_day.total_calories
            protein = today_day.total_protein
            carbs = today_day.total_carbs
            fat = today_day.total_fat
            fiber = today_day.total_fiber
            water = today_day.water_ml
        else:
            cals = 0.0
            protein = 0.0
            carbs = 0.0
            fat = 0.0
            fiber = 0.0
            water = 0.0

        # Calculate overall score
        scores = []
        if target.calories > 0:
            scores.append(min(cals / target.calories, 1.0) * 100)
        if target.protein_g > 0:
            scores.append(min(protein / target.protein_g, 1.0) * 100)
        if target.carbs_g > 0:
            scores.append(min(carbs / target.carbs_g, 1.0) * 100)
        if target.fat_g > 0:
            scores.append(min(fat / target.fat_g, 1.0) * 100)
        if target.water_ml > 0:
            scores.append(min(water / target.water_ml, 1.0) * 100)

        overall = sum(scores) / len(scores) if scores else 0.0

        return NutritionSummary(
            date=today_str,
            calories_current=cals,
            calories_target=target.calories,
            protein_current=protein,
            protein_target=target.protein_g,
            carbs_current=carbs,
            carbs_target=target.carbs_g,
            fat_current=fat,
            fat_target=target.fat_g,
            fiber_current=fiber,
            fiber_target=target.fiber_g,
            hydration_current=water,
            hydration_target=target.water_ml,
            overall_score=round(overall, 1),
            configured=self.has_data(),
        )
