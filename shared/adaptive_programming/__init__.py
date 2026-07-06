"""Adaptive Programming — Orchestrator and public API surface for the adaptation pipeline."""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime
from typing import Any
from uuid import uuid4

from shared.adaptive_programming.decision_policy import AdaptiveDecisionPolicy
from shared.adaptive_programming.domain import (
    ADAPTATION_TYPE_LABELS,
    DECISION_STATUS_LABELS,
    MONITOR_SOURCE_LABELS,
    RECOMMENDATION_PRIORITY_LABELS,
    STRATEGY_PHASE_LABELS,
    AdaptationHistory,
    AdaptationReason,
    AdaptationScenario,
    AdaptationSnapshot,
    AdaptationType,
    AdaptiveConfig,
    AdaptiveContext,
    AdaptiveDecision,
    AdaptiveMetrics,
    AdaptivePlan,
    AdaptiveRecommendation,
    AdaptiveStrategy,
    DecisionStatus,
    MonitorSource,
    RecommendationPriority,
    StrategyPhase,
)
from shared.adaptive_programming.events import (
    ADAPTIVE_PROGRAMMING_EVENT_REGISTRY,
    AdaptationApplied,
    ContextUpdated,
    DecisionApproved,
    DecisionRejected,
    DecisionRolledBack,
    RecommendationGenerated,
    ScenarioSimulated,
    StrategyPhaseChanged,
)
from shared.adaptive_programming.history import AdaptationHistoryTracker
from shared.adaptive_programming.metrics import AdaptiveMetricsCalculator
from shared.adaptive_programming.monitor_engine import AdaptiveMonitorEngine
from shared.adaptive_programming.reports import AdaptiveReportGenerator
from shared.adaptive_programming.repository import AdaptiveProgrammingRepository
from shared.adaptive_programming.serializer import (
    AdaptationHistorySerializer,
    AdaptationReasonSerializer,
    AdaptationScenarioSerializer,
    AdaptationSnapshotSerializer,
    AdaptiveConfigSerializer,
    AdaptiveContextSerializer,
    AdaptiveDecisionSerializer,
    AdaptiveMetricsSerializer,
    AdaptivePlanSerializer,
    AdaptiveRecommendationSerializer,
    AdaptiveStrategySerializer,
)
from shared.adaptive_programming.simulation import AdaptationSimulationEngine
from shared.adaptive_programming.strategy_engine import AdaptationStrategyEngine
from shared.events.event_bus import get_event_bus

__all__ = [
    # ── Label dicts ──────────────────────────────────────────────────
    "ADAPTATION_TYPE_LABELS",
    "DECISION_STATUS_LABELS",
    "STRATEGY_PHASE_LABELS",
    "RECOMMENDATION_PRIORITY_LABELS",
    "MONITOR_SOURCE_LABELS",
    # ── Enums ────────────────────────────────────────────────────────
    "AdaptationType",
    "DecisionStatus",
    "StrategyPhase",
    "RecommendationPriority",
    "MonitorSource",
    # ── Domain models ────────────────────────────────────────────────
    "AdaptiveContext",
    "AdaptationReason",
    "AdaptiveDecision",
    "AdaptiveRecommendation",
    "AdaptationHistory",
    "AdaptationSnapshot",
    "AdaptiveStrategy",
    "AdaptivePlan",
    "AdaptationScenario",
    "AdaptiveMetrics",
    "AdaptiveConfig",
    # ── Engine classes ───────────────────────────────────────────────
    "AdaptiveMonitorEngine",
    "AdaptationStrategyEngine",
    "AdaptiveDecisionPolicy",
    "AdaptationSimulationEngine",
    "AdaptiveProgrammingRepository",
    "AdaptiveMetricsCalculator",
    "AdaptiveReportGenerator",
    "AdaptationHistoryTracker",
    # ── Events ───────────────────────────────────────────────────────
    "ContextUpdated",
    "RecommendationGenerated",
    "DecisionApproved",
    "DecisionRejected",
    "DecisionRolledBack",
    "AdaptationApplied",
    "StrategyPhaseChanged",
    "ScenarioSimulated",
    "ADAPTIVE_PROGRAMMING_EVENT_REGISTRY",
    # ── Serializers ──────────────────────────────────────────────────
    "AdaptiveContextSerializer",
    "AdaptationReasonSerializer",
    "AdaptiveDecisionSerializer",
    "AdaptiveRecommendationSerializer",
    "AdaptationHistorySerializer",
    "AdaptationSnapshotSerializer",
    "AdaptiveStrategySerializer",
    "AdaptivePlanSerializer",
    "AdaptationScenarioSerializer",
    "AdaptiveMetricsSerializer",
    "AdaptiveConfigSerializer",
    # ── Orchestrator ─────────────────────────────────────────────────
    "AdaptiveProgrammingOrchestrator",
]


