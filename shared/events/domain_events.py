"""Typed domain event models for the GymOS event platform."""

from dataclasses import dataclass, field
from datetime import datetime

from shared.adaptive_programming.events import (
    AdaptationApplied as AdAdaptationApplied,
)
from shared.adaptive_programming.events import (
    ContextUpdated as AdContextUpdated,
)
from shared.adaptive_programming.events import (
    DecisionApproved as AdDecisionApproved,
)
from shared.adaptive_programming.events import (
    DecisionRejected as AdDecisionRejected,
)
from shared.adaptive_programming.events import (
    DecisionRolledBack as AdDecisionRolledBack,
)
from shared.adaptive_programming.events import (
    RecommendationGenerated as AdRecommendationGenerated,
)
from shared.adaptive_programming.events import (
    ScenarioSimulated as AdScenarioSimulated,
)
from shared.adaptive_programming.events import (
    StrategyPhaseChanged as AdStrategyPhaseChanged,
)
from shared.events.event import DomainEvent
from shared.knowledge_evolution.events import (
    ConfidenceUpdated as KevConfidenceUpdated,
)
from shared.knowledge_evolution.events import (
    ConflictDetected as KevConflictDetected,
)
from shared.knowledge_evolution.events import (
    ConflictResolved as KevConflictResolved,
)
from shared.knowledge_evolution.events import (
    EvidenceCollected as KevEvidenceCollected,
)
from shared.knowledge_evolution.events import (
    KnowledgeDeprecated as KevKnowledgeDeprecated,
)
from shared.knowledge_evolution.events import (
    KnowledgeRevised as KevKnowledgeRevised,
)
from shared.knowledge_evolution.events import (
    KnowledgeVersionPublished as KevKnowledgeVersionPublished,
)
from shared.knowledge_evolution.events import (
    SnapshotCreated as KevSnapshotCreated,
)
from shared.optimization_knowledge.events import (
    ExperienceRecorded as OptKnowledgeExperienceRecorded,
)
from shared.optimization_knowledge.events import (
    InsightGenerated as OptKnowledgeInsightGenerated,
)
from shared.optimization_knowledge.events import (
    KnowledgeVersioned as OptKnowledgeKnowledgeVersioned,
)
from shared.optimization_knowledge.events import (
    PatternMined as OptKnowledgePatternMined,
)
from shared.optimization_knowledge.events import (
    RuleDerived as OptKnowledgeRuleDerived,
)
from shared.optimization_knowledge.events import (
    StatisticsUpdated as OptKnowledgeStatisticsUpdated,
)

# ─── Workout Events ─────────────────────────────────────────

@dataclass
class WorkoutStarted(DomainEvent):
    workout_id: str = ""
    program_name: str = ""
    day_name: str = ""
    started_at: datetime | None = None
    source: str = "workout"


@dataclass
class WorkoutCompleted(DomainEvent):
    workout_id: str = ""
    program_name: str = ""
    day_name: str = ""
    duration_minutes: float = 0.0
    total_volume_kg: float = 0.0
    exercise_count: int = 0
    total_sets: int = 0
    source: str = "workout"


@dataclass
class ExerciseCompleted(DomainEvent):
    workout_id: str = ""
    exercise_id: str = ""
    exercise_name: str = ""
    sets_completed: int = 0
    total_reps: int = 0
    total_volume_kg: float = 0.0
    source: str = "workout"


@dataclass
class SetCompleted(DomainEvent):
    workout_id: str = ""
    exercise_id: str = ""
    exercise_name: str = ""
    set_number: int = 0
    reps: int = 0
    weight_kg: float = 0.0
    rir: float | None = None
    rpe: float | None = None
    source: str = "workout"


# ─── Program Events ─────────────────────────────────────────

@dataclass
class ProgramImported(DomainEvent):
    program_name: str = ""
    version: str = ""
    source_file: str = ""
    day_count: int = 0
    exercise_count: int = 0
    source: str = "workout_program"


@dataclass
class ProgramActivated(DomainEvent):
    program_name: str = ""
    version: str = ""
    previous_program: str = ""
    source: str = "workout_program"


