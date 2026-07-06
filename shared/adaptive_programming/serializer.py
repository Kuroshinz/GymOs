"""Adaptive Programming Serializer — Full round-trip serialization for domain models."""

from __future__ import annotations

from typing import Any

from shared.adaptive_programming.domain import (
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

# ── Enum helpers ──────────────────────────────────────────────────────────


def _serialize_enum(value: Any) -> str | None:
    return value.value if value is not None else None


def _deserialize_enum(cls: type, value: str | None):
    if value is None:
        return None
    return cls(value)


# ── AdaptiveContext ───────────────────────────────────────────────────────


class AdaptiveContextSerializer:

    @staticmethod
    def serialize(obj: AdaptiveContext) -> dict[str, Any]:
        return {
            "context_id": obj.context_id,
            "intent_goal": obj.intent_goal,
            "recovery_score": obj.recovery_score,
            "prediction_progress": obj.prediction_progress,
            "knowledge_confidence": obj.knowledge_confidence,
            "optimization_insight_score": obj.optimization_insight_score,
            "progress_percentage": obj.progress_percentage,
            "compliance_rate": obj.compliance_rate,
            "current_phase": _serialize_enum(obj.current_phase),
            "weeks_into_phase": obj.weeks_into_phase,
            "fatigue_level": obj.fatigue_level,
            "timestamp": obj.timestamp,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> AdaptiveContext:
        return AdaptiveContext(
            context_id=data.get("context_id", ""),
            intent_goal=data.get("intent_goal", ""),
            recovery_score=data.get("recovery_score", 0.0),
            prediction_progress=data.get("prediction_progress", 0.0),
            knowledge_confidence=data.get("knowledge_confidence", 0.0),
            optimization_insight_score=data.get("optimization_insight_score", 0.0),
            progress_percentage=data.get("progress_percentage", 0.0),
            compliance_rate=data.get("compliance_rate", 0.0),
            current_phase=_deserialize_enum(StrategyPhase, data.get("current_phase")),
            weeks_into_phase=data.get("weeks_into_phase", 0),
            fatigue_level=data.get("fatigue_level", 0.0),
            timestamp=data.get("timestamp", ""),
        )


# ── AdaptationReason ─────────────────────────────────────────────────────


class AdaptationReasonSerializer:

    @staticmethod
    def serialize(obj: AdaptationReason) -> dict[str, Any]:
        return {
            "reason_id": obj.reason_id,
            "adaptation_type": _serialize_enum(obj.adaptation_type),
            "trigger_source": _serialize_enum(obj.trigger_source),
            "trigger_value": obj.trigger_value,
            "threshold_value": obj.threshold_value,
            "description": obj.description,
            "evidence": list(obj.evidence),
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> AdaptationReason:
        return AdaptationReason(
            reason_id=data.get("reason_id", ""),
            adaptation_type=_deserialize_enum(AdaptationType, data.get("adaptation_type")),
            trigger_source=_deserialize_enum(MonitorSource, data.get("trigger_source")),
            trigger_value=data.get("trigger_value", 0.0),
            threshold_value=data.get("threshold_value", 0.0),
            description=data.get("description", ""),
            evidence=list(data.get("evidence", [])),
        )


# ── AdaptiveDecision ─────────────────────────────────────────────────────


class AdaptiveDecisionSerializer:

    @staticmethod
    def serialize(obj: AdaptiveDecision) -> dict[str, Any]:
        return {
            "decision_id": obj.decision_id,
            "adaptation_type": _serialize_enum(obj.adaptation_type),
            "previous_value": obj.previous_value,
            "new_value": obj.new_value,
            "reason": AdaptationReasonSerializer.serialize(obj.reason),
            "status": _serialize_enum(obj.status),
            "score": obj.score,
            "simulation_result": obj.simulation_result,
            "applied_at": obj.applied_at,
            "rolled_back_at": obj.rolled_back_at,
            "rollback_reason": obj.rollback_reason,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> AdaptiveDecision:
        return AdaptiveDecision(
            decision_id=data.get("decision_id", ""),
            adaptation_type=_deserialize_enum(AdaptationType, data.get("adaptation_type")),
            previous_value=data.get("previous_value", 0.0),
            new_value=data.get("new_value", 0.0),
            reason=AdaptationReasonSerializer.deserialize(data.get("reason", {})),
            status=_deserialize_enum(DecisionStatus, data.get("status")),
            score=data.get("score", 0.0),
            simulation_result=data.get("simulation_result", ""),
            applied_at=data.get("applied_at", ""),
            rolled_back_at=data.get("rolled_back_at", ""),
            rollback_reason=data.get("rollback_reason", ""),
        )


# ── AdaptiveRecommendation ───────────────────────────────────────────────


class AdaptiveRecommendationSerializer:

    @staticmethod
    def serialize(obj: AdaptiveRecommendation) -> dict[str, Any]:
        return {
            "recommendation_id": obj.recommendation_id,
            "adaptation_type": _serialize_enum(obj.adaptation_type),
            "suggested_value": obj.suggested_value,
            "current_value": obj.current_value,
            "priority": _serialize_enum(obj.priority),
            "confidence": obj.confidence,
            "expected_improvement": obj.expected_improvement,
            "reason": obj.reason,
            "supporting_evidence": list(obj.supporting_evidence),
            "created_at": obj.created_at,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> AdaptiveRecommendation:
        return AdaptiveRecommendation(
            recommendation_id=data.get("recommendation_id", ""),
            adaptation_type=_deserialize_enum(AdaptationType, data.get("adaptation_type")),
            suggested_value=data.get("suggested_value", 0.0),
            current_value=data.get("current_value", 0.0),
            priority=_deserialize_enum(RecommendationPriority, data.get("priority")),
            confidence=data.get("confidence", 0.0),
            expected_improvement=data.get("expected_improvement", 0.0),
            reason=data.get("reason", ""),
            supporting_evidence=list(data.get("supporting_evidence", [])),
            created_at=data.get("created_at", ""),
        )


# ── AdaptationHistory ────────────────────────────────────────────────────


class AdaptationHistorySerializer:

    @staticmethod
    def serialize(obj: AdaptationHistory) -> dict[str, Any]:
        return {
            "history_id": obj.history_id,
            "decision_id": obj.decision_id,
            "adaptation_type": _serialize_enum(obj.adaptation_type),
            "previous_value": obj.previous_value,
            "new_value": obj.new_value,
            "reason": obj.reason,
            "status": _serialize_enum(obj.status),
            "outcome_score": obj.outcome_score,
            "adapted_at": obj.adapted_at,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> AdaptationHistory:
        return AdaptationHistory(
            history_id=data.get("history_id", ""),
            decision_id=data.get("decision_id", ""),
            adaptation_type=_deserialize_enum(AdaptationType, data.get("adaptation_type")),
            previous_value=data.get("previous_value", 0.0),
            new_value=data.get("new_value", 0.0),
            reason=data.get("reason", ""),
            status=_deserialize_enum(DecisionStatus, data.get("status")),
            outcome_score=data.get("outcome_score", 0.0),
            adapted_at=data.get("adapted_at", ""),
        )


# ── AdaptationSnapshot ───────────────────────────────────────────────────


class AdaptationSnapshotSerializer:

    @staticmethod
    def serialize(obj: AdaptationSnapshot) -> dict[str, Any]:
        return {
            "snapshot_id": obj.snapshot_id,
            "version": obj.version,
            "decisions": [AdaptiveDecisionSerializer.serialize(d) for d in obj.decisions],
            "recommendations": [AdaptiveRecommendationSerializer.serialize(r) for r in obj.recommendations],
            "context": AdaptiveContextSerializer.serialize(obj.context),
            "created_at": obj.created_at,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> AdaptationSnapshot:
        return AdaptationSnapshot(
            snapshot_id=data.get("snapshot_id", ""),
            version=data.get("version", ""),
            decisions=[AdaptiveDecisionSerializer.deserialize(d) for d in data.get("decisions", [])],
            recommendations=[AdaptiveRecommendationSerializer.deserialize(r) for r in data.get("recommendations", [])],
            context=AdaptiveContextSerializer.deserialize(data.get("context", {})),
            created_at=data.get("created_at", ""),
        )


# ── AdaptiveStrategy ─────────────────────────────────────────────────────


class AdaptiveStrategySerializer:

    @staticmethod
    def serialize(obj: AdaptiveStrategy) -> dict[str, Any]:
        return {
            "strategy_id": obj.strategy_id,
            "user_id": obj.user_id,
            "phase": _serialize_enum(obj.phase),
            "base_volume": obj.base_volume,
            "base_frequency": obj.base_frequency,
            "current_volume": obj.current_volume,
            "current_frequency": obj.current_frequency,
            "goal": obj.goal,
            "active_decisions": [AdaptiveDecisionSerializer.serialize(d) for d in obj.active_decisions],
            "weeks_into_phase": obj.weeks_into_phase,
            "created_at": obj.created_at,
            "updated_at": obj.updated_at,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> AdaptiveStrategy:
        return AdaptiveStrategy(
            strategy_id=data.get("strategy_id", ""),
            user_id=data.get("user_id", ""),
            phase=_deserialize_enum(StrategyPhase, data.get("phase")),
            base_volume=data.get("base_volume", 0.0),
            base_frequency=data.get("base_frequency", 0),
            current_volume=data.get("current_volume", 0.0),
            current_frequency=data.get("current_frequency", 0),
            goal=data.get("goal", ""),
            active_decisions=[AdaptiveDecisionSerializer.deserialize(d) for d in data.get("active_decisions", [])],
            weeks_into_phase=data.get("weeks_into_phase", 0),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
        )


# ── AdaptivePlan ─────────────────────────────────────────────────────────


class AdaptivePlanSerializer:

    @staticmethod
    def serialize(obj: AdaptivePlan) -> dict[str, Any]:
        return {
            "plan_id": obj.plan_id,
            "user_id": obj.user_id,
            "strategy": AdaptiveStrategySerializer.serialize(obj.strategy),
            "decisions": [AdaptiveDecisionSerializer.serialize(d) for d in obj.decisions],
            "history": [AdaptationHistorySerializer.serialize(h) for h in obj.history],
            "snapshots": [AdaptationSnapshotSerializer.serialize(s) for s in obj.snapshots],
            "created_at": obj.created_at,
            "updated_at": obj.updated_at,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> AdaptivePlan:
        return AdaptivePlan(
            plan_id=data.get("plan_id", ""),
            user_id=data.get("user_id", ""),
            strategy=AdaptiveStrategySerializer.deserialize(data.get("strategy", {})),
            decisions=[AdaptiveDecisionSerializer.deserialize(d) for d in data.get("decisions", [])],
            history=[AdaptationHistorySerializer.deserialize(h) for h in data.get("history", [])],
            snapshots=[AdaptationSnapshotSerializer.deserialize(s) for s in data.get("snapshots", [])],
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
        )


# ── AdaptationScenario ───────────────────────────────────────────────────


class AdaptationScenarioSerializer:

    @staticmethod
    def serialize(obj: AdaptationScenario) -> dict[str, Any]:
        return {
            "scenario_id": obj.scenario_id,
            "adaptation_type": _serialize_enum(obj.adaptation_type),
            "proposed_value": obj.proposed_value,
            "current_value": obj.current_value,
            "context": AdaptiveContextSerializer.serialize(obj.context),
            "score": obj.score,
            "is_safe": obj.is_safe,
            "risk_factors": list(obj.risk_factors),
            "simulated_at": obj.simulated_at,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> AdaptationScenario:
        return AdaptationScenario(
            scenario_id=data.get("scenario_id", ""),
            adaptation_type=_deserialize_enum(AdaptationType, data.get("adaptation_type")),
            proposed_value=data.get("proposed_value", 0.0),
            current_value=data.get("current_value", 0.0),
            context=AdaptiveContextSerializer.deserialize(data.get("context", {})),
            score=data.get("score", 0.0),
            is_safe=data.get("is_safe", False),
            risk_factors=list(data.get("risk_factors", [])),
            simulated_at=data.get("simulated_at", ""),
        )


# ── AdaptiveMetrics ──────────────────────────────────────────────────────


class AdaptiveMetricsSerializer:

    @staticmethod
    def serialize(obj: AdaptiveMetrics) -> dict[str, Any]:
        return {
            "metrics_id": obj.metrics_id,
            "total_adaptations": obj.total_adaptations,
            "approved_adaptations": obj.approved_adaptations,
            "rejected_adaptations": obj.rejected_adaptations,
            "rolled_back_adaptations": obj.rolled_back_adaptations,
            "adaptation_frequency": obj.adaptation_frequency,
            "adaptation_quality": obj.adaptation_quality,
            "success_rate": obj.success_rate,
            "rollback_rate": obj.rollback_rate,
            "strategy_stability": obj.strategy_stability,
            "timestamp": obj.timestamp,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> AdaptiveMetrics:
        return AdaptiveMetrics(
            metrics_id=data.get("metrics_id", ""),
            total_adaptations=data.get("total_adaptations", 0),
            approved_adaptations=data.get("approved_adaptations", 0),
            rejected_adaptations=data.get("rejected_adaptations", 0),
            rolled_back_adaptations=data.get("rolled_back_adaptations", 0),
            adaptation_frequency=data.get("adaptation_frequency", 0.0),
            adaptation_quality=data.get("adaptation_quality", 0.0),
            success_rate=data.get("success_rate", 0.0),
            rollback_rate=data.get("rollback_rate", 0.0),
            strategy_stability=data.get("strategy_stability", 0.0),
            timestamp=data.get("timestamp", ""),
        )


# ── AdaptiveConfig ───────────────────────────────────────────────────────


class AdaptiveConfigSerializer:

    @staticmethod
    def serialize(obj: AdaptiveConfig) -> dict[str, Any]:
        return {
            "enable_auto_adaptation": obj.enable_auto_adaptation,
            "min_recovery_for_volume_increase": obj.min_recovery_for_volume_increase,
            "max_volume_change_per_week": obj.max_volume_change_per_week,
            "max_frequency_change_per_week": obj.max_frequency_change_per_week,
            "min_compliance_for_adaptation": obj.min_compliance_for_adaptation,
            "adaptation_cooldown_days": obj.adaptation_cooldown_days,
            "max_concurrent_adaptations": obj.max_concurrent_adaptations,
            "simulation_samples": obj.simulation_samples,
            "safety_threshold": obj.safety_threshold,
            "enable_rollback": obj.enable_rollback,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> AdaptiveConfig:
        return AdaptiveConfig(
            enable_auto_adaptation=data.get("enable_auto_adaptation", True),
            min_recovery_for_volume_increase=data.get("min_recovery_for_volume_increase", 0.6),
            max_volume_change_per_week=data.get("max_volume_change_per_week", 0.2),
            max_frequency_change_per_week=data.get("max_frequency_change_per_week", 1),
            min_compliance_for_adaptation=data.get("min_compliance_for_adaptation", 0.7),
            adaptation_cooldown_days=data.get("adaptation_cooldown_days", 14),
            max_concurrent_adaptations=data.get("max_concurrent_adaptations", 3),
            simulation_samples=data.get("simulation_samples", 10),
            safety_threshold=data.get("safety_threshold", 0.3),
            enable_rollback=data.get("enable_rollback", True),
        )
