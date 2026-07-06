"""Planning Metrics — quantifies plan quality, scientific validity, balance, and adherence.

Provides objective scores for every generated plan.
"""

from __future__ import annotations

from dataclasses import dataclass

from shared.planning.domain import (
    Macrocycle,
    MesocycleGoal,
)
from shared.planning.validator import PlanningValidator


@dataclass
class PlanQuality:
    overall: float = 0.0
    scientific_score: float = 0.0
    recovery_balance: float = 0.0
    fatigue_balance: float = 0.0
    specificity: float = 0.0
    adherence_prediction: float = 0.0
    volume_distribution: float = 0.0
    progression_quality: float = 0.0

    @property
    def grade(self) -> str:
        if self.overall >= 0.90:
            return "A"
        if self.overall >= 0.80:
            return "B"
        if self.overall >= 0.70:
            return "C"
        if self.overall >= 0.60:
            return "D"
        return "F"

    @property
    def is_acceptable(self) -> bool:
        return self.overall >= 0.70


@dataclass
class ScientificScore:
    overall: float = 0.0
    periodization: float = 0.0
    progression: float = 0.0
    deload_placement: float = 0.0
    intensity_zone_accuracy: float = 0.0
    volume_guidelines: float = 0.0
    recovery_integration: float = 0.0

    def __post_init__(self) -> None:
        self.overall = round(
            self.periodization * 0.20 +
            self.progression * 0.20 +
            self.deload_placement * 0.15 +
            self.intensity_zone_accuracy * 0.15 +
            self.volume_guidelines * 0.15 +
            self.recovery_integration * 0.15,
            2,
        )


@dataclass
class RecoveryBalance:
    overall: float = 0.0
    rest_day_adequacy: float = 0.0
    deload_frequency: float = 0.0
    sleep_alignment: float = 0.0
    fatigue_to_recovery_ratio: float = 0.0

    @property
    def needs_attention(self) -> bool:
        return self.overall < 0.5

    @property
    def healthy(self) -> bool:
        return self.overall >= 0.7


@dataclass
class FatigueBalance:
    overall: float = 0.0
    weekly_fatigue_load: float = 0.0
    session_fatigue_spike: float = 0.0
    fatigue_distribution: float = 0.0

    @property
    def is_balanced(self) -> bool:
        return self.overall >= 0.6

    @property
    def is_risky(self) -> bool:
        return self.overall < 0.4


@dataclass
class SpecificityScore:
    overall: float = 0.0
    goal_alignment: float = 0.0
    exercise_selection: float = 0.0
    intensity_matching: float = 0.0
    volume_targeting: float = 0.0

    @property
    def is_specific(self) -> bool:
        return self.overall >= 0.75


@dataclass
class AdherencePrediction:
    overall: float = 0.0
    time_commitment: float = 0.0
    session_duration: float = 0.0
    frequency_feasibility: float = 0.0
    progression_sustainability: float = 0.0
    recovery_buffer: float = 0.0

    @property
    def predicted_to_stick(self) -> bool:
        return self.overall >= 0.65

    @property
    def risk_level(self) -> str:
        if self.overall >= 0.8:
            return "low"
        if self.overall >= 0.6:
            return "moderate"
        if self.overall >= 0.4:
            return "elevated"
        return "high"


@dataclass
class PlanningMetrics:
    total_plans: int = 0
    active_plans: int = 0
    completed_plans: int = 0
    avg_plan_quality: float = 0.0
    avg_scientific_score: float = 0.0
    avg_recovery_balance: float = 0.0
    avg_fatigue_balance: float = 0.0
    avg_specificity: float = 0.0
    avg_adherence_prediction: float = 0.0
    total_validation_errors: int = 0
    total_validation_warnings: int = 0
    total_mesocycles: int = 0
    total_sessions: int = 0
    total_sets: int = 0

    @staticmethod
    def compute(plans: list[Macrocycle], validator: PlanningValidator) -> PlanningMetrics:
        if not plans:
            return PlanningMetrics()

        total = len(plans)
        qualities: list[float] = []
        scientific: list[float] = []
        recovery: list[float] = []
        fatigue: list[float] = []
        specificities: list[float] = []
        adherences: list[float] = []
        total_errors = 0
        total_warnings = 0
        total_meso = 0
        total_sess = 0
        total_set = 0

        scorer = PlanningMetricsScorer()

        for plan in plans:
            pq = scorer.score_plan_quality(plan)
            qualities.append(pq.overall)
            scientific.append(pq.scientific_score)
            recovery.append(pq.recovery_balance)
            fatigue.append(pq.fatigue_balance)
            specificities.append(pq.specificity)
            adherences.append(pq.adherence_prediction)

            validation = validator.validate(plan)
            total_errors += validation.error_count
            total_warnings += validation.warning_count
            total_meso += plan.total_mesocycles
            total_sess += plan.total_sessions
            total_set += plan.total_sets

        avg = lambda vals: sum(vals) / len(vals) if vals else 0.0

        return PlanningMetrics(
            total_plans=total,
            active_plans=total,
            avg_plan_quality=round(avg(qualities), 2),
            avg_scientific_score=round(avg(scientific), 2),
            avg_recovery_balance=round(avg(recovery), 2),
            avg_fatigue_balance=round(avg(fatigue), 2),
            avg_specificity=round(avg(specificities), 2),
            avg_adherence_prediction=round(avg(adherences), 2),
            total_validation_errors=total_errors,
            total_validation_warnings=total_warnings,
            total_mesocycles=total_meso,
            total_sessions=total_sess,
            total_sets=total_set,
        )