# ─── Body Weight Events ─────────────────────────────────────

@dataclass
class BodyWeightUpdated(DomainEvent):
    weight_kg: float = 0.0
    date: str = ""
    change_from_last: float | None = None
    source: str = "workout"


# ─── PR Events ──────────────────────────────────────────────

@dataclass
class PersonalRecordUnlocked(DomainEvent):
    exercise_id: str = ""
    exercise_name: str = ""
    pr_type: str = ""
    value: float = 0.0
    previous_value: float | None = None
    unit: str = "kg"
    source: str = "pr_engine"


# ─── Recovery Events ────────────────────────────────────────

@dataclass
class RecoveryScoreUpdated(DomainEvent):
    score: float = 0.0
    flags: list[str] = field(default_factory=list)
    session_id: str = ""
    source: str = "recovery_engine"


@dataclass
class RecoveryUpdated(DomainEvent):
    """Published when any recovery data changes."""
    date: str = ""
    update_type: str = ""  # "score", "sleep", "stress", "session", "all"
    recovery_score: float = 0.0
    source: str = "recovery"


@dataclass
class RecoveryScoreChanged(DomainEvent):
    """Published when the recovery score changes significantly."""
    date: str = ""
    previous_score: float = 0.0
    new_score: float = 0.0
    change: float = 0.0
    source: str = "recovery"


@dataclass
class ReadinessChanged(DomainEvent):
    """Published when training readiness level changes."""
    date: str = ""
    previous_level: str = ""
    new_level: str = ""
    readiness_score: float = 0.0
    source: str = "recovery"


@dataclass
class DeloadRecommended(DomainEvent):
    """Published when a deload is recommended."""
    reason: str = ""
    start_date: str = ""
    end_date: str = ""
    weeks_since_last_deload: int = 0
    source: str = "recovery"


# ─── Nutrition Events ──────────────────────────────────────

@dataclass
class MealLogged(DomainEvent):
    meal_name: str = ""
    calories: float = 0.0
    protein_g: float = 0.0
    carbs_g: float = 0.0
    fat_g: float = 0.0
    date: str = ""
    source: str = "nutrition"


@dataclass
class NutritionUpdated(DomainEvent):
    """Published when any nutrition data changes."""
    date: str = ""
    update_type: str = ""  # "meal", "hydration", "import", "all"
    entries_count: int = 0
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


# ─── Knowledge Events ───────────────────────────────────────

@dataclass
class ExerciseKnowledgeUpdated(DomainEvent):
    exercise_id: str = ""
    exercise_name: str = ""
    version: str = ""
    changed_fields: list[str] = field(default_factory=list)
    source: str = "knowledge"


# ─── Prediction Events ──────────────────────────────────────

@dataclass
class PredictionUpdated(DomainEvent):
    prediction_type: str = ""
    window: str = ""
    value: float = 0.0
    probability: float = 0.0
    confidence_score: float = 0.0
    summary: str = ""
    source: str = "prediction"


@dataclass
class PlateauPredicted(DomainEvent):
    probability: float = 0.0
    primary_factors: list[str] = field(default_factory=list)
    window: str = ""
    source: str = "prediction"


@dataclass
class GoalEtaChanged(DomainEvent):
    previous_eta_days: float = 0.0
    new_eta_days: float = 0.0
    change_days: float = 0.0
    source: str = "prediction"


@dataclass
class DeloadForecastUpdated(DomainEvent):
    deload_probability: float = 0.0
    recommended_window: str = ""
    primary_reason: str = ""
    source: str = "prediction"


@dataclass
class PredictionModelUpdated(DomainEvent):
    model_name: str = ""
    model_version: str = ""
    metrics: dict = field(default_factory=dict)
    source: str = "prediction"


# ─── GymBrain Events ────────────────────────────────────────

@dataclass
class RecommendationsUpdated(DomainEvent):
    triggered_by: str = ""
    recommendation_count: int = 0
    recommendations: list[dict] = field(default_factory=list)
    source: str = "gymbrain"


# ─── Planning Events ────────────────────────────────────────

