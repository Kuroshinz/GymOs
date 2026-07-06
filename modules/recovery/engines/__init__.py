"""GymOS Recovery Engines — deterministic, strongly-typed engines for recovery intelligence.

All engines are:
  - Deterministic (same inputs → same outputs)
  - Stateless (no internal state)
  - Pure (no side effects)
  - Composable (engines call each other)

Engine architecture:
  RecoveryScoreEngine   ← SleepAnalyzer, StressAnalyzer, FatigueAggregator
  ReadinessEngine       ← RecoveryScoreEngine, RecoveryTrendAnalyzer
  DeloadEngine          ← RecoveryScoreEngine, FatigueAggregator
"""

from __future__ import annotations

import math
from datetime import datetime, timedelta
from typing import Optional

from modules.recovery.domain import (
    DeloadPlan,
    DeloadStatus,
    FatigueFactors,
    FatigueLevel,
    ReadinessAssessment,
    ReadinessLevel,
    RecoveryFactors,
    RecoveryProfile,
    RecoveryScore,
    RecoveryTrend,
    RecoveryTrendAnalysis,
    SleepLog,
    SleepQuality,
    SorenessLevel,
    StressLevel,
    StressLog,
)

# ═══════════════════════════════════════════════════════════════
# Sleep Analyzer
# ═══════════════════════════════════════════════════════════════

class SleepAnalyzer:
    """Analyzes sleep data and produces a sleep quality score (0-100)."""

    def analyze(self, hours: float, quality: SleepQuality | None = None,
                profile: RecoveryProfile | None = None) -> float:
        """Score sleep quality from 0-100 based on duration and quality."""
        sleep_need = profile.sleep_need_hours if profile else 8.0

        # Duration score (0-60)
        if hours >= sleep_need:
            duration_score = 60.0
        elif hours >= sleep_need - 1:
            duration_score = 45.0 + (hours - (sleep_need - 1)) * 15.0
        elif hours >= sleep_need - 2:
            duration_score = 25.0 + (hours - (sleep_need - 2)) * 20.0
        elif hours >= 4.0:
            duration_score = max(0, hours / sleep_need * 25.0)
        else:
            duration_score = 0.0

        # Quality score (0-40)
        quality_scores = {
            SleepQuality.EXCELLENT: 40.0,
            SleepQuality.VERY_GOOD: 35.0,
            SleepQuality.GOOD: 28.0,
            SleepQuality.FAIR: 18.0,
            SleepQuality.POOR: 8.0,
        }
        quality_score = quality_scores.get(quality, 20.0)

        # Apply sensitivity
        sensitivity = profile.sleep_sensitivity if profile else 1.0
        total = (duration_score + quality_score) * sensitivity
        return round(min(total, 100.0), 1)

    def analyze_log(self, log: SleepLog, profile: RecoveryProfile | None = None) -> float:
        return self.analyze(log.hours, log.quality, profile)

    def get_sleep_deficit(self, hours: float, profile: RecoveryProfile | None = None) -> float:
        """Calculate sleep deficit in hours (positive = under-slept)."""
        need = profile.sleep_need_hours if profile else 8.0
        return max(0.0, need - hours)


# ═══════════════════════════════════════════════════════════════
# Stress Analyzer
# ═══════════════════════════════════════════════════════════════

class StressAnalyzer:
    """Analyzes stress levels and produces a stress impact score (0-100, higher = worse)."""

    STRESS_SCORES = {
        StressLevel.VERY_LOW: 5.0,
        StressLevel.LOW: 15.0,
        StressLevel.MODERATE: 35.0,
        StressLevel.HIGH: 60.0,
        StressLevel.VERY_HIGH: 85.0,
    }

    def analyze(self, level: StressLevel, profile: RecoveryProfile | None = None) -> float:
        """Score stress impact from 0-100 (higher = worse recovery)."""
        base_score = self.STRESS_SCORES.get(level, 35.0)
        sensitivity = profile.stress_sensitivity if profile else 1.0
        stress_score = base_score * sensitivity
        return round(min(stress_score, 100.0), 1)

    def score_from_level(self, level: StressLevel, profile: RecoveryProfile | None = None) -> float:
        """Alias for analyze()."""
        return self.analyze(level, profile)

    def recovery_impact(self, stress_score: float) -> float:
        """Convert stress score to recovery impact (0-100, higher = more impact on recovery)."""
        return round(stress_score * 0.6, 1)


