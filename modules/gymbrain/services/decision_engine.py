from __future__ import annotations

from typing import Any

from modules.gymbrain.analysis.fatigue import FatigueAnalyzer
from modules.gymbrain.analysis.goals import GoalTracker
from modules.gymbrain.analysis.muscle import MuscleAnalyzer
from modules.gymbrain.analysis.plateau import PlateauDetector
from modules.gymbrain.cache.analysis_cache import AnalysisCache
from modules.gymbrain.providers.production_provider import ProductionDataProvider
from modules.gymbrain.services.weekly_review import WeeklyReviewGenerator
from modules.gymbrain.models.analysis import FatigueResult, GoalProgress, MuscleAnalysisResult, PlateauResult, WeeklyReview
from modules.gymbrain.models.recommendations import Recommendation
from modules.gymbrain.providers.data_provider import DataProvider
from modules.gymbrain.rules.engine import RuleEngine
from modules.gymbrain.rules.volume_rules import VolumeRule, VolumeExcessRule, FrequencyRule
from modules.gymbrain.rules.progression_rules import ProgressionRule, DeloadRule
from modules.gymbrain.rules.plateau_rules import WeightPlateauRule, StrengthPlateauRule, RepPlateauRule
from modules.gymbrain.rules.fatigue_rules import FatigueRule, TechniqueRule, RestRule
from modules.gymbrain.rules.recovery_rules import RecoveryRule, ConsistencyRule



