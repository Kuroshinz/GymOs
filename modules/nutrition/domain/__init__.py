"""GymOS Nutrition Domain — typed models for all nutrition data.

Nutrition becomes a first-class domain inside GymOS.
Every nutrition feature helps the user achieve the lean bulk goal.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

# ─── Enums ──────────────────────────────────────────────────

class MealType(Enum):
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    PRE_WORKOUT = "pre_workout"
    POST_WORKOUT = "post_workout"
    SNACK = "snack"
    SUPPLEMENT = "supplement"


class NutritionGoalType(Enum):
    LEAN_BULK = "lean_bulk"
    MAINTENANCE = "maintenance"
    CUT = "cut"
    RECOMP = "recomp"


class MacroStatus(Enum):
    LOW = "low"
    ON_TRACK = "on_track"
    HIGH = "high"
    CRITICAL = "critical"


# ─── Core Models ────────────────────────────────────────────

@dataclass
class MealItem:
    """A single food item within a meal."""
    name: str
    calories: float = 0.0
    protein_g: float = 0.0
    carbs_g: float = 0.0
    fat_g: float = 0.0
    fiber_g: float = 0.0
    quantity: float = 1.0
    unit: str = "serving"

    @property
    def effective_calories(self) -> float:
        return self.calories * self.quantity

    @property
    def effective_protein(self) -> float:
        return self.protein_g * self.quantity

    @property
    def effective_carbs(self) -> float:
        return self.carbs_g * self.quantity

    @property
    def effective_fat(self) -> float:
        return self.fat_g * self.quantity

    @property
    def effective_fiber(self) -> float:
        return self.fiber_g * self.quantity


@dataclass
class Meal:
    """A single meal containing multiple food items."""
    id: str | None = None
    name: str = ""
    meal_type: MealType | None = None
    items: list[MealItem] = field(default_factory=list)
    eaten_at: datetime | None = None
    notes: str = ""

    @property
    def total_calories(self) -> float:
        return sum(i.effective_calories for i in self.items)

    @property
    def total_protein(self) -> float:
        return sum(i.effective_protein for i in self.items)

    @property
    def total_carbs(self) -> float:
        return sum(i.effective_carbs for i in self.items)

    @property
    def total_fat(self) -> float:
        return sum(i.effective_fat for i in self.items)

    @property
    def total_fiber(self) -> float:
        return sum(i.effective_fiber for i in self.items)


@dataclass
class MacroTarget:
    """Daily macronutrient targets."""
    calories: float = 2800.0
    protein_g: float = 160.0
    carbs_g: float = 350.0
    fat_g: float = 70.0
    fiber_g: float = 30.0
    water_ml: float = 3000.0
    goal_type: NutritionGoalType = NutritionGoalType.LEAN_BULK

    @property
    def protein_calories(self) -> float:
        return self.protein_g * 4

    @property
    def carbs_calories(self) -> float:
        return self.carbs_g * 4

    @property
    def fat_calories(self) -> float:
        return self.fat_g * 9

    @property
    def macro_calories(self) -> float:
        return self.protein_calories + self.carbs_calories + self.fat_calories

    @property
    def protein_percent(self) -> float:
        return (self.protein_calories / self.calories * 100) if self.calories > 0 else 0

    @property
    def carbs_percent(self) -> float:
        return (self.carbs_calories / self.calories * 100) if self.calories > 0 else 0

    @property
    def fat_percent(self) -> float:
        return (self.fat_calories / self.calories * 100) if self.calories > 0 else 0


@dataclass
class Hydration:
    """Daily hydration tracking."""
    water_ml: float = 0.0
    target_ml: float = 3000.0

    @property
    def progress(self) -> float:
        return min(self.water_ml / self.target_ml * 100, 100) if self.target_ml > 0 else 0

    @property
    def remaining(self) -> float:
        return max(0.0, self.target_ml - self.water_ml)

    @property
    def is_adequate(self) -> bool:
        return self.water_ml >= self.target_ml


@dataclass
class NutritionGoal:
    """The user's nutrition goal — lean bulk with specific targets."""
    goal_type: NutritionGoalType = NutritionGoalType.LEAN_BULK
    target_weight_kg: float = 72.0
    weekly_gain_target_kg: float = 0.35
    min_weekly_gain_kg: float = 0.25
    max_weekly_gain_kg: float = 0.5
    daily_surplus: int = 400
    calorie_adjustment_step: int = 100


