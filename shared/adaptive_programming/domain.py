"""Adaptive Programming Domain — Long-term training strategy adaptation models.

All models are frozen dataclasses. Enums have @property label methods.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

# ── Label Constants ─────────────────────────────────────────────────────

ADAPTATION_TYPE_LABELS: dict[str, str] = {
    "volume": "Volume",
    "frequency": "Frequency",
    "exercise_substitution": "Exercise Substitution",
    "mesocycle_adjustment": "Mesocycle Adjustment",
    "progression_adjustment": "Progression Adjustment",
    "deload_timing": "Deload Timing",
    "nutrition_target": "Nutrition Target",
    "goal_reprioritization": "Goal Reprioritization",
}

DECISION_STATUS_LABELS: dict[str, str] = {
    "pending": "Pending",
    "approved": "Approved",
    "rejected": "Rejected",
    "rolled_back": "Rolled Back",
    "completed": "Completed",
}

STRATEGY_PHASE_LABELS: dict[str, str] = {
    "initiation": "Initiation",
    "development": "Development",
    "peak": "Peak",
    "deload": "Deload",
    "transition": "Transition",
    "maintenance": "Maintenance",
}

RECOMMENDATION_PRIORITY_LABELS: dict[str, str] = {
    "critical": "Critical",
    "high": "High",
    "medium": "Medium",
    "low": "Low",
}

MONITOR_SOURCE_LABELS: dict[str, str] = {
    "intent": "Intent",
    "recovery": "Recovery",
    "prediction": "Prediction",
    "optimization_knowledge": "Optimization Knowledge",
    "knowledge_evolution": "Knowledge Evolution",
    "progress": "Progress",
    "compliance": "Compliance",
}


# ── Enums ──────────────────────────────────────────────────────────────


class AdaptationType(Enum):
    VOLUME = "volume"
    FREQUENCY = "frequency"
    EXERCISE_SUBSTITUTION = "exercise_substitution"
    MESOCYCLE_ADJUSTMENT = "mesocycle_adjustment"
    PROGRESSION_ADJUSTMENT = "progression_adjustment"
    DELOAD_TIMING = "deload_timing"
    NUTRITION_TARGET = "nutrition_target"
    GOAL_REPRIORITIZATION = "goal_reprioritization"

    @property
    def label(self) -> str:
        return ADAPTATION_TYPE_LABELS[self.value]


class DecisionStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ROLLED_BACK = "rolled_back"
    COMPLETED = "completed"

    @property
    def label(self) -> str:
        return DECISION_STATUS_LABELS[self.value]


class StrategyPhase(Enum):
    INITIATION = "initiation"
    DEVELOPMENT = "development"
    PEAK = "peak"
    DELOAD = "deload"
    TRANSITION = "transition"
    MAINTENANCE = "maintenance"

    @property
    def label(self) -> str:
        return STRATEGY_PHASE_LABELS[self.value]


class RecommendationPriority(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

    @property
    def label(self) -> str:
        return RECOMMENDATION_PRIORITY_LABELS[self.value]


class MonitorSource(Enum):
    INTENT = "intent"
    RECOVERY = "recovery"
    PREDICTION = "prediction"
    OPTIMIZATION_KNOWLEDGE = "optimization_knowledge"
    KNOWLEDGE_EVOLUTION = "knowledge_evolution"
    PROGRESS = "progress"
    COMPLIANCE = "compliance"

    @property
    def label(self) -> str:
        return MONITOR_SOURCE_LABELS[self.value]


# ── Domain Models ──────────────────────────────────────────────────────


@dataclass(frozen=True)
class AdaptiveContext:
    """Current state of all monitored inputs for adaptation decisions."""
    context_id: str = ""
    intent_goal: str = ""
    recovery_score: float = 0.0
    prediction_progress: float = 0.0
    knowledge_confidence: float = 0.0
    optimization_insight_score: float = 0.0
    progress_percentage: float = 0.0
    compliance_rate: float = 0.0
    current_phase: StrategyPhase = StrategyPhase.INITIATION
    weeks_into_phase: int = 0
    fatigue_level: float = 0.0
    timestamp: str = ""


@dataclass(frozen=True)
class AdaptationReason:
    """Explainable reason for an adaptation decision."""
    reason_id: str = ""
    adaptation_type: AdaptationType = AdaptationType.VOLUME
    trigger_source: MonitorSource = MonitorSource.PROGRESS
    trigger_value: float = 0.0
    threshold_value: float = 0.0
    description: str = ""
    evidence: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class AdaptiveDecision:
    """A single adaptation decision with its lifecycle."""
    decision_id: str = ""
    adaptation_type: AdaptationType = AdaptationType.VOLUME
    previous_value: float = 0.0
    new_value: float = 0.0
    reason: AdaptationReason = field(default_factory=AdaptationReason)
    status: DecisionStatus = DecisionStatus.PENDING
    score: float = 0.0
    simulation_result: str = ""
    applied_at: str = ""
    rolled_back_at: str = ""
    rollback_reason: str = ""


@dataclass(frozen=True)
class AdaptiveRecommendation:
    """A recommended adaptation before decision approval."""
    recommendation_id: str = ""
    adaptation_type: AdaptationType = AdaptationType.VOLUME
    suggested_value: float = 0.0
    current_value: float = 0.0
    priority: RecommendationPriority = RecommendationPriority.MEDIUM
    confidence: float = 0.0
    expected_improvement: float = 0.0
    reason: str = ""
    supporting_evidence: list[str] = field(default_factory=list)
    created_at: str = ""


@dataclass(frozen=True)
class AdaptationHistory:
    """Record of a single adaptation event."""
    history_id: str = ""
    decision_id: str = ""
    adaptation_type: AdaptationType = AdaptationType.VOLUME
    previous_value: float = 0.0
    new_value: float = 0.0
    reason: str = ""
    status: DecisionStatus = DecisionStatus.COMPLETED
    outcome_score: float = 0.0
    adapted_at: str = ""


@dataclass(frozen=True)
class AdaptationSnapshot:
    """Point-in-time snapshot of all active adaptations."""
    snapshot_id: str = ""
    version: str = ""
    decisions: list[AdaptiveDecision] = field(default_factory=list)
    recommendations: list[AdaptiveRecommendation] = field(default_factory=list)
    context: AdaptiveContext = field(default_factory=AdaptiveContext)
    created_at: str = ""


@dataclass(frozen=True)
class AdaptiveStrategy:
    """Current long-term training strategy with active adaptations."""
    strategy_id: str = ""
    user_id: str = ""
    phase: StrategyPhase = StrategyPhase.INITIATION
    base_volume: float = 0.0
    base_frequency: int = 0
    current_volume: float = 0.0
    current_frequency: int = 0
    goal: str = ""
    active_decisions: list[AdaptiveDecision] = field(default_factory=list)
    weeks_into_phase: int = 0
    created_at: str = ""
    updated_at: str = ""

    @property
    def volume_delta(self) -> float:
        return self.current_volume - self.base_volume

    @property
    def frequency_delta(self) -> int:
        return self.current_frequency - self.base_frequency


@dataclass(frozen=True)
class AdaptivePlan:
    """Complete adaptive plan for a user."""
    plan_id: str = ""
    user_id: str = ""
    strategy: AdaptiveStrategy = field(default_factory=AdaptiveStrategy)
    decisions: list[AdaptiveDecision] = field(default_factory=list)
    history: list[AdaptationHistory] = field(default_factory=list)
    snapshots: list[AdaptationSnapshot] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""

    @property
    def decision_count(self) -> int:
        return len(self.decisions)

    @property
    def active_decision_count(self) -> int:
        return sum(1 for d in self.decisions if d.status == DecisionStatus.APPROVED)

    @property
    def rollback_count(self) -> int:
        return sum(1 for d in self.decisions if d.status == DecisionStatus.ROLLED_BACK)


@dataclass(frozen=True)
class AdaptationScenario:
    """A simulated adaptation scenario for evaluation."""
    scenario_id: str = ""
    adaptation_type: AdaptationType = AdaptationType.VOLUME
    proposed_value: float = 0.0
    current_value: float = 0.0
    context: AdaptiveContext = field(default_factory=AdaptiveContext)
    score: float = 0.0
    is_safe: bool = False
    risk_factors: list[str] = field(default_factory=list)
    simulated_at: str = ""


@dataclass(frozen=True)
class AdaptiveMetrics:
    """Metrics for adaptive programming quality."""
    metrics_id: str = ""
    total_adaptations: int = 0
    approved_adaptations: int = 0
    rejected_adaptations: int = 0
    rolled_back_adaptations: int = 0
    adaptation_frequency: float = 0.0
    adaptation_quality: float = 0.0
    success_rate: float = 0.0
    rollback_rate: float = 0.0
    strategy_stability: float = 0.0
    timestamp: str = ""


@dataclass(frozen=True)
class AdaptiveConfig:
    enable_auto_adaptation: bool = True
    min_recovery_for_volume_increase: float = 0.6
    max_volume_change_per_week: float = 0.2
    max_frequency_change_per_week: int = 1
    min_compliance_for_adaptation: float = 0.7
    adaptation_cooldown_days: int = 14
    max_concurrent_adaptations: int = 3
    simulation_samples: int = 10
    safety_threshold: float = 0.3
    enable_rollback: bool = True
