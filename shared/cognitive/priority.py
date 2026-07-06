"""PriorityEngine — compute deterministic priority scores for all recommendations.

No AI. Simple weighted aggregation from existing signals.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class PriorityItem:
    """A single scored recommendation or signal."""
    label: str
    score: float
    category: str = "general"
    source: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class PriorityRanking:
    """Ranked output from PriorityEngine."""
    primary: list[PriorityItem] = field(default_factory=list)
    secondary: list[PriorityItem] = field(default_factory=list)
    deferred: list[PriorityItem] = field(default_factory=list)
    raw_scores: dict[str, float] = field(default_factory=dict)


class PriorityEngine:
    """Deterministic priority scoring for recommendations."""

    @staticmethod
    def rank(data: dict[str, Any]) -> PriorityRanking:
        items: list[PriorityItem] = []

        rs = data.get("recovery_score", 0)
        fs = data.get("fatigue_score", 0)
        rl = data.get("readiness_score", 0)
        pa = data.get("prediction_accuracy", 0)
        adh = data.get("weekly_adherence", 0)
        sr = data.get("sleep_score", 0)
        sh = data.get("system_health", 0)
        mc = data.get("mission_confidence", 0)
        flags = data.get("recovery_flags", [])
        prs = data.get("weekly_prs", 0)
        insights = data.get("optimization_insights", [])
        decisions = data.get("pending_decisions", [])

        if flags:
            for f in flags[:3]:
                items.append(PriorityItem(
                    label=f, score=90.0, category="health", source="recovery_flags",
                ))

        if rs < 40:
            items.append(PriorityItem(
                label=f"Critically low recovery ({rs:.0f})", score=85.0,
                category="health", source="recovery_score",
            ))
        elif rs < 60:
            items.append(PriorityItem(
                label=f"Below-optimal recovery ({rs:.0f})", score=60.0,
                category="health", source="recovery_score",
            ))

        if fs > 80:
            items.append(PriorityItem(
                label=f"High fatigue ({fs:.0f})", score=80.0,
                category="health", source="fatigue_score",
            ))
        elif fs > 60:
            items.append(PriorityItem(
                label=f"Elevated fatigue ({fs:.0f})", score=50.0,
                category="health", source="fatigue_score",
            ))

        if rl < 40:
            items.append(PriorityItem(
                label=f"Low readiness ({rl:.0f})", score=75.0,
                category="readiness", source="readiness_score",
            ))
        elif rl < 60:
            items.append(PriorityItem(
                label=f"Moderate readiness ({rl:.0f})", score=45.0,
                category="readiness", source="readiness_score",
            ))

        if sr < 50:
            items.append(PriorityItem(
                label=f"Poor sleep ({sr:.0f})", score=65.0,
                category="health", source="sleep_score",
            ))

        if prs > 0:
            items.append(PriorityItem(
                label=f"{prs} new PR(s)", score=70.0,
                category="achievement", source="weekly_prs",
            ))

        if adh > 0 and adh < 60:
            items.append(PriorityItem(
                label=f"Low adherence ({adh:.0f}%)", score=55.0,
                category="adherence", source="weekly_adherence",
            ))

        if sh > 0 and sh < 60:
            items.append(PriorityItem(
                label=f"System health ({sh:.0f}%)", score=50.0,
                category="system", source="system_health",
            ))

        if mc > 0 and mc < 40:
            items.append(PriorityItem(
                label=f"Low mission confidence ({mc:.0f}%)", score=40.0,
                category="mission", source="mission_confidence",
            ))

        if pa >= 80:
            items.append(PriorityItem(
                label=f"High-confidence predictions ({pa:.0f}%)", score=35.0,
                category="prediction", source="prediction_accuracy",
            ))

        if insights:
            items.append(PriorityItem(
                label=f"{len(insights)} new insight(s)", score=30.0,
                category="knowledge", source="optimization_insights",
            ))

        if decisions:
            items.append(PriorityItem(
                label=f"{len(decisions)} pending decision(s)", score=45.0,
                category="decision", source="pending_decisions",
            ))

        items.sort(key=lambda x: x.score, reverse=True)

        raw = {it.label: it.score for it in items}
        primary = [i for i in items if i.score >= 70]
        secondary = [i for i in items if 40 <= i.score < 70]
        deferred = [i for i in items if i.score < 40]

        return PriorityRanking(
            primary=primary,
            secondary=secondary,
            deferred=deferred,
            raw_scores=raw,
        )

    @staticmethod
    def narrative_order(data: dict[str, Any]) -> list[str]:
        """Return template names sorted by priority for narrative rendering."""
        ranking = PriorityEngine.rank(data)
        names: list[str] = []
        for item in ranking.primary:
            names.append(item.source)
        for item in ranking.secondary:
            if item.source not in names:
                names.append(item.source)
        for item in ranking.deferred:
            if item.source not in names:
                names.append(item.source)
        return names
