"""ContextEngine — build runtime context from canonical engine outputs.

No AI. Simple aggregation of existing data into a structured context.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class CognitiveContext:
    """Runtime context describing the current application state."""
    health_summary: str = "unknown"
    recovery_status: str = "unknown"
    readiness_status: str = "unknown"
    fatigue_level: str = "unknown"
    adherence_status: str = "unknown"
    prediction_confidence: str = "unknown"
    system_health_status: str = "unknown"
    active_mesocycle: str = ""
    mission_active: bool = False
    has_critical_alerts: bool = False
    alert_count: int = 0
    pending_decision_count: int = 0
    pr_count: int = 0
    insight_count: int = 0
    context_tags: list[str] = field(default_factory=list)

    def to_tags(self) -> list[str]:
        tags: list[str] = []
        if self.has_critical_alerts:
            tags.append("has-alerts")
        if self.pending_decision_count > 0:
            tags.append("has-decisions")
        if self.pr_count > 0:
            tags.append("has-achievements")
        if self.recovery_status == "critical":
            tags.append("recovery-critical")
        if self.readiness_status == "low":
            tags.append("readiness-low")
        if self.fatigue_level == "high":
            tags.append("fatigue-high")
        if self.mission_active:
            tags.append("mission-active")
        if self.insight_count > 0:
            tags.append("has-insights")
        return tags


class ContextEngine:
    """Builds a CognitiveContext from canonical engine data."""

    @staticmethod
    def build(data: dict[str, Any]) -> CognitiveContext:
        rs = data.get("recovery_score", 0)
        fs = data.get("fatigue_score", 0)
        rl = data.get("readiness_score", 0)
        sr = data.get("sleep_score", 0)
        adh = data.get("weekly_adherence", 0)
        pa = data.get("prediction_accuracy", 0)
        sh = data.get("system_health", 0)
        mc = data.get("mission_confidence", 0)
        flags = data.get("recovery_flags", [])
        prs = data.get("weekly_prs", 0)
        insights = data.get("optimization_insights", [])
        decisions = data.get("pending_decisions", [])
        meso_name = data.get("mesocycle_name", "")

        if rs >= 80:
            rs_status = "optimal"
        elif rs >= 60:
            rs_status = "adequate"
        elif rs >= 40:
            rs_status = "low"
        else:
            rs_status = "critical"

        if rl >= 80:
            rl_status = "high"
        elif rl >= 60:
            rl_status = "moderate"
        else:
            rl_status = "low"

        if fs >= 80:
            fl_status = "high"
        elif fs >= 60:
            fl_status = "elevated"
        else:
            fl_status = "normal"

        if adh >= 80:
            adh_status = "good"
        elif adh >= 50:
            adh_status = "moderate"
        elif adh > 0:
            adh_status = "low"
        else:
            adh_status = "unknown"

        if pa >= 80:
            pc_status = "high"
        elif pa >= 50:
            pc_status = "moderate"
        else:
            pc_status = "low"

        if sh >= 80:
            sh_status = "healthy"
        elif sh >= 50:
            sh_status = "degraded"
        else:
            sh_status = "critical"

        health_scores = [rs, sh, rl]
        avg_health = sum(health_scores) / len(health_scores) if health_scores else 0
        if avg_health >= 80:
            h_summary = "good"
        elif avg_health >= 50:
            h_summary = "fair"
        else:
            h_summary = "poor"

        return CognitiveContext(
            health_summary=h_summary,
            recovery_status=rs_status,
            readiness_status=rl_status,
            fatigue_level=fl_status,
            adherence_status=adh_status,
            prediction_confidence=pc_status,
            system_health_status=sh_status,
            active_mesocycle=meso_name,
            mission_active=(mc > 0),
            has_critical_alerts=len(flags) > 0,
            alert_count=len(flags),
            pending_decision_count=len(decisions),
            pr_count=prs,
            insight_count=len(insights),
            context_tags=[],
        )
