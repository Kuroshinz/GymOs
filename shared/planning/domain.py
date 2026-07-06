"""Planning Engine domain models — periodization entities and value objects.

Macrocycle → Mesocycle → Microcycle → WeekPlan → SessionPlan
These models form the single source of truth for every future program.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class CyclePhase(Enum):
    PREPARATORY = "preparatory"
    HYPERTROPHY_I = "hypertrophy_i"
    HYPERTROPHY_II = "hypertrophy_ii"
    STRENGTH_I = "strength_i"
    STRENGTH_II = "strength_ii"
    PEAKING = "peaking"
    DELOAD = "deload"
    TRANSITION = "transition"
    MAINTENANCE = "maintenance"

    @property
    def label(self) -> str:
        return {
            CyclePhase.PREPARATORY: "Preparatory",
            CyclePhase.HYPERTROPHY_I: "Hypertrophy I",
            CyclePhase.HYPERTROPHY_II: "Hypertrophy II",
            CyclePhase.STRENGTH_I: "Strength I",
            CyclePhase.STRENGTH_II: "Strength II",
            CyclePhase.PEAKING: "Peaking",
            CyclePhase.DELOAD: "Deload",
            CyclePhase.TRANSITION: "Transition",
            CyclePhase.MAINTENANCE: "Maintenance",
        }[self]

    @property
    def typical_weeks(self) -> int:
        return {
            CyclePhase.PREPARATORY: 4,
            CyclePhase.HYPERTROPHY_I: 4,
            CyclePhase.HYPERTROPHY_II: 4,
            CyclePhase.STRENGTH_I: 4,
            CyclePhase.STRENGTH_II: 4,
            CyclePhase.PEAKING: 3,
            CyclePhase.DELOAD: 1,
            CyclePhase.TRANSITION: 1,
            CyclePhase.MAINTENANCE: 2,
        }[self]


class TrainingFocus(Enum):
    STRENGTH = "strength"
    HYPERTROPHY = "hypertrophy"
    ENDURANCE = "endurance"
    POWER = "power"
    CONDITIONING = "conditioning"
    RECOVERY = "recovery"
    MAINTENANCE = "maintenance"

    @property
    def label(self) -> str:
        return {
            TrainingFocus.STRENGTH: "Strength",
            TrainingFocus.HYPERTROPHY: "Hypertrophy",
            TrainingFocus.ENDURANCE: "Endurance",
            TrainingFocus.POWER: "Power",
            TrainingFocus.CONDITIONING: "Conditioning",
            TrainingFocus.RECOVERY: "Recovery",
            TrainingFocus.MAINTENANCE: "Maintenance",
        }[self]


class DayType(Enum):
    PUSH = "push"
    PULL = "pull"
    LEGS = "legs"
    UPPER = "upper"
    LOWER = "lower"
    FULL_BODY = "full_body"
    CONDITIONING = "conditioning"
    REST = "rest"
    ACTIVE_RECOVERY = "active_recovery"
    DELOAD = "deload"

    @property
    def label(self) -> str:
        return {
            DayType.PUSH: "Push",
            DayType.PULL: "Pull",
            DayType.LEGS: "Legs",
            DayType.UPPER: "Upper",
            DayType.LOWER: "Lower",
            DayType.FULL_BODY: "Full Body",
            DayType.CONDITIONING: "Conditioning",
            DayType.REST: "Rest",
            DayType.ACTIVE_RECOVERY: "Active Recovery",
            DayType.DELOAD: "Deload",
        }[self]


class ProgressionModel(Enum):
    DOUBLE_PROGRESSION = "double_progression"
    LINEAR_PROGRESSION = "linear_progression"
    RAMPING = "ramping"
    PERIODIZATION_BLOCK = "periodization_block"
    WAVE_LOADING = "wave_loading"
    RPE_BASED = "rpe_based"
    AUTO_REGULATION = "auto_regulation"

    @property
    def label(self) -> str:
        return {
            ProgressionModel.DOUBLE_PROGRESSION: "Double Progression",
            ProgressionModel.LINEAR_PROGRESSION: "Linear Progression",
            ProgressionModel.RAMPING: "Ramping",
            ProgressionModel.PERIODIZATION_BLOCK: "Periodization Block",
            ProgressionModel.WAVE_LOADING: "Wave Loading",
            ProgressionModel.RPE_BASED: "RPE-Based",
            ProgressionModel.AUTO_REGULATION: "Auto-Regulation",
        }[self]


class SplitStyle(Enum):
    PPL_UL = "ppl_ul"
    PUSH_PULL_LEGS = "push_pull_legs"
    UPPER_LOWER = "upper_lower"
    FULL_BODY = "full_body"
    BRO_SPLIT = "bro_split"
    CUSTOM = "custom"

    @property
    def label(self) -> str:
        return {
            SplitStyle.PPL_UL: "PPL-UL",
            SplitStyle.PUSH_PULL_LEGS: "Push/Pull/Legs",
            SplitStyle.UPPER_LOWER: "Upper/Lower",
            SplitStyle.FULL_BODY: "Full Body",
            SplitStyle.BRO_SPLIT: "Bro Split",
            SplitStyle.CUSTOM: "Custom",
        }[self]


class IntensityDomain(Enum):
    STRENGTH = "strength"
    HYPERTROPHY = "hypertrophy"
    ENDURANCE = "endurance"
    POWER = "power"

    @property
    def label(self) -> str:
        return {
            IntensityDomain.STRENGTH: "Strength",
            IntensityDomain.HYPERTROPHY: "Hypertrophy",
            IntensityDomain.ENDURANCE: "Endurance",
            IntensityDomain.POWER: "Power",
        }[self]

    @property
    def rep_range(self) -> tuple[int, int]:
        return {
            IntensityDomain.STRENGTH: (1, 6),
            IntensityDomain.HYPERTROPHY: (6, 15),
            IntensityDomain.ENDURANCE: (15, 30),
            IntensityDomain.POWER: (1, 5),
        }[self]

    @property
    def intensity_range(self) -> tuple[float, float]:
        return {
            IntensityDomain.STRENGTH: (0.80, 1.0),
            IntensityDomain.HYPERTROPHY: (0.60, 0.80),
            IntensityDomain.ENDURANCE: (0.40, 0.60),
            IntensityDomain.POWER: (0.75, 0.90),
        }[self]


class MesocycleGoal(Enum):
    MAX_STRENGTH = "max_strength"
    HYPERTROPHY = "hypertrophy"
    STRENGTH_ENDURANCE = "strength_endurance"
    POWER = "power"
    CONDITIONING = "conditioning"
    FAT_LOSS = "fat_loss"
    MAINTENANCE = "maintenance"
    REHAB = "rehab"

    @property
    def label(self) -> str:
        return {
            MesocycleGoal.MAX_STRENGTH: "Max Strength",
            MesocycleGoal.HYPERTROPHY: "Hypertrophy",
            MesocycleGoal.STRENGTH_ENDURANCE: "Strength Endurance",
            MesocycleGoal.POWER: "Power",
            MesocycleGoal.CONDITIONING: "Conditioning",
            MesocycleGoal.FAT_LOSS: "Fat Loss",
            MesocycleGoal.MAINTENANCE: "Maintenance",
            MesocycleGoal.REHAB: "Rehab",
        }[self]

    @property
    def typical_weeks(self) -> int:
        return {
            MesocycleGoal.MAX_STRENGTH: 6,
            MesocycleGoal.HYPERTROPHY: 5,
            MesocycleGoal.STRENGTH_ENDURANCE: 4,
            MesocycleGoal.POWER: 4,
            MesocycleGoal.CONDITIONING: 6,
            MesocycleGoal.FAT_LOSS: 8,
            MesocycleGoal.MAINTENANCE: 4,
            MesocycleGoal.REHAB: 4,
        }[self]


@dataclass(frozen=True)
class VolumeAllocation:
    sets_per_exercise: tuple[int, int] = (3, 5)
    reps_per_set: tuple[int, int] = (6, 12)
    total_sets_per_session: int = 15
    total_sets_per_muscle_group: int = 12
    weekly_sets_per_muscle: int = 18
    rir_target: float = 1.0
    rpe_cap: float = 9.0
    intensity_percent: tuple[float, float] = (0.65, 0.80)

    @property
    def volume_per_exercise_range(self) -> str:
        return (
            f"{self.sets_per_exercise[0]}-{self.sets_per_exercise[1]} sets × "
            f"{self.reps_per_set[0]}-{self.reps_per_set[1]} reps"
        )

    @property
    def total_sets_range(self) -> tuple[int, int]:
        lo = self.sets_per_exercise[0] * self.reps_per_set[0]
        hi = self.sets_per_exercise[1] * self.reps_per_set[1]
        return (lo, hi)


@dataclass(frozen=True)
class ExerciseAllocation:
    exercise_id: str = ""
    exercise_name: str = ""
    target_muscle_group: str = ""
    sets: int = 0
    reps: int = 0
    rir: float = 1.0
    rpe: float | None = None
    load_percent: float = 0.0
    rest_seconds: int = 90
    is_warmup: bool = False
    is_primary: bool = False
    order_in_session: int = 0

    @property
    def volume_kg(self) -> float:
        return 0.0

    @property
    def estimated_duration_minutes(self) -> int:
        set_time = (self.reps * 2 + self.rest_seconds / 60)
        return int(set_time * self.sets + 3)


@dataclass(frozen=True)
class FatigueBudget:
    total_fatigue_units: float = 100.0
    used_fatigue_units: float = 0.0
    max_per_session: float = 30.0
    max_per_muscle_group: float = 20.0
    recovery_rate_per_day: float = 15.0
    current_fatigue_level: float = 0.0

    @property
    def remaining(self) -> float:
        return max(0.0, self.total_fatigue_units - self.used_fatigue_units)

    @property
    def utilization(self) -> float:
        if self.total_fatigue_units == 0:
            return 0.0
        return self.used_fatigue_units / self.total_fatigue_units

    @property
    def is_exceeded(self) -> bool:
        return self.used_fatigue_units > self.total_fatigue_units

    def estimate_fatigue_from_volume(self, sets: int, intensity: float) -> float:
        return sets * (0.5 + intensity * 0.5)


@dataclass(frozen=True)
class RecoveryBudget:
    available_hours_per_night: float = 8.0
    target_hrv_score: float = 65.0
    current_hrv_score: float = 60.0
    sleep_quality_score: float = 0.75
    nutrition_score: float = 0.70
    stress_level: float = 5.0
    readiness_score: float = 0.75
    active_recovery_minutes_per_week: int = 60
    rest_days_per_week: int = 2

    @property
    def recovery_capacity(self) -> float:
        return (
            self.sleep_quality_score * 0.35 +
            self.nutrition_score * 0.20 +
            (1.0 - self.stress_level / 10.0) * 0.20 +
            min(1.0, self.current_hrv_score / self.target_hrv_score) * 0.25
        )

    @property
    def needs_rest(self) -> bool:
        return self.recovery_capacity < 0.4

    @property
    def is_balanced(self) -> bool:
        return self.recovery_capacity >= 0.6


@dataclass(frozen=True)
class NutritionBudget:
    target_calories: float = 2500.0
    protein_g: float = 150.0
    carbs_g: float = 300.0
    fat_g: float = 70.0
    fiber_g: float = 30.0
    hydration_ml: int = 3000
    pre_workout_carbs_g: float = 30.0
    post_workout_protein_g: float = 40.0
    meal_count: int = 4

    @property
    def protein_per_kg(self) -> float:
        return self.protein_g / 75.0

    @property
    def calorie_split(self) -> str:
        protein_cals = self.protein_g * 4
        carbs_cals = self.carbs_g * 4
        fat_cals = self.fat_g * 9
        total = protein_cals + carbs_cals + fat_cals
        return (
            f"P:{protein_cals / total:.0%} C:{carbs_cals / total:.0%} "
            f"F:{fat_cals / total:.0%}"
        )


@dataclass(frozen=True)
class SessionPlan:
    session_id: str = ""
    week: int = 0
    day_of_week: int = 0
    day_type: DayType = DayType.REST
    training_focus: TrainingFocus = TrainingFocus.HYPERTROPHY
    exercises: list[ExerciseAllocation] = field(default_factory=list)
    volume_allocation: VolumeAllocation = field(default_factory=VolumeAllocation)
    fatigue_budget: FatigueBudget = field(default_factory=FatigueBudget)
    estimated_duration_minutes: int = 60
    is_deload: bool = False
    is_recovery: bool = False
    notes: str = ""

    @property
    def total_sets(self) -> int:
        return sum(e.sets for e in self.exercises if not e.is_warmup)

    @property
    def total_primary_sets(self) -> int:
        return sum(e.sets for e in self.exercises if e.is_primary)

    @property
    def primary_exercises(self) -> list[ExerciseAllocation]:
        return [e for e in self.exercises if e.is_primary]

    @property
    def is_full_body(self) -> bool:
        return self.day_type == DayType.FULL_BODY

    @property
    def has_sufficient_volume(self) -> bool:
        return self.total_sets >= 10

    @property
    def exercise_count(self) -> int:
        return len([e for e in self.exercises if not e.is_warmup])

    @property
    def muscle_groups_trained(self) -> list[str]:
        seen: set[str] = set()
        result: list[str] = []
        for e in self.exercises:
            if e.target_muscle_group and e.target_muscle_group not in seen:
                seen.add(e.target_muscle_group)
                result.append(e.target_muscle_group)
        return result


@dataclass(frozen=True)
class WeekPlan:
    week_number: int = 0
    start_date: str = ""
    end_date: str = ""
    sessions: list[SessionPlan] = field(default_factory=list)
    is_deload_week: bool = False
    is_transition_week: bool = False
    total_fatigue_budget: FatigueBudget = field(default_factory=FatigueBudget)
    recovery_budget: RecoveryBudget = field(default_factory=RecoveryBudget)
    nutrition_budget: NutritionBudget = field(default_factory=NutritionBudget)
    notes: str = ""

    @property
    def session_count(self) -> int:
        return len([s for s in self.sessions if s.day_type != DayType.REST])

    @property
    def total_sets(self) -> int:
        return sum(s.total_sets for s in self.sessions)

    @property
    def total_training_duration_minutes(self) -> int:
        return sum(s.estimated_duration_minutes for s in self.sessions)

    @property
    def training_sessions(self) -> list[SessionPlan]:
        return [s for s in self.sessions if s.day_type != DayType.REST]

    @property
    def rest_days(self) -> list[SessionPlan]:
        return [s for s in self.sessions if s.day_type == DayType.REST or s.is_recovery]

    @property
    def weekly_volume_by_muscle(self) -> dict[str, int]:
        result: dict[str, int] = {}
        for session in self.sessions:
            for ex in session.exercises:
                if ex.target_muscle_group:
                    result[ex.target_muscle_group] = (
                        result.get(ex.target_muscle_group, 0) + ex.sets
                    )
        return result


@dataclass(frozen=True)
class Microcycle:
    microcycle_id: str = ""
    phase: CyclePhase = CyclePhase.HYPERTROPHY_I
    weeks: list[WeekPlan] = field(default_factory=list)
    focus: TrainingFocus = TrainingFocus.HYPERTROPHY
    progression_model: ProgressionModel = ProgressionModel.DOUBLE_PROGRESSION
    week_count: int = 4
    start_week: int = 0

    @property
    def total_weeks(self) -> int:
        return len(self.weeks)

    @property
    def total_sessions(self) -> int:
        return sum(w.session_count for w in self.weeks)

    @property
    def total_sets(self) -> int:
        return sum(w.total_sets for w in self.weeks)

    @property
    def deload_weeks(self) -> list[WeekPlan]:
        return [w for w in self.weeks if w.is_deload_week]

    @property
    def training_weeks(self) -> list[WeekPlan]:
        return [w for w in self.weeks if not w.is_deload_week and not w.is_transition_week]

    @property
    def progression_description(self) -> str:
        if self.progression_model == ProgressionModel.DOUBLE_PROGRESSION:
            return f"{self.focus.label}: add reps to {self.training_weeks[0].total_sets} sets, then increase load"
        return f"{self.progression_model.label}: {self.focus.label} phase"


@dataclass(frozen=True)
class Mesocycle:
    mesocycle_id: str = ""
    name: str = ""
    goal: MesocycleGoal = MesocycleGoal.HYPERTROPHY
    focus: TrainingFocus = TrainingFocus.HYPERTROPHY
    phase: CyclePhase = CyclePhase.HYPERTROPHY_I
    microcycles: list[Microcycle] = field(default_factory=list)
    week_count: int = 5
    start_week: int = 0
    target_rir: float = 1.0
    target_rpe: float = 8.0
    min_volume_per_muscle: int = 8
    max_volume_per_muscle: int = 22
    intensity_zone: IntensityDomain = IntensityDomain.HYPERTROPHY
    deload_after: bool = True

    @property
    def total_weeks(self) -> int:
        return sum(m.total_weeks for m in self.microcycles)

    @property
    def total_training_weeks(self) -> int:
        return sum(len(m.training_weeks) for m in self.microcycles)

    @property
    def weeks(self) -> list[WeekPlan]:
        result: list[WeekPlan] = []
        for m in self.microcycles:
            result.extend(m.weeks)
        return result

    @property
    def sessions(self) -> list[SessionPlan]:
        result: list[SessionPlan] = []
        for w in self.weeks:
            result.extend(w.sessions)
        return result

    @property
    def volume_progression_across_weeks(self) -> list[int]:
        return [w.total_sets for w in self.weeks]


@dataclass(frozen=True)
class Macrocycle:
    macrocycle_id: str = ""
    name: str = ""
    duration_weeks: int = 24
    start_date: str = ""
    end_date: str = ""
    mesocycles: list[Mesocycle] = field(default_factory=list)
    overall_goal: str = ""
    user_intent_id: str = ""
    version: str = "1.0"

    @property
    def total_mesocycles(self) -> int:
        return len(self.mesocycles)

    @property
    def total_weeks(self) -> int:
        return sum(m.total_weeks for m in self.mesocycles)

    @property
    def weeks(self) -> list[WeekPlan]:
        result: list[WeekPlan] = []
        for m in self.mesocycles:
            result.extend(m.weeks)
        return result

    @property
    def sessions(self) -> list[SessionPlan]:
        return [s for w in self.weeks for s in w.sessions]

    @property
    def training_weeks(self) -> list[WeekPlan]:
        return [w for w in self.weeks if not w.is_deload_week]

    @property
    def deload_weeks(self) -> list[WeekPlan]:
        return [w for w in self.weeks if w.is_deload_week]

    @property
    def total_sessions(self) -> int:
        return len(self.sessions)

    @property
    def total_sets(self) -> int:
        return sum(s.total_sets for s in self.sessions)

    @property
    def average_session_volume(self) -> float:
        training = [s for s in self.sessions if not s.is_deload and s.day_type != DayType.REST]
        if not training:
            return 0.0
        return sum(s.total_sets for s in training) / len(training)

    @property
    def weekly_volume_trend(self) -> list[int]:
        return [w.total_sets for w in self.weeks]


@dataclass(frozen=True)
class PlanProgress:
    current_macrocycle: Macrocycle | None = None
    current_mesocycle_index: int = 0
    current_week_index: int = 0
    current_session_index: int = 0
    weeks_completed: int = 0
    sessions_completed: int = 0
    total_weeks: int = 0
    total_sessions: int = 0
    adherence_rate: float = 0.0
    is_complete: bool = False

    @property
    def completion_percent(self) -> float:
        if self.total_weeks == 0:
            return 0.0
        return min(100.0, (self.weeks_completed / self.total_weeks) * 100.0)

    @property
    def week_summary(self) -> str:
        return f"Week {self.weeks_completed + 1}/{self.total_weeks}"

    @property
    def session_summary(self) -> str:
        return f"Session {self.sessions_completed + 1}/{self.total_sessions}"


@dataclass(frozen=True)
class PlanningState:
    has_active_plan: bool = False
    active_macrocycle_id: str = ""
    plan_count: int = 0
    active_plan_progress: PlanProgress | None = None
    last_updated: str = ""
    current_phase: CyclePhase | None = None


@dataclass(frozen=True)
class PlanningConfig:
    min_weeks_per_mesocycle: int = 3
    max_weeks_per_mesocycle: int = 8
    default_macrocycle_weeks: int = 24
    deload_frequency_weeks: int = 6
    min_sessions_per_week: int = 2
    max_sessions_per_week: int = 7
    min_sets_per_session: int = 8
    max_sets_per_session: int = 25
    min_sets_per_muscle_weekly: int = 6
    max_sets_per_muscle_weekly: int = 30
    default_rir: float = 1.0
    default_rpe_cap: float = 9.0
    recovery_week_interval: int = 4
    transition_week_interval: int = 12
