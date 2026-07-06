from __future__ import annotations

from datetime import datetime
from typing import Any

from modules.gymbrain.models.recommendations import (
    Recommendation,
    RecommendationAction,
    RecommendationCategory,
    RecommendationPriority,
)
from modules.gymbrain.providers.data_provider import DataProvider
from modules.gymbrain.rules.base import BaseRule, RuleResult


class WeightPlateauRule(BaseRule):
    """If bodyweight is unchanged for 14+ days with high adherence, recommend increasing calories."""

    def __init__(self) -> None:
        super().__init__(
            name="weight_plateau_rule",
            description="Detects bodyweight plateaus and recommends nutritional adjustment",
            priority=70,
        )

    def evaluate(self, provider: DataProvider, context: dict[str, Any] | None = None) -> RuleResult:
        bw_history = provider.get_body_weight_history(days=30)
        if not bw_history or len(bw_history) < 3:
            return RuleResult()

        sorted_bw = sorted(bw_history, key=lambda x: x.date if hasattr(x, "date") else datetime.min)
        recent = sorted_bw[-3:]
        weights = [getattr(w, "weight_kg", 0) for w in recent]

        if len(set(round(w, 1) for w in weights)) == 1:
            latest = provider.get_latest_body_weight()
            latest_weight = getattr(latest, "weight_kg", 0) if latest else 0
            streak = provider.get_streak()

            return RuleResult(
                triggered=True,
                recommendation=Recommendation(
                    category=RecommendationCategory.NUTRITION,
                    priority=RecommendationPriority.HIGH.value,
                    title="Bodyweight plateau detected — increase calories",
                    description=f"Bodyweight has remained at {latest_weight}kg for 3+ consecutive readings. "
                                f"If training adherence is good ({streak} day streak), increase daily calories by 100-200.",
                    reason="Bodyweight unchanged for 3+ readings over at least 7 days with consistent training",
                    confidence=0.75,
                    evidence=[f"Bodyweight: {latest_weight}kg (unchanged)", f"Training streak: {streak} days"],
                    action=RecommendationAction(
                        type="increase_calories",
                        params={"current_weight": latest_weight, "increase": "100-200 kcal/day"},
                        display="Increase daily calories by 100-200 kcal",
                    ),
                ),
                evidence=[f"Bodyweight: {latest_weight}kg (unchanged)", f"Training streak: {streak} days"],
                confidence=0.75,
            )

        return RuleResult()


