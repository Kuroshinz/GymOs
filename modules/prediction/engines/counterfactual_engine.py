"""Counterfactual Engine — answers "what if" questions by computing deltas.

Supported queries:
  - What if sleep = 8h?
  - What if calories +250?
  - What if miss workout?
  - What if increase chest volume?
  - What if deload now?
"""

from __future__ import annotations

from modules.prediction.domain import CounterfactualQuery, CounterfactualResult, CounterfactualType
from modules.prediction.engines import (
    BodyweightPredictionEngine,
    ConsistencyPredictionEngine,
    DeloadPredictionEngine,
    FatiguePredictionEngine,
    PlateauPredictionEngine,
    PRPredictionEngine,
    RecoveryPredictionEngine,
    VolumePredictionEngine,
)


class CounterfactualEngine:
    """Evaluates counterfactual (what-if) scenarios against a baseline.

    Each what-if query modifies a single input parameter and re-runs the
    relevant prediction engine(s), returning the delta vs baseline.
    """

    def __init__(self) -> None:
        self._plateau = PlateauPredictionEngine()
        self._pr = PRPredictionEngine()
        self._recovery = RecoveryPredictionEngine()
        self._fatigue = FatiguePredictionEngine()
        self._bodyweight = BodyweightPredictionEngine()
        self._volume = VolumePredictionEngine()
        self._consistency = ConsistencyPredictionEngine()
        self._deload = DeloadPredictionEngine()

    def _get_default_baseline(self) -> dict:
        return {
            "sleep_avg": 6.5,
            "sleep_trend": -0.3,
            "calorie_surplus_avg": 0.0,
            "calorie_adherence": 0.8,
            "current_bodyweight": 75.0,
            "bodyweight_history": [75.0, 75.2, 75.1, 75.3],
            "recent_volume_7d": 14000,
            "recent_volume_14d": 26000,
            "current_fatigue": 45.0,
            "fatigue_trend": 1.0,
            "recovery_scores": [70, 68, 66, 69, 67],
            "current_recovery_score": 67,
            "days_since_deload": 30,
            "weeks_since_last_deload": 6,
            "stress_trend": 0.2,
            "training_volume_trend": 2.0,
            "session_frequency": 4.0,
            "current_streak": 5,
            "missed_last_7d": 2,
            "recovery_avg": 67.0,
            "recent_completion_rate": 0.75,
            "motivation_score": 0.6,
            "estimated_mrv": 20000.0,
            "current_weekly_volume": 14000.0,
            "weekly_volumes": [13000, 14000],
            "session_count": 4,
            "average_rpe": 7.0,
            "recent_volume_trend": 100.0,
            "average_rir": 2.0,
            "recovery_score": 67.0,
            "recent_prs": 1,
            "days_since_last_pr": 14,
            "consistency_streak": 5,
            "is_deload_week": False,
            "volume_change_percent": 0.0,
            "reps_in_rir_avg": 2.0,
            "days_since_weight_change": 14,
            "recent_pr_count": 1,
            "session_count_last_14d": 7,
            "volume_ratio_14d_7d": 1.1,
            "session_count_7d": 4,
            "deload_frequency_weeks": 6,
            "stress_avg": 35.0,
            "days_since_last_miss": 1,
        }

    def _slice_kwargs(self, kwargs: dict, keys: list[str]) -> dict:
        return {k: v for k, v in kwargs.items() if k in keys}

    def evaluate(self, query: CounterfactualQuery, baseline_kwargs: dict | None = None) -> CounterfactualResult:
        kwargs = baseline_kwargs or self._get_default_baseline()
        mods = dict(kwargs)
        affected: list[str] = []
        bl_prediction = 0.0
        cf_prediction = 0.0

        if query.cf_type == CounterfactualType.SLEEP:
            mods["sleep_avg"] = query.proposed_value
            mods["sleep_trend"] = query.proposed_value - query.current_value
            bl_prediction = self._recovery.predict(**self._slice_kwargs(kwargs, [
                "recovery_scores", "sleep_trend", "stress_trend",
                "training_volume_trend", "current_recovery_score", "days_since_deload",
            ])).value
            cf_prediction = self._recovery.predict(**self._slice_kwargs(mods, [
                "recovery_scores", "sleep_trend", "stress_trend",
                "training_volume_trend", "current_recovery_score", "days_since_deload",
            ])).value
            affected = ["Recovery Score", "Fatigue Score", "Readiness"]

        elif query.cf_type == CounterfactualType.CALORIES:
            mods["calorie_surplus_avg"] = query.proposed_value
            bl_prediction = self._bodyweight.predict(**self._slice_kwargs(kwargs, [
                "bodyweight_history", "calorie_surplus_avg",
                "current_bodyweight", "calorie_adherence",
            ])).value
            cf_prediction = self._bodyweight.predict(**self._slice_kwargs(mods, [
                "bodyweight_history", "calorie_surplus_avg",
                "current_bodyweight", "calorie_adherence",
            ])).value
            affected = ["Bodyweight", "Goal ETA"]

        elif query.cf_type == CounterfactualType.WORKOUT_MISS:
            mods["missed_last_7d"] = kwargs.get("missed_last_7d", 2) + 1
            mods["current_streak"] = 0
            mods["days_since_last_miss"] = 0
            bl_prediction = self._consistency.predict(**self._slice_kwargs(kwargs, [
                "current_streak", "missed_last_7d", "recovery_avg",
                "recent_completion_rate", "motivation_score", "days_since_last_miss",
            ])).probability
            cf_prediction = self._consistency.predict(**self._slice_kwargs(mods, [
                "current_streak", "missed_last_7d", "recovery_avg",
                "recent_completion_rate", "motivation_score", "days_since_last_miss",
            ])).probability
            affected = ["Consistency", "Workout Completion"]

        elif query.cf_type == CounterfactualType.VOLUME_CHANGE:
            mods["recent_volume_7d"] = query.proposed_value
            mods["current_weekly_volume"] = query.proposed_value
            bl_prediction = self._fatigue.predict(**self._slice_kwargs(kwargs, [
                "current_fatigue", "recent_volume_7d", "recent_volume_14d",
                "sleep_avg", "stress_avg", "days_since_deload", "session_frequency",
            ])).value
            cf_prediction = self._fatigue.predict(**self._slice_kwargs(mods, [
                "current_fatigue", "recent_volume_7d", "recent_volume_14d",
                "sleep_avg", "stress_avg", "days_since_deload", "session_frequency",
            ])).value
            affected = ["Fatigue Score", "MRV Risk", "Plateau Risk"]

        elif query.cf_type == CounterfactualType.DELOAD_NOW:
            mods["days_since_deload"] = 0
            mods["weeks_since_last_deload"] = 0
            mods["is_deload_week"] = True
            bl_prediction = self._recovery.predict(**self._slice_kwargs(kwargs, [
                "recovery_scores", "sleep_trend", "stress_trend",
                "training_volume_trend", "current_recovery_score", "days_since_deload",
            ])).value
            cf_prediction = self._recovery.predict(**self._slice_kwargs(mods, [
                "recovery_scores", "sleep_trend", "stress_trend",
                "training_volume_trend", "current_recovery_score", "days_since_deload",
            ])).value
            affected = ["Recovery Score", "Fatigue", "Deload Risk", "PR Probability"]

        else:
            bl_prediction = 0.0
            cf_prediction = 0.0
            affected = ["Unknown"]

        return CounterfactualResult(
            query=query,
            baseline_prediction=round(bl_prediction, 4),
            counterfactual_prediction=round(cf_prediction, 4),
            explanation=self._build_explanation(query, bl_prediction, cf_prediction),
            affected_predictions=affected,
        )

    def evaluate_sleep_8h(self, baseline_kwargs: dict | None = None) -> CounterfactualResult:
        return self.evaluate(CounterfactualQuery(
            cf_type=CounterfactualType.SLEEP,
            parameter="sleep_avg", current_value=6.5, proposed_value=8.0, unit="hours",
        ), baseline_kwargs)

    def evaluate_calories_plus_250(self, baseline_kwargs: dict | None = None) -> CounterfactualResult:
        return self.evaluate(CounterfactualQuery(
            cf_type=CounterfactualType.CALORIES,
            parameter="calorie_surplus_avg", current_value=0.0, proposed_value=250.0, unit="kcal",
        ), baseline_kwargs)

    def evaluate_miss_workout(self, baseline_kwargs: dict | None = None) -> CounterfactualResult:
        return self.evaluate(CounterfactualQuery(
            cf_type=CounterfactualType.WORKOUT_MISS,
            parameter="missed_last_7d", current_value=2, proposed_value=3, unit="sessions",
        ), baseline_kwargs)

    def evaluate_increase_chest_volume(self, baseline_kwargs: dict | None = None) -> CounterfactualResult:
        kwargs = baseline_kwargs or self._get_default_baseline()
        current_vol = kwargs.get("recent_volume_7d", 14000)
        increased = current_vol * 1.15
        return self.evaluate(CounterfactualQuery(
            cf_type=CounterfactualType.VOLUME_CHANGE,
            parameter="recent_volume_7d", current_value=current_vol,
            proposed_value=increased, unit="kg",
        ), kwargs)

    def evaluate_deload_now(self, baseline_kwargs: dict | None = None) -> CounterfactualResult:
        return self.evaluate(CounterfactualQuery(
            cf_type=CounterfactualType.DELOAD_NOW,
            parameter="days_since_deload", current_value=30, proposed_value=0, unit="days",
        ), baseline_kwargs)

    def evaluate_all(self, baseline_kwargs: dict | None = None) -> list[CounterfactualResult]:
        return [
            self.evaluate_sleep_8h(baseline_kwargs),
            self.evaluate_calories_plus_250(baseline_kwargs),
            self.evaluate_miss_workout(baseline_kwargs),
            self.evaluate_increase_chest_volume(baseline_kwargs),
            self.evaluate_deload_now(baseline_kwargs),
        ]

    @staticmethod
    def _build_explanation(query: CounterfactualQuery, baseline: float, cf: float) -> str:
        delta = cf - baseline
        pct = (delta / baseline * 100) if baseline != 0 else 0.0
        direction = "increase" if delta > 0 else "decrease"
        if query.cf_type == CounterfactualType.SLEEP:
            return f"Increasing sleep from {query.current_value}h to {query.proposed_value}h would {direction} recovery score by {abs(delta):.1f} points ({abs(pct):.1f}%)"
        elif query.cf_type == CounterfactualType.CALORIES:
            return f"Adding {query.proposed_value:.0f}kcal would {direction} bodyweight by {abs(delta):.2f}kg ({abs(pct):.1f}%)"
        elif query.cf_type == CounterfactualType.WORKOUT_MISS:
            return f"Missing a workout would {direction} consistency probability by {abs(pct):.1f}%"
        elif query.cf_type == CounterfactualType.VOLUME_CHANGE:
            return f"Changing weekly volume to {query.proposed_value:.0f}kg would {direction} fatigue score by {abs(delta):.1f} points"
        elif query.cf_type == CounterfactualType.DELOAD_NOW:
            return f"Deloading now would {direction} recovery score by {abs(delta):.1f} points ({abs(pct):.1f}%)"
        return f"Changing {query.parameter} from {query.current_value} to {query.proposed_value} would {direction} prediction by {abs(delta):.4f}"
