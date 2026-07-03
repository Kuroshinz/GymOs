from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from modules.gymbrain.models.analysis import GoalProgress
from modules.gymbrain.providers.data_provider import DataProvider


class GoalTracker:
    """Tracks bodyweight goals and bulking/cutting progress."""

    def __init__(self, provider: DataProvider) -> None:
        self._provider = provider

    def get_progress(
        self,
        goal_weight_kg: float | None = None,
        target_calorie_surplus: int = 300,
    ) -> GoalProgress:
        bw_history = self._provider.get_body_weight_history(days=90)
        latest_bw = self._provider.get_latest_body_weight()

        if not bw_history or not latest_bw:
            return GoalProgress()

        current_weight = getattr(latest_bw, "weight_kg", 0)
        if current_weight == 0:
            return GoalProgress()

        sorted_bw = sorted(
            bw_history,
            key=lambda x: getattr(x, "date", datetime.min) if hasattr(x, "date") else datetime.min,
        )
        weights = [getattr(w, "weight_kg", 0) for w in sorted_bw if hasattr(w, "weight_kg")]
        dates = [
            getattr(w, "date", datetime.min) if hasattr(w, "date") else datetime.min
            for w in sorted_bw
        ]

        if len(weights) < 3:
            return GoalProgress(current_weight_kg=current_weight)

        # Weekly gain rate
        weekly_gain = self._calculate_weekly_rate(weights, dates)

        if goal_weight_kg is None:
            goal_weight_kg = current_weight

        remaining = goal_weight_kg - current_weight
        estimated_weeks = remaining / weekly_gain if weekly_gain > 0 else 0
        estimated_date = ""
        if estimated_weeks > 0 and estimated_weeks < 52:
            est_date = datetime.now() + timedelta(weeks=estimated_weeks)
            estimated_date = est_date.strftime("%Y-%m-%d")

        # Lean bulk quality
        quality = self._assess_bulk_quality(weekly_gain, weights)

        # Bodyweight trend
        trend = self._determine_trend(weights, dates)

        # Progress score
        progress_score = self._calculate_progress_score(
            current_weight, goal_weight_kg, weekly_gain, weights
        )

        return GoalProgress(
            current_weight_kg=current_weight,
            goal_weight_kg=goal_weight_kg,
            weekly_gain_rate=round(weekly_gain, 2),
            estimated_completion_weeks=round(estimated_weeks, 1),
            estimated_completion_date=estimated_date,
            lean_bulk_quality=quality,
            bodyweight_trend=trend,
            progress_score=round(progress_score, 1),
            target_calorie_surplus=target_calorie_surplus,
            weeks_of_data=max(len(weights) // 3, 1),
        )

    def _calculate_weekly_rate(self, weights: list[float], dates: list[datetime]) -> float:
        if len(weights) < 3:
            return 0.0

        recent = weights[-3:]
        recent_dates = dates[-3:]
        if len(recent) < 2:
            return 0.0

        span_days = (recent_dates[-1] - recent_dates[0]).days
        if span_days < 1:
            return 0.0

        return (recent[-1] - recent[0]) / (span_days / 7)

    def _assess_bulk_quality(self, weekly_gain: float, weights: list[float]) -> str:
        if weekly_gain <= 0:
            return "Not gaining — increase calories"
        if weekly_gain < 0.15:
            return "Very slow gain — increase calories by 100-200"
        if weekly_gain < 0.25:
            return "Slow gain — consider slight calorie increase"
        if weekly_gain <= 0.5:
            return "Optimal lean bulk rate"
        if weekly_gain <= 0.75:
            return "Moderate gain — monitor for excess fat gain"
        return "Rapid gain — reduce surplus to minimize fat gain"

    def _determine_trend(self, weights: list[float], dates: list[datetime]) -> str:
        if len(weights) < 4:
            return "Insufficient data"

        recent_3 = weights[-3:]
        oldest_3 = weights[:3]
        recent_avg = sum(recent_3) / 3
        oldest_avg = sum(oldest_3) / 3

        if recent_avg > oldest_avg * 1.02:
            return "Increasing"
        if recent_avg < oldest_avg * 0.98:
            return "Decreasing"
        return "Stable"

    def _calculate_progress_score(
        self,
        current_weight: float,
        goal_weight: float,
        weekly_gain: float,
        weights: list[float],
    ) -> float:
        if goal_weight <= 0:
            return 0.0

        progress_pct = min((current_weight / goal_weight) * 100, 100)
        rate_score = 0.0
        if 0.25 <= weekly_gain <= 0.5:
            rate_score = 30.0
        elif weekly_gain > 0:
            rate_score = 15.0

        consistency_score = min(len(weights) * 2, 20)

        return progress_pct * 0.5 + rate_score + consistency_score
