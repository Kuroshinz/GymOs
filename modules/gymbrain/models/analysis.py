from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class FatigueLevel(Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"


class PlateauType(Enum):
    WEIGHT = "weight"
    REP = "rep"
    VOLUME = "volume"
    STRENGTH = "strength"
    BODYWEIGHT = "bodyweight"
    TIME = "time"


class MuscleStatus(Enum):
    LOW = "low"
    BUILDING = "building"
    OPTIMAL = "optimal"
    MAINTENANCE = "maintenance"
    HIGH = "high"


@dataclass
class FatigueResult:
    level: FatigueLevel = FatigueLevel.LOW
    score: float = 0.0
    explanation: str = ""
    factors: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)

    def to_dict(self: FatigueResult) -> dict[str, Any]:
        return {
            "level": self.level.value,
            "score": self.score,
            "explanation": self.explanation,
            "factors": self.factors,
            "recommendations": self.recommendations,
        }


@dataclass
class PlateauResult:
    plateau_type: PlateauType = PlateauType.WEIGHT
    detected: bool = False
    duration_days: int = 0
    severity: str = "none"
    exercise_name: str = ""
    current_value: float = 0.0
    previous_best: float = 0.0
    explanation: str = ""
    suggested_action: str = ""

    def to_dict(self: PlateauResult) -> dict[str, Any]:
        return {
            "plateau_type": self.plateau_type.value,
            "detected": self.detected,
            "duration_days": self.duration_days,
            "severity": self.severity,
            "exercise_name": self.exercise_name,
            "current_value": self.current_value,
            "previous_best": self.previous_best,
            "explanation": self.explanation,
            "suggested_action": self.suggested_action,
        }


@dataclass
class MuscleAnalysisResult:
    muscle_id: str = ""
    display_name: str = ""
    current_sets: float = 0.0
    recommended_min_sets: float = 0.0
    recommended_max_sets: float = 0.0
    status: MuscleStatus = MuscleStatus.OPTIMAL
    progress: str = ""
    weakness: str = ""
    suggested_exercises: list[str] = field(default_factory=list)
    weekly_frequency: int = 0
    recommended_frequency: str = ""
    recovery_status: str = ""

    def to_dict(self: MuscleAnalysisResult) -> dict[str, Any]:
        return {
            "muscle_id": self.muscle_id,
            "display_name": self.display_name,
            "current_sets": self.current_sets,
            "recommended_min_sets": self.recommended_min_sets,
            "recommended_max_sets": self.recommended_max_sets,
            "status": self.status.value,
            "progress": self.progress,
            "weakness": self.weakness,
            "suggested_exercises": self.suggested_exercises,
            "weekly_frequency": self.weekly_frequency,
            "recommended_frequency": self.recommended_frequency,
            "recovery_status": self.recovery_status,
        }


@dataclass
class GoalProgress:
    current_weight_kg: float = 0.0
    goal_weight_kg: float = 0.0
    weekly_gain_rate: float = 0.0
    estimated_completion_weeks: float = 0.0
    estimated_completion_date: str = ""
    lean_bulk_quality: str = ""
    bodyweight_trend: str = ""
    progress_score: float = 0.0
    target_calorie_surplus: int = 0
    weeks_of_data: int = 0

    def to_dict(self: GoalProgress) -> dict[str, Any]:
        return {
            "current_weight_kg": self.current_weight_kg,
            "goal_weight_kg": self.goal_weight_kg,
            "weekly_gain_rate": self.weekly_gain_rate,
            "estimated_completion_weeks": self.estimated_completion_weeks,
            "estimated_completion_date": self.estimated_completion_date,
            "lean_bulk_quality": self.lean_bulk_quality,
            "bodyweight_trend": self.bodyweight_trend,
            "progress_score": self.progress_score,
            "target_calorie_surplus": self.target_calorie_surplus,
            "weeks_of_data": self.weeks_of_data,
        }


@dataclass
class WeeklyReview:
    week_label: str = ""
    total_workouts: int = 0
    total_sets: int = 0
    total_volume_kg: float = 0.0
    best_pr: str = ""
    most_improved_muscle: str = ""
    lowest_volume_muscle: str = ""
    missed_sessions: int = 0
    recovery_score: str = ""
    bodyweight_change: float = 0.0
    next_week_priorities: list[str] = field(default_factory=list)
    fatigue_level: str = ""
    recommendations_count: int = 0

    def to_dict(self: WeeklyReview) -> dict[str, Any]:
        return {
            "week_label": self.week_label,
            "total_workouts": self.total_workouts,
            "total_sets": self.total_sets,
            "total_volume_kg": self.total_volume_kg,
            "best_pr": self.best_pr,
            "most_improved_muscle": self.most_improved_muscle,
            "lowest_volume_muscle": self.lowest_volume_muscle,
            "missed_sessions": self.missed_sessions,
            "recovery_score": self.recovery_score,
            "bodyweight_change": self.bodyweight_change,
            "next_week_priorities": self.next_week_priorities,
            "fatigue_level": self.fatigue_level,
            "recommendations_count": self.recommendations_count,
        }