@dataclass
class MacrocycleGenerated(DomainEvent):
    macrocycle_id: str = ""
    duration_weeks: int = 0
    mesocycle_count: int = 0
    total_sessions: int = 0
    source: str = "planning"


@dataclass
class MesocycleGenerated(DomainEvent):
    mesocycle_id: str = ""
    macrocycle_id: str = ""
    goal: str = ""
    focus: str = ""
    week_count: int = 0
    source: str = "planning"


@dataclass
class WeekPlanGenerated(DomainEvent):
    week_number: int = 0
    macrocycle_id: str = ""
    session_count: int = 0
    total_sets: int = 0
    is_deload: bool = False
    source: str = "planning"


@dataclass
class SessionPlanGenerated(DomainEvent):
    session_id: str = ""
    week_number: int = 0
    day_type: str = ""
    exercise_count: int = 0
    total_sets: int = 0
    estimated_duration: int = 0
    source: str = "planning"


@dataclass
class PlanActivated(DomainEvent):
    macrocycle_id: str = ""
    name: str = ""
    duration_weeks: int = 0
    source: str = "planning"


@dataclass
class PlanProgressed(DomainEvent):
    macrocycle_id: str = ""
    week_completed: int = 0
    sessions_completed: int = 0
    adherence_rate: float = 0.0
    completion_percent: float = 0.0
    source: str = "planning"


@dataclass
class PlanModified(DomainEvent):
    macrocycle_id: str = ""
    modification_type: str = ""
    description: str = ""
    source: str = "planning"


@dataclass
class PlanCompleted(DomainEvent):
    macrocycle_id: str = ""
    name: str = ""
    total_sessions_completed: int = 0
    adherence_rate: float = 0.0
    source: str = "planning"


@dataclass
class DeloadWeekGenerated(DomainEvent):
    macrocycle_id: str = ""
    week_number: int = 0
    reason: str = ""
    weeks_since_last_deload: int = 0
    source: str = "planning"


@dataclass
class VolumeAllocationAdjusted(DomainEvent):
    session_id: str = ""
    previous_sets: int = 0
    new_sets: int = 0
    reason: str = ""
    source: str = "planning"


# ─── Planning Optimizer Events ──────────────────────────────

@dataclass
class OptimizationRequested(DomainEvent):
    source: str = "planning_optimizer"
    request_id: str = ""
    objectives_count: int = 0
    constraints_count: int = 0
    population_size: int = 0


@dataclass
class OptimizationStarted(DomainEvent):
    source: str = "planning_optimizer"
    request_id: str = ""
    total_iterations: int = 0


@dataclass
class CandidateGenerated(DomainEvent):
    source: str = "planning_optimizer"
    request_id: str = ""
    candidate_id: str = ""
    generation: int = 0
    population_size: int = 0


@dataclass
class CandidateEvaluated(DomainEvent):
    source: str = "planning_optimizer"
    request_id: str = ""
    candidate_id: str = ""
    overall_score: float = 0.0
    is_feasible: bool = True


@dataclass
class GenerationCompleted(DomainEvent):
    source: str = "planning_optimizer"
    request_id: str = ""
    generation: int = 0
    best_score: float = 0.0
    average_score: float = 0.0
    feasible_count: int = 0


@dataclass
class OptimizationCompleted(DomainEvent):
    source: str = "planning_optimizer"
    request_id: str = ""
    best_score: float = 0.0
    total_generations: int = 0
    total_evaluated: int = 0
    feasible_count: int = 0


@dataclass
class OptimizationFailed(DomainEvent):
    source: str = "planning_optimizer"
    request_id: str = ""
    reason: str = ""


@dataclass
class OptimizationConstraintViolated(DomainEvent):
    source: str = "planning_optimizer"
    request_id: str = ""
    candidate_id: str = ""
    constraint_type: str = ""
    violation_detail: str = ""


# ─── Event Registry ─────────────────────────────────────────