# ═══════════════════════════════════════════════════════════════
# Fatigue Aggregator
# ═══════════════════════════════════════════════════════════════

class FatigueAggregator:
    """Aggregates multiple fatigue signals into a composite fatigue score (0-100)."""

    SORENESS_SCORES = {
        SorenessLevel.NONE: 0.0,
        SorenessLevel.MILD: 15.0,
        SorenessLevel.MODERATE: 35.0,
        SorenessLevel.SEVERE: 60.0,
        SorenessLevel.VERY_SEVERE: 85.0,
    }

    FATIGUE_SCORES = {
        FatigueLevel.VERY_LOW: 5.0,
        FatigueLevel.LOW: 15.0,
        FatigueLevel.MODERATE: 35.0,
        FatigueLevel.HIGH: 65.0,
        FatigueLevel.VERY_HIGH: 85.0,
    }

    def aggregate(
        self,
        training_fatigue: float = 0.0,
        sleep_score: float = 100.0,
        stress_score: float = 0.0,
        soreness: SorenessLevel | None = None,
        subjective_fatigue: int | None = None,
        profile: RecoveryProfile | None = None,
    ) -> float:
        """Compute composite fatigue score (0-100, higher = more fatigued)."""
        # Training fatigue (30%)
        tf_weight = 0.30

        # Sleep inversion: high sleep_score = low fatigue contribution (25%)
        sleep_fatigue = 100.0 - sleep_score
        sf_weight = 0.25

        # Stress (20%)
        st_weight = 0.20

        # Soreness (15%)
        soreness_score = self.SORENESS_SCORES.get(soreness, 0.0) if soreness else 0.0
        so_weight = 0.15

        # Subjective fatigue (10%)
        if subjective_fatigue is not None:
            subj_score = (subjective_fatigue - 1) / 4.0 * 100.0
        else:
            subj_score = 0.0
        su_weight = 0.10

        # Apply sensitivity
        sensitivity = profile.fatigue_sensitivity if profile else 1.0

        total = (
            training_fatigue * tf_weight +
            sleep_fatigue * sf_weight +
            stress_score * st_weight +
            soreness_score * so_weight +
            subj_score * su_weight
        ) * sensitivity

        return round(min(total, 100.0), 1)

    def compute_fatigue_factors(
        self,
        recent_volume_7d: float = 0.0,
        recent_volume_14d: float = 0.0,
        session_count_7d: int = 0,
        average_rpe: float = 7.0,
        days_since_deload: int = 999,
        recent_sleep_avg: float = 7.0,
        recent_stress_avg: float = 30.0,
    ) -> FatigueFactors:
        """Compute detailed fatigue factor breakdown."""
        volume_ratio = (recent_volume_14d / recent_volume_7d) if recent_volume_7d > 0 else 0.0

        # Overall fatigue from training load
        vol_score = min(recent_volume_7d / 50000.0, 1.0) * 40.0 if recent_volume_7d > 0 else 0.0
        freq_score = min(session_count_7d / 7.0, 1.0) * 20.0
        intensity_score = (average_rpe / 10.0) * 20.0
        deload_penalty = max(0, (30 - days_since_deload) / 30.0) * 20.0 if days_since_deload < 30 else 0.0
        sleep_penalty = max(0, (8.0 - recent_sleep_avg) / 8.0) * 50.0
        stress_penalty = recent_stress_avg * 0.3

        overall = min(vol_score + freq_score + intensity_score + deload_penalty
                      + sleep_penalty + stress_penalty, 100.0)

        return FatigueFactors(
            training_volume_kg=recent_volume_7d,
            training_intensity=average_rpe,
            session_frequency=session_count_7d,
            cumulative_volume_7d=recent_volume_7d,
            cumulative_volume_14d=recent_volume_14d,
            volume_ratio=round(volume_ratio, 2),
            days_since_deload=days_since_deload,
            recent_sleep_avg=recent_sleep_avg,
            recent_stress_avg=recent_stress_avg,
            overall_fatigue=round(overall, 1),
        )


