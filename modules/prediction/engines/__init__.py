"""GymOS Prediction Engines — deterministic, stateless, composable forecast engines.

All engines are:
  - Deterministic (same inputs → same outputs)
  - Stateless (no internal state)
  - Pure (no side effects)
  - Composable (engines may be combined by the PredictionService)

Engine list:
  PlateauPredictionEngine        — probability of plateau in next N days
  PRPredictionEngine             — probability of hitting a new PR in next N days
  RecoveryPredictionEngine       — forecast recovery score trajectory
  FatiguePredictionEngine        — forecast fatigue accumulation trajectory
  BodyweightPredictionEngine     — forecast bodyweight over time
  GoalEtaPredictionEngine        — estimated time to reach bodyweight goal
  VolumePredictionEngine         — forecast volume trends and MRV risk
  ConsistencyPredictionEngine    — forecast consistency decay / workout completion
  DeloadPredictionEngine         — probability of needing a deload
  PredictionScenarioEngine       — what-if intervention scenario evaluation
  CounterfactualEngine           — counterfactual what-if analysis
  ExplainabilityEngine           — factor ranking, reason chains, NL/MR explanations
  RiskEngine                     — stability, sensitivity, uncertainty, volatility
"""

from __future__ import annotations

import math
from datetime import datetime, timedelta
from typing import Optional

from modules.prediction.domain import (
    ConfidenceLevel,
    Forecast,
    ForecastPoint,
    Prediction,
    PredictionConfidence,
    PredictionEvidence,
    PredictionExplanation,
    PredictionScenario,
    PredictionType,
    PredictionWindow,
    TrendModel,
)

# ═══════════════════════════════════════════════════════════════
# Utility helpers
# ═══════════════════════════════════════════════════════════════


def _linear_regression(values: list[float]) -> tuple[float, float]:
    n = len(values)
    if n < 2:
        return 0.0, values[0] if values else 0.0
    x_mean = (n - 1) / 2.0
    y_mean = sum(values) / n
    num = sum((i - x_mean) * (v - y_mean) for i, v in enumerate(values))
    den = sum((i - x_mean) ** 2 for i in range(n))
    slope = num / den if den else 0.0
    intercept = y_mean - slope * x_mean
    return slope, intercept


def _calculate_variance(values: list[float], mean: float) -> float:
    n = len(values)
    if n < 2:
        return 0.0
    return sum((v - mean) ** 2 for v in values) / n


def _moving_average(values: list[float], window: int = 3) -> list[float]:
    if len(values) < window:
        return [sum(values) / len(values)] if values else []
    result = []
    for i in range(len(values) - window + 1):
        result.append(sum(values[i:i + window]) / window)
    return result


def _confidence_from_variance(values: list[float]) -> float:
    n = len(values)
    if n < 3:
        return 0.3
    mean = sum(values) / n
    variance = _calculate_variance(values, mean)
    std_dev = variance ** 0.5
    cv = std_dev / mean if mean != 0 else 1.0
    if cv < 0.05:
        return 0.85
    if cv < 0.10:
        return 0.70
    if cv < 0.20:
        return 0.50
    if cv < 0.35:
        return 0.35
    return 0.20


def _generate_forecast_points(
    current_value: float,
    slope: float,
    window: PredictionWindow,
    base_confidence: float = 0.5,
) -> list[ForecastPoint]:
    today = datetime.now()
    points: list[ForecastPoint] = []
    for day in range(1, window.days + 1):
        date = (today + timedelta(days=day)).strftime("%Y-%m-%d")
        predicted = current_value + slope * day
        confidence_decay = base_confidence * math.exp(-0.05 * day)
        margin = max(abs(predicted) * 0.1 * (1 + 0.15 * day), 5.0)
        points.append(ForecastPoint(
            date=date,
            predicted_value=round(predicted, 2),
            lower_bound=round(predicted - margin, 2),
            upper_bound=round(predicted + margin, 2),
            confidence_at_point=round(confidence_decay, 3),
        ))
    return points


# ═══════════════════════════════════════════════════════════════
# 1. Plateau Prediction Engine
# ═══════════════════════════════════════════════════════════════

