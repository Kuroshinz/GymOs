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


class FatigueRule(BaseRule):
    """If fatigue level is HIGH or VERY_HIGH, recommend recovery-focused actions."""

    def __init__(self) -> None:
        super().__init__(
            name="fatigue_rule",
            description="Recommends recovery actions when fatigue is elevated",
            priority=95,
        )

    def evaluate(self, provider: DataProvider, context: dict[str, Any] | None = None) -> RuleResult:
        from modules.gymbrain.analysis.fatigue import FatigueAnalyzer

        analyzer = FatigueAnalyzer(provider)
        result = analyzer.analyze()

        if result.level.value in ("high", "very_high"):
            return RuleResult(
                triggered=True,
                recommendation=Recommendation(
                    category=RecommendationCategory.RECOVERY,
                    priority=RecommendationPriority.CRITICAL.value,
                    title=f"Fatigue level is {result.level.value.upper()} — prioritize recovery",
                    description=result.explanation,
                    reason="Fatigue analysis indicates elevated systemic fatigue",
                    confidence=0.90,
                    evidence=result.factors,
                    action=RecommendationAction(
                        type="reduce_fatigue",
                        params={"level": result.level.value, "recommendations": result.recommendations},
                        display="Prioritize sleep, nutrition, and reduce training volume",
                    ),
                ),
                evidence=result.factors,
                confidence=0.90,
                reason=result.explanation,
            )

        return RuleResult()


class TechniqueRule(BaseRule):
    """If fatigue or recovery flags indicate technique degradation, recommend technique review."""

    def __init__(self) -> None:
        super().__init__(
            name="technique_rule",
            description="Recommends technique review when fatigue affects form",
            priority=50,
        )

    def evaluate(self, provider: DataProvider, context: dict[str, Any] | None = None) -> RuleResult:
        sessions = provider.get_recent_sessions(days=14)
        technique_flags: list[str] = []

        for s in sessions:
            if not hasattr(s, "exercises"):
                continue
            report = provider.analyse_session(s)
            if report and hasattr(report, "flags"):
                for flag in report.flags:
                    if hasattr(flag, "flag_type") and flag.flag_type == "rep_drop":
                        technique_flags.append(
                            f"{getattr(flag, 'exercise_name', 'unknown')}: {getattr(flag, 'message', 'rep drop detected')}"
                        )

        if not technique_flags:
            return RuleResult()

        return RuleResult(
            triggered=True,
            recommendation=Recommendation(
                category=RecommendationCategory.TECHNIQUE,
                priority=RecommendationPriority.MEDIUM.value,
                title="Technique review recommended",
                description="Rep drop detected across sets, which may indicate technique degradation due to fatigue. "
                            "Review exercise form, consider reducing weight, or adding rest time.",
                reason=f"Rep drop detected on {len(technique_flags)} exercise(s)",
                confidence=0.65,
                evidence=technique_flags,
                action=RecommendationAction(
                    type="technique_review",
                    params={"exercises": technique_flags},
                    display="Review technique on flagged exercises",
                ),
            ),
            evidence=technique_flags,
            confidence=0.65,
        )


class RestRule(BaseRule):
    """If RIR is consistently 0 across sessions, recommend increased rest times."""

    def __init__(self) -> None:
        super().__init__(
            name="rest_rule",
            description="Recommends increasing rest between sets when RIR is consistently 0",
            priority=60,
        )

    def evaluate(self, provider: DataProvider, context: dict[str, Any] | None = None) -> RuleResult:
        sessions = provider.get_recent_sessions(days=7)
        rir_zero_exercises: list[str] = []

        for s in sessions:
            if not hasattr(s, "exercises"):
                continue
            for ex in s.exercises:
                if not hasattr(ex, "name") or not hasattr(ex, "sets"):
                    continue
                rir_values = [getattr(se, "rir", 2) for se in ex.sets if hasattr(se, "rir")]
                if not rir_values:
                    continue
                avg_rir = sum(rir_values) / len(rir_values)
                if avg_rir < 0.5 and len(rir_values) >= 3:
                    rir_zero_exercises.append(
                        f"{ex.name}: avg RIR {avg_rir:.1f} across {len(rir_values)} sets"
                    )

        if not rir_zero_exercises:
            return RuleResult()

        return RuleResult(
            triggered=True,
            recommendation=Recommendation(
                category=RecommendationCategory.RECOVERY,
                priority=RecommendationPriority.HIGH.value,
                title="Increase rest between sets",
                description=f"Average RIR is near zero on {len(rir_zero_exercises)} exercise(s). "
                            f"Increase rest intervals by 30-60 seconds to maintain performance.",
                reason="Consistently low RIR indicates insufficient recovery between sets",
                confidence=0.75,
                evidence=rir_zero_exercises,
                action=RecommendationAction(
                    type="increase_rest",
                    params={"exercises": rir_zero_exercises},
                    display="Add 30-60s rest between sets on flagged exercises",
                ),
            ),
            evidence=rir_zero_exercises,
            confidence=0.75,
        )
