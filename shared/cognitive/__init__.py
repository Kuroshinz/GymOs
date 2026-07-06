"""Cognitive Layer — Attention, Priority, Context, Focus, Notifications, WorkspaceState.

Deterministic platform above all existing engines.
No AI, no LLM, no probabilistic generation.
"""

from shared.cognitive.attention import AttentionEngine, AttentionItem, AttentionSignal
from shared.cognitive.context import CognitiveContext, ContextEngine
from shared.cognitive.focus import FocusEngine, FocusRecommendation
from shared.cognitive.models import CognitiveInput, CognitiveOutput
from shared.cognitive.orchestrator import CognitiveOrchestrator, CognitiveResult
from shared.cognitive.policy import NotificationDecision, NotificationPolicy
from shared.cognitive.priority import PriorityEngine, PriorityItem, PriorityRanking
from shared.cognitive.state import WorkspaceState, WorkspaceStateEnum, compute_workspace_state

__all__ = [
    "AttentionEngine",
    "AttentionItem",
    "AttentionSignal",
    "PriorityEngine",
    "PriorityRanking",
    "PriorityItem",
    "ContextEngine",
    "CognitiveContext",
    "FocusEngine",
    "FocusRecommendation",
    "NotificationPolicy",
    "NotificationDecision",
    "WorkspaceState",
    "WorkspaceStateEnum",
    "compute_workspace_state",
    "CognitiveInput",
    "CognitiveOutput",
    "CognitiveOrchestrator",
    "CognitiveResult",
]
