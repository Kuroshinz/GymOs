"""Recovery presentation layer — UI-facing view models and formatters."""

from __future__ import annotations

from dataclasses import dataclass, field

from modules.recovery.domain import ReadinessLevel, RecoveryTrend


@dataclass
class RecoveryViewModel:
    """View model for the Recovery Dashboard."""
    recovery_score: float = 0.0
    readiness_score: float = 0.0
    readiness_level: ReadinessLevel = ReadinessLevel.GOOD
    fatigue_score: float = 0.0
    sleep_score: float = 0.0
    sleep_hours: float = 0.0
    stress_score: float = 0.0
    trend_direction: str = "stable"
    trend_slope: float = 0.0
    seven_day_avg: float = 0.0
    flags: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    has_data: bool = False
    active_deload: bool = False
    deload_end_date: str = ""


class RecoveryFormatter:
    """Formats recovery data for UI display."""

    @staticmethod
    def format_score(score: float) -> str:
        return f"{score:.0f}/100"

    @staticmethod
    def format_readiness_level(level: ReadinessLevel) -> str:
        return level.label

    @staticmethod
    def format_trend(trend: RecoveryTrend) -> str:
        return trend.direction.value.title()

    @staticmethod
    def format_hours(hours: float) -> str:
        return f"{hours:.1f}h"

    @staticmethod
    def get_score_color(score: float) -> str:
        if score >= 80:
            return "#4ADE80"  # Green
        if score >= 60:
            return "#FBBF24"  # Yellow
        if score >= 40:
            return "#FB923C"  # Orange
        return "#EF4444"  # Red

    @staticmethod
    def get_trend_icon(trend: RecoveryTrend) -> str:
        icons = {
            RecoveryTrend.IMPROVING: "▲",
            RecoveryTrend.STABLE: "◆",
            RecoveryTrend.DECLINING: "▼",
            RecoveryTrend.VOLATILE: "◈",
        }
        return icons.get(trend, "◆")

    @staticmethod
    def get_readiness_emoji(level: ReadinessLevel) -> str:
        emojis = {
            ReadinessLevel.READY: "🚀",
            ReadinessLevel.GOOD: "✅",
            ReadinessLevel.CAUTION: "⚠️",
            ReadinessLevel.FATIGUED: "😴",
            ReadinessLevel.DELOAD: "🔄",
        }
        return emojis.get(level, "✅")
