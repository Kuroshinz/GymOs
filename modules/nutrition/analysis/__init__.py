"""Nutrition Analysis Engines — macro tracking and lean bulk quality analysis.

These analyzers produce structured, explainable results consumed by:
  - GymBrain rules (for recommendations)
  - Dashboard (for display)
  - Weekly review (for summary)
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Optional

from modules.nutrition.domain import (
    DailyNutrition,
    LeanBulkAnalysis,
    MacroAnalysis,
    MacroStatus,
    MacroStatusResult,
    MacroTarget,
)
from modules.nutrition.providers import NutritionProvider


class MacroAnalyzer:
    """Analyzes daily macronutrient intake against targets.

    Produces a MacroAnalysis with per-macro status, score, and difference.
    Never hard-codes thresholds — all thresholds come from MacroTarget.
    """

    def __init__(self, provider: NutritionProvider) -> None:
        self._provider = provider

    def analyze_day(self, date: str | None = None) -> MacroAnalysis:
        """Analyze a single day's macro intake."""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        day = self._provider.get_day(date)
        target = self._provider.get_default_target()

        if not day or not day.has_data:
            return MacroAnalysis(
                date=date,
                overall_score=0.0,
            )

        return self._build_analysis(day, target, date)

    def analyze_recent(self, days: int = 7) -> MacroAnalysis:
        """Analyze average macro intake over the last N days."""
        days_list = self._provider.get_recent_days(days)
        target = self._provider.get_default_target()

        if not days_list:
            return MacroAnalysis(overall_score=0.0)

        # Aggregate data
        total_calories = sum(d.total_calories for d in days_list)
        total_protein = sum(d.total_protein for d in days_list)
        total_carbs = sum(d.total_carbs for d in days_list)
        total_fat = sum(d.total_fat for d in days_list)
        total_fiber = sum(d.total_fiber for d in days_list)
        total_water = sum(d.water_ml for d in days_list)
        n = len(days_list)

        avg_day = DailyNutrition(date=f"{days}-day average")
        avg_day._calories = total_calories / n
        avg_day._protein = total_protein / n
        avg_day._carbs = total_carbs / n
        avg_day._fat = total_fat / n
        avg_day._fiber = total_fiber / n
        avg_day._water = total_water / n

        # Build analysis with averaged values
        date_range = f"{days_list[-1].date} to {days_list[0].date}"
        analysis = MacroAnalysis(date=date_range)

        analysis.calories = self._make_result("Calories", total_calories / n, target.calories, "kcal")
        analysis.protein = self._make_result("Protein", total_protein / n, target.protein_g, "g")
        analysis.carbs = self._make_result("Carbs", total_carbs / n, target.carbs_g, "g")
        analysis.fat = self._make_result("Fat", total_fat / n, target.fat_g, "g")
        analysis.fiber = self._make_result("Fiber", total_fiber / n, target.fiber_g, "g")
        analysis.hydration = self._make_result("Hydration", total_water / n, target.water_ml, "ml")

        analysis.overall_score = self._calculate_overall_score(analysis.results)
        return analysis

    def _build_analysis(self, day: DailyNutrition, target: MacroTarget, date: str) -> MacroAnalysis:
        analysis = MacroAnalysis(date=date)

        analysis.calories = self._make_result("Calories", day.total_calories, target.calories, "kcal")
        analysis.protein = self._make_result("Protein", day.total_protein, target.protein_g, "g")
        analysis.carbs = self._make_result("Carbs", day.total_carbs, target.carbs_g, "g")
        analysis.fat = self._make_result("Fat", day.total_fat, target.fat_g, "g")
        analysis.fiber = self._make_result("Fiber", day.total_fiber, target.fiber_g, "g")
        analysis.hydration = self._make_result("Hydration", day.water_ml, target.water_ml, "ml")

        analysis.overall_score = self._calculate_overall_score(analysis.results)
        return analysis

    def _make_result(self, name: str, current: float, target: float, unit: str) -> MacroStatusResult:
        diff = current - target
        score = min(current / target * 100, 100) if target > 0 else 0
        status = self._determine_status(name, score, target)
        return MacroStatusResult(
            name=name,
            current=round(current, 1),
            target=target,
            unit=unit,
            difference=round(diff, 1),
            score=round(score, 1),
            status=status,
        )

    def _determine_status(self, name: str, score: float, target: float) -> MacroStatus:
        if target == 0:
            return MacroStatus.ON_TRACK

        if name == "Protein":
            if score >= 90:
                return MacroStatus.ON_TRACK
            if score >= 70:
                return MacroStatus.LOW
            return MacroStatus.CRITICAL

        if name == "Hydration":
            if score >= 80:
                return MacroStatus.ON_TRACK
            if score >= 50:
                return MacroStatus.LOW
            return MacroStatus.CRITICAL

        # Calories, Carbs, Fat, Fiber
        if 80 <= score <= 120:
            return MacroStatus.ON_TRACK
        if 50 <= score <= 150:
            return MacroStatus.LOW
        return MacroStatus.CRITICAL

    def _calculate_overall_score(self, results: list[MacroStatusResult]) -> float:
        if not results:
            return 0.0
        # Weighted: protein matters most for hypertrophy
        weights = {
            "Protein": 0.30,
            "Calories": 0.25,
            "Carbs": 0.15,
            "Fat": 0.10,
            "Fiber": 0.10,
            "Hydration": 0.10,
        }
        total = 0.0
        weight_sum = 0.0
        for r in results:
            w = weights.get(r.name, 0.1)
            total += r.score * w
            weight_sum += w
        return round(total / weight_sum, 1) if weight_sum > 0 else 0.0