class PlateauPredictionEngine:
    """Predicts probability of hitting a training plateau."""

    def predict(
        self,
        window: PredictionWindow = PredictionWindow.NEXT_7_DAYS,
        recent_volume_7d: float = 0.0,
        recent_volume_14d: float = 0.0,
        volume_change_percent: float = 0.0,
        reps_in_rir_avg: float = 2.0,
        days_since_weight_change: int = 0,
        recent_pr_count: int = 0,
        session_count_last_14d: int = 0,
    ) -> Prediction:
        slope, _ = _linear_regression([recent_volume_7d, recent_volume_14d]) if recent_volume_7d > 0 and recent_volume_14d > 0 else (0.0, 0.0)

        plateau_score = 0.0
        factors: list[str] = []

        if volume_change_percent < -5:
            plateau_score += 0.2
            factors.append(f"Volume dropping {volume_change_percent:.0f}% — possible stall")
        if reps_in_rir_avg > 3:
            plateau_score += 0.3
            factors.append(f"High RIR ({reps_in_rir_avg:.1f}) — insufficient intensity")
        if days_since_weight_change > 21:
            plateau_score += 0.2
            factors.append(f"{days_since_weight_change} days without weight progression")
        if recent_pr_count == 0 and session_count_last_14d >= 6:
            plateau_score += 0.15
            factors.append("No PRs despite consistent training")
        if slope < 0 and recent_volume_14d > 0:
            plateau_score += 0.15
            factors.append("Volume trending downward")

        plateau_score = min(plateau_score, 0.95)
        confidence_score = _confidence_from_variance([recent_volume_7d, recent_volume_14d, float(session_count_last_14d)])

        reasons = [f"Plateau risk: {plateau_score * 100:.0f}%"] + factors
        explanation = PredictionExplanation(
            summary=f"{'Likely' if plateau_score > 0.5 else 'Unlikely'} plateau in next {window.days} days",
            reasoning=reasons,
            assumptions=["Volume is reliable proxy for progression", "RIR reported accurately"],
            risk_factors=["Overtraining", "Insufficient recovery", "Poor exercise selection"],
            evidence=[
                PredictionEvidence(source="volume_analysis", data_point="volume_change_pct", value=volume_change_percent),
                PredictionEvidence(source="rir_analysis", data_point="avg_rir", value=reps_in_rir_avg),
            ],
        )

        forecast = Forecast(
            prediction_type=PredictionType.PLATEAU_PROBABILITY,
            window=window,
            points=_generate_forecast_points(plateau_score, slope * 0.01, window, confidence_score),
            trend_model=TrendModel.LINEAR,
            confidence=PredictionConfidence(score=round(confidence_score, 2), sample_size=session_count_last_14d),
            explanation=explanation,
        )

        return Prediction(
            prediction_type=PredictionType.PLATEAU_PROBABILITY,
            window=window,
            value=round(plateau_score * 100, 1),
            probability=round(plateau_score, 2),
            confidence=PredictionConfidence(score=round(confidence_score, 2), sample_size=session_count_last_14d),
            explanation=explanation,
            forecast=forecast,
            scenarios=[
                PredictionScenario(name="Breakthrough", description="New progression stimulus applied", probability=0.3),
                PredictionScenario(name="Stall", description="No progress for 2+ weeks", probability=0.4),
                PredictionScenario(name="Regression", description="Strength/volume decrease", probability=0.3),
            ],
        )


# ═══════════════════════════════════════════════════════════════
# 2. PR Prediction Engine
# ═══════════════════════════════════════════════════════════════

class PRPredictionEngine:
    """Predicts probability of achieving a new personal record."""

    def predict(
        self,
        window: PredictionWindow = PredictionWindow.NEXT_7_DAYS,
        recent_prs: int = 0,
        recent_volume_trend: float = 0.0,
        consistency_streak: int = 0,
        average_rir: float = 2.0,
        days_since_last_pr: int = 0,
        recovery_score: float = 70.0,
        is_deload_week: bool = False,
    ) -> Prediction:
        pr_score = 0.0
        factors: list[str] = []

        if is_deload_week:
            pr_score += 0.05
            factors.append("Deload week — low PR probability")
        else:
            base = 0.25
            if consistency_streak >= 10:
                base += 0.15
                factors.append(f"Strong consistency streak ({consistency_streak} sessions)")
            if recent_volume_trend > 0:
                base += 0.15
                factors.append("Volume trending up — good PR conditions")
            if average_rir <= 1.5:
                base += 0.15
                factors.append(f"Low RIR ({average_rir:.1f}) — proximity to failure")
            if days_since_last_pr > 14:
                base += 0.10
                factors.append(f"{days_since_last_pr} days since last PR — due")
            if recovery_score >= 80:
                base += 0.10
                factors.append("Excellent recovery — optimal PR conditions")
            elif recovery_score < 50:
                base -= 0.15
                factors.append("Poor recovery — reduced PR probability")
            if recent_prs > 0:
                base += 0.05 * min(recent_prs, 3)

            pr_score = min(base, 0.90)

        pr_score = max(pr_score, 0.05)
        confidence_score = min(0.5 + consistency_streak * 0.02, 0.85)

        explanation = PredictionExplanation(
            summary=f"{pr_score * 100:.0f}% chance of PR in next {window.days} days",
            reasoning=factors + [f"Overall PR probability: {pr_score * 100:.0f}%"],
            assumptions=["Linear strength progression", "Recovery stays stable", "Training adherence maintained"],
            risk_factors=["Injury", "Illness", "Unexpected deload", "Life stress"],
            evidence=[
                PredictionEvidence(source="consistency_tracker", data_point="streak", value=float(consistency_streak)),
                PredictionEvidence(source="recovery", data_point="score", value=recovery_score),
            ],
        )

        forecast = Forecast(
            prediction_type=PredictionType.NEXT_PR_PROBABILITY,
            window=window,
            points=_generate_forecast_points(pr_score, 0.01, window, confidence_score),
            trend_model=TrendModel.LINEAR,
            confidence=PredictionConfidence(score=round(confidence_score, 2), sample_size=consistency_streak),
            explanation=explanation,
        )

        return Prediction(
            prediction_type=PredictionType.NEXT_PR_PROBABILITY,
            window=window,
            value=round(pr_score * 100, 1),
            probability=round(pr_score, 2),
            confidence=PredictionConfidence(score=round(confidence_score, 2), sample_size=consistency_streak),
            explanation=explanation,
            forecast=forecast,
            scenarios=[
                PredictionScenario(name="PR Hit", description="New personal record achieved", probability=pr_score),
                PredictionScenario(name="No Change", description="Matched but didn't exceed", probability=max(0.3, 1.0 - pr_score - 0.15)),
                PredictionScenario(name="Miss", description="Below previous performance", probability=0.15),
            ],
        )


