"""CognitiveOrchestrator — run the full cognitive pipeline in one call."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from shared.cognitive.attention import AttentionEngine, AttentionItem
from shared.cognitive.context import CognitiveContext, ContextEngine
from shared.cognitive.focus import FocusEngine, FocusRecommendation
from shared.cognitive.models import CognitiveOutput
from shared.cognitive.policy import NotificationDecision, NotificationPolicy
from shared.cognitive.state import WorkspaceState, compute_workspace_state


@dataclass
class CognitiveResult:
    """Full result from the cognitive pipeline."""
    attention: list[AttentionItem]
    context: CognitiveContext
    focus: FocusRecommendation
    workspace: WorkspaceState
    output: CognitiveOutput
    policy_results: list[tuple[AttentionItem, NotificationDecision]]


class CognitiveOrchestrator:
    """Run the full cognitive pipeline from raw data."""

    @staticmethod
    def run(data: dict[str, Any]) -> CognitiveResult:
        attention = AttentionEngine.compute(data)
        context = ContextEngine.build(data)
        focus = FocusEngine.determine(attention, context)
        workspace = compute_workspace_state(context)
        policy_results = NotificationPolicy.filter_all(attention, context.to_tags())

        output = CognitiveOutput(
            workspace_state=workspace.state.value,
            primary_focus=focus.action,
            primary_focus_reason=focus.reason,
            critical_alerts=[i.label for i in attention if i.score >= 80],
            secondary_recommendations=[i.label for i in attention if 50 <= i.score < 80],
            deferred_items=[i.label for i in attention if i.score < 50],
            achievements=[i.label for i in attention if i.signal.value == "pr_achieved"],
            milestones=[],
            upcoming_risks=[
                i.label for i in attention
                if i.signal.value in ("recovery_drop", "fatigue_spike", "readiness_low")
            ],
            attention_items=[
                {"label": i.label, "score": i.score, "signal": i.signal.value}
                for i in attention
            ],
            priority_rankings=[],
            suppressed_notifications=NotificationPolicy.suppressed_count(policy_results),
        )

        return CognitiveResult(
            attention=attention,
            context=context,
            focus=focus,
            workspace=workspace,
            output=output,
            policy_results=policy_results,
        )
