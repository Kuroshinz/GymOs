"""Allocation Engine — distributes volume, intensity, frequency, RIR, and recovery across a plan.

Every allocation is deterministic, derived from the user's intent and
scientific guidelines.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from shared.planning.domain import (
    ExerciseAllocation,
    FatigueBudget,
    IntensityDomain,
    Macrocycle,
    MesocycleGoal,
    NutritionBudget,
    RecoveryBudget,
    SessionPlan,
    TrainingFocus,
    VolumeAllocation,
)


@dataclass
class VolumeDistribution:
    per_session: dict[str, int] = field(default_factory=dict)
    per_muscle_group: dict[str, int] = field(default_factory=dict)
    weekly_total: int = 0
    mesocycle_total: int = 0
    macrocycle_total: int = 0

    @property
    def weekly_avg_per_session(self) -> float:
        if not self.per_session:
            return 0.0
        return sum(self.per_session.values()) / len(self.per_session)


@dataclass
class IntensityDistribution:
    zone: IntensityDomain = IntensityDomain.HYPERTROPHY
    rep_ranges: dict[str, tuple[int, int]] = field(default_factory=dict)
    load_percentages: dict[str, tuple[float, float]] = field(default_factory=dict)
    average_intensity: float = 0.70

    @property
    def description(self) -> str:
        return f"{self.zone.label}: {self.zone.rep_range[0]}-{self.zone.rep_range[1]} reps @ {self.average_intensity:.0%}"


@dataclass
class RecoveryDistribution:
    rest_days_per_week: int = 2
    active_recovery_minutes: int = 60
    deload_frequency_weeks: int = 6
    recovery_sessions_per_week: int = 1
    sleep_target: float = 8.0
    nutrition_priority: str = "maintenance"

    @property
    def training_to_rest_ratio(self) -> float:
        return 5.0 / max(1, self.rest_days_per_week)


class AllocationEngine:
    """Deterministically distributes training variables across a plan."""

    @staticmethod
    def distribute_volume(
        session: SessionPlan,
        target_sets: int = 15,
        primary_ratio: float = 0.4,
    ) -> VolumeAllocation:
        primary_sets = int(target_sets * primary_ratio)
        return VolumeAllocation(
            sets_per_exercise=(3, 5),
            reps_per_set=session.volume_allocation.reps_per_set
            if session.volume_allocation
            else (6, 12),
            total_sets_per_session=target_sets,
            total_sets_per_muscle_group=primary_sets,
            rir_target=session.volume_allocation.rir_target
            if session.volume_allocation
            else 1.0,
            rpe_cap=session.volume_allocation.rpe_cap
            if session.volume_allocation
            else 9.0,
        )

    @staticmethod
    def distribute_intensity(
        focus: TrainingFocus,
        week_number: int,
        total_weeks: int,
        is_deload: bool = False,
    ) -> IntensityDistribution:
        if is_deload:
            return IntensityDistribution(
                zone=IntensityDomain.HYPERTROPHY,
                average_intensity=0.50,
            )
        if focus == TrainingFocus.STRENGTH:
            progress = week_number / max(1, total_weeks)
            intensity = 0.75 + progress * 0.15
            return IntensityDistribution(
                zone=IntensityDomain.STRENGTH,
                rep_ranges={"primary": (3, 5), "secondary": (5, 8)},
                load_percentages={"primary": (0.80, 0.95), "secondary": (0.70, 0.80)},
                average_intensity=min(0.95, intensity),
            )
        if focus == TrainingFocus.HYPERTROPHY:
            return IntensityDistribution(
                zone=IntensityDomain.HYPERTROPHY,
                rep_ranges={"primary": (8, 12), "secondary": (12, 15)},
                load_percentages={"primary": (0.65, 0.80), "secondary": (0.55, 0.70)},
                average_intensity=0.72,
            )
        if focus == TrainingFocus.ENDURANCE:
            return IntensityDistribution(
                zone=IntensityDomain.ENDURANCE,
                rep_ranges={"all": (15, 25)},
                load_percentages={"all": (0.40, 0.60)},
                average_intensity=0.50,
            )
        return IntensityDistribution(
            zone=IntensityDomain.HYPERTROPHY,
            average_intensity=0.70,
        )

    @staticmethod
    def distribute_frequency(
        sessions_per_week: int,
        split_style: str = "ppl_ul",
    ) -> dict[str, int]:
        if split_style == "ppl_ul":
            return {
                "push": 2, "pull": 2, "legs": 2,
                "upper": 1, "lower": 1,
            }
        if split_style == "push_pull_legs":
            return {"push": 2, "pull": 2, "legs": 2}
        if split_style == "upper_lower":
            return {"upper": 3, "lower": 2}
        if split_style == "full_body":
            return {"full_body": sessions_per_week}
        return {"custom": sessions_per_week}

    @staticmethod
    def distribute_rir(
        mesocycle_goal: MesocycleGoal,
        week_number: int,
        total_weeks: int,
    ) -> float:
        progress = week_number / max(1, total_weeks)
        if mesocycle_goal == MesocycleGoal.MAX_STRENGTH:
            return max(0.0, 2.0 - progress * 2.0)
        if mesocycle_goal in (MesocycleGoal.HYPERTROPHY, MesocycleGoal.STRENGTH_ENDURANCE):
            return max(0.0, 1.5 - progress * 1.5)
        if mesocycle_goal == MesocycleGoal.POWER:
            return max(0.0, 2.5 - progress * 2.5)
        return 1.0

    @staticmethod
    def distribute_recovery(
        sessions_per_week: int,
        fatigue_level: float = 0.0,
    ) -> RecoveryDistribution:
        if sessions_per_week <= 3:
            return RecoveryDistribution(
                rest_days_per_week=4,
                active_recovery_minutes=30,
                deload_frequency_weeks=8,
            )
        if sessions_per_week <= 5:
            return RecoveryDistribution(
                rest_days_per_week=2,
                active_recovery_minutes=60,
                deload_frequency_weeks=6,
            )
        return RecoveryDistribution(
            rest_days_per_week=1,
            active_recovery_minutes=90,
            deload_frequency_weeks=4,
            recovery_sessions_per_week=2,
        )

    @staticmethod
    def compute_fatigue_budget(
        volume_allocation: VolumeAllocation,
        recovery_budget: RecoveryBudget,
    ) -> FatigueBudget:
        total = volume_allocation.total_sets_per_session * 7
        recovery = recovery_budget.recovery_capacity
        adjusted = total * (1.5 - recovery * 0.5)
        return FatigueBudget(
            total_fatigue_units=adjusted,
            max_per_session=volume_allocation.total_sets_per_session * 1.2,
            max_per_muscle_group=volume_allocation.total_sets_per_muscle_group * 1.5,
            recovery_rate_per_day=recovery * 20,
        )

    @staticmethod
    def compute_nutrition_budget(
        target_calories: float,
        body_weight_kg: float = 75.0,
        activity_factor: float = 1.5,
    ) -> NutritionBudget:
        protein = body_weight_kg * 2.0
        fat = max(60.0, body_weight_kg * 0.9)
        remaining = target_calories - (protein * 4 + fat * 9)
        carbs = max(0.0, remaining / 4)
        return NutritionBudget(
            target_calories=target_calories,
            protein_g=round(protein, 1),
            carbs_g=round(carbs, 1),
            fat_g=round(fat, 1),
            fiber_g=30,
            hydration_ml=3000,
            pre_workout_carbs_g=30,
            post_workout_protein_g=40,
            meal_count=4,
        )

    @staticmethod
    def allocate_exercises_to_session(
        session: SessionPlan,
        primary_exercises: list[tuple[str, str, str]],
        accessory_exercises: list[tuple[str, str, str]],
        target_sets: int = 15,
    ) -> SessionPlan:
        allocated: list[ExerciseAllocation] = []
        sets_per_primary = max(3, int(target_sets * 0.4 / max(1, len(primary_exercises))))
        sets_per_accessory = max(
            2,
            (target_sets - sets_per_primary * len(primary_exercises))
            // max(1, len(accessory_exercises)),
        )
        order = 0
        for ex_id, ex_name, muscle in primary_exercises:
            order += 1
            allocated.append(ExerciseAllocation(
                exercise_id=ex_id,
                exercise_name=ex_name,
                target_muscle_group=muscle,
                sets=sets_per_primary,
                reps=session.volume_allocation.reps_per_set[0]
                if session.volume_allocation else 10,
                rir=session.volume_allocation.rir_target
                if session.volume_allocation else 1.0,
                is_primary=True,
                order_in_session=order,
            ))
        for ex_id, ex_name, muscle in accessory_exercises:
            order += 1
            allocated.append(ExerciseAllocation(
                exercise_id=ex_id,
                exercise_name=ex_name,
                target_muscle_group=muscle,
                sets=sets_per_accessory,
                reps=session.volume_allocation.reps_per_set[1]
                if session.volume_allocation else 12,
                rir=session.volume_allocation.rir_target
                if session.volume_allocation else 1.0,
                is_primary=False,
                order_in_session=order,
            ))
        return SessionPlan(
            session_id=session.session_id,
            week=session.week,
            day_of_week=session.day_of_week,
            day_type=session.day_type,
            training_focus=session.training_focus,
            exercises=allocated,
            volume_allocation=session.volume_allocation,
            fatigue_budget=session.fatigue_budget,
            estimated_duration_minutes=sum(
                e.estimated_duration_minutes for e in allocated
            ),
            is_deload=session.is_deload,
            is_recovery=session.is_recovery,
            notes=session.notes,
        )

    @staticmethod
    def compute_volume_distribution(macrocycle: Macrocycle) -> VolumeDistribution:
        weekly: dict[str, int] = {}
        muscle: dict[str, int] = {}
        macro_total = 0

        for week in macrocycle.weeks:
            weekly[f"Week {week.week_number}"] = week.total_sets
            macro_total += week.total_sets
            for mg, vol in week.weekly_volume_by_muscle.items():
                muscle[mg] = muscle.get(mg, 0) + vol

        return VolumeDistribution(
            per_session=weekly,
            per_muscle_group=muscle,
            weekly_total=sum(weekly.values()) // max(1, len(weekly)),
            macrocycle_total=macro_total,
        )
