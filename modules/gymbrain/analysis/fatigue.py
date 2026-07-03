from __future__ import annotations

from typing import Any

from modules.gymbrain.models.analysis import FatigueLevel, FatigueResult
from modules.gymbrain.providers.data_provider import DataProvider


class FatigueAnalyzer:
    """Analyzes systemic fatigue from training data.

    Combines recovery flags, RIR data, session volume, and frequency
    to produce a fatigue level and explanation.
    """

    def __init__(self, provider: DataProvider) -> None:
        self._provider = provider

    def analyze(self, days: int = 14) -> FatigueResult:
        sessions = self._provider.get_recent_sessions(days=days)
        factors: list[str] = []
        score = 0.0

        # Factor 1: Session count and frequency
        num_sessions = len(sessions)
        if num_sessions == 0:
            return FatigueResult(
                level=FatigueLevel.LOW,
                score=0.0,
                explanation="No recent training data available for fatigue analysis",
                factors=["No recent sessions"],
                recommendations=["Start training to get fatigue analysis"],
            )

        sessions_per_week = num_sessions / (days / 7)
        if sessions_per_week > 6:
            score += 30
            factors.append(f"High frequency: {sessions_per_week:.1f} sessions/week")
        elif sessions_per_week > 4:
            score += 15
            factors.append(f"Moderate frequency: {sessions_per_week:.1f} sessions/week")
        else:
            factors.append(f"Normal frequency: {sessions_per_week:.1f} sessions/week")

        # Factor 2: Recovery flags from RecoveryEngine
        total_flags = 0
        critical_flags = 0
        for s in sessions:
            if not hasattr(s, "exercises"):
                continue
            report = self._provider.analyse_session(s)
            if report and hasattr(report, "flags"):
                total_flags += len(report.flags)
                for f in report.flags:
                    severity = getattr(f, "severity", "info")
                    if severity == "critical":
                        critical_flags += 1
                    elif severity == "warning":
                        score += 10

        if critical_flags >= 3:
            score += 30
            factors.append(f"{critical_flags} critical recovery flags")
        elif critical_flags >= 1:
            score += 15
            factors.append(f"{critical_flags} critical recovery flag(s)")

        if total_flags > 0:
            factors.append(f"{total_flags} total recovery flags")

        # Factor 3: RIR analysis — consistently low RIR = high fatigue
        rir_values: list[float] = []
        for s in sessions:
            if not hasattr(s, "exercises"):
                continue
            for ex in s.exercises:
                if hasattr(ex, "sets"):
                    for se in ex.sets:
                        rir = getattr(se, "rir", None)
                        if rir is not None:
                            rir_values.append(float(rir))

        if rir_values:
            avg_rir = sum(rir_values) / len(rir_values)
            low_rir_pct = sum(1 for r in rir_values if r < 1) / len(rir_values) * 100
            if low_rir_pct > 50:
                score += 25
                factors.append(f"Low RIR on {low_rir_pct:.0f}% of sets (avg RIR {avg_rir:.1f})")
            elif low_rir_pct > 25:
                score += 10
                factors.append(f"Low RIR on {low_rir_pct:.0f}% of sets (avg RIR {avg_rir:.1f})")

            if avg_rir < 0.5:
                score += 15
                factors.append(f"Very low average RIR: {avg_rir:.1f}")

        # Factor 4: High volume sessions
        high_volume_count = 0
        for s in sessions:
            total_sets = sum(len(getattr(ex, "sets", [])) for ex in getattr(s, "exercises", []))
            if total_sets > 20:
                high_volume_count += 1
                score += 10
        if high_volume_count > 0:
            factors.append(f"{high_volume_count} high-volume session(s) (>20 sets)")

        # Factor 5: Recent volume trend (last 7 days)
        recent_volume = self._provider.get_recent_volume(days=7)
        if recent_volume > 50000:
            score += 15
            factors.append(f"High weekly volume: {recent_volume:.0f}kg")
        elif recent_volume > 30000:
            score += 5
            factors.append(f"Moderate weekly volume: {recent_volume:.0f}kg")

        # Determine fatigue level
        score = min(score, 100)
        if score >= 70:
            level = FatigueLevel.VERY_HIGH
            explanation = "Very high fatigue detected. Consider immediate deload or rest week."
            recommendations = [
                "Take 3-5 days of complete rest",
                "Prioritize 8-9 hours of sleep",
                "Increase protein intake to support recovery",
                "Consider active recovery (light walking, stretching)",
            ]
        elif score >= 45:
            level = FatigueLevel.HIGH
            explanation = "High fatigue levels. Training quality may be compromised."
            recommendations = [
                "Reduce training volume by 20-30%",
                "Add an extra rest day this week",
                "Focus on sleep quality (7-9 hours)",
                "Monitor RIR to avoid overreaching",
            ]
        elif score >= 20:
            level = FatigueLevel.MODERATE
            explanation = "Moderate fatigue. Manageable with proper recovery protocols."
            recommendations = [
                "Ensure adequate sleep (7-9 hours)",
                "Maintain current training volume",
                "Consider active recovery on rest days",
                "Monitor RIR across sets",
            ]
        else:
            level = FatigueLevel.LOW
            explanation = "Fatigue levels are well-managed. Continue current training."
            recommendations = [
                "Continue current training plan",
                "Maintain recovery protocols",
                "Focus on progressive overload",
            ]

        return FatigueResult(
            level=level,
            score=score,
            explanation=explanation,
            factors=factors,
            recommendations=recommendations,
        )
