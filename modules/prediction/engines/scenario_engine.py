"""Scenario Engine — models the effect of interventions on predictions.

Supports 10 interventions:
  Increase/Decrease Volume
  Early/Late Deload
  Increase/Decrease Calories
  Higher/Lower Sleep
  Higher/Lower Adherence
"""

from __future__ import annotations

from modules.prediction.domain import (
    PredictionConfidence,
    ScenarioComparison,
    ScenarioIntervention,
    ScenarioRanking,
    ScenarioResult,
)
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


class ScenarioBuilder:
    """Builds modified prediction inputs for a given intervention."""

    @staticmethod
    def build_modifiers(
        intervention: ScenarioIntervention,
        base_kwargs: dict,
    ) -> dict:
        mods = dict(base_kwargs)
        pct = 0.20

        if intervention == ScenarioIntervention.INCREASE_VOLUME:
            v7 = mods.get("recent_volume_7d", 14000)
            v14 = mods.get("recent_volume_14d", 26000)
            mods["recent_volume_7d"] = v7 * (1 + pct)
            mods["recent_volume_14d"] = v14 * (1 + pct * 0.5)
            mods["weekly_volumes"] = [v * (1 + pct * 0.5) for v in mods.get("weekly_volumes", [14000, 14000])]
            mods["current_weekly_volume"] = mods.get("current_weekly_volume", 14000) * (1 + pct)

        elif intervention == ScenarioIntervention.DECREASE_VOLUME:
            v7 = mods.get("recent_volume_7d", 14000)
            v14 = mods.get("recent_volume_14d", 26000)
            mods["recent_volume_7d"] = v7 * (1 - pct)
            mods["recent_volume_14d"] = v14 * (1 - pct * 0.5)
            mods["weekly_volumes"] = [v * (1 - pct * 0.5) for v in mods.get("weekly_volumes", [14000, 14000])]
            mods["current_weekly_volume"] = mods.get("current_weekly_volume", 14000) * (1 - pct)

        elif intervention == ScenarioIntervention.EARLY_DELOAD:
            mods["days_since_deload"] = 0
            mods["weeks_since_last_deload"] = 0
            mods["is_deload_week"] = True

        elif intervention == ScenarioIntervention.LATE_DELOAD:
            mods["days_since_deload"] = max(mods.get("days_since_deload", 30) + 14, 60)
            mods["weeks_since_last_deload"] = max(mods.get("weeks_since_last_deload", 6) + 2, 10)

        elif intervention == ScenarioIntervention.INCREASE_CALORIES:
            mods["calorie_surplus_avg"] = mods.get("calorie_surplus_avg", 0) + 250
            mods["calorie_adherence"] = min(mods.get("calorie_adherence", 0.8) * 1.05, 1.0)

        elif intervention == ScenarioIntervention.DECREASE_CALORIES:
            mods["calorie_surplus_avg"] = mods.get("calorie_surplus_avg", 0) - 250
            mods["calorie_adherence"] = max(mods.get("calorie_adherence", 0.8) * 0.95, 0.3)

        elif intervention == ScenarioIntervention.HIGHER_SLEEP:
            mods["sleep_avg"] = min(mods.get("sleep_avg", 7.0) + 1.0, 10.0)
            mods["sleep_trend"] = mods.get("sleep_trend", 0) + 0.3

        elif intervention == ScenarioIntervention.LOWER_SLEEP:
            mods["sleep_avg"] = max(mods.get("sleep_avg", 7.0) - 1.5, 4.0)
            mods["sleep_trend"] = mods.get("sleep_trend", 0) - 0.5

        elif intervention == ScenarioIntervention.HIGHER_ADHERENCE:
            mods["calorie_adherence"] = min(mods.get("calorie_adherence", 0.8) * 1.15, 1.0)
            mods["recent_completion_rate"] = min(mods.get("recent_completion_rate", 0.8) * 1.1, 1.0)
            mods["motivation_score"] = min(mods.get("motivation_score", 0.7) + 0.15, 1.0)

        elif intervention == ScenarioIntervention.LOWER_ADHERENCE:
            mods["calorie_adherence"] = max(mods.get("calorie_adherence", 0.8) * 0.7, 0.2)
            mods["recent_completion_rate"] = max(mods.get("recent_completion_rate", 0.8) * 0.8, 0.2)
            mods["motivation_score"] = max(mods.get("motivation_score", 0.7) - 0.2, 0.1)

        return mods