# ═══════════════════════════════════════════════════════════════
# Recovery Score Engine
# ═══════════════════════════════════════════════════════════════

class RecoveryScoreEngine:
    """Computes composite recovery scores (0-100) from all recovery signals.

    Weighted factors:
      Training fatigue        — 25%
      Sleep quality           — 20%
      Sleep duration          — 15%
      Stress                  — 15%
      Bodyweight trend        — 5%
      Nutrition adherence     — 10%
      Workout consistency     — 5%
      Recent deload benefit   — 5%
      Muscle recovery         — 0% (adjusts sleep/stress impact)
    """

    def __init__(self) -> None:
        self._sleep_analyzer = SleepAnalyzer()
        self._stress_analyzer = StressAnalyzer()
        self._fatigue_aggregator = FatigueAggregator()

    def compute(
        self,
        sleep_hours: float = 8.0,
        sleep_quality: SleepQuality | None = None,
        stress_level: StressLevel | None = None,
        soreness_level: SorenessLevel | None = None,
        subjective_fatigue: int | None = None,
        hrv_value: float | None = None,
        resting_hr: float | None = None,
        training_fatigue_score: float = 30.0,
        bodyweight_trend_score: float = 80.0,
        nutrition_adherence_score: float = 80.0,
        consistency_score: float = 80.0,
        days_since_deload: int = 999,
        profile: RecoveryProfile | None = None,
    ) -> RecoveryScore:
        """Compute full recovery score with component breakdown."""
        sleep_score = self._sleep_analyzer.analyze(sleep_hours, sleep_quality, profile)
        stress_score = self._stress_analyzer.analyze(stress_level or StressLevel.MODERATE, profile)

        muscle_recovery = self._compute_muscle_recovery(soreness_level)
        deload_benefit = self._compute_deload_benefit(days_since_deload)

        # Composite score (weighted)
        weights = {
            "training_fatigue": 0.25,
            "sleep": 0.35,        # sleep_score already combines duration + quality
            "stress": 0.15,
            "bodyweight_trend": 0.05,
            "nutrition_adherence": 0.10,
            "consistency": 0.05,
            "deload_benefit": 0.05,
        }

        raw = (
            (100.0 - training_fatigue_score) * weights["training_fatigue"] +
            sleep_score * weights["sleep"] +
            (100.0 - stress_score) * weights["stress"] +
            bodyweight_trend_score * weights["bodyweight_trend"] +
            nutrition_adherence_score * weights["nutrition_adherence"] +
            consistency_score * weights["consistency"] +
            deload_benefit * weights["deload_benefit"]
        )

        # Muscle recovery adjustment: soreness reduces effective score
        muscle_adjustment = muscle_recovery / 100.0  # 0.0-1.0 multiplier
        overall_score = round(raw * (0.85 + muscle_adjustment * 0.15), 1)
        overall_score = min(max(overall_score, 0.0), 100.0)

        # Readiness score is the recovery score with a slight fatigue penalty
        fatigue_penalty = training_fatigue_score * 0.3
        readiness_score = round(max(0.0, min(overall_score - fatigue_penalty * 0.1, 100.0)), 1)

        # Fatigue score is the inverse
        fatigue_composite = self._fatigue_aggregator.aggregate(
            training_fatigue=training_fatigue_score,
            sleep_score=sleep_score,
            stress_score=stress_score,
            soreness=soreness_level,
            subjective_fatigue=subjective_fatigue,
            profile=profile,
        )

        return RecoveryScore(
            overall_score=overall_score,
            readiness_score=readiness_score,
            readiness_level=ReadinessLevel.from_score(readiness_score),
            fatigue_score=fatigue_composite,
            sleep_score=round(sleep_score, 1),
            sleep_hours=sleep_hours,
            sleep_quality=sleep_quality,
            stress_score=round(stress_score, 1),
            stress_level=stress_level,
            soreness_level=soreness_level,
            muscle_recovery_score=round(muscle_recovery, 1),
            training_fatigue_score=round(training_fatigue_score, 1),
            nutrition_adherence_score=round(nutrition_adherence_score, 1),
            bodyweight_trend_score=round(bodyweight_trend_score, 1),
            consistency_score=round(consistency_score, 1),
            hrv_value=hrv_value,
            resting_hr=resting_hr,
            subjective_fatigue=subjective_fatigue,
        )

    def _compute_muscle_recovery(self, soreness: SorenessLevel | None = None) -> float:
        """Score muscle recovery based on soreness (0-100, higher = more recovered)."""
        scores = {
            SorenessLevel.NONE: 95.0,
            SorenessLevel.MILD: 75.0,
            SorenessLevel.MODERATE: 50.0,
            SorenessLevel.SEVERE: 25.0,
            SorenessLevel.VERY_SEVERE: 10.0,
        }
        return scores.get(soreness, 100.0)

    def _compute_deload_benefit(self, days_since_deload: int) -> float:
        """Score deload benefit (0-100, higher = more benefit from recent deload)."""
        if days_since_deload <= 7:
            return 100.0  # Peak benefit in first week after deload
        if days_since_deload <= 14:
            return 80.0
        if days_since_deload <= 21:
            return 60.0
        if days_since_deload <= 42:
            return 40.0
        return 20.0  # Benefit fades after 6+ weeks


