"""Adaptive Programming Events — Domain events for the adaptive programming pipeline."""

from __future__ import annotations

from dataclasses import dataclass

from shared.events.event import DomainEvent


@dataclass
class ContextUpdated(DomainEvent):
    source: str = "adaptive_programming"
    context_id: str = ""
    recovery_score: float = 0.0
    compliance_rate: float = 0.0
    progress_percentage: float = 0.0


@dataclass
class RecommendationGenerated(DomainEvent):
    source: str = "adaptive_programming"
    recommendation_id: str = ""
    adaptation_type: str = ""
    suggested_value: float = 0.0
    priority: str = ""


@dataclass
class DecisionApproved(DomainEvent):
    source: str = "adaptive_programming"
    decision_id: str = ""
    adaptation_type: str = ""
    previous_value: float = 0.0
    new_value: float = 0.0


@dataclass
class DecisionRejected(DomainEvent):
    source: str = "adaptive_programming"
    decision_id: str = ""
    adaptation_type: str = ""
    reason: str = ""


@dataclass
class DecisionRolledBack(DomainEvent):
    source: str = "adaptive_programming"
    decision_id: str = ""
    adaptation_type: str = ""
    rollback_reason: str = ""


@dataclass
class AdaptationApplied(DomainEvent):
    source: str = "adaptive_programming"
    history_id: str = ""
    decision_id: str = ""
    adaptation_type: str = ""
    new_value: float = 0.0


@dataclass
class StrategyPhaseChanged(DomainEvent):
    source: str = "adaptive_programming"
    strategy_id: str = ""
    previous_phase: str = ""
    new_phase: str = ""
    reason: str = ""


@dataclass
class ScenarioSimulated(DomainEvent):
    source: str = "adaptive_programming"
    scenario_id: str = ""
    adaptation_type: str = ""
    score: float = 0.0
    is_safe: bool = False


ADAPTIVE_PROGRAMMING_EVENT_REGISTRY: dict[str, type[DomainEvent]] = {
    "ContextUpdated": ContextUpdated,
    "RecommendationGenerated": RecommendationGenerated,
    "DecisionApproved": DecisionApproved,
    "DecisionRejected": DecisionRejected,
    "DecisionRolledBack": DecisionRolledBack,
    "AdaptationApplied": AdaptationApplied,
    "StrategyPhaseChanged": StrategyPhaseChanged,
    "ScenarioSimulated": ScenarioSimulated,
}
