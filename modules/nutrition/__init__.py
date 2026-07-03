"""GymOS Nutrition Intelligence — first-class nutrition domain for GymBrain.

GymBrain combines: Training + Body Weight + Nutrition + Recovery
to generate better recommendations for the user's lean bulk goal.

Usage:
    from modules.nutrition import NutritionService
    from modules.nutrition.infrastructure.repository import NutritionRepository

    repo = NutritionRepository("data/gymos.db")
    service = NutritionService(repo)
    summary = service.get_summary()
"""

from modules.nutrition.analysis import LeanBulkAnalyzer, MacroAnalyzer
from modules.nutrition.domain import (
    DailyNutrition, Hydration, LeanBulkAnalysis, MacroAnalysis,
    MacroStatusResult, MacroStatus, MacroTarget, Meal,
    MealItem, MealType, NutritionGoal, NutritionGoalType, NutritionSummary,
)
from modules.nutrition.infrastructure.repository import NutritionRepository
from modules.nutrition.providers import NutritionProvider, ProductionNutritionProvider
from modules.nutrition.services import NutritionService

__all__ = [
    # Domain
    "DailyNutrition",
    "Hydration",
    "MacroTarget",
    "Meal",
    "MealItem",
    "MealType",
    "NutritionGoal",
    "NutritionGoalType",
    "NutritionSummary",
    "MacroStatus",
    "MacroStatusResult",
    "MacroAnalysis",
    "LeanBulkAnalysis",
    # Services
    "NutritionService",
    # Repository
    "NutritionRepository",
    # Providers
    "NutritionProvider",
    "ProductionNutritionProvider",
    # Analysis
    "MacroAnalyzer",
    "LeanBulkAnalyzer",
]