# ═══════════════════════════════════════════════════════════════
# 3. Recovery Prediction Engine
# ═══════════════════════════════════════════════════════════════

class RecoveryPredictionEngine:
    """Forecasts recovery score trajectory."""

    def predict(
        self,
        window: PredictionWindow = PredictionWindow.NEXT_7_DAYS,
        recovery_scores: list[float] | None = None,
        sleep_trend: float = 0.0,
        stress_trend: float = 0.0,
        training_volume_trend: float = 0.0,
        current_recovery_score: float = 70.0,
        days_since_deload: int = 30,
    ) -> Prediction:
        scores = recovery_scores or [current_recovery_score]
        slope, _ = _linear_regression(scores)
        adjusted_slope = slope + (sleep_trend * 0.3) - (stress_trend * 0.3) - (training_volume_trend * 0.1)
        if days_since_deload > 42:
            adjusted_slope -= 0.5

        score_at_end = current_recovery_score + adjusted_slope * window.days
        declining = score_at_end < current_recovery_score - 5
        decline_prob = 0.0
        factors: list[str] = []

        if declining:
            decline_prob = min(abs(adjusted_slope) * window.days / 100.0, 0.9)
            factors.append(f"Recovery trending down ({adjusted_slope:+.2f}/day)")
        if sleep_trend < -0.5:
            decline_prob += 0.15
            factors.append(f"Sleep declining ({sleep_trend:+.2f}h/day)")
        if stress_trend > 0.5:
            decline_prob += 0.15
            factors.append(f"Stress increasing ({stress_trend:+.2f}/day)")
        if training_volume_trend > 5:
            decline_prob += 0.15
            factors.append(f"Volume rapidly increasing ({training_volume_trend:+.0f}kg/day)")

        decline_prob = min(decline_prob, 0.95)
        confidence_score = _confidence_from_variance(scores)

        explanation = PredictionExplanation(
            summary=f"Recovery score forecast: {score_at_end:.0f}/100 in {window.days} days",
            reasoning=factors + [f"Projected recovery: {current_recovery_score:.0f} → {score_at_end:.0f}"],
            assumptions=["Current training load maintained", "Sleep/stress patterns stable", "No illness or injury"],
            risk_factors=["Unexpected illness", "Life stress spike", "Poor sleep streak"],
            evidence=[
                PredictionEvidence(source="recovery_history", data_point="current_score", value=current_recovery_score),
                PredictionEvidence(source="sleep_analysis", data_point="sleep_trend", value=sleep_trend),
                PredictionEvidence(source="stress_analysis", data_point="stress_trend", value=stress_trend),
            ],
        )

        forecast = Forecast(
            prediction_type=PredictionType.RECOVERY_DECLINE,
            window=window,
            points=_generate_forecast_points(current_recovery_score, adjusted_slope, window, confidence_score),
            trend_model=TrendModel.LINEAR,
            confidence=PredictionConfidence(score=round(confidence_score, 2), sample_size=len(scores)),
            explanation=explanation,
        )

        return Prediction(
            prediction_type=PredictionType.RECOVERY_DECLINE,
            window=window,
            value=round(score_at_end, 1),
            probability=round(decline_prob, 2),
            confidence=PredictionConfidence(score=round(confidence_score, 2), sample_size=len(scores)),
            explanation=explanation,
            forecast=forecast,
            scenarios=[
                PredictionScenario(name="Full Recovery", description="Recovery rebounds to 80+", probability=max(0.0, 1.0 - decline_prob - 0.2)),
                PredictionScenario(name="Stable", description="Recovery stays within ±5", probability=0.3),
                PredictionScenario(name="Decline", description="Recovery drops below 50", probability=decline_prob),
            ],
        )


