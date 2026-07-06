"""Canonical input/output models for the Cognitive Layer."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class CognitiveInput:
    """All canonical data consumed by the Cognitive Layer.

    Every field is sourced from existing engine outputs.
    No new data is generated here — only consumed.
    """
    recovery_score: float = 0.0
    recovery_level: str = ""
    recovery_trend: str = "stable"
    sleep_score: float = 0.0
    fatigue_score: float = 0.0
    stress_score: float = 0.0
    recovery_flags: list[str] = field(default_factory=list)

    readiness_score: float = 0.0
    readiness_level: str = ""
    limiting_factor: str = ""
    readiness_recommendations: list[str] = field(default_factory=list)

    prediction_accuracy: float = 0.0
    prediction_trend: str = "stable"
    prediction_count: int = 0
    predictions: list[dict] = field(default_factory=list)

    mesocycle_name: str = ""
    mesocycle_goal: str = ""
    mesocycle_phase: str = ""
    mesocycle_week: int = 0
    mesocycle_total_weeks: int = 0
    mesocycle_focus: str = ""

    weekly_sessions_completed: int = 0
    weekly_sessions_total: int = 0
    weekly_adherence: float = 0.0
    weekly_volume: float = 0.0
    weekly_prs: int = 0

    knowledge_updates: list[dict] = field(default_factory=list)
    optimization_insights: list[dict] = field(default_factory=list)

    adaptation_count: int = 0
    decision_count: int = 0
    pending_decisions: list[dict] = field(default_factory=list)

    kernel_status: str = ""
    system_health: float = 0.0
    capability_count: int = 0
    capability_complete: int = 0

    mission_title: str = ""
    mission_confidence: float = 0.0

    def is_empty(self) -> bool:
        return all(
            getattr(self, f.name) == f.default or getattr(self, f.name) == []
            for f in self.__dataclass_fields__.values()
        )


@dataclass
class CognitiveOutput:
    """Aggregated output from the full Cognitive Layer pipeline."""
    workspace_state: str = "unknown"
    primary_focus: str = ""
    primary_focus_reason: str = ""
    critical_alerts: list[str] = field(default_factory=list)
    secondary_recommendations: list[str] = field(default_factory=list)
    deferred_items: list[str] = field(default_factory=list)
    achievements: list[str] = field(default_factory=list)
    milestones: list[str] = field(default_factory=list)
    upcoming_risks: list[str] = field(default_factory=list)
    attention_items: list[dict] = field(default_factory=list)
    priority_rankings: list[dict] = field(default_factory=list)
    suppressed_notifications: int = 0
