"""Integration bridge classes for GymOS module ↔ knowledge evidence conversion.

Each bridge accepts dict-like data or prototype objects to avoid
direct cross-module imports.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from shared.knowledge_evolution.domain import (
    ConfidenceLevel,
    EvidenceType,
    KnowledgeConfidence,
    KnowledgeEvidence,
    KnowledgeRecord,
    LifecycleStage,
)


def _get(data: Any, key: str, default: Any = None) -> Any:
    """Safely extract an attribute from a dict or object."""
    if isinstance(data, dict):
        return data.get(key, default)
    return getattr(data, key, default)


# ── Helpers ──────────────────────────────────────────────────────────────────


def _now() -> str:
    return datetime.utcnow().isoformat() + "Z"


def _default_evidence(
    evidence_id: str,
    knowledge_id: str,
    evidence_type: EvidenceType,
    source: str,
    supports: bool = True,
    weight: float = 1.0,
    **extra: Any,
) -> dict:
    return {
        "evidence_id": evidence_id,
        "knowledge_id": knowledge_id,
        "source": source,
        "evidence_type": evidence_type,
        "supports": supports,
        "weight": weight,
        "timestamp": _now(),
        "metadata": extra,
    }


# ── 1. OptimizationKnowledgeBridge ──────────────────────────────────────────


class OptimizationKnowledgeBridge:
    """Converts GymOS optimization data to knowledge evidence/records."""

    @staticmethod
    def from_optimization_experience(experience: Any) -> KnowledgeEvidence:
        exp_id = _get(experience, "experience_id", "")
        knowledge_id = _get(experience, "knowledge_id", "")
        reward = _get(experience, "reward", 0.0)
        supports = reward >= 0
        weight = abs(reward) if reward else 1.0
        kwargs = _default_evidence(
            evidence_id=exp_id,
            knowledge_id=knowledge_id,
            evidence_type=EvidenceType.OPTIMIZATION_RESULT,
            source="optimizer",
            supports=supports,
            weight=max(weight, 0.1),
            context=_get(experience, "context"),
            action=_get(experience, "action"),
            reward=reward,
            metadata=_get(experience, "metadata", {}),
        )
        return KnowledgeEvidence(**kwargs)

    @staticmethod
    def from_optimization_pattern(pattern: Any) -> KnowledgeRecord:
        pattern_id = _get(pattern, "pattern_id", "")
        domain = _get(pattern, "domain", "")
        statement = _get(pattern, "description", "")
        experiences_count = _get(pattern, "experiences_count", 0)
        confidence_val = _get(pattern, "confidence", 0.5)
        created = _get(pattern, "created_at", _now())
        updated = _get(pattern, "updated_at", created)

        return KnowledgeRecord(
            knowledge_id=pattern_id,
            domain=domain,
            statement=statement,
            confidence=KnowledgeConfidence(
                knowledge_id=pattern_id,
                level=_numeric_to_confidence_level(confidence_val),
                score=confidence_val,
                support_count=experiences_count,
                total_evidence=experiences_count,
                last_updated=updated,
            ),
            lifecycle_stage=LifecycleStage.ACTIVE,
            created_at=created,
            updated_at=updated,
        )


# ── 2. PlanningOptimizerBridge ──────────────────────────────────────────────


class PlanningOptimizerBridge:
    """Converts planning/optimizer results to knowledge evidence."""

    @staticmethod
    def from_optimization_result(result: Any) -> KnowledgeEvidence:
        res_id = _get(result, "result_id", "")
        knowledge_id = _get(result, "knowledge_id", "")
        outcome_label = _get(result, "outcome", "")
        supports = outcome_label in ("success", "improved", True)
        metrics = _get(result, "metrics", {})
        weight = metrics.get("improvement", 1.0) if isinstance(metrics, dict) else 1.0

        kwargs = _default_evidence(
            evidence_id=res_id,
            knowledge_id=knowledge_id,
            evidence_type=EvidenceType.OPTIMIZATION_RESULT,
            source="planning_optimizer",
            supports=supports,
            weight=max(float(weight), 0.1),
            strategy=_get(result, "strategy"),
            outcome=outcome_label,
            metrics=metrics,
            metadata=_get(result, "metadata", {}),
        )
        return KnowledgeEvidence(**kwargs)

    @staticmethod
    def from_candidate(candidate: Any) -> KnowledgeEvidence:
        cand_id = _get(candidate, "candidate_id", "")
        knowledge_id = _get(candidate, "knowledge_id", "")
        improvement = _get(candidate, "expected_improvement", 0.0)
        supports = improvement >= 0
        weight = abs(improvement) if improvement else 0.5

        kwargs = _default_evidence(
            evidence_id=cand_id,
            knowledge_id=knowledge_id,
            evidence_type=EvidenceType.OPTIMIZATION_RESULT,
            source="planning_candidate",
            supports=supports,
            weight=max(float(weight), 0.1),
            strategy=_get(candidate, "strategy"),
            parameters=_get(candidate, "parameters"),
            expected_improvement=improvement,
            confidence=_get(candidate, "confidence"),
            metadata=_get(candidate, "metadata", {}),
        )
        return KnowledgeEvidence(**kwargs)


# ── 3. PredictionBridge ─────────────────────────────────────────────────────


class PredictionBridge:
    """Converts prediction results to knowledge evidence."""

    @staticmethod
    def from_prediction_result(prediction: Any) -> KnowledgeEvidence:
        pred_id = _get(prediction, "prediction_id", "")
        knowledge_id = _get(prediction, "knowledge_id", "")
        error = _get(prediction, "error", None)
        actual = _get(prediction, "actual_value", None)
        predicted = _get(prediction, "predicted_value", None)
        # small error → supports
        if error is not None:
            supports = abs(error) < 0.5
            weight = 1.0 / (1.0 + abs(error)) if error != 0 else 1.0
        else:
            supports = True
            weight = 1.0

        kwargs = _default_evidence(
            evidence_id=pred_id,
            knowledge_id=knowledge_id,
            evidence_type=EvidenceType.PREDICTION_OUTCOME,
            source="predictor",
            supports=supports,
            weight=weight,
            variable=_get(prediction, "variable"),
            predicted_value=predicted,
            actual_value=actual,
            error=error,
            metadata=_get(prediction, "metadata", {}),
        )
        return KnowledgeEvidence(**kwargs)


# ── 4. RecoveryBridge ───────────────────────────────────────────────────────


class RecoveryBridge:
    """Converts recovery observations to knowledge evidence."""

    @staticmethod
    def from_recovery_observation(observation: Any) -> KnowledgeEvidence:
        obs_id = _get(observation, "observation_id", "")
        knowledge_id = _get(observation, "knowledge_id", "")
        success = _get(observation, "success", True)
        weight = 1.0 if success else 0.8

        kwargs = _default_evidence(
            evidence_id=obs_id,
            knowledge_id=knowledge_id,
            evidence_type=EvidenceType.RECOVERY_OBSERVATION,
            source="recovery_monitor",
            supports=bool(success),
            weight=weight,
            event_type=_get(observation, "event_type"),
            context=_get(observation, "context"),
            recovery_action=_get(observation, "recovery_action"),
            success=success,
            metadata=_get(observation, "metadata", {}),
        )
        return KnowledgeEvidence(**kwargs)


# ── 5. NutritionBridge ─────────────────────────────────────────────────────


class NutritionBridge:
    """Converts nutrition observations to knowledge evidence."""

    @staticmethod
    def from_nutrition_observation(observation: Any) -> KnowledgeEvidence:
        obs_id = _get(observation, "observation_id", "")
        knowledge_id = _get(observation, "knowledge_id", "")
        impact = _get(observation, "impact", None)
        supports = bool(impact) if impact is not None else True
        weight = (
            float(impact.get("score", 1.0))
            if isinstance(impact, dict)
            else (float(impact) if impact else 1.0)
        )

        kwargs = _default_evidence(
            evidence_id=obs_id,
            knowledge_id=knowledge_id,
            evidence_type=EvidenceType.NUTRITION_OBSERVATION,
            source="nutrition_analyzer",
            supports=supports,
            weight=max(float(weight), 0.1),
            meal_type=_get(observation, "meal_type"),
            nutrients=_get(observation, "nutrients"),
            impact=impact,
            metadata=_get(observation, "metadata", {}),
        )
        return KnowledgeEvidence(**kwargs)


# ── 6. DecisionBridge ───────────────────────────────────────────────────────


class DecisionBridge:
    """Converts decision outcomes to knowledge evidence."""

    @staticmethod
    def from_decision_outcome(outcome: Any) -> KnowledgeEvidence:
        out_id = _get(outcome, "outcome_id", "")
        knowledge_id = _get(outcome, "knowledge_id", "")
        result_label = _get(outcome, "result", "")
        supports = result_label in ("success", "positive", True)
        weight = _get(outcome, "confidence", 1.0)

        kwargs = _default_evidence(
            evidence_id=out_id,
            knowledge_id=knowledge_id,
            evidence_type=EvidenceType.DECISION_OUTCOME,
            source="decision_engine",
            supports=supports,
            weight=max(float(weight), 0.1),
            decision_context=_get(outcome, "decision_context"),
            action_taken=_get(outcome, "action_taken"),
            result=result_label,
            alternatives=_get(outcome, "alternatives"),
            metadata=_get(outcome, "metadata", {}),
        )
        return KnowledgeEvidence(**kwargs)


# ── Helpers (internal) ──────────────────────────────────────────────────────


def _numeric_to_confidence_level(value: float) -> ConfidenceLevel:
    if value >= 0.9:
        return ConfidenceLevel.VERY_HIGH
    if value >= 0.7:
        return ConfidenceLevel.HIGH
    if value >= 0.5:
        return ConfidenceLevel.MEDIUM
    if value >= 0.3:
        return ConfidenceLevel.LOW
    return ConfidenceLevel.VERY_LOW
