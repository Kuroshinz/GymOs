"""Planning Engine — deterministic periodization pipeline for GymOS.

Planning is the single source of truth for every future program.
Workout generation no longer produces workouts directly — it consumes
plans produced by this engine.

Usage:
    from shared.planning import (
        PlanningOrchestrator, PlanningEngine, AllocationEngine,
        PlanningValidator, PlanningMetricsScorer, PlanningReports,
        PlanningRepository, PlanningSerializer, PlanningHistory,
    )

    orch = PlanningOrchestrator()
    output = orch.generate_plan(
        duration_weeks=24,
        goal="hypertrophy",
        sessions_per_week=5,
    )
    print(output.validation)
    print(orch.report())
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from shared.planning.allocation import AllocationEngine, VolumeDistribution
from shared.planning.domain import (
    CyclePhase,
    DayType,
    ExerciseAllocation,
    FatigueBudget,
    IntensityDomain,
    Macrocycle,
    Mesocycle,
    MesocycleGoal,
    Microcycle,
    NutritionBudget,
    PlanningConfig,
    PlanningState,
    PlanProgress,
    ProgressionModel,
    RecoveryBudget,
    SessionPlan,
    SplitStyle,
    TrainingFocus,
    VolumeAllocation,
    WeekPlan,
)
from shared.planning.engine import PlanningEngine, PlanningOutput

# Re-export all event types
from shared.planning.events import (
    PLANNING_EVENT_REGISTRY,
    DeloadWeekGenerated,
    MacrocycleGenerated,
    MesocycleGenerated,
    PlanActivated,
    PlanCompleted,
    PlanModified,
    PlanProgressed,
    SessionPlanGenerated,
    VolumeAllocationAdjusted,
    WeekPlanGenerated,
)
from shared.planning.history import PlanningHistory
from shared.planning.metrics import (
    AdherencePrediction,
    FatigueBalance,
    PlanningMetrics,
    PlanningMetricsScorer,
    PlanQuality,
    RecoveryBalance,
    ScientificScore,
    SpecificityScore,
)
from shared.planning.reports import PlanningReports
from shared.planning.repository import PlanningRepository
from shared.planning.serializer import PlanningSerializer
from shared.planning.validator import (
    ConstraintValidator,
    FrequencyValidator,
    PlanningValidator,
    RecoveryValidator,
    ScientificValidator,
    ValidationError,
    ValidationResult,
    VolumeValidator,
)


@dataclass
class PlanningOrchestrator:
    """Unified entry point for all planning operations.

    Provides a single facade over the Planning Engine, Allocation Engine,
    Validator, Metrics Scorer, Reports, Repository, Serializer, and History.
    """

    engine: PlanningEngine = field(default_factory=PlanningEngine)
    allocation: AllocationEngine = field(default_factory=AllocationEngine)
    validator: PlanningValidator = field(default_factory=PlanningValidator)
    scorer: PlanningMetricsScorer = field(default_factory=PlanningMetricsScorer)
    repository: PlanningRepository = field(default_factory=PlanningRepository)
    serializer: PlanningSerializer = field(default_factory=PlanningSerializer)
    history: PlanningHistory = field(default_factory=PlanningHistory)
    reports: PlanningReports = field(default_factory=PlanningReports)

    # ── Plan Generation ────────────────────────────────────────

    def generate_plan(
        self,
        duration_weeks: int = 24,
        goal: str = "hypertrophy",
        sessions_per_week: int = 5,
        split_style: str = "ppl_ul",
        start_date: str | None = None,
        name: str = "",
    ) -> PlanningOutput:
        output = self.engine.generate_macrocycle(
            duration_weeks=duration_weeks,
            goal=goal,
            sessions_per_week=sessions_per_week,
            split_style=split_style,
            start_date=start_date,
            name=name,
        )
        self.repository.save_macrocycle(output.macrocycle)
        self.history.record_snapshot(output.macrocycle, "Initial generation")
        return output

    def generate_from_intent(self, intent_config: dict[str, Any]) -> PlanningOutput:
        from shared.intent import IntentBuilder
        intent = IntentBuilder.build(intent_config)
        sessions = intent.timeline.sessions_per_week
        goal = IntentBuilder._build_goals(
            intent_config.get("goals", [])
        )
        goal_str = goal[0].goal_type.value if goal else "hypertrophy"
        duration = 24
        if goal[0].target_date:
            try:
                from datetime import date
                start = date.today()
                target = date.fromisoformat(goal[0].target_date)
                days = (target - start).days
                duration = max(4, days // 7)
            except (ValueError, TypeError):
                pass
        training = intent.training
        split = training.style.value if training.style else "ppl_ul"
        return self.generate_plan(
            duration_weeks=duration,
            goal=goal_str,
            sessions_per_week=sessions,
            split_style=split,
            name=f"{goal_str.capitalize()} Plan",
        )

    # ── Plan Management ────────────────────────────────────────

    def activate_plan(self, macrocycle_id: str) -> bool:
        result = self.repository.set_active_macrocycle(macrocycle_id)
        return result

    def get_active_plan(self) -> Macrocycle | None:
        return self.repository.get_active_macrocycle()

    def get_plan(self, macrocycle_id: str) -> Macrocycle | None:
        return self.repository.find_macrocycle(macrocycle_id)

    def list_plans(self) -> list[Macrocycle]:
        return self.repository.list_macrocycles()

    def delete_plan(self, macrocycle_id: str) -> bool:
        return self.repository.delete_macrocycle(macrocycle_id)

    def clear_all(self) -> None:
        self.repository.clear()
        self.history.clear()

    # ── Progress Tracking ──────────────────────────────────────

    def get_progress(self, macrocycle_id: str) -> PlanProgress | None:
        return self.repository.find_progress(macrocycle_id)

    def update_progress(
        self,
        macrocycle_id: str,
        weeks_completed: int = 0,
        sessions_completed: int = 0,
        adherence_rate: float = 0.0,
    ) -> PlanProgress | None:
        macro = self.repository.find_macrocycle(macrocycle_id)
        if macro is None:
            return None
        progress = PlanProgress(
            current_macrocycle=macro,
            weeks_completed=weeks_completed,
            sessions_completed=sessions_completed,
            total_weeks=macro.total_weeks,
            total_sessions=macro.total_sessions,
            adherence_rate=adherence_rate,
            is_complete=weeks_completed >= macro.total_weeks,
        )
        self.repository.save_progress(macrocycle_id, progress)
        self.history.record_adherence(macrocycle_id, adherence_rate)
        return progress

    def complete_plan(self, macrocycle_id: str) -> PlanProgress | None:
        macro = self.repository.find_macrocycle(macrocycle_id)
        if macro is None:
            return None
        existing = self.repository.find_progress(macrocycle_id)
        progress = PlanProgress(
            current_macrocycle=macro,
            weeks_completed=macro.total_weeks,
            sessions_completed=macro.total_sessions,
            total_weeks=macro.total_weeks,
            total_sessions=macro.total_sessions,
            adherence_rate=existing.adherence_rate if existing else 0.0,
            is_complete=True,
        )
        self.repository.save_progress(macrocycle_id, progress)
        self.history.mark_completed(macrocycle_id)
        return progress

    # ── Quality & Validation ───────────────────────────────────

    def score_plan(self, macrocycle: Macrocycle | None = None) -> PlanQuality:
        if macrocycle is None:
            macrocycle = self.repository.get_active_macrocycle()
        if macrocycle is None:
            return PlanQuality()
        return self.scorer.score_plan_quality(macrocycle)

    def validate_plan(self, macrocycle: Macrocycle | None = None) -> ValidationResult:
        if macrocycle is None:
            macrocycle = self.repository.get_active_macrocycle()
        if macrocycle is None:
            return ValidationResult(is_valid=False)
        return self.validator.validate(macrocycle)

    def get_metrics(self) -> PlanningMetrics:
        plans = self.repository.list_macrocycles()
        return PlanningMetrics.compute(plans, self.validator)

    # ── Reporting ──────────────────────────────────────────────

    def report(self, macrocycle_id: str | None = None) -> str:
        if macrocycle_id:
            macro = self.repository.find_macrocycle(macrocycle_id)
        else:
            macro = self.repository.get_active_macrocycle()
        if macro is None:
            return "No plan available."
        quality = self.scorer.score_plan_quality(macro)
        return self.reports.generate_plan_report(macro, quality)

    def validation_report(self, macrocycle_id: str | None = None) -> str:
        if macrocycle_id:
            macro = self.repository.find_macrocycle(macrocycle_id)
        else:
            macro = self.repository.get_active_macrocycle()
        if macro is None:
            return "No plan available."
        validation = self.validator.validate(macro)
        return self.reports.generate_validation_report(macro, validation)

    def summary_report(self, macrocycle_id: str | None = None) -> str:
        if macrocycle_id:
            macro = self.repository.find_macrocycle(macrocycle_id)
        else:
            macro = self.repository.get_active_macrocycle()
        if macro is None:
            return "No plan available."
        return self.reports.generate_summary_report(macro)

    def weekly_overview(self, week_number: int, macrocycle_id: str | None = None) -> str:
        if macrocycle_id:
            macro = self.repository.find_macrocycle(macrocycle_id)
        else:
            macro = self.repository.get_active_macrocycle()
        if macro is None:
            return "No plan available."
        return self.reports.generate_weekly_overview(macro, week_number)

    def metrics_report(self) -> str:
        metrics = self.get_metrics()
        return self.reports.generate_metrics_report(metrics)

    def comparison_report(self, plan_ids: list[str] | None = None) -> str:
        if plan_ids:
            plans = [p for p in self.repository.list_macrocycles()
                     if p.macrocycle_id in plan_ids]
        else:
            plans = self.repository.list_macrocycles()
        return self.reports.generate_comparison_report(plans, self.validator)

    # ── History ────────────────────────────────────────────────

    def get_history(self, macrocycle_id: str):
        return self.history.get_snapshots(macrocycle_id)

    def get_changes(self, macrocycle_id: str):
        return self.history.get_changes(macrocycle_id)

    def get_history_entry(self, macrocycle_id: str):
        return self.history.get_entry(macrocycle_id)

    def list_history(self):
        return self.history.list_entries()

    # ── Serialization ──────────────────────────────────────────

    def to_dict(self, macrocycle: Macrocycle | None = None) -> dict:
        if macrocycle is None:
            macrocycle = self.repository.get_active_macrocycle()
        if macrocycle is None:
            return {}
        return self.serializer.macrocycle_to_dict(macrocycle)

    def to_json(self, macrocycle: Macrocycle | None = None, indent: int = 2) -> str:
        if macrocycle is None:
            macrocycle = self.repository.get_active_macrocycle()
        if macrocycle is None:
            return "{}"
        return self.serializer.macrocycle_to_json(macrocycle, indent=indent)

    def from_dict(self, data: dict) -> Macrocycle:
        macro = self.serializer.macrocycle_from_dict(data)
        self.repository.save_macrocycle(macro)
        return macro

    def from_json(self, json_str: str) -> Macrocycle:
        macro = self.serializer.macrocycle_from_json(json_str)
        self.repository.save_macrocycle(macro)
        return macro

    # ── State ──────────────────────────────────────────────────

    def get_state(self) -> PlanningState:
        return self.repository.get_state()

    # ── Integration helpers ────────────────────────────────────

    def get_volume_distribution(self, macrocycle: Macrocycle | None = None) -> VolumeDistribution:
        if macrocycle is None:
            macrocycle = self.repository.get_active_macrocycle()
        if macrocycle is None:
            return VolumeDistribution()
        return self.allocation.compute_volume_distribution(macrocycle)


__all__ = (
    # Orchestrator
    "PlanningOrchestrator",
    # Engine
    "PlanningEngine",
    "PlanningOutput",
    # Allocation
    "AllocationEngine",
    "VolumeDistribution",
    # Validators
    "PlanningValidator",
    "ScientificValidator",
    "VolumeValidator",
    "RecoveryValidator",
    "FrequencyValidator",
    "ConstraintValidator",
    "ValidationResult",
    "ValidationError",
    # Metrics
    "PlanningMetricsScorer",
    "PlanningMetrics",
    "PlanQuality",
    "ScientificScore",
    "RecoveryBalance",
    "FatigueBalance",
    "SpecificityScore",
    "AdherencePrediction",
    # Domain
    "Macrocycle",
    "Mesocycle",
    "Microcycle",
    "WeekPlan",
    "SessionPlan",
    "ExerciseAllocation",
    "VolumeAllocation",
    "FatigueBudget",
    "RecoveryBudget",
    "NutritionBudget",
    "PlanProgress",
    "PlanningState",
    "PlanningConfig",
    # Enums
    "CyclePhase",
    "TrainingFocus",
    "DayType",
    "ProgressionModel",
    "SplitStyle",
    "IntensityDomain",
    "MesocycleGoal",
    # Reports
    "PlanningReports",
    # Repository
    "PlanningRepository",
    # Serializer
    "PlanningSerializer",
    # History
    "PlanningHistory",
    # Events
    "PLANNING_EVENT_REGISTRY",
    "MacrocycleGenerated",
    "MesocycleGenerated",
    "WeekPlanGenerated",
    "SessionPlanGenerated",
    "PlanActivated",
    "PlanProgressed",
    "PlanModified",
    "PlanCompleted",
    "DeloadWeekGenerated",
    "VolumeAllocationAdjusted",
)