# ═══════════════════════════════════════════════════════════════
# Readiness Engine
# ═══════════════════════════════════════════════════════════════

class ReadinessEngine:
    """Determines training readiness from recovery data.

    Produces a ReadinessAssessment with:
      - Readiness score & level
      - Suggested volume/intensity modifiers
      - Recommended action
      - Flags for the user
    """

    def __init__(self) -> None:
        self._score_engine = RecoveryScoreEngine()

    def assess(
        self,
        recovery_score: RecoveryScore,
        trend: RecoveryTrendAnalysis | None = None,
        profile: RecoveryProfile | None = None,
    ) -> ReadinessAssessment:
        """Assess training readiness from recovery and trend data."""
        level = recovery_score.readiness_level

        # Determine modifiers
        intensity_mod, volume_mod = self._get_training_modifiers(level)
        flags: list[str] = []

        # Apply trend adjustments
        if trend:
            if trend.direction.value == "declining":
                volume_mod *= 0.9
                intensity_mod *= 0.9
                flags.append("Recovery declining — consider lighter session")
            elif trend.direction.value == "volatile":
                volume_mod *= 0.95
                flags.append("Recovery unstable — monitor closely")

        # Check specific factors
        if recovery_score.sleep_score < 40:
            flags.append("Poor sleep quality — prioritize rest tonight")
        if recovery_score.stress_score > 60:
            flags.append("Elevated stress — consider active recovery")
        if recovery_score.fatigue_score > 70:
            flags.append("High fatigue — reduce volume by 20-30%")
        if recovery_score.soreness_level in (SorenessLevel.SEVERE, SorenessLevel.VERY_SEVERE):
            flags.append("High muscle soreness — consider upper/lower split or rest")
        if recovery_score.hrv_value and profile:
            hrv_drop = (profile.hrv_baseline - recovery_score.hrv_value) / profile.hrv_baseline * 100
            if hrv_drop > 20:
                flags.append(f"HRV {hrv_drop:.0f}% below baseline — prioritize recovery")

        # Recommended action
        action = self._get_recommended_action(level, flags)

        return ReadinessAssessment(
            date=recovery_score.date or datetime.now().strftime("%Y-%m-%d"),
            readiness_score=recovery_score.readiness_score,
            readiness_level=level,
            recovery_score=recovery_score.overall_score,
            fatigue_score=recovery_score.fatigue_score,
            suggested_intensity_modifier=round(intensity_mod, 2),
            suggested_volume_modifier=round(volume_mod, 2),
            recommended_action=action,
            flags=flags,
        )

    @staticmethod
    def _get_training_modifiers(level: ReadinessLevel) -> tuple[float, float]:
        """Get intensity and volume modifiers for a readiness level."""
        modifiers = {
            ReadinessLevel.READY: (1.0, 1.0),
            ReadinessLevel.GOOD: (0.95, 0.95),
            ReadinessLevel.CAUTION: (0.85, 0.80),
            ReadinessLevel.FATIGUED: (0.70, 0.60),
            ReadinessLevel.DELOAD: (0.50, 0.40),
        }
        return modifiers.get(level, (0.85, 0.80))

    @staticmethod
    def _get_recommended_action(level: ReadinessLevel, flags: list[str]) -> str:
        if level == ReadinessLevel.READY:
            return "Train as planned. Push intensity if feeling good."
        if level == ReadinessLevel.GOOD:
            return "Train as planned. Maintain normal intensity."
        if level == ReadinessLevel.CAUTION:
            return "Train but reduce RPE by 1-2. Consider dropping one set per exercise."
        if level == ReadinessLevel.FATIGUED:
            return "Light session or active recovery recommended. Consider taking a rest day."
        return "Deload recommended. Take a rest day or perform light active recovery."