# ═══════════════════════════════════════════════════════════════
# 4. Fatigue Prediction Engine
# ═══════════════════════════════════════════════════════════════

class FatiguePredictionEngine:
    """Forecasts fatigue accumulation trajectory."""

    def predict(
        self,
        window: PredictionWindow = PredictionWindow.NEXT_7_DAYS,
        current_fatigue: float = 40.0,
        recent_volume_7d: float = 0.0,
        recent_volume_14d: float = 0.0,
        sleep_avg: float = 7.0,
        stress_avg: float = 30.0,
        days_since_deload: int = 30,
        session_frequency: float = 4.0,
    ) -> Prediction:
        volume_daily_avg = recent_volume_7d / 7.0 if recent_volume_7d > 0 else 0.0
        sleep_deficit = max(0.0, 8.0 - sleep_avg)
        stress_factor = stress_avg / 100.0

        daily_fatigue_accumulation = (volume_daily_avg / 10000.0 * 3.0) + (sleep_deficit * 2.0) + (stress_factor * 1.5) - (5.0 if days_since_deload < 14 else 0.0)
        fatigue_at_end = current_fatigue + daily_fatigue_accumulation * window.days
        fatigue_at_end = max(0.0, min(fatigue_at_end, 100.0))

        high_fatigue_prob = max(0.0, min((fatigue_at_end - 60.0) / 40.0, 0.95)) if fatigue_at_end > 60 else 0.0
        factors: list[str] = []

        if daily_fatigue_accumulation > 1:
            factors.append(f"Fatigue accumulating at {daily_fatigue_accumulation:.1f}/day")
        if sleep_deficit > 1:
            factors.append(f"Sleep deficit ({sleep_deficit:.1f}h) adding {sleep_deficit * 2:.1f}/day")
        if stress_factor > 0.5:
            factors.append(f"Elevated stress adding {stress_factor * 1.5:.1f}/day")
        if days_since_deload > 42:
            factors.append(f"{days_since_deload} days since deload — accumulated fatigue")
        if session_frequency > 5:
            factors.append(f"High frequency ({session_frequency:.0f}x/week) — limited recovery")

        confidence_score = min(0.6, 0.3 + (1.0 / max(1, window.days)) * 2.0)

        explanation = PredictionExplanation(
            summary=f"Fatigue forecast: {current_fatigue:.0f} → {fatigue_at_end:.0f}/100 in {window.days} days",
            reasoning=factors + [f"Projected fatigue: {fatigue_at_end:.0f}/100"],
            assumptions=["Training volume maintained", "Sleep/stress patterns continue", "No deload in forecast window"],
            risk_factors=["Overtraining", "Recovery debt compounding", "Injury risk at >70 fatigue"],
            evidence=[
                PredictionEvidence(source="volume_analysis", data_point="volume_7d", value=recent_volume_7d),
                PredictionEvidence(source="sleep_analysis", data_point="sleep_avg", value=sleep_avg),
                PredictionEvidence(source="stress_analysis", data_point="stress_avg", value=stress_avg),
            ],
        )

        forecast = Forecast(
            prediction_type=PredictionType.MRV_VIOLATION_RISK,
            window=window,
            points=_generate_forecast_points(current_fatigue, daily_fatigue_accumulation, window, confidence_score),
            trend_model=TrendModel.LINEAR,
            confidence=PredictionConfidence(score=round(confidence_score, 2)),
            explanation=explanation,
        )

        return Prediction(
            prediction_type=PredictionType.MRV_VIOLATION_RISK,
            window=window,
            value=round(fatigue_at_end, 1),
            probability=round(high_fatigue_prob, 2),
            confidence=PredictionConfidence(score=round(confidence_score, 2)),
            explanation=explanation,
            forecast=forecast,
            scenarios=[
                PredictionScenario(name="Fatigue Controlled", description="Fatigue stays under 50", probability=1.0 - high_fatigue_prob),
                PredictionScenario(name="Elevated Fatigue", description="Fatigue between 50-70", probability=0.3),
                PredictionScenario(name="Critical Fatigue", description="Fatigue exceeds 70 — deload needed", probability=high_fatigue_prob),
            ],
        )


# ═══════════════════════════════════════════════════════════════
# 5. Bodyweight Prediction Engine
# ═══════════════════════════════════════════════════════════════

