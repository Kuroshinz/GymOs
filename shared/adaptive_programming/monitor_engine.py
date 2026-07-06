"""Adaptive Monitor Engine — continuously monitors inputs from all platform sources."""

from __future__ import annotations

from dataclasses import replace
from typing import Any

from shared.adaptive_programming.domain import AdaptiveContext


class AdaptiveMonitorEngine:
    """Continuously monitors inputs from all platform sources."""

    @staticmethod
    def update_context(current: AdaptiveContext, updates: dict) -> AdaptiveContext:
        """Merge updates into current context, returning a new frozen instance."""
        valid_fields = {
            "context_id", "intent_goal", "recovery_score",
            "prediction_progress", "knowledge_confidence",
            "optimization_insight_score", "progress_percentage",
            "compliance_rate", "current_phase", "weeks_into_phase",
            "fatigue_level", "timestamp",
        }
        filtered = {k: v for k, v in updates.items() if k in valid_fields}
        return replace(current, **filtered)

    @staticmethod
    def check_intent_changes(old_goal: str, new_goal: str) -> bool:
        """Return True if the goal changed significantly."""
        old_norm = old_goal.strip().lower()
        new_norm = new_goal.strip().lower()
        return old_norm != new_norm

    @staticmethod
    def check_recovery_status(
        recovery_score: float, threshold: float = 0.6,
    ) -> tuple[bool, str]:
        """Return (is_recovered, description)."""
        if recovery_score >= threshold:
            return True, f"Recovery score {recovery_score:.2f} meets threshold {threshold:.2f}"
        return False, f"Recovery score {recovery_score:.2f} below threshold {threshold:.2f}"

    @staticmethod
    def check_prediction_progress(
        prediction_progress: float, expected: float,
    ) -> tuple[bool, str]:
        """Return (on_track, description)."""
        if prediction_progress >= expected:
            return True, f"Prediction progress {prediction_progress:.2f} meets expected {expected:.2f}"
        return False, f"Prediction progress {prediction_progress:.2f} below expected {expected:.2f}"

    @staticmethod
    def check_knowledge_confidence(
        confidence: float, threshold: float = 0.7,
    ) -> tuple[bool, str]:
        """Return (confident, description)."""
        if confidence >= threshold:
            return True, f"Knowledge confidence {confidence:.2f} meets threshold {threshold:.2f}"
        return False, f"Knowledge confidence {confidence:.2f} below threshold {threshold:.2f}"

    @staticmethod
    def check_compliance(
        compliance_rate: float, threshold: float = 0.7,
    ) -> tuple[bool, str]:
        """Return (compliant, description)."""
        if compliance_rate >= threshold:
            return True, f"Compliance rate {compliance_rate:.2f} meets threshold {threshold:.2f}"
        return False, f"Compliance rate {compliance_rate:.2f} below threshold {threshold:.2f}"

    @staticmethod
    def check_progress(
        progress_pct: float, target: float,
    ) -> tuple[bool, str]:
        """Return (making_progress, description)."""
        if progress_pct >= target:
            return True, f"Progress {progress_pct:.2f}% meets target {target:.2f}%"
        return False, f"Progress {progress_pct:.2f}% below target {target:.2f}%"

    @staticmethod
    def get_monitor_summary(context: AdaptiveContext) -> dict[str, Any]:
        """Return a dict with all monitor statuses."""
        recovery_status, recovery_desc = AdaptiveMonitorEngine.check_recovery_status(
            context.recovery_score,
        )
        prediction_status, prediction_desc = AdaptiveMonitorEngine.check_prediction_progress(
            context.prediction_progress, 0.0,
        )
        confidence_status, confidence_desc = AdaptiveMonitorEngine.check_knowledge_confidence(
            context.knowledge_confidence,
        )
        compliance_status, compliance_desc = AdaptiveMonitorEngine.check_compliance(
            context.compliance_rate,
        )
        progress_status, progress_desc = AdaptiveMonitorEngine.check_progress(
            context.progress_percentage, 0.0,
        )

        return {
            "context_id": context.context_id,
            "intent_goal": context.intent_goal,
            "recovery": {
                "score": context.recovery_score,
                "healthy": recovery_status,
                "description": recovery_desc,
            },
            "prediction": {
                "progress": context.prediction_progress,
                "on_track": prediction_status,
                "description": prediction_desc,
            },
            "knowledge_confidence": {
                "score": context.knowledge_confidence,
                "confident": confidence_status,
                "description": confidence_desc,
            },
            "compliance": {
                "rate": context.compliance_rate,
                "compliant": compliance_status,
                "description": compliance_desc,
            },
            "progress": {
                "percentage": context.progress_percentage,
                "making_progress": progress_status,
                "description": progress_desc,
            },
            "current_phase": context.current_phase.label,
            "weeks_into_phase": context.weeks_into_phase,
            "fatigue_level": context.fatigue_level,
        }
