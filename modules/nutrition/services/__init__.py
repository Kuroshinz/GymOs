"""Nutrition Service — application-layer orchestration for all nutrition features.

Coordinates repository, analysis engines, providers, and event publishing.
This is the primary API consumed by the Dashboard and GymBrain.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Optional

from modules.nutrition.analysis import LeanBulkAnalyzer, MacroAnalyzer
from modules.nutrition.domain import (
    DailyNutrition,
    LeanBulkAnalysis,
    MacroAnalysis,
    MacroTarget,
    Meal,
    MealItem,
    NutritionGoal,
    NutritionSummary,
)
from modules.nutrition.infrastructure.importers import (
    CSVNutritionImporter,
    ExportResult,
    ImportResult,
    JSONNutritionImporter,
    NutritionExporter,
)
from modules.nutrition.infrastructure.repository import NutritionRepository
from modules.nutrition.providers import NutritionProvider, ProductionNutritionProvider
from shared.events.domain_events import MacroTargetChanged, MealLogged, NutritionUpdated

logger = logging.getLogger("nexus.nutrition.service")


class NutritionService:
    """Application service for all nutrition operations.

    This is the primary entry point for:
      - Dashboard (via get_summary())
      - GymBrain rules (via provider)
      - Meal logging
      - Data import/export
    """

    def __init__(
        self,
        repository: NutritionRepository,
        db: Any = None,
        event_bus: Any = None,
    ) -> None:
        self._repo = repository
        self._db = db
        self._event_bus = event_bus
        self._provider = ProductionNutritionProvider(repository, db)
        self._macro_analyzer = MacroAnalyzer(self._provider)
        self._lean_bulk_analyzer = LeanBulkAnalyzer(self._provider)
        self._csv_importer = CSVNutritionImporter()
        self._json_importer = JSONNutritionImporter()
        self._exporter = NutritionExporter()
        self._goal = NutritionGoal()

    @property
    def provider(self) -> NutritionProvider:
        return self._provider

    @property
    def macro_analyzer(self) -> MacroAnalyzer:
        return self._macro_analyzer

    @property
    def lean_bulk_analyzer(self) -> LeanBulkAnalyzer:
        return self._lean_bulk_analyzer

    # ─── Data Access ─────────────────────────────────────────

    def get_today(self) -> DailyNutrition | None:
        return self._repo.get_day(datetime.now().strftime("%Y-%m-%d"))

    def get_day(self, date: str) -> DailyNutrition | None:
        return self._repo.get_day(date)

    def get_recent_days(self, days: int = 7) -> list[DailyNutrition]:
        return self._repo.get_recent_days(days)

    def has_data(self) -> bool:
        return self._repo.has_data()

    # ─── Meal Logging ────────────────────────────────────────

    def log_meal(self, date: str, meal: Meal) -> DailyNutrition:
        """Log a meal for a specific date."""
        day = self._repo.get_day(date) or DailyNutrition(date=date)
        day.meals.append(meal)
        saved = self._repo.save_day(day)
        self._publish_event(MealLogged(
            meal_name=meal.name,
            calories=meal.total_calories,
            protein_g=meal.total_protein,
            carbs_g=meal.total_carbs,
            fat_g=meal.total_fat,
            date=date,
        ))
        return saved

    def log_water(self, date: str, ml: float) -> DailyNutrition:
        """Log water intake for a specific date."""
        day = self._repo.get_day(date) or DailyNutrition(date=date)
        day.water_ml += ml
        saved = self._repo.save_day(day)
        self._publish_event(NutritionUpdated(
            date=date,
            update_type="hydration",
            entries_count=1,
        ))
        return saved

    # ─── Targets ─────────────────────────────────────────────

    def get_target(self) -> MacroTarget:
        return self._repo.get_default_target()

    def set_target(self, target: MacroTarget) -> None:
        self._repo.save_target(target)
        self._publish_event(MacroTargetChanged(
            calories=target.calories,
            protein_g=target.protein_g,
            carbs_g=target.carbs_g,
            fat_g=target.fat_g,
            goal_type=target.goal_type.value if target.goal_type else "",
        ))

    # ─── Analysis ────────────────────────────────────────────

    def get_macro_analysis(self, days: int = 1) -> MacroAnalysis:
        if days <= 1:
            return self._macro_analyzer.analyze_day()
        return self._macro_analyzer.analyze_recent(days)

    def get_lean_bulk_analysis(self, weeks: int = 4) -> LeanBulkAnalysis:
        return self._lean_bulk_analyzer.analyze(weeks)

    def get_summary(self) -> NutritionSummary:
        """Get a Dashboard-consumable nutrition summary."""
        summary = self._provider.get_summary()
        if self.has_data() and self._db:
            try:
                lean_bulk = self.get_lean_bulk_analysis(weeks=4)
                summary.lean_bulk = lean_bulk
            except Exception:
                pass
        return summary

    # ─── Import / Export ─────────────────────────────────────

    def import_file(self, filepath: str) -> ImportResult:
        """Import nutrition data from a file. Auto-detects format."""
        if self._csv_importer.can_handle(filepath):
            result = self._csv_importer.import_file(filepath)
        elif self._json_importer.can_handle(filepath):
            result = self._json_importer.import_file(filepath)
        else:
            return ImportResult(success=False, errors=["Unsupported file format. Use CSV or JSON."])

        if result.success and result.days:
            for day in result.days:
                self._repo.save_day(day)
            self._publish_event(NutritionUpdated(
                date=datetime.now().strftime("%Y-%m-%d"),
                update_type="import",
                entries_count=result.entries_imported,
            ))
        return result

    def preview_import(self, filepath: str) -> dict:
        """Preview what would be imported."""
        if self._csv_importer.can_handle(filepath):
            return self._csv_importer.preview(filepath)
        elif self._json_importer.can_handle(filepath):
            return self._json_importer.preview(filepath)
        return {"error": "Unsupported file format"}

    def export_csv(self, filepath: str, days: int = 30) -> ExportResult:
        days_list = self._repo.get_recent_days(days)
        return self._exporter.export_csv(days_list, filepath)

    def export_json(self, filepath: str, days: int = 30) -> ExportResult:
        days_list = self._repo.get_recent_days(days)
        return self._exporter.export_json(days_list, filepath)

    # ─── Events ──────────────────────────────────────────────

    def _publish_event(self, event: object) -> None:
        if not self._event_bus:
            return
        try:
            self._event_bus.publish(event)
        except Exception:
            logger.warning("Failed to publish %s event", type(event).__name__, exc_info=True)

    # ─── Cleanup ─────────────────────────────────────────────

    def dispose(self) -> None:
        self._repo.dispose()