class BodyweightPredictionEngine:
    """Forecasts bodyweight trajectory based on caloric data and trends."""

    def predict(
        self,
        window: PredictionWindow = PredictionWindow.NEXT_14_DAYS,
        bodyweight_history: list[float] | None = None,
        calorie_surplus_avg: float = 0.0,
        current_bodyweight: float = 75.0,
        calorie_adherence: float = 0.8,
    ) -> Prediction:
        bw = bodyweight_history or [current_bodyweight]
        slope, _ = _linear_regression(bw)

        bw_weekly_change = slope * 7.0
        metabolic_factor = calorie_surplus_avg / 7700.0
        effective_weekly_change = bw_weekly_change + metabolic_factor * calorie_adherence
        daily_change = effective_weekly_change / 7.0

        bw_at_end = current_bodyweight + daily_change * window.days
        confidence_score = _confidence_from_variance(bw)

        factors: list[str] = []
        if abs(daily_change * 7) < 0.1:
            factors.append("Bodyweight is stable")
        elif daily_change > 0:
            factors.append(f"Gaining {daily_change * 7:.2f}kg/week")
        else:
            factors.append(f"Losing {abs(daily_change * 7):.2f}kg/week")

        if calorie_adherence < 0.5:
            factors.append(f"Low adherence ({calorie_adherence * 100:.0f}%) reduces prediction confidence")

        explanation = PredictionExplanation(
            summary=f"Bodyweight forecast: {current_bodyweight:.1f} → {bw_at_end:.1f}kg in {window.days} days",
            reasoning=factors + [f"Projected weight: {bw_at_end:.1f}kg ({'gain' if bw_at_end > current_bodyweight else 'loss'}: {abs(bw_at_end - current_bodyweight):.2f}kg)"],
            assumptions=["Caloric intake remains consistent", "Activity level unchanged", "Metabolic adaptation minimal"],
            risk_factors=["Metabolic adaptation", "Water weight fluctuations", "Diet adherence drops"],
            evidence=[
                PredictionEvidence(source="bodyweight_history", data_point="current", value=current_bodyweight),
                PredictionEvidence(source="nutrition", data_point="calorie_surplus", value=calorie_surplus_avg),
            ],
        )

        forecast = Forecast(
            prediction_type=PredictionType.BODYWEIGHT_TREND,
            window=window,
            points=_generate_forecast_points(current_bodyweight, daily_change, window, confidence_score),
            trend_model=TrendModel.LINEAR,
            confidence=PredictionConfidence(score=round(confidence_score, 2), sample_size=len(bw)),
            explanation=explanation,
        )

        return Prediction(
            prediction_type=PredictionType.BODYWEIGHT_TREND,
            window=window,
            value=round(bw_at_end, 1),
            probability=round(min(abs(effective_weekly_change) / 1.0, 0.95), 2),
            confidence=PredictionConfidence(score=round(confidence_score, 2), sample_size=len(bw)),
            explanation=explanation,
            forecast=forecast,
            scenarios=[
                PredictionScenario(name="On Track", description="Weight change within 0.5kg of target trajectory", probability=0.5),
                PredictionScenario(name="Faster", description="Weight change exceeds trajectory by 0.5kg+", probability=0.25),
                PredictionScenario(name="Slower", description="Weight change lags trajectory by 0.5kg+", probability=0.25),
            ],
        )


# ═══════════════════════════════════════════════════════════════
# 6. Goal ETA Prediction Engine
# ═══════════════════════════════════════════════════════════════

