"""Typed domain event models for the GymOS event platform."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from shared.events.event import DomainEvent


# ─── Workout Events ─────────────────────────────────────────

@dataclass
class WorkoutStarted(DomainEvent):
    workout_id: str = ""
    program_name: str = ""
    day_name: str = ""
    started_at: Optional[datetime] = None
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
    rir: Optional[float] = None
    rpe: Optional[float] = None
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
    change_from_last: Optional[float] = None
    source: str = "workout"


# ─── PR Events ──────────────────────────────────────────────

@dataclass
class PersonalRecordUnlocked(DomainEvent):
    exercise_id: str = ""
    exercise_name: str = ""
    pr_type: str = ""
    value: float = 0.0
    previous_value: Optional[float] = None
    unit: str = "kg"
    source: str = "pr_engine"


# ─── Recovery Events ────────────────────────────────────────

@dataclass
class RecoveryScoreUpdated(DomainEvent):
    score: float = 0.0
    flags: list[str] = field(default_factory=list)
    session_id: str = ""
    source: str = "recovery_engine"


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


# ─── GymBrain Events ────────────────────────────────────────

@dataclass
class RecommendationsUpdated(DomainEvent):
    triggered_by: str = ""
    recommendation_count: int = 0
    recommendations: list[dict] = field(default_factory=list)
    source: str = "gymbrain"


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
    "MealLogged": MealLogged,
    "NutritionUpdated": NutritionUpdated,
    "MacroTargetChanged": MacroTargetChanged,
    "ExerciseKnowledgeUpdated": ExerciseKnowledgeUpdated,
    "RecommendationsUpdated": RecommendationsUpdated,
}


def event_from_dict(data: dict) -> DomainEvent:
    event_name = data.get("event_name", "")
    cls = DOMAIN_EVENT_REGISTRY.get(event_name)
    if cls is None:
        raise ValueError(f"Unknown domain event: {event_name}")
    return cls.from_dict(data)
