from __future__ import annotations

from typing import Any

from modules.gymbrain.models.recommendations import (
    Recommendation,
    RecommendationAction,
    RecommendationCategory,
    RecommendationPriority,
)
from modules.gymbrain.providers.data_provider import DataProvider
from modules.gymbrain.rules.base import BaseRule, RuleResult


class ProgressionRule(BaseRule):
    """If target reps are reached with adequate RIR, recommend increasing load."""

    def __init__(self) -> None:
        super().__init__(
            name="progression_rule",
            description="Recommends increasing load when progression criteria are met",
            priority=90,
        )

    def evaluate(self, provider: DataProvider, context: dict[str, Any] | None = None) -> RuleResult:
        sessions = provider.get_recent_sessions(days=7)
        if not sessions:
            return RuleResult()

        ready: list[str] = []
        for s in sessions:
            if not hasattr(s, "exercises"):
                continue
            for ex in s.exercises:
                if not hasattr(ex, "name") or not hasattr(ex, "sets"):
                    continue

                ex_data = provider.get_exercise_by_name(ex.name)
                if not ex_data:
                    continue
                rec = provider.get_progression_recommendation(ex.name)
                if rec and hasattr(rec, "should_increase") and rec.should_increase:
                    ready.append(f"{ex.name}: increase from {rec.current_weight}kg to {rec.suggested_weight}kg (reps: {rec.suggested_reps})")

        if not ready:
            return RuleResult()

        return RuleResult(
            triggered=True,
            recommendation=Recommendation(
                category=RecommendationCategory.PROGRESSION,
                priority=RecommendationPriority.CRITICAL.value,
                title="Ready to increase load on key exercises",
                description=f"{len(ready)} exercises are ready for progression: {'; '.join(ready)}",
                reason="All target reps were completed for consecutive sessions with adequate RIR",
                confidence=0.95,
                evidence=ready,
                action=RecommendationAction(
                    type="increase_load",
                    params={"exercises": ready},
                    display="Increase weight on exercises ready for progression",
                ),
            ),
            evidence=ready,
            confidence=0.95,
            reason="Double progression criteria met: all target reps with RIR >= 2",
        )


class DeloadRule(BaseRule):
    """If recovery flags indicate a deload is needed, recommend deload week."""

    def __init__(self) -> None:
        super().__init__(
            name="deload_rule",
            description="Recommends deload when recovery or fatigue indicates overreaching",
            priority=85,
        )

    def evaluate(self, provider: DataProvider, context: dict[str, Any] | None = None) -> RuleResult:
        sessions = provider.get_recent_sessions(days=7)
        recovery_flags: list[str] = []

        for s in sessions:
            if not hasattr(s, "exercises"):
                continue
            report = provider.analyse_session(s)
            if report is None:
                continue
            if hasattr(report, "flags"):
                for flag in report.flags:
                    if hasattr(flag, "severity") and flag.severity in ("warning", "critical"):
                        recovery_flags.append(f"{getattr(flag, 'flag_type', 'unknown')}: {getattr(flag, 'message', '')}")
            if hasattr(report, "should_deload") and report.should_deload:
                return RuleResult(
                    triggered=True,
                    recommendation=Recommendation(
                        category=RecommendationCategory.DELOAD,
                        priority=RecommendationPriority.CRITICAL.value,
                        title="Deload week recommended",
                        description="Your recovery analysis suggests accumulated fatigue warrants a deload week. "
                                    "Reduce volume and intensity by 40-60% for 5-7 days.",
                        reason="Recovery engine detected multiple warning or critical flags indicating overreaching",
                        confidence=0.90,
                        evidence=recovery_flags,
                        action=RecommendationAction(
                            type="deload",
                            params={},
                            display="Schedule a deload week (40-60% reduction in volume and intensity)",
                        ),
                    ),
                    evidence=recovery_flags,
                    confidence=0.90,
                )

        if recovery_flags:
            return RuleResult(
                triggered=True,
                recommendation=Recommendation(
                    category=RecommendationCategory.DELOAD,
                    priority=RecommendationPriority.MEDIUM.value,
                    title="Monitor recovery — deload may be needed soon",
                    description="Recovery flags detected. Consider a deload if symptoms persist.",
                    reason=f"Recovery flags present: {'; '.join(recovery_flags[:3])}",
                    confidence=0.60,
                    evidence=recovery_flags,
                    action=RecommendationAction(
                        type="monitor_recovery",
                        params={"flags": recovery_flags},
                        display="Monitor recovery and consider deload if flags worsen",
                    ),
                ),
                evidence=recovery_flags,
                confidence=0.60,
            )

        return RuleResult()