class PlanningMetricsScorer:
    """Scores individual plans across all quality dimensions."""

    @staticmethod
    def score_plan_quality(macrocycle: Macrocycle) -> PlanQuality:
        scientific = PlanningMetricsScorer._compute_scientific(macrocycle)
        recovery_bal = PlanningMetricsScorer._compute_recovery_balance(macrocycle)
        fatigue_bal = PlanningMetricsScorer._compute_fatigue_balance(macrocycle)
        specificity = PlanningMetricsScorer._compute_specificity(macrocycle)
        adherence = PlanningMetricsScorer._compute_adherence_prediction(macrocycle)
        volume_dist = PlanningMetricsScorer._compute_volume_distribution(macrocycle)
        progression = PlanningMetricsScorer._compute_progression_quality(macrocycle)

        overall = round(
            scientific.overall * 0.20 +
            recovery_bal.overall * 0.15 +
            fatigue_bal.overall * 0.15 +
            specificity.overall * 0.15 +
            adherence.overall * 0.15 +
            volume_dist * 0.10 +
            progression * 0.10,
            2,
        )
        return PlanQuality(
            overall=overall,
            scientific_score=scientific.overall,
            recovery_balance=recovery_bal.overall,
            fatigue_balance=fatigue_bal.overall,
            specificity=specificity.overall,
            adherence_prediction=adherence.overall,
            volume_distribution=volume_dist,
            progression_quality=progression,
        )

    @staticmethod
    def score_scientific(macrocycle: Macrocycle) -> ScientificScore:
        return PlanningMetricsScorer._compute_scientific(macrocycle)

    @staticmethod
    def score_recovery_balance(macrocycle: Macrocycle) -> RecoveryBalance:
        return PlanningMetricsScorer._compute_recovery_balance(macrocycle)

    @staticmethod
    def score_fatigue_balance(macrocycle: Macrocycle) -> FatigueBalance:
        return PlanningMetricsScorer._compute_fatigue_balance(macrocycle)

    @staticmethod
    def score_specificity(macrocycle: Macrocycle) -> SpecificityScore:
        return PlanningMetricsScorer._compute_specificity(macrocycle)

    @staticmethod
    def score_adherence(macrocycle: Macrocycle) -> AdherencePrediction:
        return PlanningMetricsScorer._compute_adherence_prediction(macrocycle)

    # ── Internal computation methods ──────────────────────────

    @staticmethod
    def _compute_scientific(macrocycle: Macrocycle) -> ScientificScore:
        periodization = 0.0
        progression = 0.0
        deload_placement = 0.0
        intensity_accuracy = 0.0
        volume_guidelines = 0.0
        recovery_integration = 0.0

        if macrocycle.mesocycles:
            valid_goals = sum(1 for m in macrocycle.mesocycles
                              if m.goal in (MesocycleGoal.HYPERTROPHY,
                                            MesocycleGoal.MAX_STRENGTH,
                                            MesocycleGoal.STRENGTH_ENDURANCE,
                                            MesocycleGoal.CONDITIONING,
                                            MesocycleGoal.MAINTENANCE,
                                            MesocycleGoal.FAT_LOSS,
                                            MesocycleGoal.POWER))
            periodization = valid_goals / len(macrocycle.mesocycles)

        if macrocycle.mesocycles:
            varied = sum(1 for i in range(1, len(macrocycle.mesocycles))
                         if macrocycle.mesocycles[i].goal != macrocycle.mesocycles[i - 1].goal)
            progression = min(1.0, varied / max(1, len(macrocycle.mesocycles) - 1) * 1.2)

        total_weeks = len(macrocycle.weeks)
        deload_count = len(macrocycle.deload_weeks)
        if total_weeks > 0:
            deload_per_12_weeks = deload_count / (total_weeks / 12) if total_weeks >= 12 else 1
            deload_placement = min(1.0, deload_per_12_weeks * 0.5)

        intensity_accuracy = 1.0

        has_excessive = any(
            w.total_sets > 25 for w in macrocycle.weeks if not w.is_deload_week
        )
        has_deficient = any(
            w.total_sets < 8 for w in macrocycle.weeks if not w.is_deload_week
        )
        volume_guidelines = 0.0 if has_excessive else (0.5 if has_deficient else 1.0)

        recovery_integration = 0.5 if deload_count > 0 else 0.0
        if deload_count > 0 and any(w.recovery_budget.recovery_capacity > 0.6 for w in macrocycle.weeks):
            recovery_integration = 0.8

        return ScientificScore(
            periodization=periodization,
            progression=progression,
            deload_placement=deload_placement,
            intensity_zone_accuracy=intensity_accuracy,
            volume_guidelines=volume_guidelines,
            recovery_integration=recovery_integration,
        )

    @staticmethod
    def _compute_recovery_balance(macrocycle: Macrocycle) -> RecoveryBalance:
        rest_adequacy = 0.0
        deload_freq = 0.0
        sleep_align = 0.0
        fatigue_ratio = 0.0

        weeks = macrocycle.weeks
        if weeks:
            weeks_with_rest = sum(1 for w in weeks
                                  if any(s.day_type.value in ("rest", "active_recovery")
                                         for s in w.sessions))
            rest_adequacy = weeks_with_rest / len(weeks)

        total_weeks = len(weeks)
        deload_count = len(macrocycle.deload_weeks)
        if total_weeks >= 6:
            ideal_deloads = max(1, total_weeks // 6)
            deload_freq = min(1.0, deload_count / ideal_deloads)
        else:
            deload_freq = 0.5

        recovery_caps = [w.recovery_budget.recovery_capacity for w in weeks if w.recovery_budget]
        if recovery_caps:
            sleep_align = sum(recovery_caps) / len(recovery_caps)

        sets_per_week = [w.total_sets for w in weeks if not w.is_deload_week]
        if sets_per_week:
            avg_weekly = sum(sets_per_week) / len(sets_per_week)
            fatigue_ratio = max(0.0, 1.0 - avg_weekly / 100.0)

        overall = round(
            rest_adequacy * 0.30 +
            deload_freq * 0.25 +
            sleep_align * 0.25 +
            fatigue_ratio * 0.20,
            2,
        )
        return RecoveryBalance(
            overall=overall,
            rest_day_adequacy=rest_adequacy,
            deload_frequency=deload_freq,
            sleep_alignment=sleep_align,
            fatigue_to_recovery_ratio=fatigue_ratio,
        )

    @staticmethod
    def _compute_fatigue_balance(macrocycle: Macrocycle) -> FatigueBalance:
        weeks = macrocycle.weeks
        if not weeks:
            return FatigueBalance()

        weekly_sets = [w.total_sets for w in weeks if not w.is_deload_week]
        if not weekly_sets:
            return FatigueBalance()

        avg_weekly = sum(weekly_sets) / len(weekly_sets)
        weekly_fatigue = min(1.0, 1.0 - abs(avg_weekly - 18.0) / 30.0)

        max_session_sets = max(
            (s.total_sets for w in weeks for s in w.sessions if not s.is_deload),
            default=0,
        )
        session_spike = min(1.0, 1.0 - max(0, max_session_sets - 20) / 20.0)

        if len(weekly_sets) > 1:
            variance = sum((s - avg_weekly) ** 2 for s in weekly_sets) / len(weekly_sets)
            cv = (variance ** 0.5) / avg_weekly if avg_weekly > 0 else 0
            distribution = max(0.0, 1.0 - cv)
        else:
            distribution = 0.5

        overall = round(
            weekly_fatigue * 0.40 +
            session_spike * 0.30 +
            distribution * 0.30,
            2,
        )
        return FatigueBalance(
            overall=overall,
            weekly_fatigue_load=weekly_fatigue,
            session_fatigue_spike=session_spike,
            fatigue_distribution=distribution,
        )

    @staticmethod
    def _compute_specificity(macrocycle: Macrocycle) -> SpecificityScore:
        if not macrocycle.mesocycles:
            return SpecificityScore()

        goal = macrocycle.overall_goal.lower()
        goal_alignment = 0.5
        if goal in ("hypertrophy", "muscle_growth"):
            has_hypertrophy = any(
                m.goal == MesocycleGoal.HYPERTROPHY for m in macrocycle.mesocycles
            )
            goal_alignment = 0.9 if has_hypertrophy else 0.3
        elif goal in ("strength", "powerlifting"):
            has_strength = any(
                m.goal == MesocycleGoal.MAX_STRENGTH for m in macrocycle.mesocycles
            )
            goal_alignment = 0.9 if has_strength else 0.3
        elif goal in ("fat_loss", "cutting", "weight_loss"):
            has_conditioning = any(
                m.goal == MesocycleGoal.CONDITIONING for m in macrocycle.mesocycles
            )
            goal_alignment = 0.8 if has_conditioning else 0.4

        exercise_selection = 0.7
        intensity_matching = 0.7
        volume_targeting = 0.7

        if goal in ("hypertrophy", "muscle_growth"):
            intensity_matching = 0.85
            volume_targeting = 0.85
        elif goal in ("strength", "powerlifting"):
            intensity_matching = 0.90
            volume_targeting = 0.70

        overall = round(
            goal_alignment * 0.35 +
            exercise_selection * 0.20 +
            intensity_matching * 0.25 +
            volume_targeting * 0.20,
            2,
        )
        return SpecificityScore(
            overall=overall,
            goal_alignment=goal_alignment,
            exercise_selection=exercise_selection,
            intensity_matching=intensity_matching,
            volume_targeting=volume_targeting,
        )

    @staticmethod
    def _compute_adherence_prediction(macrocycle: Macrocycle) -> AdherencePrediction:
        weeks = macrocycle.weeks
        if not weeks:
            return AdherencePrediction()

        training_weeks = [w for w in weeks if not w.is_deload_week]
        if not training_weeks:
            return AdherencePrediction()

        avg_sessions = sum(w.session_count for w in training_weeks) / len(training_weeks)
        time_com = max(0.0, 1.0 - abs(avg_sessions - 4.0) / 8.0)

        avg_duration = sum(
            s.estimated_duration_minutes for w in training_weeks for s in w.training_sessions
        ) / max(1, sum(len(w.training_sessions) for w in training_weeks))
        duration_score = max(0.0, 1.0 - max(0, avg_duration - 45) / 90.0)

        freq_feasible = max(0.0, 1.0 - max(0, avg_sessions - 5) / 5.0)

        weekly_sets = [w.total_sets for w in training_weeks]
        if len(weekly_sets) > 1:
            max_increase = max(
                (weekly_sets[i] - weekly_sets[i - 1]) / max(1, weekly_sets[i - 1])
                for i in range(1, len(weekly_sets))
            )
            sustainability = max(0.0, 1.0 - max(0, max_increase - 0.1) / 0.3)
        else:
            sustainability = 0.5

        deload_present = len(macrocycle.deload_weeks) > 0
        recovery_buffer = 0.8 if deload_present else 0.3

        overall = round(
            time_com * 0.25 +
            duration_score * 0.20 +
            freq_feasible * 0.20 +
            sustainability * 0.20 +
            recovery_buffer * 0.15,
            2,
        )
        return AdherencePrediction(
            overall=overall,
            time_commitment=time_com,
            session_duration=duration_score,
            frequency_feasibility=freq_feasible,
            progression_sustainability=sustainability,
            recovery_buffer=recovery_buffer,
        )

    @staticmethod
    def _compute_volume_distribution(macrocycle: Macrocycle) -> float:
        weeks = macrocycle.weeks
        training_weeks = [w for w in weeks if not w.is_deload_week]
        if len(training_weeks) < 2:
            return 0.5

        weekly_sets = [w.total_sets for w in training_weeks]
        mean = sum(weekly_sets) / len(weekly_sets)
        if mean == 0:
            return 0.5
        variance = sum((s - mean) ** 2 for s in weekly_sets) / len(weekly_sets)
        cv = (variance ** 0.5) / mean
        return max(0.0, 1.0 - cv * 2)

    @staticmethod
    def _compute_progression_quality(macrocycle: Macrocycle) -> float:
        weeks = macrocycle.weeks
        training_weeks = [w for w in weeks if not w.is_deload_week]
        if len(training_weeks) < 2:
            return 0.5

        weekly_sets = [w.total_sets for w in training_weeks]
        increasing = sum(
            1 for i in range(1, len(weekly_sets))
            if weekly_sets[i] > weekly_sets[i - 1]
        )
        progression_ratio = increasing / max(1, len(weekly_sets) - 1)
        return min(1.0, progression_ratio * 1.5)
