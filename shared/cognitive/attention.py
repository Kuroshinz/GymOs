"""AttentionEngine — rank signals by urgency, confidence, impact, and context.

Deterministic weighted scoring. No AI. No probabilistic generation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class AttentionSignal(Enum):
    CRITICAL_ALERT = "critical_alert"
    RECOVERY_DROP = "recovery_drop"
    FATIGUE_SPIKE = "fatigue_spike"
    READINESS_LOW = "readiness_low"
    PR_ACHIEVED = "pr_achieved"
    PREDICTION_CONFIDENCE = "prediction_confidence"
    MILESTONE_REACHED = "milestone_reached"
    ADHERENCE_DROP = "adherence_drop"
    ADAPTATION_APPLIED = "adaptation_applied"
    DECISION_PENDING = "decision_pending"
    KNOWLEDGE_UPDATE = "knowledge_update"
    SYSTEM_HEALTH = "system_health"
    MISSION_CONFIDENCE = "mission_confidence"


@dataclass
class AttentionItem:
    """A single ranked item from the AttentionEngine."""
    signal: AttentionSignal
    label: str
    score: float
    urgency: float
    confidence: float
    impact: float
    source_key: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


class AttentionEngine:
    """Ranks signals by composite score = urgency*0.4 + confidence*0.3 + impact*0.3."""

    @staticmethod
    def compute(data: dict[str, Any]) -> list[AttentionItem]:
        items: list[AttentionItem] = []
        add = items.append

        rs = data.get("recovery_score", 0)
        fs = data.get("fatigue_score", 0)
        rl = data.get("readiness_score", 0)
        pa = data.get("prediction_accuracy", 0)
        sr = data.get("sleep_score", 0)
        adh = data.get("weekly_adherence", 0)
        prs = data.get("weekly_prs", 0)
        flags = data.get("recovery_flags", [])
        sh = data.get("system_health", 0)
        mc = data.get("mission_confidence", 0)
        dc = data.get("decision_count", 0)

        if flags:
            add(AttentionItem(
                signal=AttentionSignal.CRITICAL_ALERT,
                label=f"Flags: {', '.join(flags[:3])}",
                score=100.0, urgency=1.0, confidence=1.0, impact=1.0,
                source_key="recovery_flags",
            ))

        if rs < 40:
            add(AttentionItem(
                signal=AttentionSignal.RECOVERY_DROP,
                label=f"Recovery critically low: {rs:.0f}",
                score=85.0, urgency=0.9, confidence=0.9, impact=0.8,
                source_key="recovery_score",
            ))

        if fs > 80:
            add(AttentionItem(
                signal=AttentionSignal.FATIGUE_SPIKE,
                label=f"Fatigue very high: {fs:.0f}",
                score=80.0, urgency=0.8, confidence=0.85, impact=0.8,
                source_key="fatigue_score",
            ))

        if rl < 40:
            add(AttentionItem(
                signal=AttentionSignal.READINESS_LOW,
                label=f"Low readiness: {rl:.0f}",
                score=75.0, urgency=0.8, confidence=0.8, impact=0.7,
                source_key="readiness_score",
            ))

        if sr < 50:
            add(AttentionItem(
                signal=AttentionSignal.RECOVERY_DROP,
                label=f"Poor sleep score: {sr:.0f}",
                score=65.0, urgency=0.6, confidence=0.7, impact=0.6,
                source_key="sleep_score",
            ))

        if prs > 0:
            add(AttentionItem(
                signal=AttentionSignal.PR_ACHIEVED,
                label=f"{prs} new PR(s) this week",
                score=70.0, urgency=0.3, confidence=1.0, impact=0.7,
                source_key="weekly_prs",
            ))

        if pa >= 80:
            add(AttentionItem(
                signal=AttentionSignal.PREDICTION_CONFIDENCE,
                label=f"High prediction accuracy: {pa:.0f}%",
                score=55.0, urgency=0.3, confidence=0.9, impact=0.5,
                source_key="prediction_accuracy",
            ))

        if adh > 0 and adh < 50:
            add(AttentionItem(
                signal=AttentionSignal.ADHERENCE_DROP,
                label=f"Low adherence: {adh:.0f}%",
                score=60.0, urgency=0.5, confidence=0.8, impact=0.5,
                source_key="weekly_adherence",
            ))

        if sh > 0 and sh < 50:
            add(AttentionItem(
                signal=AttentionSignal.SYSTEM_HEALTH,
                label=f"System health: {sh:.0f}%",
                score=50.0, urgency=0.4, confidence=0.9, impact=0.6,
                source_key="system_health",
            ))

        if mc > 0 and mc < 30:
            add(AttentionItem(
                signal=AttentionSignal.MISSION_CONFIDENCE,
                label=f"Mission confidence low: {mc:.0f}%",
                score=45.0, urgency=0.3, confidence=0.7, impact=0.4,
                source_key="mission_confidence",
            ))

        if dc > 0:
            add(AttentionItem(
                signal=AttentionSignal.DECISION_PENDING,
                label=f"{dc} pending decision(s)",
                score=40.0, urgency=0.4, confidence=0.8, impact=0.3,
                source_key="decision_count",
            ))

        for item in items:
            item.score = round(item.urgency * 40 + item.confidence * 30 + item.impact * 30, 1)

        items.sort(key=lambda x: x.score, reverse=True)
        return items

    @staticmethod
    def critical_alerts(items: list[AttentionItem]) -> list[AttentionItem]:
        return [i for i in items if i.score >= 80]

    @staticmethod
    def top_n(items: list[AttentionItem], n: int = 5) -> list[AttentionItem]:
        return items[:n]
