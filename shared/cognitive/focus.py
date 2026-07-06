"""FocusEngine — determine the single primary action for the current session.

Consumes AttentionEngine + ContextEngine outputs to produce one focus.
"""

from __future__ import annotations

from dataclasses import dataclass

from shared.cognitive.attention import AttentionItem
from shared.cognitive.context import CognitiveContext


@dataclass
class FocusRecommendation:
    """The single primary focus for the current session."""
    action: str
    reason: str
    source_signal: str = ""
    narrative_key: str = ""
    severity: str = "info"


_FOCUS_RULES: list[tuple[str, str, str, str]] = [
    ("address critical alerts", "flags require immediate attention", "critical_alert", "risk_alerts"),
    ("prioritise recovery", "recovery critically low", "recovery_drop", "recovery_summary"),
    ("reduce training load", "fatigue very high", "fatigue_spike", "recovery_summary"),
    ("focus on recovery and mobility", "readiness is low", "readiness_low", "morning_brief"),
    ("improve sleep quality", "sleep score is poor", "recovery_drop", "recovery_summary"),
    ("improve workout adherence", "adherence rate is low", "adherence_drop", "planning_summary"),
    ("review pending decisions", "decisions waiting for input", "decision_pending", "decision_feed"),
    ("check system health", "system health is degraded", "system_health", "risk_alerts"),
    ("review latest insights", "new knowledge available", "knowledge_update", "knowledge_summary"),
    ("train as planned", "all signals nominal, readiness adequate", "readiness_low", "today_focus"),
]


class FocusEngine:
    """Determines the single primary action for the current session."""

    @staticmethod
    def determine(
        attention_items: list[AttentionItem],
        context: CognitiveContext,
    ) -> FocusRecommendation:
        if not attention_items:
            return FocusRecommendation(
                action="continue monitoring",
                reason="no signals detected, maintaining baseline",
                narrative_key="today_focus",
                severity="info",
            )

        top = attention_items[0]
        for action, reason, signal, narrative_key in _FOCUS_RULES:
            if top.signal.value == signal:
                sev = "critical" if top.score >= 80 else ("warning" if top.score >= 50 else "info")
                return FocusRecommendation(
                    action=action,
                    reason=reason,
                    source_signal=top.signal.value,
                    narrative_key=narrative_key,
                    severity=sev,
                )

        return FocusRecommendation(
            action="continue with planned training",
            reason="no overriding signals detected",
            narrative_key="today_focus",
            severity="info",
        )

    @staticmethod
    def narrative_key_for_focus(focus: FocusRecommendation) -> str:
        return focus.narrative_key or "today_focus"
