"""Planning Engine — deterministic periodization pipeline.

Generates macrocycles, mesocycles, weekly splits, sessions, progression
blocks, deload blocks, recovery budgets, and nutrition budgets.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

from shared.planning.allocation import AllocationEngine
from shared.planning.domain import (
    CyclePhase,
    DayType,
    FatigueBudget,
    IntensityDomain,
    Macrocycle,
    Mesocycle,
    MesocycleGoal,
    Microcycle,
    NutritionBudget,
    PlanningConfig,
    ProgressionModel,
    RecoveryBudget,
    SessionPlan,
    SplitStyle,
    TrainingFocus,
    VolumeAllocation,
    WeekPlan,
)
from shared.planning.validator import PlanningValidator, ValidationResult


@dataclass
class MesocycleBlueprint:
    goal: MesocycleGoal = MesocycleGoal.HYPERTROPHY
    focus: TrainingFocus = TrainingFocus.HYPERTROPHY
    phase: CyclePhase = CyclePhase.HYPERTROPHY_I
    weeks: int = 5
    intensity_zone: IntensityDomain = IntensityDomain.HYPERTROPHY
    target_rir: float = 1.0
    target_rpe: float = 8.0
    deload_after: bool = True
    min_volume: int = 8
    max_volume: int = 22


@dataclass
class PlanningOutput:
    macrocycle: Macrocycle
    validation: ValidationResult
    weeks_generated: int
    sessions_generated: int
    total_sets: int
    mesocycle_count: int


def _generate_id(prefix: str = "plan") -> str:
    import uuid
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


class PlanningEngine:
    """Deterministic training plan generator.

    Produces a full macrocycle from user intent parameters. Every output
    is a pure function of the inputs — no randomness, no LLM calls.
    """

    def __init__(
        self,
        config: PlanningConfig = PlanningConfig(),
        validator: PlanningValidator = PlanningValidator(),
    ) -> None:
        self.config = config
        self.validator = validator
        self.allocation = AllocationEngine()

    def generate_macrocycle(
        self,
        duration_weeks: int = 24,
        goal: str = "hypertrophy",
        sessions_per_week: int = 5,
        split_style: str = "ppl_ul",
        start_date: str | None = None,
        name: str = "",
    ) -> PlanningOutput:
        blueprints = self._design_mesocycles(duration_weeks, goal)
        mesocycles: list[Mesocycle] = []
        current_week = 0

        for bp in blueprints:
            meso = self.generate_mesocycle(
                goal=bp.goal,
                focus=bp.focus,
                phase=bp.phase,
                weeks=bp.weeks,
                intensity_zone=bp.intensity_zone,
                target_rir=bp.target_rir,
                target_rpe=bp.target_rpe,
                deload_after=bp.deload_after,
                min_volume=bp.min_volume,
                max_volume=bp.max_volume,
                start_week=current_week,
                sessions_per_week=sessions_per_week,
                split_style=split_style,
            )
            mesocycles.append(meso)
            current_week += bp.weeks

        macro_id = _generate_id("macro")
        effective_start = start_date or date.today().isoformat()
        macro = Macrocycle(
            macrocycle_id=macro_id,
            name=name or f"{goal.capitalize()} Macrocycle",
            duration_weeks=duration_weeks,
            start_date=effective_start,
            end_date=self._compute_end_date(effective_start, duration_weeks),
            mesocycles=mesocycles,
            overall_goal=goal,
        )

        validation = self.validator.validate(macro)
        return PlanningOutput(
            macrocycle=macro,
            validation=validation,
            weeks_generated=macro.total_weeks,
            sessions_generated=macro.total_sessions,
            total_sets=macro.total_sets,
            mesocycle_count=macro.total_mesocycles,
        )

    def generate_mesocycle(
        self,
        goal: MesocycleGoal = MesocycleGoal.HYPERTROPHY,
        focus: TrainingFocus = TrainingFocus.HYPERTROPHY,
        phase: CyclePhase = CyclePhase.HYPERTROPHY_I,
        weeks: int = 5,
        intensity_zone: IntensityDomain = IntensityDomain.HYPERTROPHY,
        target_rir: float = 1.0,
        target_rpe: float = 8.0,
        deload_after: bool = True,
        min_volume: int = 8,
        max_volume: int = 22,
        start_week: int = 0,
        sessions_per_week: int = 5,
        split_style: str = "ppl_ul",
    ) -> Mesocycle:
        microcycles: list[Microcycle] = []
        training_weeks = weeks - 1 if deload_after and weeks > 1 else weeks
        deload_at_end = deload_after and weeks > 1

        # Build microcycles from mesocycle
        micro = self._build_microcycle(
            phase=phase,
            focus=focus,
            progression_model=self._select_progression_model(goal),
            weeks=training_weeks,
            start_week=start_week,
            sessions_per_week=sessions_per_week,
            split_style=split_style,
            intensity_zone=intensity_zone,
            target_rir=target_rir,
        )
        microcycles.append(micro)

        # Add deload microcycle at end if needed
        if deload_at_end:
            deload_weeks = self._build_deload_block(
                week_number=start_week + training_weeks,
                sessions_per_week=sessions_per_week,
                split_style=split_style,
                reason="Mesocycle completion",
            )
            deload_micro = Microcycle(
                microcycle_id=_generate_id("deload_micro"),
                phase=CyclePhase.DELOAD,
                weeks=deload_weeks,
                focus=TrainingFocus.RECOVERY,
                progression_model=ProgressionModel.AUTO_REGULATION,
                week_count=1,
                start_week=start_week + training_weeks,
            )
            microcycles.append(deload_micro)

        return Mesocycle(
            mesocycle_id=_generate_id("meso"),
            name=f"{goal.label} - {focus.label}",
            goal=goal,
            focus=focus,
            phase=phase,
            microcycles=microcycles,
            week_count=weeks,
            start_week=start_week,
            target_rir=target_rir,
            target_rpe=target_rpe,
            min_volume_per_muscle=min_volume,
            max_volume_per_muscle=max_volume,
            intensity_zone=intensity_zone,
            deload_after=deload_after,
        )

    def generate_weekly_split(
        self,
        sessions_per_week: int = 5,
        split_style: str = "ppl_ul",
        week_number: int = 0,
        is_deload: bool = False,
    ) -> list[DayType]:
        if is_deload:
            return self._generate_deload_split(sessions_per_week)

        if split_style == "ppl_ul" or split_style == SplitStyle.PPL_UL.value:
            if sessions_per_week == 6:
                return [DayType.PUSH, DayType.PULL, DayType.LEGS,
                        DayType.UPPER, DayType.LOWER, DayType.FULL_BODY, DayType.REST]
            return [DayType.PUSH, DayType.PULL, DayType.LEGS,
                    DayType.UPPER, DayType.LOWER, DayType.REST, DayType.REST]

        if split_style == "push_pull_legs" or split_style == SplitStyle.PUSH_PULL_LEGS.value:
            if sessions_per_week == 6:
                return [DayType.PUSH, DayType.PULL, DayType.LEGS,
                        DayType.PUSH, DayType.PULL, DayType.LEGS, DayType.REST]
            return [DayType.PUSH, DayType.PULL, DayType.LEGS,
                    DayType.PUSH, DayType.PULL, DayType.REST, DayType.REST]

        if split_style == "upper_lower" or split_style == SplitStyle.UPPER_LOWER.value:
            if sessions_per_week == 4:
                return [DayType.UPPER, DayType.LOWER, DayType.REST,
                        DayType.UPPER, DayType.LOWER, DayType.REST, DayType.REST]
            return [DayType.UPPER, DayType.LOWER, DayType.UPPER,
                    DayType.REST, DayType.LOWER, DayType.UPPER, DayType.REST]

        if split_style == "full_body" or split_style == SplitStyle.FULL_BODY.value:
            days = [DayType.FULL_BODY] * min(sessions_per_week, 7)
            while len(days) < 7:
                days.append(DayType.REST)
            return days[:7]

        return self._generate_custom_split(sessions_per_week)

    def generate_daily_session(
        self,
        day_type: DayType,
        week_number: int,
        day_of_week: int,
        focus: TrainingFocus = TrainingFocus.HYPERTROPHY,
        is_deload: bool = False,
        volume_allocation: VolumeAllocation = VolumeAllocation(),
    ) -> SessionPlan:
        session_id = _generate_id("session")
        fatigue = FatigueBudget(
            total_fatigue_units=volume_allocation.total_sets_per_session * 1.5,
            max_per_session=volume_allocation.total_sets_per_session * 1.2,
        )
        return SessionPlan(
            session_id=session_id,
            week=week_number,
            day_of_week=day_of_week,
            day_type=day_type,
            training_focus=TrainingFocus.RECOVERY if is_deload else focus,
            exercises=[],
            volume_allocation=volume_allocation,
            fatigue_budget=fatigue,
            estimated_duration_minutes=45 if is_deload else 60,
            is_deload=is_deload,
            is_recovery=day_type == DayType.ACTIVE_RECOVERY,
            notes="Deload session: reduce load 40-50%" if is_deload else "",
        )

    def generate_progression_block(
        self,
        base_volume: VolumeAllocation,
        weeks: int = 4,
        progression_rate: float = 0.025,
    ) -> list[VolumeAllocation]:
        blocks: list[VolumeAllocation] = []
        for w in range(weeks):
            factor = 1.0 + progression_rate * w
            blocks.append(VolumeAllocation(
                sets_per_exercise=(
                    int(base_volume.sets_per_exercise[0] * factor),
                    int(base_volume.sets_per_exercise[1] * factor),
                ),
                reps_per_set=base_volume.reps_per_set,
                total_sets_per_session=int(base_volume.total_sets_per_session * factor),
                total_sets_per_muscle_group=int(base_volume.total_sets_per_muscle_group * factor),
                rir_target=max(0.0, base_volume.rir_target - w * 0.25),
                rpe_cap=min(10.0, base_volume.rpe_cap + w * 0.25),
            ))
        return blocks

    def generate_deload_block(
        self,
        week_number: int,
        sessions_per_week: int = 3,
        split_style: str = "ppl_ul",
        reason: str = "",
    ) -> list[WeekPlan]:
        return self._build_deload_block(week_number, sessions_per_week, split_style, reason)

    def generate_recovery_budget(
        self,
        sessions_per_week: int = 5,
        sleep_target: float = 8.0,
        hrv_score: float = 60.0,
    ) -> RecoveryBudget:
        return RecoveryBudget(
            available_hours_per_night=sleep_target,
            target_hrv_score=65.0,
            current_hrv_score=hrv_score,
            sleep_quality_score=0.75,
            nutrition_score=0.70,
            stress_level=5.0,
            readiness_score=min(1.0, hrv_score / 65.0 * 0.8 + 0.2),
            active_recovery_minutes_per_week=30 + sessions_per_week * 10,
            rest_days_per_week=max(1, 7 - sessions_per_week),
        )

    def generate_nutrition_budget(
        self,
        target_calories: float = 2500.0,
        body_weight_kg: float = 75.0,
        goal: str = "hypertrophy",
    ) -> NutritionBudget:
        return self.allocation.compute_nutrition_budget(
            target_calories=target_calories,
            body_weight_kg=body_weight_kg,
        )

    # ── Internal helpers ──────────────────────────────────────────

    def _design_mesocycles(
        self,
        total_weeks: int,
        goal: str,
    ) -> list[MesocycleBlueprint]:
        goal = goal.lower()
        if goal in ("hypertrophy", "muscle_growth"):
            return [
                MesocycleBlueprint(
                    goal=MesocycleGoal.HYPERTROPHY,
                    focus=TrainingFocus.HYPERTROPHY,
                    phase=CyclePhase.HYPERTROPHY_I,
                    weeks=6,
                ),
                MesocycleBlueprint(
                    goal=MesocycleGoal.STRENGTH_ENDURANCE,
                    focus=TrainingFocus.STRENGTH,
                    phase=CyclePhase.STRENGTH_I,
                    weeks=5,
                    deload_after=True,
                ),
                MesocycleBlueprint(
                    goal=MesocycleGoal.HYPERTROPHY,
                    focus=TrainingFocus.HYPERTROPHY,
                    phase=CyclePhase.HYPERTROPHY_II,
                    weeks=6,
                ),
                MesocycleBlueprint(
                    goal=MesocycleGoal.MAX_STRENGTH,
                    focus=TrainingFocus.STRENGTH,
                    phase=CyclePhase.STRENGTH_II,
                    weeks=5,
                    intensity_zone=IntensityDomain.STRENGTH,
                    target_rir=0.5,
                    target_rpe=9.0,
                    min_volume=6,
                    max_volume=16,
                    deload_after=True,
                ),
            ]
        if goal in ("strength", "powerlifting"):
            return [
                MesocycleBlueprint(
                    goal=MesocycleGoal.HYPERTROPHY,
                    focus=TrainingFocus.HYPERTROPHY,
                    phase=CyclePhase.HYPERTROPHY_I,
                    weeks=4,
                ),
                MesocycleBlueprint(
                    goal=MesocycleGoal.MAX_STRENGTH,
                    focus=TrainingFocus.STRENGTH,
                    phase=CyclePhase.STRENGTH_I,
                    weeks=5,
                    intensity_zone=IntensityDomain.STRENGTH,
                    target_rir=0.5,
                    target_rpe=9.0,
                ),
                MesocycleBlueprint(
                    goal=MesocycleGoal.MAX_STRENGTH,
                    focus=TrainingFocus.STRENGTH,
                    phase=CyclePhase.STRENGTH_II,
                    weeks=4,
                    intensity_zone=IntensityDomain.STRENGTH,
                    target_rir=0.0,
                    target_rpe=9.5,
                    deload_after=True,
                ),
                MesocycleBlueprint(
                    goal=MesocycleGoal.POWER,
                    focus=TrainingFocus.POWER,
                    phase=CyclePhase.PEAKING,
                    weeks=3,
                    intensity_zone=IntensityDomain.POWER,
                    target_rir=0.0,
                    target_rpe=9.5,
                    deload_after=True,
                ),
            ]
        if goal in ("fat_loss", "cutting", "weight_loss"):
            return [
                MesocycleBlueprint(
                    goal=MesocycleGoal.HYPERTROPHY,
                    focus=TrainingFocus.HYPERTROPHY,
                    phase=CyclePhase.HYPERTROPHY_I,
                    weeks=6,
                ),
                MesocycleBlueprint(
                    goal=MesocycleGoal.CONDITIONING,
                    focus=TrainingFocus.CONDITIONING,
                    phase=CyclePhase.TRANSITION,
                    weeks=4,
                    deload_after=True,
                ),
                MesocycleBlueprint(
                    goal=MesocycleGoal.HYPERTROPHY,
                    focus=TrainingFocus.HYPERTROPHY,
                    phase=CyclePhase.HYPERTROPHY_II,
                    weeks=6,
                ),
                MesocycleBlueprint(
                    goal=MesocycleGoal.MAINTENANCE,
                    focus=TrainingFocus.MAINTENANCE,
                    phase=CyclePhase.MAINTENANCE,
                    weeks=4,
                    min_volume=6,
                    max_volume=12,
                    deload_after=True,
                ),
            ]
        # default generic
        base = MesocycleBlueprint(goal=MesocycleGoal.HYPERTROPHY)
        repeat = total_weeks // base.weeks
        remainder = total_weeks % base.weeks
        blueprints = [base] * repeat
        if remainder:
            blueprints.append(MesocycleBlueprint(weeks=remainder))
        return blueprints

    def _build_microcycle(
        self,
        phase: CyclePhase,
        focus: TrainingFocus,
        progression_model: ProgressionModel,
        weeks: int,
        start_week: int,
        sessions_per_week: int,
        split_style: str,
        intensity_zone: IntensityDomain,
        target_rir: float,
    ) -> Microcycle:
        week_plans: list[WeekPlan] = []
        progression_blocks = self.generate_progression_block(
            VolumeAllocation(), weeks=weeks
        )

        for w in range(weeks):
            week_num = start_week + w
            vol = progression_blocks[w] if w < len(progression_blocks) else VolumeAllocation()
            recovery = self.generate_recovery_budget(sessions_per_week)
            nutrition = self.generate_nutrition_budget()
            fatigue = self.allocation.compute_fatigue_budget(vol, recovery)
            day_types = self.generate_weekly_split(
                sessions_per_week=sessions_per_week,
                split_style=split_style,
                week_number=week_num,
                is_deload=False,
            )

            sessions: list[SessionPlan] = []
            for d, day_type in enumerate(day_types):
                if day_type == DayType.REST:
                    sessions.append(SessionPlan(
                        session_id=_generate_id("rest"),
                        week=week_num, day_of_week=d, day_type=DayType.REST,
                        estimated_duration_minutes=0,
                    ))
                    continue
                session = self.generate_daily_session(
                    day_type=day_type,
                    week_number=week_num,
                    day_of_week=d,
                    focus=focus,
                    is_deload=False,
                    volume_allocation=vol,
                )
                sessions.append(session)

            week_plans.append(WeekPlan(
                week_number=week_num,
                sessions=sessions,
                is_deload_week=False,
                is_transition_week=False,
                total_fatigue_budget=fatigue,
                recovery_budget=recovery,
                nutrition_budget=nutrition,
            ))

        return Microcycle(
            microcycle_id=_generate_id("micro"),
            phase=phase,
            weeks=week_plans,
            focus=focus,
            progression_model=progression_model,
            week_count=weeks,
            start_week=start_week,
        )

    def _build_deload_block(
        self,
        week_number: int,
        sessions_per_week: int = 3,
        split_style: str = "ppl_ul",
        reason: str = "",
    ) -> list[WeekPlan]:
        recovery = RecoveryBudget(
            available_hours_per_night=9.0,
            sleep_quality_score=0.85,
            rest_days_per_week=4,
        )
        nutrition = NutritionBudget(
            target_calories=2200,
            protein_g=150,
            carbs_g=200,
            fat_g=70,
        )
        fatigue = FatigueBudget(
            total_fatigue_units=50,
            max_per_session=12,
            recovery_rate_per_day=25,
        )
        vol = VolumeAllocation(
            sets_per_exercise=(2, 3),
            reps_per_set=(6, 10),
            total_sets_per_session=8,
            total_sets_per_muscle_group=6,
            rir_target=3.0,
            rpe_cap=6.0,
            intensity_percent=(0.40, 0.55),
        )

        deload_sessions = max(2, min(sessions_per_week // 2, 4))
        sessions: list[SessionPlan] = []
        for d in range(7):
            if d < deload_sessions:
                session = SessionPlan(
                    session_id=_generate_id("deload_session"),
                    week=week_number,
                    day_of_week=d,
                    day_type=[DayType.PUSH, DayType.PULL, DayType.LEGS,
                              DayType.UPPER, DayType.LOWER][d % 5],
                    training_focus=TrainingFocus.RECOVERY,
                    exercises=[],
                    volume_allocation=vol,
                    fatigue_budget=fatigue,
                    estimated_duration_minutes=30,
                    is_deload=True,
                    notes=f"Deload: {reason or 'Scheduled recovery week'}. Reduce load 40-50%.",
                )
                sessions.append(session)
            else:
                sessions.append(SessionPlan(
                    session_id=_generate_id("rest"),
                    week=week_number, day_of_week=d, day_type=DayType.REST,
                    estimated_duration_minutes=0,
                    is_recovery=True,
                ))

        return [WeekPlan(
            week_number=week_number,
            sessions=sessions,
            is_deload_week=True,
            total_fatigue_budget=fatigue,
            recovery_budget=recovery,
            nutrition_budget=nutrition,
            notes=f"Deload Week: {reason or 'Recovery'}",
        )]

    def _generate_deload_split(self, sessions_per_week: int) -> list[DayType]:
        count = max(2, min(sessions_per_week // 2, 4))
        days: list[DayType] = []
        template = [DayType.PUSH, DayType.PULL, DayType.LEGS,
                    DayType.UPPER, DayType.LOWER]
        for d in range(7):
            if d < count:
                days.append(template[d % len(template)])
            else:
                days.append(DayType.REST)
        return days

    def _generate_custom_split(self, sessions_per_week: int) -> list[DayType]:
        templates = [
            DayType.UPPER, DayType.LOWER, DayType.REST,
            DayType.PUSH, DayType.PULL, DayType.LEGS, DayType.REST,
        ]
        training_days = [d for d in templates if d != DayType.REST]
        result: list[DayType] = []
        ti = 0
        for d in range(7):
            if d < sessions_per_week:
                result.append(training_days[ti % len(training_days)])
                ti += 1
            else:
                result.append(DayType.REST)
        return result

    def _select_progression_model(self, goal: MesocycleGoal) -> ProgressionModel:
        return {
            MesocycleGoal.MAX_STRENGTH: ProgressionModel.LINEAR_PROGRESSION,
            MesocycleGoal.HYPERTROPHY: ProgressionModel.DOUBLE_PROGRESSION,
            MesocycleGoal.STRENGTH_ENDURANCE: ProgressionModel.RAMPING,
            MesocycleGoal.POWER: ProgressionModel.WAVE_LOADING,
            MesocycleGoal.CONDITIONING: ProgressionModel.AUTO_REGULATION,
            MesocycleGoal.FAT_LOSS: ProgressionModel.AUTO_REGULATION,
            MesocycleGoal.MAINTENANCE: ProgressionModel.DOUBLE_PROGRESSION,
            MesocycleGoal.REHAB: ProgressionModel.AUTO_REGULATION,
        }[goal]

    @staticmethod
    def _compute_end_date(
        start_date: str | None,
        duration_weeks: int,
    ) -> str:
        if not start_date:
            return ""
        try:
            start = date.fromisoformat(start_date)
            end = start + timedelta(weeks=duration_weeks) - timedelta(days=1)
            return end.isoformat()
        except (ValueError, TypeError):
            return ""