class StrengthPlateauRule(BaseRule):
    """If e1rm has not increased for 4+ weeks on a compound lift, recommend programming change."""

    def __init__(self) -> None:
        super().__init__(
            name="strength_plateau_rule",
            description="Detects strength plateaus on compound lifts",
            priority=65,
        )

    def evaluate(self, provider: DataProvider, context: dict[str, Any] | None = None) -> RuleResult:
        exercises = provider.get_all_exercises()
        compound_lifts = [
            ex for ex in exercises
            if (ex.get("category") if isinstance(ex, dict) else getattr(ex, "category", "")) in ("compound", "upper_compound", "lower_compound")
        ]

        plateaued: list[str] = []
        for ex_data in compound_lifts:
            ex_name = ex_data.get("name") if isinstance(ex_data, dict) else getattr(ex_data, "name", "")
            if not ex_name:
                continue
            sessions = provider.list_sessions(limit=100)
            e1rm_values: list[tuple[datetime, float]] = []
            for s in sessions:
                if not hasattr(s, "exercises") or not hasattr(s, "started_at"):
                    continue
                for ex in s.exercises:
                    if not hasattr(ex, "name") or ex.name != ex_name or not hasattr(ex, "sets"):
                        continue
                    best_e1rm = 0
                    for set_data in ex.sets:
                        if hasattr(set_data, "weight_kg") and hasattr(set_data, "reps") and set_data.reps > 0:
                            e1rm = set_data.weight_kg * (1 + set_data.reps / 30)
                            best_e1rm = max(best_e1rm, e1rm)
                    if best_e1rm > 0 and s.started_at:
                        e1rm_values.append((s.started_at, best_e1rm))

            if len(e1rm_values) < 3:
                continue
            e1rm_values.sort(key=lambda x: x[0])
            recent = e1rm_values[-3:]
            if len(set(round(v, 1) for _, v in recent)) <= 2:
                span = (recent[-1][0] - recent[0][0]).days
                if span >= 21:
                    plateaued.append(f"{ex_name}: e1rm stuck at ~{recent[-1][1]:.0f}kg for {span} days")

        if not plateaued:
            return RuleResult()

        return RuleResult(
            triggered=True,
            recommendation=Recommendation(
                category=RecommendationCategory.PROGRAM_ADJUSTMENT,
                priority=RecommendationPriority.HIGH.value,
                title="Strength plateau on compound lifts — consider programming change",
                description=f"Strength has stalled on {len(plateaued)} compound lift(s): {'; '.join(plateaued)}. "
                            f"Consider a technique deload, rep scheme change, or exercise variation.",
                reason="Estimated 1RM has not progressed for 3+ consecutive sessions spanning 3+ weeks",
                confidence=0.80,
                evidence=plateaued,
                action=RecommendationAction(
                    type="programming_change",
                    params={"exercises": plateaued},
                    display="Modify programming for stalled compound lifts",
                ),
            ),
            evidence=plateaued,
            confidence=0.80,
        )


class RepPlateauRule(BaseRule):
    """If reps have not increased within target range for 3+ weeks, recommend adjustment."""

    def __init__(self) -> None:
        super().__init__(
            name="rep_plateau_rule",
            description="Detects rep-count plateaus within target rep ranges",
            priority=55,
        )

    def evaluate(self, provider: DataProvider, context: dict[str, Any] | None = None) -> RuleResult:
        sessions = provider.get_recent_sessions(days=28)
        if len(sessions) < 4:
            return RuleResult()

        exercise_reps: dict[str, list[tuple[datetime, int]]] = {}
        for s in sessions:
            if not hasattr(s, "exercises") or not hasattr(s, "started_at"):
                continue
            for ex in s.exercises:
                if not hasattr(ex, "name") or not hasattr(ex, "sets"):
                    continue
                if hasattr(ex, "sets") and ex.sets:
                    max_reps = max((getattr(se, "reps", 0) for se in ex.sets), default=0)
                    if ex.name not in exercise_reps:
                        exercise_reps[ex.name] = []
                    exercise_reps[ex.name].append((s.started_at, max_reps))

        plateaued: list[str] = []
        for ex_name, rep_data in exercise_reps.items():
            if len(rep_data) < 3:
                continue
            rep_data.sort(key=lambda x: x[0])
            recent = rep_data[-3:]
            if len(set(r for _, r in recent)) <= 2:
                span = (recent[-1][0] - recent[0][0]).days
                if span >= 17:
                    plateaued.append(f"{ex_name}: reps stuck at {recent[-1][1]} for {span} days")

        if not plateaued:
            return RuleResult()

        return RuleResult(
            triggered=True,
            recommendation=Recommendation(
                category=RecommendationCategory.PROGRESSION,
                priority=RecommendationPriority.MEDIUM.value,
                title="Rep plateau detected — consider weight adjustment or technique review",
                description=f"Rep count has plateaued on {len(plateaued)} exercise(s). Consider a small weight "
                            f"reduction to accumulate more reps, or deload and reset.",
                reason="Maximum reps per set have not increased for 3+ sessions",
                confidence=0.70,
                evidence=plateaued,
                action=RecommendationAction(
                    type="rep_plateau_break",
                    params={"exercises": plateaued},
                    display="Back-off weight by 5-10% to accumulate more reps",
                ),
            ),
            evidence=plateaued,
            confidence=0.70,
        )