class GoalEtaPredictionEngine:
    """Estimates time remaining to reach a bodyweight goal."""

    def predict(
        self,
        current_bodyweight: float = 75.0,
        goal_bodyweight: float = 70.0,
        bodyweight_history: list[float] | None = None,
        calorie_surplus_avg: float = 0.0,
        calorie_adherence: float = 0.8,
        window: PredictionWindow = PredictionWindow.NEXT_28_DAYS,
    ) -> Prediction:
        bw_values = bodyweight_history or [current_bodyweight]
        slope, _ = _linear_regression(bw_values)
        historical_rate = slope * 7.0 if abs(slope) > 0.001 else 0.0

        if abs(historical_rate) > 0.01:
            effective_rate = historical_rate
        else:
            effective_rate = (calorie_surplus_avg / 7700.0) * calorie_adherence

        weight_diff = goal_bodyweight - current_bodyweight
        losing = weight_diff < 0

        if abs(effective_rate) < 0.01:
            days_remaining = 999
            eta_date = "unknown"
        else:
            days_remaining = abs(int(weight_diff / (effective_rate / 7.0)))
            eta_date = (datetime.now() + timedelta(days=days_remaining)).strftime("%Y-%m-%d") if days_remaining < 9999 else "unknown"

        achievable = days_remaining < 365 or (days_remaining >= 365 and abs(weight_diff) < 5)
        confidence_score = min(0.8, 0.3 + (calorie_adherence * 0.4) + (0.1 if days_remaining < 365 else 0.0))

        factors: list[str] = []
        direction = "lose" if losing else "gain"
        factors.append(f"Need to {direction} {abs(weight_diff):.1f}kg")
        factors.append(f"Current rate: {abs(effective_rate):.2f}kg/week")
        if days_remaining < 90:
            factors.append(f"ETA: {days_remaining} days ({eta_date}) — achievable")
        elif days_remaining < 365:
            factors.append(f"ETA: ~{days_remaining} days ({eta_date}) — on track")
        else:
            factors.append("Goal is distant — may need faster rate")

        explanation = PredictionExplanation(
            summary=f"Goal ETA: {days_remaining} days ({eta_date})" if days_remaining < 9999 else "Goal ETA: beyond prediction horizon",
            reasoning=factors,
            assumptions=["Current rate maintained", "Adherence continues", "Metabolic adaptation minimal"],
            risk_factors=["Plateau", "Adherence drop", "Metabolic adaptation", "Goal recalibration"],
            evidence=[
                PredictionEvidence(source="bodyweight_history", data_point="current", value=current_bodyweight),
                PredictionEvidence(source="bodyweight_history", data_point="goal", value=goal_bodyweight),
                PredictionEvidence(source="nutrition", data_point="calorie_adherence", value=calorie_adherence),
            ],
        )

        return Prediction(
            prediction_type=PredictionType.GOAL_ETA,
            window=window,
            value=float(days_remaining),
            probability=round(confidence_score, 2),
            confidence=PredictionConfidence(score=round(confidence_score, 2), sample_size=len(bw_values)),
            explanation=explanation,
            scenarios=[
                PredictionScenario(name="On Schedule", description="Hitting goal by ETA", probability=confidence_score),
                PredictionScenario(name="Delayed", description="Goal pushed 30-60 days out", probability=0.3 * (1.0 - calorie_adherence)),
                PredictionScenario(name="Accelerated", description="Goal achieved early", probability=0.15 * calorie_adherence),
            ],
        )


# ═══════════════════════════════════════════════════════════════
# 7. Volume / MRV Prediction Engine
# ═══════════════════════════════════════════════════════════════