class PredictionScenarioEngine:
    """Evaluates scenarios (what-if interventions) against a baseline prediction.

    For each supported intervention, computes the delta across 8 prediction
    engines and returns ScenarioResult objects with comparisons.
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

    def _get_baseline_kwargs(self) -> dict:
        return {
            "recent_volume_7d": 14000.0,
            "recent_volume_14d": 26000.0,
            "weekly_volumes": [13000, 14000],
            "current_weekly_volume": 14000.0,
            "volume_change_percent": 0.0,
            "reps_in_rir_avg": 2.0,
            "days_since_weight_change": 14,
            "recent_pr_count": 1,
            "session_count_last_14d": 7,
            "consistency_streak": 8,
            "recent_volume_trend": 100.0,
            "average_rir": 2.0,
            "recovery_score": 70.0,
            "is_deload_week": False,
            "recovery_scores": [72, 70, 68, 71, 69],
            "sleep_trend": 0.0,
            "stress_trend": 0.0,
            "training_volume_trend": 1.0,
            "current_recovery_score": 70.0,
            "days_since_deload": 30,
            "current_fatigue": 45.0,
            "sleep_avg": 7.0,
            "stress_avg": 35.0,
            "session_frequency": 4.0,
            "bodyweight_history": [75.0, 75.3, 75.1, 75.4],
            "calorie_surplus_avg": 100.0,
            "current_bodyweight": 75.0,
            "calorie_adherence": 0.8,
            "estimated_mrv": 20000.0,
            "session_count": 4,
            "average_rpe": 7.0,
            "current_streak": 8,
            "missed_last_7d": 1,
            "recovery_avg": 70.0,
            "recent_completion_rate": 0.8,
            "weeks_since_last_deload": 6,
            "volume_ratio_14d_7d": 1.2,
            "session_count_7d": 4,
            "deload_frequency_weeks": 6,
            "fatigue_trend": 0.5,
            "motivation_score": 0.7,
            "days_since_last_miss": 3,
            "days_since_last_pr": 10,
        }

    def _run_baseline(self, kwargs: dict) -> dict[str, float]:
        return {
            "pr_probability": self._pr.predict(**{k: v for k, v in kwargs.items() if k in (
                "consistency_streak", "recent_volume_trend", "average_rir",
                "recovery_score", "is_deload_week", "days_since_last_pr",
                "recent_prs",
            )}).probability,
            "plateau_probability": self._plateau.predict(**{k: v for k, v in kwargs.items() if k in (
                "recent_volume_7d", "recent_volume_14d", "volume_change_percent",
                "reps_in_rir_avg", "days_since_weight_change", "recent_pr_count",
                "session_count_last_14d",
            )}).probability,
            "recovery_score": self._recovery.predict(**{k: v for k, v in kwargs.items() if k in (
                "recovery_scores", "sleep_trend", "stress_trend",
                "training_volume_trend", "current_recovery_score", "days_since_deload",
            )}).value,
            "fatigue_score": self._fatigue.predict(**{k: v for k, v in kwargs.items() if k in (
                "current_fatigue", "recent_volume_7d", "recent_volume_14d",
                "sleep_avg", "stress_avg", "days_since_deload", "session_frequency",
            )}).value,
            "bodyweight": self._bodyweight.predict(**{k: v for k, v in kwargs.items() if k in (
                "bodyweight_history", "calorie_surplus_avg",
                "current_bodyweight", "calorie_adherence",
            )}).value,
            "mrv_risk": self._volume.predict(**{k: v for k, v in kwargs.items() if k in (
                "weekly_volumes", "estimated_mrv", "current_weekly_volume",
                "session_count", "average_rpe",
            )}).probability,
            "deload_risk": self._deload.predict(**{k: v for k, v in kwargs.items() if k in (
                "weeks_since_last_deload", "recovery_scores", "current_fatigue",
                "fatigue_trend", "volume_ratio_14d_7d", "sleep_avg",
                "session_count_7d", "deload_frequency_weeks",
            )}).probability,
            "consistency": self._consistency.predict(**{k: v for k, v in kwargs.items() if k in (
                "current_streak", "missed_last_7d", "recovery_avg",
                "recent_completion_rate", "motivation_score",
                "days_since_last_miss",
            )}).probability,
        }

    def _describe_intervention(
        self, intervention: ScenarioIntervention, comparisons: list[ScenarioComparison],
    ) -> str:
        pos = sum(1 for c in comparisons if c.is_positive)
        total = len(comparisons)
        if pos == total:
            return f"{intervention.label} improves all {total} metrics"
        if pos >= total * 0.6:
            return f"{intervention.label} improves {pos}/{total} metrics"
        if pos >= total * 0.3:
            return f"{intervention.label} has mixed effects ({pos}/{total} positive)"
        return f"{intervention.label} negatively impacts {total - pos}/{total} metrics"

    def evaluate_intervention(
        self,
        intervention: ScenarioIntervention,
        base_kwargs: dict | None = None,
    ) -> ScenarioResult:
        kwargs = base_kwargs or self._get_baseline_kwargs()
        baseline = self._run_baseline(kwargs)
        mods = ScenarioBuilder.build_modifiers(intervention, kwargs)
        scenario = self._run_baseline(mods)

        comparisons: list[ScenarioComparison] = []
        keys_labels = [
            ("pr_probability", "PR Probability"),
            ("plateau_probability", "Plateau Risk"),
            ("recovery_score", "Recovery Score"),
            ("fatigue_score", "Fatigue Score"),
            ("bodyweight", "Bodyweight"),
            ("mrv_risk", "MRV Risk"),
            ("deload_risk", "Deload Risk"),
            ("consistency", "Consistency"),
        ]
        for key, label in keys_labels:
            bv = baseline.get(key, 0.0)
            sv = scenario.get(key, 0.0)
            comparisons.append(ScenarioComparison(
                intervention=intervention,
                baseline_value=bv,
                scenario_value=sv,
                description=label,
            ))

        confidence_score = min(0.8, 0.4 + len(comparisons) * 0.02)
        return ScenarioResult(
            intervention=intervention,
            comparisons=comparisons,
            overall_assessment=self._describe_intervention(intervention, comparisons),
            recommended=sum(1 for c in comparisons if c.is_positive) >= len(comparisons) * 0.5,
            risk_level="high" if any(abs(c.delta_percent) > 30 for c in comparisons) else
                      "moderate" if any(abs(c.delta_percent) > 15 for c in comparisons) else "low",
            confidence=PredictionConfidence(score=confidence_score, sample_size=len(comparisons)),
        )

    def evaluate_all(self, base_kwargs: dict | None = None) -> list[ScenarioResult]:
        results: list[ScenarioResult] = []
        for intervention in ScenarioIntervention:
            results.append(self.evaluate_intervention(intervention, base_kwargs))
        return results

    def rank_scenarios(
        self, results: list[ScenarioResult] | None = None, base_kwargs: dict | None = None,
    ) -> ScenarioRanking:
        if results is None:
            results = self.evaluate_all(base_kwargs)
        rankings: list[tuple[ScenarioIntervention, float]] = []
        for r in results:
            net_score = sum(c.scenario_value for c in r.comparisons if c.is_positive) - \
                        sum(c.scenario_value for c in r.comparisons if not c.is_positive)
            rankings.append((r.intervention, net_score))
        return ScenarioRanking(rankings=rankings)

    def compare_interventions(
        self, interventions: list[ScenarioIntervention],
    ) -> dict[str, list[ScenarioComparison]]:
        kwargs = self._get_baseline_kwargs()
        baseline = self._run_baseline(kwargs)
        result: dict[str, list[ScenarioComparison]] = {}
        for intervention in interventions:
            mods = ScenarioBuilder.build_modifiers(intervention, kwargs)
            scenario = self._run_baseline(mods)
            comps: list[ScenarioComparison] = []
            keys_labels = [
                ("pr_probability", "PR Probability"),
                ("plateau_probability", "Plateau Risk"),
                ("recovery_score", "Recovery Score"),
                ("fatigue_score", "Fatigue Score"),
                ("bodyweight", "Bodyweight"),
                ("mrv_risk", "MRV Risk"),
                ("deload_risk", "Deload Risk"),
                ("consistency", "Consistency"),
            ]
            for key, label in keys_labels:
                bv = baseline.get(key, 0.0)
                sv = scenario.get(key, 0.0)
                comps.append(ScenarioComparison(
                    intervention=intervention, baseline_value=bv,
                    scenario_value=sv, description=label,
                ))
            result[intervention.label] = comps
        return result