class LeanBulkAnalyzer:
    """Analyzes lean bulk progress combining weight and nutrition data.

    Produces a LeanBulkAnalysis with:
      - Weekly weight gain rate
      - Average calorie surplus
      - Protein consistency
      - Overall quality score and recommendation
    """

    def __init__(self, provider: NutritionProvider) -> None:
        self._provider = provider

    def analyze(self, weeks: int = 4) -> LeanBulkAnalysis:
        """Analyze lean bulk progress over the given number of weeks."""
        days_of_data = weeks * 7
        nutrition_days = self._provider.get_recent_days(days_of_data)
        bw_history = self._provider.get_body_weight_history(days=days_of_data + 14)
        latest_bw = self._provider.get_latest_body_weight()
        target = self._provider.get_default_target()

        # Calculate weekly weight gain
        weekly_gain = self._calculate_weekly_gain(bw_history)
        avg_surplus = self._calculate_avg_calorie_surplus(nutrition_days, target)
        avg_protein = self._calculate_avg_protein(nutrition_days)
        protein_consistency = self._calculate_protein_consistency(nutrition_days, target)

        quality_score = self._calculate_quality_score(
            weekly_gain, avg_surplus, protein_consistency
        )
        quality_label = self._quality_label(quality_score)
        is_on_track = quality_score >= 75

        # Generate recommendation
        recommendation = self._generate_recommendation(
            weekly_gain, avg_surplus, protein_consistency, quality_score,
            nutrition_days, target,
        )

        # Calorie adjustment
        calorie_adj = "Maintain current intake"
        if weekly_gain < 0.25 and len(nutrition_days) >= 7:
            calorie_adj = "Increase by 100-200 kcal/day"
        elif weekly_gain > 0.5:
            calorie_adj = "Reduce by 100 kcal/day"

        return LeanBulkAnalysis(
            weekly_weight_gain_kg=round(weekly_gain, 2),
            average_calorie_surplus=round(avg_surplus, 1),
            average_daily_protein=round(avg_protein, 1),
            protein_consistency_score=round(protein_consistency, 1),
            quality_score=round(quality_score, 1),
            quality_label=quality_label,
            recommendation=recommendation,
            weeks_of_data=min(len(nutrition_days) // 7, weeks),
            is_on_track=is_on_track,
            calorie_adjustment=calorie_adj,
            protein_status=self._protein_status(avg_protein, target),
        )

    def _calculate_weekly_gain(self, bw_history: list) -> float:
        if not bw_history or len(bw_history) < 2:
            return 0.0

        sorted_bw = sorted(
            bw_history,
            key=lambda x: getattr(x, "date", datetime.min) if hasattr(x, "date") else datetime.min,
        )
        weights = [getattr(w, "weight_kg", 0) for w in sorted_bw]

        if len(weights) < 2:
            return 0.0

        # Use first and last weight, divide by weeks spanned
        span_days = (datetime.now() - datetime.strptime(
            getattr(sorted_bw[0], "date", datetime.now().strftime("%Y-%m-%d")),
            "%Y-%m-%d"
        )).days if hasattr(sorted_bw[0], "date") else len(weights)
        span_days = max(span_days, 1)

        return (weights[-1] - weights[0]) / (span_days / 7)

    def _calculate_avg_calorie_surplus(
        self, days: list[DailyNutrition], target: MacroTarget
    ) -> float:
        if not days:
            return 0.0
        avg_calories = sum(d.total_calories for d in days) / len(days)
        return avg_calories - target.calories

    def _calculate_avg_protein(self, days: list[DailyNutrition]) -> float:
        if not days:
            return 0.0
        return sum(d.total_protein for d in days) / len(days)

    def _calculate_protein_consistency(
        self, days: list[DailyNutrition], target: MacroTarget
    ) -> float:
        """Calculate how consistently protein targets are met."""
        if not days:
            return 0.0
        scores = []
        for d in days:
            if target.protein_g > 0:
                score = min(d.total_protein / target.protein_g * 100, 100)
                scores.append(score)
        return sum(scores) / len(scores) if scores else 0.0

    def _calculate_quality_score(
        self, weekly_gain: float, avg_surplus: float, protein_consistency: float
    ) -> float:
        """Weighted quality score (0-100)."""
        # Weight gain score (40%): ideal = 0.25-0.5 kg/week
        if 0.25 <= weekly_gain <= 0.5:
            gain_score = 40
        elif 0.15 <= weekly_gain <= 0.75:
            gain_score = 25
        elif weekly_gain > 0:
            gain_score = 15
        else:
            gain_score = 0

        # Calorie surplus score (30%): ideal = 300-500 surplus
        if 300 <= avg_surplus <= 500:
            surplus_score = 30
        elif 200 <= avg_surplus <= 600:
            surplus_score = 20
        elif avg_surplus > 0:
            surplus_score = 10
        else:
            surplus_score = 0

        # Protein consistency score (30%)
        protein_score = protein_consistency * 0.30

        return min(gain_score + surplus_score + protein_score, 100)

    def _quality_label(self, score: float) -> str:
        if score >= 90:
            return "Excellent"
        if score >= 75:
            return "Good"
        if score >= 50:
            return "Fair"
        if score >= 25:
            return "Poor"
        return "Critical"

    def _protein_status(self, avg_protein: float, target: MacroTarget) -> str:
        if target.protein_g <= 0:
            return "Unknown"
        ratio = avg_protein / target.protein_g if target.protein_g > 0 else 0
        if ratio >= 0.9:
            return "Excellent"
        if ratio >= 0.75:
            return "Good"
        if ratio >= 0.5:
            return "Needs Improvement"
        return "Critical"

    def _generate_recommendation(
        self, weekly_gain: float, avg_surplus: float,
        protein_consistency: float, quality_score: float,
        days: list[DailyNutrition], target: MacroTarget,
    ) -> str:
        parts: list[str] = []

        if not days:
            return "Start tracking nutrition to get lean bulk analysis."

        if quality_score >= 75:
            parts.append("Lean bulk is on track. Continue current plan.")
        elif quality_score >= 50:
            parts.append("Lean bulk needs attention.")
        else:
            parts.append("Lean bulk requires significant adjustment.")

        if weekly_gain < 0.25:
            parts.append(f"Gain rate ({weekly_gain:.2f} kg/week) is below target. Increase calories by 100-200/day.")
        elif weekly_gain > 0.5:
            parts.append(f"Gain rate ({weekly_gain:.2f} kg/week) exceeds target. Reduce calories by 100/day to minimize fat gain.")

        if protein_consistency < 80:
            parts.append("Prioritize hitting protein targets — this is the most critical macro for hypertrophy.")

        return " ".join(parts)
