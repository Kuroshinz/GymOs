from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class TrainingStyle(Enum):
    PPL_UL = "ppl_ul"
    PUSH_PULL_LEGS = "push_pull_legs"
    FULL_BODY = "full_body"
    UPPER_LOWER = "upper_lower"
    BRO_SPLIT = "bro_split"

    @property
    def label(self) -> str:
        return {
            TrainingStyle.PPL_UL: "PPL-UL",
            TrainingStyle.PUSH_PULL_LEGS: "Push/Pull/Legs",
            TrainingStyle.FULL_BODY: "Full Body",
            TrainingStyle.UPPER_LOWER: "Upper/Lower",
            TrainingStyle.BRO_SPLIT: "Bro Split",
        }[self]


class NutritionApproach(Enum):
    LEAN_BULK = "lean_bulk"
    MAINTENANCE = "maintenance"
    CUT = "cut"
    REVERSE_DIET = "reverse_diet"

    @property
    def label(self) -> str:
        return {
            NutritionApproach.LEAN_BULK: "Lean Bulk",
            NutritionApproach.MAINTENANCE: "Maintenance",
            NutritionApproach.CUT: "Cut",
            NutritionApproach.REVERSE_DIET: "Reverse Diet",
        }[self]


class RecoveryPriority(Enum):
    MAXIMIZE_PERFORMANCE = "maximize_performance"
    BALANCE_LIFESTYLE = "balance_lifestyle"
    MINIMIZE_EFFORT = "minimize_effort"

    @property
    def label(self) -> str:
        return {
            RecoveryPriority.MAXIMIZE_PERFORMANCE: "Maximize Performance",
            RecoveryPriority.BALANCE_LIFESTYLE: "Balance Lifestyle",
            RecoveryPriority.MINIMIZE_EFFORT: "Minimize Effort",
        }[self]


class RiskLevel(Enum):
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"

    @property
    def label(self) -> str:
        return {
            RiskLevel.CONSERVATIVE: "Conservative",
            RiskLevel.MODERATE: "Moderate",
            RiskLevel.AGGRESSIVE: "Aggressive",
        }[self]


class ConstraintType(Enum):
    TIME = "time"
    EQUIPMENT = "equipment"
    HEALTH = "health"
    LIFESTYLE = "lifestyle"
    INJURY = "injury"

    @property
    def label(self) -> str:
        return {
            ConstraintType.TIME: "Time",
            ConstraintType.EQUIPMENT: "Equipment",
            ConstraintType.HEALTH: "Health",
            ConstraintType.LIFESTYLE: "Lifestyle",
            ConstraintType.INJURY: "Injury",
        }[self]


class IntentConflictSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IntentStatus(Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    SUPERSEDED = "superseded"
    DRAFT = "draft"


class GoalType(Enum):
    WEIGHT = "weight"
    STRENGTH = "strength"
    HYPERTROPHY = "hypertrophy"
    ENDURANCE = "endurance"
    BODY_COMPOSITION = "body_composition"
    MAINTENANCE = "maintenance"


class EquipmentLevel(Enum):
    NONE = "none"
    MINIMAL = "minimal"
    HOME_GYM = "home_gym"
    COMMERCIAL = "commercial"
    FULL = "full"

    @property
    def label(self) -> str:
        return {
            EquipmentLevel.NONE: "No Equipment",
            EquipmentLevel.MINIMAL: "Minimal (Dumbbells + Band)",
            EquipmentLevel.HOME_GYM: "Home Gym",
            EquipmentLevel.COMMERCIAL: "Commercial Gym",
            EquipmentLevel.FULL: "Full Gym",
        }[self]


class DayPreference(Enum):
    WEEKDAYS = "weekdays"
    WEEKENDS = "weekends"
    EVERYDAY = "everyday"
    CUSTOM = "custom"


class TimeOfDay(Enum):
    MORNING = "morning"
    AFTERNOON = "afternoon"
    EVENING = "evening"
    FLEXIBLE = "flexible"


class AdaptiveScope(Enum):
    VOLUME = "volume"
    EXERCISE_SELECTION = "exercise_selection"
    DELOAD_TIMING = "deload_timing"
    NUTRITION = "nutrition"
    RECOVERY = "recovery"
    ALL = "all"


class IntentDimension(Enum):
    TRAINING = "training"
    NUTRITION = "nutrition"
    RECOVERY = "recovery"
    CONSISTENCY = "consistency"
    LIFESTYLE = "lifestyle"


@dataclass(frozen=True)
class GoalIntent:
    goal_type: GoalType = GoalType.HYPERTROPHY
    target_value: float = 0.0
    current_value: float = 0.0
    unit: str = ""
    target_date: str = ""
    priority: int = 5
    description: str = ""

    @property
    def progress(self) -> float:
        if self.target_value == self.current_value:
            return 1.0
        if self.target_value == 0:
            return 0.0
        return max(0.0, min(1.0, self.current_value / self.target_value))

    @property
    def remaining(self) -> float:
        return max(0.0, self.target_value - self.current_value)


@dataclass(frozen=True)
class Constraint:
    constraint_type: ConstraintType = ConstraintType.TIME
    name: str = ""
    description: str = ""
    severity: str = "medium"
    value: str = ""
    is_active: bool = True


@dataclass(frozen=True)
class Timeline:
    sessions_per_week: int = 5
    session_duration_minutes: int = 60
    preferred_days: list[DayPreference] = field(default_factory=lambda: [DayPreference.EVERYDAY])
    preferred_time: TimeOfDay = TimeOfDay.FLEXIBLE
    available_start_hour: int = 6
    available_end_hour: int = 22

    @property
    def weekly_hours(self) -> float:
        return (self.sessions_per_week * self.session_duration_minutes) / 60.0


@dataclass(frozen=True)
class EquipmentProfile:
    level: EquipmentLevel = EquipmentLevel.COMMERCIAL
    available_items: list[str] = field(default_factory=list)
    missing_items: list[str] = field(default_factory=list)
    home_items: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class LifestyleProfile:
    occupation: str = ""
    occupation_hours_per_week: int = 40
    commute_minutes_per_day: int = 30
    sleep_target_hours: float = 8.0
    sleep_avg_hours: float = 7.0
    stress_level: str = "moderate"
    has_children: bool = False
    social_commitments_per_week: int = 2


@dataclass(frozen=True)
class ComplianceProfile:
    training_compliance_rate: float = 0.85
    nutrition_compliance_rate: float = 0.80
    recovery_compliance_rate: float = 0.70
    streak_days: int = 0
    avg_missed_per_month: float = 2.0
    common_skip_reasons: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class RiskTolerance:
    training_risk: RiskLevel = RiskLevel.MODERATE
    nutrition_risk: RiskLevel = RiskLevel.CONSERVATIVE
    recovery_risk: RiskLevel = RiskLevel.CONSERVATIVE
    overall: RiskLevel = RiskLevel.MODERATE

    def __post_init__(self) -> None:
        levels = [self.training_risk, self.nutrition_risk, self.recovery_risk]
        scores = {"conservative": 1, "moderate": 2, "aggressive": 3}
        avg = sum(scores[r.value] for r in levels) / len(levels)
        if avg >= 2.5:
            object.__setattr__(self, "overall", RiskLevel.AGGRESSIVE)
        elif avg >= 1.5:
            object.__setattr__(self, "overall", RiskLevel.MODERATE)
        else:
            object.__setattr__(self, "overall", RiskLevel.CONSERVATIVE)


@dataclass(frozen=True)
class TrainingPreference:
    style: TrainingStyle = TrainingStyle.PPL_UL
    focus_muscles: list[str] = field(default_factory=lambda: ["shoulders", "upper_chest", "back_width", "arms"])
    priority_muscle_groups: list[str] = field(default_factory=list)
    min_volume_per_muscle: int = 8
    max_volume_per_muscle: int = 22
    prefer_compound_first: bool = True
    warmup_minutes: int = 10
    cardio_minutes_per_week: int = 60
    progression_style: str = "double_progression"
    deload_frequency_weeks: int = 6
    rpe_target_max: float = 9.0
    rir_target_min: float = 0
    rest_minutes_between_sets: int = 2


@dataclass(frozen=True)
class NutritionPreference:
    approach: NutritionApproach = NutritionApproach.LEAN_BULK
    protein_g_per_kg: float = 2.0
    fat_min_g: float = 60.0
    fiber_g: float = 30.0
    meal_count_per_day: int = 4
    prefer_whole_foods: bool = True
    allow_supplements: bool = True
    hydration_ml_per_day: int = 3000
    caffeine_mg_per_day: int = 200
    meal_prep_sunday: bool = True


@dataclass(frozen=True)
class RecoveryPreference:
    priority: RecoveryPriority = RecoveryPriority.BALANCE_LIFESTYLE
    sleep_target: float = 8.0
    sleep_minimum: float = 6.0
    track_hrv: bool = False
    track_soreness: bool = True
    auto_deload: bool = True
    deload_trigger_fatigue: float = 80.0
    recovery_checkin_weekly: bool = True
    stress_management: bool = True


@dataclass(frozen=True)
class AdaptivePreference:
    enabled_scopes: list[AdaptiveScope] = field(default_factory=lambda: [AdaptiveScope.VOLUME, AdaptiveScope.DELOAD_TIMING])
    require_approval: bool = True
    max_change_percent: float = 20.0
    adaptation_speed: str = "moderate"
    learning_period_days: int = 14
    min_data_points: int = 10


@dataclass(frozen=True)
class Priority:
    training_priority: int = 5
    nutrition_priority: int = 4
    recovery_priority: int = 3
    consistency_priority: int = 5
    lifestyle_priority: int = 3

    def __post_init__(self) -> None:
        for dim in ("training_priority", "nutrition_priority", "recovery_priority",
                    "consistency_priority", "lifestyle_priority"):
            val = getattr(self, dim)
            clamped = max(1, min(10, val))
            if clamped != val:
                object.__setattr__(self, dim, clamped)

    def get(self, dimension: IntentDimension) -> int:
        return {
            IntentDimension.TRAINING: self.training_priority,
            IntentDimension.NUTRITION: self.nutrition_priority,
            IntentDimension.RECOVERY: self.recovery_priority,
            IntentDimension.CONSISTENCY: self.consistency_priority,
            IntentDimension.LIFESTYLE: self.lifestyle_priority,
        }[dimension]


@dataclass(frozen=True)
class IntentConflict:
    dimension_a: str = ""
    dimension_b: str = ""
    description: str = ""
    severity: IntentConflictSeverity = IntentConflictSeverity.MEDIUM
    resolution: str = ""
    is_resolved: bool = False

    def with_resolution(self, resolution: str) -> IntentConflict:
        return IntentConflict(
            dimension_a=self.dimension_a, dimension_b=self.dimension_b,
            description=self.description, severity=self.severity,
            resolution=resolution, is_resolved=True,
        )


@dataclass(frozen=True)
class UserIntent:
    intent_id: str = ""
    version: str = "1.0"
    status: IntentStatus = IntentStatus.ACTIVE
    created_at: str = ""
    updated_at: str = ""

    goals: list[GoalIntent] = field(default_factory=list)
    constraints: list[Constraint] = field(default_factory=list)
    timeline: Timeline = field(default_factory=Timeline)
    equipment: EquipmentProfile = field(default_factory=EquipmentProfile)
    lifestyle: LifestyleProfile = field(default_factory=LifestyleProfile)
    compliance: ComplianceProfile = field(default_factory=ComplianceProfile)
    risk_tolerance: RiskTolerance = field(default_factory=RiskTolerance)

    training: TrainingPreference = field(default_factory=TrainingPreference)
    nutrition: NutritionPreference = field(default_factory=NutritionPreference)
    recovery: RecoveryPreference = field(default_factory=RecoveryPreference)
    adaptive: AdaptivePreference = field(default_factory=AdaptivePreference)
    priorities: Priority = field(default_factory=Priority)

    conflicts: list[IntentConflict] = field(default_factory=list)

    @property
    def is_complete(self) -> bool:
        return bool(self.goals and self.timeline)

    @property
    def primary_goal(self) -> GoalIntent | None:
        return self.goals[0] if self.goals else None


@dataclass(frozen=True)
class IntentSnapshot:
    intent: UserIntent = field(default_factory=UserIntent)
    timestamp: str = ""
    snapshot_version: str = ""
    score: float = 0.0
    change_description: str = ""