# ═══════════════════════════════════════════════════════════════
# Deload Engine
# ═══════════════════════════════════════════════════════════════

class DeloadEngine:
    """Determines when and how to deload based on recovery and training data."""

    def __init__(self) -> None:
        self._score_engine = RecoveryScoreEngine()
        self._fatigue_aggregator = FatigueAggregator()

    def should_deload(
        self,
        weeks_since_last_deload: int,
        recent_scores: list[float],
        fatigue_factors: FatigueFactors | None = None,
        profile: RecoveryProfile | None = None,
    ) -> tuple[bool, str]:
        """Determine if a deload is recommended.

        Returns (should_deload, reason).
        """
        reasons: list[str] = []

        # Check deload frequency
        frequency = profile.deload_frequency_weeks if profile else 6
        if weeks_since_last_deload >= frequency:
            reasons.append(f"{weeks_since_last_deload} weeks since last deload (target: {frequency})")

        # Check recovery scores
        if recent_scores:
            avg_recovery = sum(recent_scores) / len(recent_scores)
            if avg_recovery < 50:
                reasons.append(f"Average recovery score {avg_recovery:.0f}/100 — below 50 threshold")
            if len(recent_scores) >= 3 and all(s < 40 for s in recent_scores[-3:]):
                reasons.append("Last 3 recovery scores below 40 — significant fatigue accumulation")

        # Check fatigue factors
        if fatigue_factors:
            if fatigue_factors.overall_fatigue > 70:
                reasons.append(f"Fatigue level {fatigue_factors.overall_fatigue:.0f}/100 — very high")
            if fatigue_factors.volume_ratio > 2.0:
                reasons.append(f"Volume ratio {fatigue_factors.volume_ratio:.1f}x — training load accumulating")
            if fatigue_factors.recent_sleep_avg < 6:
                reasons.append(f"Weekly sleep average {fatigue_factors.recent_sleep_avg:.1f}h — below recovery threshold")

        if not reasons:
            return False, "Deload not needed. Recovery metrics look good."

        return True, "; ".join(reasons)

    def create_deload_plan(
        self,
        reason: str,
        weeks_since_last_deload: int = 6,
        profile: RecoveryProfile | None = None,
    ) -> DeloadPlan:
        """Create a deload plan with recommended dates and instructions."""
        today = datetime.now()
        start = today.strftime("%Y-%m-%d")
        end = (today + timedelta(days=7)).strftime("%Y-%m-%d")

        instructions = (
            "DELOAD PROTOCOL:\n"
            "- Reduce volume by 40-60% (fewer sets)\n"
            "- Keep intensity (weight) the same — don't drop weight\n"
            "- Maintain training frequency (same split)\n"
            "- RPE target: 5-6 (leave 4-5 reps in reserve)\n"
            "- Focus on technique and mind-muscle connection\n"
            "- After deload: resume normal progression\n"
            "- Expect DOMS on first week back — this is normal"
        )

        return DeloadPlan(
            start_date=start,
            end_date=end,
            reason=reason,
            volume_reduction_percent=50.0,
            intensity_reduction_percent=20.0,
            instructions=instructions,
            status=DeloadStatus.PLANNED,
            weeks_since_last_deload=weeks_since_last_deload,
        )


# ═══════════════════════════════════════════════════════════════
# Recovery Trend Analyzer
# ═══════════════════════════════════════════════════════════════