def _generate_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


class AdaptiveProgrammingOrchestrator:
    """Top-level orchestrator that coordinates all adaptive programming sub-engines.

    Wraps the monitor, strategy engine, decision policy, simulation engine,
    repository, metrics calculator, report generator, and history tracker into
    a single convenience interface.  Emits domain events through the shared
    event bus for every lifecycle step.
    """

    def __init__(self, config: AdaptiveConfig = AdaptiveConfig()) -> None:
        self.config = config
        self.monitor = AdaptiveMonitorEngine()
        self.strategy_engine = AdaptationStrategyEngine()
        self.decision_policy = AdaptiveDecisionPolicy()
        self.simulation = AdaptationSimulationEngine()
        self.repository = AdaptiveProgrammingRepository()
        self.metrics_calc = AdaptiveMetricsCalculator()
        self.reports_gen = AdaptiveReportGenerator()
        self.history_tracker = AdaptationHistoryTracker()

    # ── Context ─────────────────────────────────────────────────────────

    def update_context(
        self, context: AdaptiveContext, updates: dict,
    ) -> AdaptiveContext:
        """Merge *updates* into *context* via the monitor engine."""
        updated = self.monitor.update_context(context, updates)
        get_event_bus().publish(ContextUpdated(
            context_id=updated.context_id,
            recovery_score=updated.recovery_score,
            compliance_rate=updated.compliance_rate,
            progress_percentage=updated.progress_percentage,
        ))
        return updated

    # ── Strategy evaluation ─────────────────────────────────────────────

    def evaluate_strategies(
        self, strategy: AdaptiveStrategy, context: AdaptiveContext,
    ) -> list[AdaptiveRecommendation]:
        """Run all strategy adapters and return non-None recommendations."""
        recommendations = self.strategy_engine.evaluate_all_strategies(
            strategy, context, self.config,
        )
        for rec in recommendations:
            get_event_bus().publish(RecommendationGenerated(
                recommendation_id=rec.recommendation_id,
                adaptation_type=rec.adaptation_type.value,
                suggested_value=rec.suggested_value,
                priority=rec.priority.value,
            ))
        return recommendations

    # ── Simulation ──────────────────────────────────────────────────────

    def simulate_recommendations(
        self,
        recommendations: list[AdaptiveRecommendation],
        context: AdaptiveContext,
    ) -> list[AdaptationScenario]:
        """Simulate every recommendation and emit ScenarioSimulated events."""
        scenarios = self.simulation.simulate_all(
            recommendations, context, self.config,
        )
        for sc in scenarios:
            get_event_bus().publish(ScenarioSimulated(
                scenario_id=sc.scenario_id,
                adaptation_type=sc.adaptation_type.value,
                score=sc.score,
                is_safe=sc.is_safe,
            ))
        return scenarios

    # ── Decision lifecycle ──────────────────────────────────────────────

    def approve_decision(
        self,
        rec: AdaptiveRecommendation,
        context: AdaptiveContext,
        strategy: AdaptiveStrategy,
    ) -> AdaptiveDecision:
        """Evaluate, simulate, safety-check and (if safe) approve a recommendation."""
        approved, policy_reason = self.decision_policy.evaluate_recommendation(
            rec, context, self.config, strategy.active_decisions,
        )
        if not approved:
            return self.reject_decision(rec, policy_reason)

        scenario = self.simulation.simulate_adaptation(rec, context, self.config)
        get_event_bus().publish(ScenarioSimulated(
            scenario_id=scenario.scenario_id,
            adaptation_type=scenario.adaptation_type.value,
            score=scenario.score,
            is_safe=scenario.is_safe,
        ))

        is_safe, risk_factors = self.decision_policy.check_safety(scenario, self.config)

        decision = AdaptiveDecision(
            decision_id=_generate_id("dec"),
            adaptation_type=rec.adaptation_type,
            previous_value=rec.current_value,
            new_value=rec.suggested_value,
            reason=AdaptationReason(
                reason_id=_generate_id("reason"),
                adaptation_type=rec.adaptation_type,
                trigger_source=MonitorSource.PREDICTION,
                trigger_value=rec.confidence,
                threshold_value=0.5,
                description=policy_reason,
                evidence=list(rec.supporting_evidence),
            ),
            status=DecisionStatus.APPROVED if is_safe else DecisionStatus.REJECTED,
            score=scenario.score,
            simulation_result="; ".join(risk_factors) if risk_factors else "safe",
        )
        self.repository.store_decision(decision)

        if is_safe:
            get_event_bus().publish(DecisionApproved(
                decision_id=decision.decision_id,
                adaptation_type=decision.adaptation_type.value,
                previous_value=decision.previous_value,
                new_value=decision.new_value,
            ))
        else:
            get_event_bus().publish(DecisionRejected(
                decision_id=decision.decision_id,
                adaptation_type=decision.adaptation_type.value,
                reason="; ".join(risk_factors),
            ))
        return decision

    def reject_decision(
        self, rec: AdaptiveRecommendation, reason: str,
    ) -> AdaptiveDecision:
        """Create a rejected AdaptiveDecision and emit DecisionRejected."""
        decision = AdaptiveDecision(
            decision_id=_generate_id("dec"),
            adaptation_type=rec.adaptation_type,
            previous_value=rec.current_value,
            new_value=rec.suggested_value,
            reason=AdaptationReason(
                reason_id=_generate_id("reason"),
                adaptation_type=rec.adaptation_type,
                trigger_source=MonitorSource.PREDICTION,
                trigger_value=rec.confidence,
                threshold_value=0.5,
                description=reason,
                evidence=list(rec.supporting_evidence),
            ),
            status=DecisionStatus.REJECTED,
            score=0.0,
            simulation_result=reason,
        )
        self.repository.store_decision(decision)
        get_event_bus().publish(DecisionRejected(
            decision_id=decision.decision_id,
            adaptation_type=decision.adaptation_type.value,
            reason=reason,
        ))
        return decision

    def apply_adaptation(
        self, decision: AdaptiveDecision, strategy: AdaptiveStrategy,
    ) -> tuple[AdaptationHistory, AdaptiveStrategy]:
        """Apply an approved decision to *strategy*, record history, emit event."""
        updated_decision = replace(
            decision,
            status=DecisionStatus.COMPLETED,
            applied_at=datetime.now().isoformat(),
        )
        self.repository.store_decision(updated_decision)

        history = self.history_tracker.record_adaptation(updated_decision, decision.score)
        self.repository.store_history(history)

        updated_strategy = self._apply_to_strategy(strategy, updated_decision)
        self.repository.store_plan(
            AdaptivePlan(
                plan_id=strategy.strategy_id,
                user_id=strategy.user_id,
                strategy=updated_strategy,
            ),
        )

        get_event_bus().publish(AdaptationApplied(
            history_id=history.history_id,
            decision_id=decision.decision_id,
            adaptation_type=decision.adaptation_type.value,
            new_value=decision.new_value,
        ))
        return history, updated_strategy

    def rollback_decision(
        self,
        decision: AdaptiveDecision,
        strategy: AdaptiveStrategy,
        reason: str,
    ) -> tuple[AdaptiveDecision, AdaptiveStrategy]:
        """Roll back a previously approved/completed decision and revert the strategy."""
        rolled_back = replace(
            decision,
            status=DecisionStatus.ROLLED_BACK,
            rollback_reason=reason,
            rolled_back_at=datetime.now().isoformat(),
        )
        self.repository.store_decision(rolled_back)

        reverted_strategy = self._revert_strategy(strategy, rolled_back)

        get_event_bus().publish(DecisionRolledBack(
            decision_id=rolled_back.decision_id,
            adaptation_type=rolled_back.adaptation_type.value,
            rollback_reason=reason,
        ))
        return rolled_back, reverted_strategy

    # ── Snapshot ────────────────────────────────────────────────────────

    def create_snapshot(
        self,
        strategy: AdaptiveStrategy,
        decisions: list[AdaptiveDecision],
        recommendations: list[AdaptiveRecommendation],
        context: AdaptiveContext,
    ) -> AdaptationSnapshot:
        """Capture a point-in-time snapshot and store it in the repository."""
        snapshot = AdaptationSnapshot(
            snapshot_id=_generate_id("snap"),
            version="1.0",
            decisions=list(decisions),
            recommendations=list(recommendations),
            context=context,
            created_at=datetime.now().isoformat(),
        )
        self.repository.store_snapshot(snapshot)
        return snapshot

    # ── Metrics ─────────────────────────────────────────────────────────

    def compute_metrics(self, plan: AdaptivePlan) -> AdaptiveMetrics:
        """Compute quality metrics for *plan* using the metrics calculator."""
        return self.metrics_calc.compute_metrics(plan, plan.decisions)

    # ── Reports ─────────────────────────────────────────────────────────

    def generate_adaptive_report(self, plan: AdaptivePlan) -> str:
        return self.reports_gen.generate_adaptive_report(
            plan, self.compute_metrics(plan),
        )

    def generate_strategy_evolution(self, plan: AdaptivePlan) -> str:
        return self.reports_gen.generate_strategy_evolution(plan)

    def generate_adaptation_history(self, plan: AdaptivePlan) -> str:
        return self.reports_gen.generate_adaptation_history(plan)

    # ── State ───────────────────────────────────────────────────────────

    def get_state(self) -> dict[str, Any]:
        """Return a plain-dict representation of the orchestrator's current state."""
        return {
            "config": self.config,
            "plans": self.repository.list_plans(),
            "decisions": self.repository.list_decisions(),
            "history": self.repository.list_history(),
            "snapshots": self.repository.list_snapshots(),
        }

    # ── Serialization ───────────────────────────────────────────────────

    def to_dict(self) -> dict[str, Any]:
        """Serialize the full orchestrator state to JSON-compatible dicts."""
        return {
            "config": AdaptiveConfigSerializer.serialize(self.config),
            "plans": [
                AdaptivePlanSerializer.serialize(p) for p in self.repository.list_plans()
            ],
            "decisions": [
                AdaptiveDecisionSerializer.serialize(d)
                for d in self.repository.list_decisions()
            ],
            "history": [
                AdaptationHistorySerializer.serialize(h)
                for h in self.repository.list_history()
            ],
            "snapshots": [
                AdaptationSnapshotSerializer.serialize(s)
                for s in self.repository.list_snapshots()
            ],
        }

    @classmethod
    def from_dict(cls, data: dict) -> AdaptiveProgrammingOrchestrator:
        """Deserialize a previously serialized orchestrator state."""
        obj = cls(config=AdaptiveConfigSerializer.deserialize(data.get("config", {})))
        for plan_data in data.get("plans", []):
            obj.repository.store_plan(AdaptivePlanSerializer.deserialize(plan_data))
        for dec_data in data.get("decisions", []):
            obj.repository.store_decision(AdaptiveDecisionSerializer.deserialize(dec_data))
        for hist_data in data.get("history", []):
            obj.repository.store_history(AdaptationHistorySerializer.deserialize(hist_data))
        for snap_data in data.get("snapshots", []):
            obj.repository.store_snapshot(AdaptationSnapshotSerializer.deserialize(snap_data))
        return obj

    # ── Lifecycle ───────────────────────────────────────────────────────

    def clear_all(self) -> None:
        """Reset the in-memory repository — all plans, decisions, history
        and snapshots are discarded."""
        self.repository.clear_all()

    # ── Internal helpers ────────────────────────────────────────────────

    @staticmethod
    def _apply_to_strategy(
        strategy: AdaptiveStrategy, decision: AdaptiveDecision,
    ) -> AdaptiveStrategy:
        """Return a new strategy with *decision* applied to its parameters."""
        now = datetime.now().isoformat()
        if decision.adaptation_type == AdaptationType.VOLUME:
            return replace(
                strategy,
                current_volume=decision.new_value,
                updated_at=now,
            )
        if decision.adaptation_type == AdaptationType.FREQUENCY:
            return replace(
                strategy,
                current_frequency=int(decision.new_value),
                updated_at=now,
            )
        return replace(strategy, updated_at=now)

    @staticmethod
    def _revert_strategy(
        strategy: AdaptiveStrategy, decision: AdaptiveDecision,
    ) -> AdaptiveStrategy:
        """Revert *strategy* back to pre-decision values."""
        now = datetime.now().isoformat()
        if decision.adaptation_type == AdaptationType.VOLUME:
            return replace(
                strategy,
                current_volume=decision.previous_value,
                updated_at=now,
            )
        if decision.adaptation_type == AdaptationType.FREQUENCY:
            return replace(
                strategy,
                current_frequency=int(decision.previous_value),
                updated_at=now,
            )
        return replace(strategy, updated_at=now)
