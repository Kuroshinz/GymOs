"""GymBrain Nutrition Rules — evidence-based nutrition recommendations.

These rules consume the NutritionProvider (from modules.nutrition) and
combine it with training data to generate actionable recommendations.

Rules:
  1. ProteinDeficitRule — if protein < target, recommend increase
  2. CalorieAdjustmentRule — if bodyweight stalled, recommend calorie adjustment
  3. GainRateRule — if weekly gain too fast/slow, recommend adjustment
  4. HydrationRule — if water intake is low, recommend hydration
  5. LeanBulkQualityRule — overall lean bulk quality assessment
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from modules.gymbrain.models.recommendations import (
    Recommendation,
    RecommendationAction,
    RecommendationCategory,
    RecommendationPriority,
)
from modules.gymbrain.providers.data_provider import DataProvider
from modules.gymbrain.rules.base import BaseRule, RuleResult


class ProteinDeficitRule(BaseRule):
    """If protein intake is below target, recommend increasing protein."""

    def __init__(self) -> None:
        super().__init__(
            name="protein_deficit_rule",
            description="Recommends increasing protein when intake is below target",
            priority=90,
        )

    def evaluate(self, provider: DataProvider, context: dict[str, Any] | None = None) -> RuleResult:
        nutrition = getattr(provider, "nutrition_provider", None)
        if nutrition is None:
            return RuleResult()

        try:
            target = nutrition.get_default_target()
            avg_protein = nutrition.get_average_protein(days=7)
        except Exception:
            return RuleResult()

        if target.protein_g <= 0 or avg_protein <= 0:
            return RuleResult()

        deficit_pct = (target.protein_g - avg_protein) / target.protein_g * 100

        if deficit_pct > 20:
            return RuleResult(
                triggered=True,
                recommendation=Recommendation(
                    category=RecommendationCategory.NUTRITION,
                    priority=RecommendationPriority.CRITICAL.value,
                    title="Protein intake is critically low",
                    description=f"Average protein intake ({avg_protein:.0f}g) is "
                                f"{deficit_pct:.0f}% below target ({target.protein_g}g). "
                                f"Protein is the most critical nutrient for hypertrophy.",
                    reason=f"{deficit_pct:.0f}% protein deficit over the last 7 days",
                    confidence=0.90,
                    evidence=[
                        f"Daily target: {target.protein_g}g",
                        f"7-day average: {avg_protein:.0f}g",
                        f"Deficit: {deficit_pct:.0f}%",
                    ],
                    action=RecommendationAction(
                        type="increase_protein",
                        params={"deficit_pct": deficit_pct, "target": target.protein_g},
                        display=f"Add {int(target.protein_g - avg_protein)}g protein per day",
                    ),
                ),
                evidence=[f"Target: {target.protein_g}g", f"Average: {avg_protein:.0f}g"],
                confidence=0.90,
            )

        if deficit_pct > 10:
            return RuleResult(
                triggered=True,
                recommendation=Recommendation(
                    category=RecommendationCategory.NUTRITION,
                    priority=RecommendationPriority.HIGH.value,
                    title="Protein intake is below target",
                    description=f"Average protein intake ({avg_protein:.0f}g) is below "
                                f"your target ({target.protein_g}g). Aim for at least 1.6g/kg bodyweight.",
                    reason=f"{deficit_pct:.0f}% protein deficit",
                    confidence=0.80,
                    evidence=[
                        f"Target: {target.protein_g}g/day",
                        f"7-day average: {avg_protein:.0f}g/day",
                    ],
                    action=RecommendationAction(
                        type="improve_protein",
                        params={"deficit_pct": deficit_pct, "target": target.protein_g},
                        display="Prioritize protein at every meal (30-40g per meal)",
                    ),
                ),
                evidence=[f"Target: {target.protein_g}g", f"Average: {avg_protein:.0f}g"],
                confidence=0.80,
            )

        return RuleResult()


class CalorieAdjustmentRule(BaseRule):
    """If bodyweight has stalled for 14+ days and calories are below target, recommend increase."""

    def __init__(self) -> None:
        super().__init__(
            name="calorie_adjustment_rule",
            description="Recommends calorie adjustments based on bodyweight trends and intake",
            priority=85,
        )

    def evaluate(self, provider: DataProvider, context: dict[str, Any] | None = None) -> RuleResult:
        nutrition = getattr(provider, "nutrition_provider", None)
        if nutrition is None:
            return RuleResult()

        try:
            bw_history = nutrition.get_body_weight_history(days=21)
            avg_calories = nutrition.get_average_calories(days=7)
            target = nutrition.get_default_target()
        except Exception:
            return RuleResult()

        if not bw_history or len(bw_history) < 3:
            return RuleResult()

        sorted_bw = sorted(
            bw_history,
            key=lambda x: getattr(x, "date", datetime.min) if hasattr(x, "date") else datetime.min,
        )
        weights = [getattr(w, "weight_kg", 0) for w in sorted_bw]
        recent_3 = weights[-3:] if len(weights) >= 3 else weights

        if len(set(round(w, 1) for w in recent_3)) == 1 and avg_calories < target.calories:
            return RuleResult(
                triggered=True,
                recommendation=Recommendation(
                    category=RecommendationCategory.NUTRITION,
                    priority=RecommendationPriority.HIGH.value,
                    title="Bodyweight stalled — increase calories",
                    description=f"Bodyweight has been stable at ~{recent_3[-1]:.1f}kg "
                                f"while consuming {avg_calories:.0f} kcal (target: {target.calories:.0f} kcal). "
                                f"Increase daily intake by 100-200 kcal.",
                    reason="Bodyweight unchanged despite training consistency",
                    confidence=0.80,
                    evidence=[
                        f"Bodyweight: {recent_3[-1]:.1f}kg (stable)",
                        f"Current intake: {avg_calories:.0f} kcal/day",
                        f"Target intake: {target.calories:.0f} kcal/day",
                    ],
                    action=RecommendationAction(
                        type="increase_calories",
                        params={
                            "increase": "100-200 kcal/day",
                            "current_intake": avg_calories,
                            "target": target.calories,
                        },
                        display="Increase daily calories by 100-200 kcal",
                    ),
                ),
                evidence=[f"Weight: {recent_3[-1]:.1f}kg", f"Intake: {avg_calories:.0f}/{target.calories:.0f} kcal"],
                confidence=0.80,
            )

        return RuleResult()


class GainRateRule(BaseRule):
    """If weekly gain rate is too fast or too slow, recommend adjustment."""

    def __init__(self) -> None:
        super().__init__(
            name="gain_rate_rule",
            description="Recommends calorie adjustments based on rate of weight gain",
            priority=80,
        )

    def evaluate(self, provider: DataProvider, context: dict[str, Any] | None = None) -> RuleResult:
        nutrition = getattr(provider, "nutrition_provider", None)
        if nutrition is None:
            return RuleResult()

        try:
            from modules.nutrition.analysis import LeanBulkAnalyzer

            analyzer = LeanBulkAnalyzer(nutrition)
            analysis = analyzer.analyze(weeks=4)
        except Exception:
            return RuleResult()

        if not analysis or analysis.weeks_of_data < 1:
            return RuleResult()

        # Too fast
        if analysis.weekly_weight_gain_kg > 0.5:
            return RuleResult(
                triggered=True,
                recommendation=Recommendation(
                    category=RecommendationCategory.NUTRITION,
                    priority=RecommendationPriority.HIGH.value,
                    title="Weight gain is too rapid",
                    description=f"Gaining {analysis.weekly_weight_gain_kg:.2f} kg/week exceeds "
                                f"the optimal range (0.25-0.5 kg/week). Reduce surplus to minimize fat gain.",
                    reason=f"Weight gain rate ({analysis.weekly_weight_gain_kg:.2f} kg/wk) exceeds target",
                    confidence=0.85,
                    evidence=[
                        f"Weekly gain: {analysis.weekly_weight_gain_kg:.2f} kg",
                        f"Optimal range: 0.25-0.5 kg/week",
                        f"Quality score: {analysis.quality_score:.0f}/100",
                    ],
                    action=RecommendationAction(
                        type="reduce_calories",
                        params={"weekly_gain": analysis.weekly_weight_gain_kg},
                        display="Reduce daily calories by 100-200 kcal",
                    ),
                ),
                evidence=[f"Gain rate: {analysis.weekly_weight_gain_kg:.2f} kg/week"],
                confidence=0.85,
            )

        # Too slow
        if analysis.weekly_weight_gain_kg < 0.25 and analysis.weekly_weight_gain_kg > 0:
            return RuleResult(
                triggered=True,
                recommendation=Recommendation(
                    category=RecommendationCategory.NUTRITION,
                    priority=RecommendationPriority.MEDIUM.value,
                    title="Weight gain is below target",
                    description=f"Gaining {analysis.weekly_weight_gain_kg:.2f} kg/week is below "
                                f"the optimal range (0.25-0.5 kg/week). Consider increasing calories slightly.",
                    reason=f"Weight gain rate ({analysis.weekly_weight_gain_kg:.2f} kg/wk) below target",
                    confidence=0.75,
                    evidence=[
                        f"Weekly gain: {analysis.weekly_weight_gain_kg:.2f} kg",
                        f"Optimal range: 0.25-0.5 kg/week",
                    ],
                    action=RecommendationAction(
                        type="increase_calories_slight",
                        params={"weekly_gain": analysis.weekly_weight_gain_kg},
                        display="Increase daily calories by 100 kcal and monitor for 2 weeks",
                    ),
                ),
                evidence=[f"Gain rate: {analysis.weekly_weight_gain_kg:.2f} kg/week"],
                confidence=0.75,
            )

        # Losing weight
        if analysis.weekly_weight_gain_kg <= 0:
            return RuleResult(
                triggered=True,
                recommendation=Recommendation(
                    category=RecommendationCategory.NUTRITION,
                    priority=RecommendationPriority.CRITICAL.value,
                    title="Weight is decreasing during lean bulk",
                    description=f"Weight is decreasing by {abs(analysis.weekly_weight_gain_kg):.2f} kg/week. "
                                f"You need a calorie surplus to build muscle. "
                                f"Increase daily intake by 200-300 kcal immediately.",
                    reason="Weight loss during bulking phase — insufficient calorie surplus",
                    confidence=0.90,
                    evidence=[
                        f"Weekly change: {analysis.weekly_weight_gain_kg:.2f} kg",
                        "Goal: positive gain (0.25-0.5 kg/week)",
                    ],
                    action=RecommendationAction(
                        type="increase_calories_significant",
                        params={"weekly_change": analysis.weekly_weight_gain_kg},
                        display="Increase daily calories by 200-300 kcal",
                    ),
                ),
                evidence=[f"Weekly change: {analysis.weekly_weight_gain_kg:.2f} kg/week"],
                confidence=0.90,
            )

        return RuleResult()


class HydrationRule(BaseRule):
    """If water intake is below target, recommend hydration."""

    def __init__(self) -> None:
        super().__init__(
            name="hydration_rule",
            description="Recommends increasing water intake when below target",
            priority=50,
        )

    def evaluate(self, provider: DataProvider, context: dict[str, Any] | None = None) -> RuleResult:
        nutrition = getattr(provider, "nutrition_provider", None)
        if nutrition is None:
            return RuleResult()

        try:
            target = nutrition.get_default_target()
            today_nutrition = nutrition.get_today()
        except Exception:
            return RuleResult()

        if today_nutrition is None or target.water_ml <= 0:
            return RuleResult()

        water_pct = (today_nutrition.water_ml / target.water_ml) * 100 if target.water_ml > 0 else 100

        if water_pct < 30:
            return RuleResult(
                triggered=True,
                recommendation=Recommendation(
                    category=RecommendationCategory.NUTRITION,
                    priority=RecommendationPriority.HIGH.value,
                    title="Hydration is critically low",
                    description=f"You've only consumed {today_nutrition.water_ml:.0f}ml of water today "
                                f"({water_pct:.0f}% of target). Dehydration impairs strength and recovery.",
                    reason=f"Only {water_pct:.0f}% of hydration target met",
                    confidence=0.85,
                    evidence=[f"Current: {today_nutrition.water_ml:.0f}ml", f"Target: {target.water_ml:.0f}ml"],
                    action=RecommendationAction(
                        type="drink_water",
                        params={"remaining": target.water_ml - today_nutrition.water_ml},
                        display=f"Drink {target.water_ml - today_nutrition.water_ml:.0f}ml more water today",
                    ),
                ),
                evidence=[f"Current: {today_nutrition.water_ml:.0f}ml", f"Target: {target.water_ml:.0f}ml"],
                confidence=0.85,
            )

        if water_pct < 60:
            return RuleResult(
                triggered=True,
                recommendation=Recommendation(
                    category=RecommendationCategory.NUTRITION,
                    priority=RecommendationPriority.MEDIUM.value,
                    title="Increase water intake",
                    description=f"You've consumed {today_nutrition.water_ml:.0f}ml of water "
                                f"({water_pct:.0f}% of target). Aim for {target.water_ml:.0f}ml daily.",
                    reason=f"Hydration at {water_pct:.0f}% of target",
                    confidence=0.70,
                    evidence=[f"Current: {today_nutrition.water_ml:.0f}ml", f"Target: {target.water_ml:.0f}ml"],
                    action=RecommendationAction(
                        type="improve_hydration",
                        params={"current": today_nutrition.water_ml, "target": target.water_ml},
                        display="Sip water consistently throughout the day",
                    ),
                ),
                evidence=[f"Current: {today_nutrition.water_ml:.0f}ml", f"Target: {target.water_ml:.0f}ml"],
                confidence=0.70,
            )

        return RuleResult()


class LeanBulkQualityRule(BaseRule):
    """Overall lean bulk quality assessment — combines all nutrition metrics."""

    def __init__(self) -> None:
        super().__init__(
            name="lean_bulk_quality_rule",
            description="Provides overall lean bulk quality assessment and recommendations",
            priority=70,
        )

    def evaluate(self, provider: DataProvider, context: dict[str, Any] | None = None) -> RuleResult:
        nutrition = getattr(provider, "nutrition_provider", None)
        if nutrition is None:
            return RuleResult()

        try:
            from modules.nutrition.analysis import LeanBulkAnalyzer

            analyzer = LeanBulkAnalyzer(nutrition)
            analysis = analyzer.analyze(weeks=4)
        except Exception:
            return RuleResult()

        if not analysis or analysis.weeks_of_data < 1:
            return RuleResult()

        if not analysis.is_on_track:
            return RuleResult(
                triggered=True,
                recommendation=Recommendation(
                    category=RecommendationCategory.NUTRITION,
                    priority=RecommendationPriority.HIGH.value,
                    title=f"Lean bulk quality: {analysis.quality_label}",
                    description=analysis.recommendation,
                    reason=f"Quality score: {analysis.quality_score:.0f}/100",
                    confidence=0.80,
                    evidence=[
                        f"Quality score: {analysis.quality_score:.0f}/100",
                        f"Weight gain: {analysis.weekly_weight_gain_kg:.2f} kg/week",
                        f"Calorie surplus: {analysis.average_calorie_surplus:.0f} kcal",
                        f"Protein: {analysis.average_daily_protein:.0f}g/day",
                    ],
                    action=RecommendationAction(
                        type="improve_lean_bulk",
                        params={"quality_score": analysis.quality_score},
                        display=analysis.calorie_adjustment,
                    ),
                ),
                evidence=[f"Quality: {analysis.quality_score:.0f}/100"],
                confidence=0.80,
            )

        return RuleResult()