DOMAIN_EVENT_REGISTRY: dict[str, type[DomainEvent]] = {
    "WorkoutStarted": WorkoutStarted,
    "WorkoutCompleted": WorkoutCompleted,
    "ExerciseCompleted": ExerciseCompleted,
    "SetCompleted": SetCompleted,
    "ProgramImported": ProgramImported,
    "ProgramActivated": ProgramActivated,
    "BodyWeightUpdated": BodyWeightUpdated,
    "PersonalRecordUnlocked": PersonalRecordUnlocked,
    "RecoveryScoreUpdated": RecoveryScoreUpdated,
    "RecoveryUpdated": RecoveryUpdated,
    "RecoveryScoreChanged": RecoveryScoreChanged,
    "ReadinessChanged": ReadinessChanged,
    "DeloadRecommended": DeloadRecommended,
    "MealLogged": MealLogged,
    "NutritionUpdated": NutritionUpdated,
    "MacroTargetChanged": MacroTargetChanged,
    "ExerciseKnowledgeUpdated": ExerciseKnowledgeUpdated,
    "RecommendationsUpdated": RecommendationsUpdated,
    "PredictionUpdated": PredictionUpdated,
    "PlateauPredicted": PlateauPredicted,
    "GoalEtaChanged": GoalEtaChanged,
    "DeloadForecastUpdated": DeloadForecastUpdated,
    "PredictionModelUpdated": PredictionModelUpdated,
    # Planning Engine events
    "MacrocycleGenerated": MacrocycleGenerated,
    "MesocycleGenerated": MesocycleGenerated,
    "WeekPlanGenerated": WeekPlanGenerated,
    "SessionPlanGenerated": SessionPlanGenerated,
    "PlanActivated": PlanActivated,
    "PlanProgressed": PlanProgressed,
    "PlanModified": PlanModified,
    "PlanCompleted": PlanCompleted,
    "DeloadWeekGenerated": DeloadWeekGenerated,
    "VolumeAllocationAdjusted": VolumeAllocationAdjusted,
    # Planning Optimizer events
    "OptimizationRequested": OptimizationRequested,
    "OptimizationStarted": OptimizationStarted,
    "CandidateGenerated": CandidateGenerated,
    "CandidateEvaluated": CandidateEvaluated,
    "GenerationCompleted": GenerationCompleted,
    "OptimizationCompleted": OptimizationCompleted,
    "OptimizationFailed": OptimizationFailed,
    "OptimizationConstraintViolated": OptimizationConstraintViolated,
    # Optimization Knowledge events
    "ExperienceRecorded": OptKnowledgeExperienceRecorded,
    "PatternMined": OptKnowledgePatternMined,
    "StatisticsUpdated": OptKnowledgeStatisticsUpdated,
    "InsightGenerated": OptKnowledgeInsightGenerated,
    "RuleDerived": OptKnowledgeRuleDerived,
    "KnowledgeVersioned": OptKnowledgeKnowledgeVersioned,
    # Knowledge Evolution events
    "EvidenceCollected": KevEvidenceCollected,
    "ConfidenceUpdated": KevConfidenceUpdated,
    "ConflictDetected": KevConflictDetected,
    "ConflictResolved": KevConflictResolved,
    "KnowledgeRevised": KevKnowledgeRevised,
    "KnowledgeDeprecated": KevKnowledgeDeprecated,
    "KnowledgeVersionPublished": KevKnowledgeVersionPublished,
    "SnapshotCreated": KevSnapshotCreated,
    # Adaptive Programming events
    "ContextUpdated": AdContextUpdated,
    "RecommendationGenerated": AdRecommendationGenerated,
    "DecisionApproved": AdDecisionApproved,
    "DecisionRejected": AdDecisionRejected,
    "DecisionRolledBack": AdDecisionRolledBack,
    "AdaptationApplied": AdAdaptationApplied,
    "StrategyPhaseChanged": AdStrategyPhaseChanged,
    "ScenarioSimulated": AdScenarioSimulated,
}


def event_from_dict(data: dict) -> DomainEvent:
    event_name = data.get("event_name", "")
    cls = DOMAIN_EVENT_REGISTRY.get(event_name)
    if cls is None:
        raise ValueError(f"Unknown domain event: {event_name}")
    return cls.from_dict(data)