@dataclass
class DailyNutrition:
    """Complete nutrition data for a single day."""
    date: str = ""
    meals: list[Meal] = field(default_factory=list)
    water_ml: float = 0.0
    target: MacroTarget | None = None
    notes: str = ""

    @property
    def total_calories(self) -> float:
        return sum(m.total_calories for m in self.meals)

    @property
    def total_protein(self) -> float:
        return sum(m.total_protein for m in self.meals)

    @property
    def total_carbs(self) -> float:
        return sum(m.total_carbs for m in self.meals)

    @property
    def total_fat(self) -> float:
        return sum(m.total_fat for m in self.meals)

    @property
    def total_fiber(self) -> float:
        return sum(m.total_fiber for m in self.meals)

    @property
    def meal_count(self) -> int:
        return len(self.meals)

    @property
    def has_data(self) -> bool:
        return len(self.meals) > 0 or self.water_ml > 0

    def calories_remaining(self, target: MacroTarget | None = None) -> float:
        t = target or self.target
        if not t:
            return 0.0
        return max(0.0, t.calories - self.total_calories)

    def protein_remaining(self, target: MacroTarget | None = None) -> float:
        t = target or self.target
        if not t:
            return 0.0
        return max(0.0, t.protein_g - self.total_protein)


# ─── Analysis Models ────────────────────────────────────────

@dataclass
class MacroStatusResult:
    """Status of a single macronutrient."""
    name: str = ""
    current: float = 0.0
    target: float = 0.0
    unit: str = ""
    difference: float = 0.0
    score: float = 0.0
    status: MacroStatus = MacroStatus.ON_TRACK

    @property
    def percent_complete(self) -> float:
        return min(self.current / self.target * 100, 100) if self.target > 0 else 0


@dataclass
class MacroAnalysis:
    """Complete macro analysis for a day or period."""
    date: str = ""
    calories: MacroStatusResult = field(default_factory=lambda: MacroStatusResult(
        name="Calories", unit="kcal"
    ))
    protein: MacroStatusResult = field(default_factory=lambda: MacroStatusResult(
        name="Protein", unit="g"
    ))
    carbs: MacroStatusResult = field(default_factory=lambda: MacroStatusResult(
        name="Carbs", unit="g"
    ))
    fat: MacroStatusResult = field(default_factory=lambda: MacroStatusResult(
        name="Fat", unit="g"
    ))
    fiber: MacroStatusResult = field(default_factory=lambda: MacroStatusResult(
        name="Fiber", unit="g"
    ))
    hydration: MacroStatusResult = field(default_factory=lambda: MacroStatusResult(
        name="Hydration", unit="ml"
    ))
    overall_score: float = 0.0

    @property
    def results(self) -> list[MacroStatusResult]:
        return [self.calories, self.protein, self.carbs, self.fat, self.fiber, self.hydration]


@dataclass
class LeanBulkAnalysis:
    """Analysis of lean bulk progress combining weight and nutrition data."""
    weekly_weight_gain_kg: float = 0.0
    average_calorie_surplus: float = 0.0
    average_daily_protein: float = 0.0
    protein_consistency_score: float = 0.0
    quality_score: float = 0.0
    quality_label: str = "Insufficient Data"
    recommendation: str = ""
    weeks_of_data: int = 0
    is_on_track: bool = False
    calorie_adjustment: str = ""
    protein_status: str = ""


@dataclass
class NutritionSummary:
    """Summary of nutrition data for a date range, consumable by the Dashboard."""
    date: str = ""
    calories_current: float = 0.0
    calories_target: float = 2800.0
    protein_current: float = 0.0
    protein_target: float = 160.0
    carbs_current: float = 0.0
    carbs_target: float = 350.0
    fat_current: float = 0.0
    fat_target: float = 70.0
    fiber_current: float = 0.0
    fiber_target: float = 30.0
    hydration_current: float = 0.0
    hydration_target: float = 3000.0
    overall_score: float = 0.0
    configured: bool = True
    lean_bulk: LeanBulkAnalysis | None = None

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "calories": {"current": self.calories_current, "target": self.calories_target},
            "protein": {"current": self.protein_current, "target": self.protein_target},
            "carbs": {"current": self.carbs_current, "target": self.carbs_target},
            "fat": {"current": self.fat_current, "target": self.fat_target},
            "fiber": {"current": self.fiber_current, "target": self.fiber_target},
            "hydration": {"current": self.hydration_current, "target": self.hydration_target},
        }
        if self.lean_bulk:
            result["lean_bulk"] = {
                "quality_score": self.lean_bulk.quality_score,
                "quality_label": self.lean_bulk.quality_label,
                "weekly_weight_gain_kg": self.lean_bulk.weekly_weight_gain_kg,
                "is_on_track": self.lean_bulk.is_on_track,
                "calorie_adjustment": self.lean_bulk.calorie_adjustment,
                "recommendation": self.lean_bulk.recommendation,
            }
        return result