class RecoveryTrendAnalyzer:
    """Analyzes recovery score trends over time.

    Produces a RecoveryTrend with direction, slope, and volatility metrics.
    """

    def analyze(self, scores: list[RecoveryScore]) -> RecoveryTrendAnalysis:
        """Analyze a list of recovery scores for trend information."""
        if not scores:
            return RecoveryTrendAnalysis(days_analyzed=0)

        sorted_scores = sorted(scores, key=lambda s: s.date)
        values = [s.overall_score for s in sorted_scores]
        dates = [s.date for s in sorted_scores]
        n = len(values)

        avg = sum(values) / n
        mn = min(values)
        mx = max(values)
        variance = sum((v - avg) ** 2 for v in values) / n
        std_dev = variance ** 0.5
        cv = std_dev / avg if avg > 0 else 0.0

        # Linear regression slope
        x_mean = (n - 1) / 2.0
        y_mean = avg
        num = sum((i - x_mean) * (v - y_mean) for i, v in enumerate(values))
        den = sum((i - x_mean) ** 2 for i in range(n))
        slope = num / den if den else 0.0

        # Weekly averages
        weekly_avgs: list[float] = []
        for i in range(0, n, 7):
            chunk = values[i:i + 7]
            weekly_avgs.append(sum(chunk) / len(chunk))

        # Direction
        if cv > 0.25:
            direction = RecoveryTrend.VOLATILE
        elif slope > 0.5:
            direction = RecoveryTrend.IMPROVING
        elif slope < -0.5:
            direction = RecoveryTrend.DECLINING
        else:
            direction = RecoveryTrend.STABLE

        return RecoveryTrendAnalysis(
            direction=direction,
            average_score=round(avg, 1),
            min_score=round(mn, 1),
            max_score=round(mx, 1),
            std_dev=round(std_dev, 1),
            slope=round(slope, 2),
            days_analyzed=n,
            recent_scores=values,
            recent_dates=dates,
            weekly_averages=weekly_avgs,
            explanation=self._explain(direction, slope, cv),
        )

    @staticmethod
    def _explain(direction: RecoveryTrend, slope: float, cv: float) -> str:
        parts = [f"Trend: {direction.value}"]
        if direction == RecoveryTrend.IMPROVING:
            parts.append(f"Improving at {slope:+.2f} points/day")
        elif direction == RecoveryTrend.DECLINING:
            parts.append(f"Declining at {slope:.2f} points/day")
        elif direction == RecoveryTrend.VOLATILE:
            parts.append(f"High volatility (CV: {cv:.2f}) — recovery is inconsistent")
        else:
            parts.append("Recovery is stable")
        return " | ".join(parts)


# ═══════════════════════════════════════════════════════════════
# Recovery Factors Calculator
# ═══════════════════════════════════════════════════════════════

class RecoveryFactorsCalculator:
    """Calculates RecoveryFactors from individual component scores."""

    def calculate(
        self,
        sleep_score: float = 0.0,
        stress_score: float = 0.0,
        hrv_score: float = 0.0,
        nutrition_score: float = 0.0,
        hydration_score: float = 0.0,
        bodyweight_trend: float = 0.0,
        training_consistency: float = 0.0,
        muscle_recovery: float = 0.0,
        deload_benefit: float = 0.0,
    ) -> RecoveryFactors:
        """Compute RecoveryFactors with 0-100 scores for each dimension."""
        overall = (
            sleep_score * 0.25 +
            (100.0 - stress_score) * 0.15 +
            hrv_score * 0.15 +
            nutrition_score * 0.15 +
            training_consistency * 0.10 +
            muscle_recovery * 0.10 +
            deload_benefit * 0.05 +
            bodyweight_trend * 0.05
        )
        return RecoveryFactors(
            sleep_quality_score=round(sleep_score, 1),
            sleep_duration_score=round(sleep_score, 1),
            stress_level_score=round(stress_score, 1),
            hrv_score=round(hrv_score, 1),
            nutrition_score=round(nutrition_score, 1),
            hydration_score=round(hydration_score, 1),
            bodyweight_trend=round(bodyweight_trend, 1),
            training_consistency=round(training_consistency, 1),
            muscle_recovery=round(muscle_recovery, 1),
            deload_benefit=round(deload_benefit, 1),
            overall=round(overall, 1),
        )
