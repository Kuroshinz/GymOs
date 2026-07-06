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


class RecoveryRule(BaseRule):
    """If recovery score is low or declining, recommend recovery-focused interventions."""

    def __init__(self) -> None:
        super().__init__(
            name="recovery_rule",
            description="Recommends recovery interventions when recovery score is low",
            priority=80,
        )

    def evaluate(self, provider: DataProvider, context: dict[str, Any] | None = None) -> RuleResult:
        sessions = provider.get_recent_sessions(days=7)
        total_flags = 0
        critical_flags = 0
        flag_details: list[str] = []

        for s in sessions:
            if not hasattr(s, "exercises"):
                continue
            report = provider.analyse_session(s)
            if report is None:
                continue
            if hasattr(report, "flags"):
                total_flags += len(report.flags)
                for f in report.flags:
                    severity = getattr(f, "severity", "info")
                    if severity == "critical":
                        critical_flags += 1
                    flag_details.append(getattr(f, "message", ""))

        if total_flags == 0:
            return RuleResult()

        if critical_flags >= 2:
            return RuleResult(
                triggered=True,
                recommendation=Recommendation(
                    category=RecommendationCategory.RECOVERY,
                    priority=RecommendationPriority.CRITICAL.value,
                    title="Critical recovery issues detected",
                    description=f"{critical_flags} critical recovery flags found across recent sessions. "
                                f"Take immediate recovery measures: prioritize sleep, reduce training volume, "
                                f"and consider a rest day.",
                    reason=f"{critical_flags} critical recovery flag(s) detected",
                    confidence=0.90,
                    evidence=flag_details,
                    action=RecommendationAction(
                        type="critical_recovery",
                        params={"flags": flag_details},
                        display="Take rest day and prioritize recovery",
                    ),
                ),
                evidence=flag_details,
                confidence=0.90,
            )

        return RuleResult(
            triggered=True,
            recommendation=Recommendation(
                category=RecommendationCategory.RECOVERY,
                priority=RecommendationPriority.MEDIUM.value,
                title="Recovery optimization needed",
                description=f"{total_flags} recovery flag(s) detected. Focus on sleep quality (7-9 hours), "
                            f"adequate protein intake, and active recovery.",
                reason=f"{total_flags} recovery flag(s) detected in recent sessions",
                confidence=0.70,
                evidence=flag_details,
                action=RecommendationAction(
                    type="improve_recovery",
                    params={"flag_count": total_flags},
                    display="Optimize sleep and nutrition for better recovery",
                ),
            ),
            evidence=flag_details,
            confidence=0.70,
        )


class ConsistencyRule(BaseRule):
    """If sessions have been missed or frequency has dropped, recommend consistency."""

    def __init__(self) -> None:
        super().__init__(
            name="consistency_rule",
            description="Recommends improving training consistency when sessions are missed",
            priority=50,
        )

    def evaluate(self, provider: DataProvider, context: dict[str, Any] | None = None) -> RuleResult:
        sessions = provider.get_recent_sessions(days=14)

        program = provider.get_program()
        expected_per_week = 0
        if program and isinstance(program, dict):
            days = program.get("days", [])
            expected_per_week = len(days)

        if expected_per_week == 0:
            return RuleResult()

        week_sessions = [s for s in sessions if hasattr(s, "started_at")]
        from datetime import datetime
        now = datetime.now()

        weeks: dict[int, int] = {}
        for s in week_sessions:
            if s.started_at:
                days_ago = (now - s.started_at).days
                week_num = days_ago // 7
                if week_num < 2:
                    weeks[week_num] = weeks.get(week_num, 0) + 1

        missed: list[str] = []
        for week_num in range(2):
            actual = weeks.get(week_num, 0)
            if actual < expected_per_week:
                diff = expected_per_week - actual
                label = "This week" if week_num == 0 else "Last week"
                missed.append(f"{label}: {actual}/{expected_per_week} sessions completed")

        if not missed:
            return RuleResult()

        this_week_missed = weeks.get(0, 0) < expected_per_week
        priority = RecommendationPriority.HIGH.value if this_week_missed else RecommendationPriority.MEDIUM.value
        title = "Missed training sessions this week" if this_week_missed else "Inconsistent training frequency detected"

        return RuleResult(
            triggered=True,
            recommendation=Recommendation(
                category=RecommendationCategory.CONSISTENCY,
                priority=priority,
                title=title,
                description="You completed fewer sessions than your program prescribes. "
                            "Consistency is the most important factor for hypertrophy.",
                reason="; ".join(missed),
                confidence=0.80,
                evidence=missed,
                action=RecommendationAction(
                    type="improve_consistency",
                    params={"missed": missed, "expected_per_week": expected_per_week},
                    display="Prioritize completing all weekly sessions",
                ),
            ),
            evidence=missed,
            confidence=0.80,
        )