class DecisionEngine:
    """Central GymBrain decision engine.

    Orchestrates all analysis and rule evaluation to produce
    structured, explainable recommendations.

    This is the primary API consumed by the application layer.

    Production wiring (one-liner)::

        engine = DecisionEngine.from_production(db=my_db)
    """

    def __init__(self, provider: DataProvider | None = None, cache: AnalysisCache | None = None) -> None:
        self._provider = provider or DataProvider()
        self._rule_engine = RuleEngine()
        self._register_default_rules()
        self._plateau_detector = PlateauDetector(self._provider)
        self._fatigue_analyzer = FatigueAnalyzer(self._provider)
        self._muscle_analyzer = MuscleAnalyzer(self._provider)
        self._goal_tracker = GoalTracker(self._provider)
        self._cache = cache

    @classmethod
    def from_production(
        cls,
        db: Any,
        knowledge_service: Any = None,
        volume_engine: Any = None,
        pr_engine: Any = None,
        recovery_engine: Any = None,
        progression_engine: Any = None,
        exercise_repo: Any = None,
        muscle_repo: Any = None,
        program_repo: Any = None,
        nutrition_provider: Any = None,
        cache: AnalysisCache | None = None,
    ) -> DecisionEngine:
        """Build a fully-wired DecisionEngine backed by production infrastructure.

        Accepts a ``GymDatabase`` instance and optional engine/repository overrides.
        When engines are omitted they are auto-created from the db.

        Usage::

            from modules.workout.infrastructure.repository import GymDatabase
            engine = DecisionEngine.from_production(db=GymDatabase("data/gymos.db"))
        """
        from modules.workout.application.pr_engine import PREngine
        from modules.workout.application.recovery_engine import RecoveryEngine
        from modules.workout.application.progression_engine import ProgressionEngine

        # Auto-create engines from db if not provided
        pr_engine = pr_engine or PREngine(db)
        recovery_engine = recovery_engine or RecoveryEngine(db)
        progression_engine = progression_engine or ProgressionEngine(db)

        provider = ProductionDataProvider(
            db=db,
            exercise_repo=exercise_repo,
            muscle_repo=muscle_repo,
            program_repo=program_repo,
            knowledge_service=knowledge_service,
            volume_engine=volume_engine,
            pr_engine=pr_engine,
            recovery_engine=recovery_engine,
            progression_engine=progression_engine,
            nutrition_provider=nutrition_provider,
        )
        return cls(provider=provider, cache=cache)

    def _register_default_rules(self) -> None:
        rules = [
            ProgressionRule(),
            VolumeRule(),
            VolumeExcessRule(),
            FrequencyRule(),
            DeloadRule(),
            WeightPlateauRule(),
            StrengthPlateauRule(),
            RepPlateauRule(),
            FatigueRule(),
            TechniqueRule(),
            RestRule(),
            RecoveryRule(),
            ConsistencyRule(),
            # Nutrition Intelligence rules
            self._import_rule("ProteinDeficitRule"),
            self._import_rule("CalorieAdjustmentRule"),
            self._import_rule("GainRateRule"),
            self._import_rule("HydrationRule"),
            self._import_rule("LeanBulkQualityRule"),
        ]
        for rule in rules:
            self._rule_engine.register(rule)

    def _import_rule(self, name: str):
        """Lazy-import a rule by class name to avoid circular imports."""
        import importlib
        module = importlib.import_module("modules.gymbrain.rules.nutrition_rules")
        cls = getattr(module, name)
        return cls()

    @property
    def rule_engine(self) -> RuleEngine:
        return self._rule_engine

    @property
    def provider(self) -> DataProvider:
        return self._provider

    # ── Dashboard Integration API ──────────────────────────────────

    def get_today_recommendations(self, max_recs: int = 10) -> list[Recommendation]:
        return self._rule_engine.evaluate(self._provider, max_recommendations=max_recs)

    def get_weekly_review(self) -> WeeklyReview:
        generator = WeeklyReviewGenerator(self._provider)
        return generator.generate()

    def get_goal_progress(self, goal_weight: float | None = None) -> GoalProgress:
        return self._goal_tracker.get_progress(goal_weight_kg=goal_weight)

    def get_priority_muscles(self) -> list[MuscleAnalysisResult]:
        if self._cache:
            cached = self._cache.get("priority_muscles")
            if cached is not None:
                return cached
        result = self._muscle_analyzer.analyze()
        if self._cache:
            self._cache.set("priority_muscles", result)
        return result

    def get_recovery_status(self) -> FatigueResult:
        if self._cache:
            cached = self._cache.get("recovery_status")
            if cached is not None:
                return cached
        result = self._fatigue_analyzer.analyze()
        if self._cache:
            self._cache.set("recovery_status", result)
        return result

    def get_plateau_analysis(self) -> list[PlateauResult]:
        if self._cache:
            cached = self._cache.get("plateau_analysis")
            if cached is not None:
                return cached
        exercises = self._provider.get_all_exercises()
        compound = [
            ex.get("name", "") if isinstance(ex, dict) else getattr(ex, "name", "")
            for ex in exercises
            if (ex.get("category") if isinstance(ex, dict) else getattr(ex, "category", "")) in ("compound", "upper_compound", "lower_compound")
        ]
        result = self._plateau_detector.detect_all(compound_exercises=compound[:5])
        if self._cache:
            self._cache.set("plateau_analysis", result)
        return result

    def get_muscle_analysis(self, muscle_ids: list[str] | None = None) -> list[MuscleAnalysisResult]:
        return self._muscle_analyzer.analyze(muscle_ids)

    def set_provider(self, provider: DataProvider) -> None:
        self._provider = provider
        self._plateau_detector = PlateauDetector(self._provider)
        self._fatigue_analyzer = FatigueAnalyzer(self._provider)
        self._muscle_analyzer = MuscleAnalyzer(self._provider)
        self._goal_tracker = GoalTracker(self._provider)
        self.invalidate_cache()

    def invalidate_cache(self, key: str | None = None) -> None:
        """Invalidate AnalysisCache entries. Pass a key to invalidate one, or None for all."""
        if not self._cache:
            return
        if key:
            self._cache.invalidate(key)
        else:
            self._cache.clear()

    def evaluate_rules(self, max_recommendations: int = 20) -> list[Recommendation]:
        return self._rule_engine.evaluate(self._provider, max_recommendations=max_recommendations)
