"""WorkspaceState — describe the current cognitive state of the application.

Deterministic state machine based on canonical engine outputs.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from shared.cognitive.context import CognitiveContext


class WorkspaceStateEnum(Enum):
    NOMINAL = "nominal"
    RECOVERY_FOCUSED = "recovery_focused"
    HIGH_FATIGUE = "high_fatigue"
    LOW_READINESS = "low_readiness"
    ALERT = "alert"
    ACHIEVEMENT = "achievement"
    DECISION_PENDING = "decision_pending"
    SYSTEM_DEGRADED = "system_degraded"
    OFF_SEASON = "off_season"


@dataclass
class WorkspaceState:
    """Current cognitive state of the application."""
    state: WorkspaceStateEnum
    label: str
    description: str = ""
    transitions_to: list[WorkspaceStateEnum] | None = None


_STATES: dict[WorkspaceStateEnum, WorkspaceState] = {
    WorkspaceStateEnum.NOMINAL: WorkspaceState(
        state=WorkspaceStateEnum.NOMINAL,
        label="Nominal",
        description="All systems normal. Continue as planned.",
    ),
    WorkspaceStateEnum.RECOVERY_FOCUSED: WorkspaceState(
        state=WorkspaceStateEnum.RECOVERY_FOCUSED,
        label="Recovery Focused",
        description="Recovery is below optimal. Prioritise rest and recovery.",
    ),
    WorkspaceStateEnum.HIGH_FATIGUE: WorkspaceState(
        state=WorkspaceStateEnum.HIGH_FATIGUE,
        label="High Fatigue",
        description="Fatigue is elevated. Consider deload or reduced volume.",
    ),
    WorkspaceStateEnum.LOW_READINESS: WorkspaceState(
        state=WorkspaceStateEnum.LOW_READINESS,
        label="Low Readiness",
        description="Readiness is low. Focus on mobility and light activity.",
    ),
    WorkspaceStateEnum.ALERT: WorkspaceState(
        state=WorkspaceStateEnum.ALERT,
        label="Alert",
        description="Critical signals detected. Attention required.",
    ),
    WorkspaceStateEnum.ACHIEVEMENT: WorkspaceState(
        state=WorkspaceStateEnum.ACHIEVEMENT,
        label="Achievement",
        description="New achievements or PRs to celebrate.",
    ),
    WorkspaceStateEnum.DECISION_PENDING: WorkspaceState(
        state=WorkspaceStateEnum.DECISION_PENDING,
        label="Decision Pending",
        description="Decisions require your input.",
    ),
    WorkspaceStateEnum.SYSTEM_DEGRADED: WorkspaceState(
        state=WorkspaceStateEnum.SYSTEM_DEGRADED,
        label="System Degraded",
        description="System health is below acceptable levels.",
    ),
    WorkspaceStateEnum.OFF_SEASON: WorkspaceState(
        state=WorkspaceStateEnum.OFF_SEASON,
        label="Off Season",
        description="No active mesocycle. Consider setting a new goal.",
    ),
}


def compute_workspace_state(context: CognitiveContext) -> WorkspaceState:
    """Determine the workspace state from cognitive context."""
    if context.has_critical_alerts:
        return _STATES[WorkspaceStateEnum.ALERT]

    if context.system_health_status in ("critical", "degraded"):
        return _STATES[WorkspaceStateEnum.SYSTEM_DEGRADED]

    if context.recovery_status == "critical":
        return _STATES[WorkspaceStateEnum.RECOVERY_FOCUSED]

    if context.fatigue_level == "high":
        return _STATES[WorkspaceStateEnum.HIGH_FATIGUE]

    if context.readiness_status == "low":
        return _STATES[WorkspaceStateEnum.LOW_READINESS]

    if context.pr_count > 0:
        return _STATES[WorkspaceStateEnum.ACHIEVEMENT]

    if context.pending_decision_count > 0:
        return _STATES[WorkspaceStateEnum.DECISION_PENDING]

    if not context.active_mesocycle:
        return _STATES[WorkspaceStateEnum.OFF_SEASON]

    return _STATES[WorkspaceStateEnum.NOMINAL]


def compute_output(context: CognitiveContext, data: dict[str, any]) -> dict:
    """Build the full CognitiveOutput dict from context and raw data."""
    from shared.cognitive.attention import AttentionEngine

    attention = AttentionEngine.compute(data)
    ws = compute_workspace_state(context)

    return {
        "workspace_state": ws.state.value,
        "primary_focus": ws.label,
        "primary_focus_reason": ws.description,
        "critical_alerts": [i.label for i in attention if i.score >= 80],
        "secondary_recommendations": [i.label for i in attention if 50 <= i.score < 80],
        "deferred_items": [i.label for i in attention if i.score < 50],
        "achievements": [i.label for i in attention if i.signal.value == "pr_achieved"],
        "upcoming_risks": [i.label for i in attention if i.signal.value in ("recovery_drop", "fatigue_spike", "readiness_low")],
        "attention_items": [{"label": i.label, "score": i.score, "signal": i.signal.value} for i in attention],
    }