class VolumePredictionEngine:
    """Forecasts volume trends and MRV violation risk."""

    def predict(
        self,
        window: PredictionWindow = PredictionWindow.NEXT_7_DAYS,
        weekly_volumes: list[float] | None = None,
        estimated_mrv: float = 20000.0,
        current_weekly_volume: float = 14000.0,
        session_count: int = 4,
        average_rpe: float = 7.0,
    ) -> Prediction:
        volumes = weekly_volumes or [current_weekly_volume]
        slope, _ = _linear_regression(volumes)

        volume_at_end = current_weekly_volume + slope * max(1, window.days // 7)
        volume_ratio_to_mrv = volume_at_end / estimated_mrv
        mrv_violation_risk = max(0.0, min((volume_ratio_to_mrv - 0.8) / 0.2, 0.95)) if volume_ratio_to_mrv > 0.8 else 0.0

        factors: list[str] = []
        if slope > 500:
            factors.append(f"Volume increasing rapidly ({slope:.0f}kg/week)")
        elif slope < -500:
            factors.append(f"Volume decreasing ({slope:.0f}kg/week)")
        else:
            factors.append("Volume is stable")

        if volume_ratio_to_mrv > 1.0:
            factors.append(f"Volume ({volume_at_end:.0f}kg) EXCEEDS MRV ({estimated_mrv:.0f}kg) — high risk!")
        elif volume_ratio_to_mrv > 0.9:
            factors.append(f"Volume approaching MRV ({volume_ratio_to_mrv * 100:.0f}%)")
        else:
            factors.append(f"Volume at {volume_ratio_to_mrv * 100:.0f}% of MRV — safe")

        if average_rpe > 8:
            factors.append(f"High RPE ({average_rpe:.1f}) — intensity may need adjustment")

        confidence_score = _confidence_from_variance(volumes)

        explanation = PredictionExplanation(
            summary=f"Volume forecast: {current_weekly_volume:.0f} → {volume_at_end:.0f}kg/wk (MRV: {estimated_mrv:.0f})",
            reasoning=factors + [f"MRV violation risk: {mrv_violation_risk * 100:.0f}%"],
            assumptions=["Current program maintained", "MRV estimate accurate for user experience level", "No deload planned"],
            risk_factors=["Joint/tendon overuse", "Systemic fatigue", "Recovery debt", "Stalled progress"],
            evidence=[
                PredictionEvidence(source="volume_tracking", data_point="current_volume", value=current_weekly_volume),
                PredictionEvidence(source="volume_tracking", data_point="estimated_mrv", value=estimated_mrv),
            ],
        )

        forecast = Forecast(
            prediction_type=PredictionType.MRV_VIOLATION_RISK,
            window=window,
            points=_generate_forecast_points(current_weekly_volume, slope / 7.0, window, confidence_score),
            trend_model=TrendModel.LINEAR,
            confidence=PredictionConfidence(score=round(confidence_score, 2), sample_size=len(volumes)),
            explanation=explanation,
        )

        return Prediction(
            prediction_type=PredictionType.MRV_VIOLATION_RISK,
            window=window,
            value=round(volume_at_end, 0),
            probability=round(mrv_violation_risk, 2),
            confidence=PredictionConfidence(score=round(confidence_score, 2), sample_size=len(volumes)),
            explanation=explanation,
            forecast=forecast,
            scenarios=[
                PredictionScenario(name="Volume Safe", description="Volume stays below 80% MRV", probability=max(0.0, 1.0 - mrv_violation_risk - 0.2)),
                PredictionScenario(name="Approaching MRV", description="Volume at 80-100% MRV — monitor", probability=0.3),
                PredictionScenario(name="MRV Exceeded", description="Volume exceeds MRV — deload recommended", probability=mrv_violation_risk),
            ],
        )


# ═══════════════════════════════════════════════════════════════
# 8. Consistency / Workout Completion Prediction Engine
# ═══════════════════════════════════════════════════════════════

class ConsistencyPredictionEngine:
    """Forecasts consistency decay and workout completion probability."""

    def predict(
        self,
        window: PredictionWindow = PredictionWindow.NEXT_14_DAYS,
        current_streak: int = 0,
        weekly_consistency: list[float] | None = None,
        planned_sessions_per_week: int = 4,
        recent_completion_rate: float = 0.8,
        missed_last_7d: int = 0,
        recovery_avg: float = 70.0,
        motivation_score: float = 0.7,
        days_since_last_miss: int = 0,
    ) -> Prediction:
        consistency = weekly_consistency or [recent_completion_rate]
        slope, _ = _linear_regression(consistency)

        consistency_at_end = recent_completion_rate + slope * max(1, window.days // 7)
        consistency_at_end = max(0.0, min(consistency_at_end, 1.0))

        decay_detected = slope < -0.02
        decay_prob = 0.0
        completion_prob = recent_completion_rate + (current_streak * 0.01) - (missed_last_7d * 0.05) - (max(0, 70.0 - recovery_avg) * 0.005)
        completion_prob = max(0.0, min(completion_prob, 1.0))

        factors: list[str] = []
        if decay_detected:
            decay_prob = min(abs(slope) * 10 * (window.days / 7.0), 0.9)
            factors.append(f"Consistency declining ({slope:+.2f}/week)")
        if missed_last_7d > 1:
            factors.append(f"{missed_last_7d} missed sessions in last 7 days")
            decay_prob += 0.1 * missed_last_7d
        if current_streak > 14:
            factors.append(f"Strong streak ({current_streak} sessions) — positive")
            completion_prob += 0.1
        if recovery_avg < 50:
            factors.append("Low recovery — likely to miss upcoming sessions")
            decay_prob += 0.15
        if motivation_score < 0.4:
            factors.append("Low motivation — consistency risk")
            decay_prob += 0.15

        decay_prob = min(decay_prob, 0.95)
        confidence_score = _confidence_from_variance(consistency)

        explanation = PredictionExplanation(
            summary=f"Completion probability: {completion_prob * 100:.0f}% per session over {window.days} days",
            reasoning=factors + [f"Consistency forecast: {recent_completion_rate * 100:.0f}% → {consistency_at_end * 100:.0f}%"],
            assumptions=["Schedule maintained", "No injury/illness", "Motivation remains stable"],
            risk_factors=["Life schedule changes", "Injury", "Motivation drop", "Holiday/break"],
            evidence=[
                PredictionEvidence(source="consistency_tracker", data_point="streak", value=float(current_streak)),
                PredictionEvidence(source="consistency_tracker", data_point="missed_7d", value=float(missed_last_7d)),
                PredictionEvidence(source="recovery", data_point="avg_score", value=recovery_avg),
            ],
        )

        forecast = Forecast(
            prediction_type=PredictionType.CONSISTENCY_DECAY,
            window=window,
            points=_generate_forecast_points(recent_completion_rate * 100, slope * 100 / 7.0, window, confidence_score),
            trend_model=TrendModel.LINEAR,
            confidence=PredictionConfidence(score=round(confidence_score, 2), sample_size=len(consistency)),
            explanation=explanation,
        )

        return Prediction(
            prediction_type=PredictionType.CONSISTENCY_DECAY,
            window=window,
            value=round(completion_prob * 100, 1),
            probability=round(completion_prob, 2),
            confidence=PredictionConfidence(score=round(confidence_score, 2), sample_size=len(consistency)),
            explanation=explanation,
            forecast=forecast,
            scenarios=[
                PredictionScenario(name="Strong Consistency", description="Completion rate > 80%", probability=completion_prob),
                PredictionScenario(name="Moderate Drop", description="Completion rate 50-80%", probability=0.3),
                PredictionScenario(name="Significant Decay", description="Completion rate < 50%", probability=1.0 - completion_prob - 0.3),
            ],
        )


# ═══════════════════════════════════════════════════════════════
# 9. Deload Probability Engine
# ═══════════════════════════════════════════════════════════════

class DeloadPredictionEngine:
    """Predicts probability that a deload will be needed."""

    def predict(
        self,
        window: PredictionWindow = PredictionWindow.NEXT_14_DAYS,
        weeks_since_last_deload: int = 6,
        recovery_scores: list[float] | None = None,
        current_fatigue: float = 40.0,
        fatigue_trend: float = 0.0,
        volume_ratio_14d_7d: float = 1.0,
        sleep_avg: float = 7.0,
        session_count_7d: int = 4,
        deload_frequency_weeks: int = 6,
    ) -> Prediction:
        scores = recovery_scores or []
        deload_score = 0.0
        factors: list[str] = []

        # Time-based
        if weeks_since_last_deload >= deload_frequency_weeks:
            deload_score += 0.25
            factors.append(f"{weeks_since_last_deload} weeks since last deload (target: {deload_frequency_weeks})")

        # Recovery-based
        if scores:
            avg = sum(scores) / len(scores)
            if avg < 50:
                deload_score += 0.2
                factors.append(f"Average recovery {avg:.0f}/100 — below threshold")
            if len(scores) >= 3 and all(s < 40 for s in scores[-3:]):
                deload_score += 0.15
                factors.append("Last 3 scores below 40 — fatigue accumulation")

        # Fatigue-based
        if current_fatigue > 70:
            deload_score += 0.15
            factors.append(f"Fatigue {current_fatigue:.0f}/100 — very high")
        if fatigue_trend > 2:
            deload_score += 0.1
            factors.append(f"Fatigue increasing {fatigue_trend:.1f}/day")

        # Volume ratio
        if volume_ratio_14d_7d > 2.0:
            deload_score += 0.1
            factors.append(f"Volume ratio {volume_ratio_14d_7d:.1f}x — accumulating")
        if session_count_7d > 5:
            deload_score += 0.05
            factors.append(f"High frequency ({session_count_7d}x/week)")

        # Sleep
        if sleep_avg < 6:
            deload_score += 0.1
            factors.append(f"Poor sleep ({sleep_avg:.1f}h avg)")

        deload_score = min(deload_score, 0.95)
        confidence_score = min(0.7, 0.3 + len(scores) * 0.02)

        explanation = PredictionExplanation(
            summary=f"Deload probability: {deload_score * 100:.0f}% in next {window.days} days",
            reasoning=factors + [f"Overall deload risk: {deload_score * 100:.0f}%"],
            assumptions=["Current training load maintained", "No lifestyle changes", "Recovery patterns continue"],
            risk_factors=["Overtraining", "Injury from accumulated fatigue", "Performance stagnation"],
            evidence=[
                PredictionEvidence(source="recovery_history", data_point="score_avg", value=sum(scores) / len(scores) if scores else 0),
                PredictionEvidence(source="fatigue_monitoring", data_point="current", value=current_fatigue),
                PredictionEvidence(source="deload_history", data_point="weeks_since", value=float(weeks_since_last_deload)),
            ],
        )

        forecast = Forecast(
            prediction_type=PredictionType.DELOAD_PROBABILITY,
            window=window,
            points=_generate_forecast_points(deload_score, 0.02, window, confidence_score),
            trend_model=TrendModel.LINEAR,
            confidence=PredictionConfidence(score=round(confidence_score, 2), sample_size=len(scores)),
            explanation=explanation,
        )

        return Prediction(
            prediction_type=PredictionType.DELOAD_PROBABILITY,
            window=window,
            value=round(deload_score * 100, 1),
            probability=round(deload_score, 2),
            confidence=PredictionConfidence(score=round(confidence_score, 2), sample_size=len(scores)),
            explanation=explanation,
            forecast=forecast,
            scenarios=[
                PredictionScenario(name="No Deload Needed", description="Recovery sufficient, continue training", probability=1.0 - deload_score),
                PredictionScenario(name="Deload Recommended", description="Deload in next 1-2 weeks", probability=deload_score * 0.7),
                PredictionScenario(name="Deload Urgent", description="Immediate deload recommended", probability=deload_score * 0.3),
            ],
        )


# ═══════════════════════════════════════════════════════════════
# Imports from new engine modules (RFC-020.5)
# ═══════════════════════════════════════════════════════════════

from modules.prediction.engines.counterfactual_engine import (
    CounterfactualEngine,
)
from modules.prediction.engines.explainability_engine import (
    ExplainabilityEngine,
)
from modules.prediction.engines.risk_engine import (
    RiskEngine,
)
from modules.prediction.engines.scenario_engine import (
    PredictionScenarioEngine,
    ScenarioBuilder,
)
