"""Adaptation History Tracker — Record and query adaptation history events."""

from __future__ import annotations

from datetime import datetime, timedelta

from shared.adaptive_programming.domain import (
    AdaptationHistory,
    AdaptationType,
    AdaptiveDecision,
    DecisionStatus,
)


class AdaptationHistoryTracker:
    """Tracks and queries adaptation history events."""

    def record_adaptation(
        self,
        decision: AdaptiveDecision,
        outcome_score: float,
    ) -> AdaptationHistory:
        """Create a new history record from a decision and its outcome."""
        return AdaptationHistory(
            decision_id=decision.decision_id,
            adaptation_type=decision.adaptation_type,
            previous_value=decision.previous_value,
            new_value=decision.new_value,
            reason=decision.reason.description,
            status=decision.status,
            outcome_score=outcome_score,
            adapted_at=datetime.now().isoformat(),
        )

    def get_history_for_decision(
        self,
        decision_id: str,
        all_history: list[AdaptationHistory],
    ) -> AdaptationHistory | None:
        """Find the history record for a specific decision."""
        for h in all_history:
            if h.decision_id == decision_id:
                return h
        return None

    def get_history_by_type(
        self,
        adaptation_type: AdaptationType,
        all_history: list[AdaptationHistory],
    ) -> list[AdaptationHistory]:
        """Filter history records by adaptation type."""
        return [h for h in all_history if h.adaptation_type == adaptation_type]

    def get_recent_history(
        self,
        all_history: list[AdaptationHistory],
        days: int,
    ) -> list[AdaptationHistory]:
        """Return history records within the last N days."""
        cutoff = datetime.now() - timedelta(days=days)
        result: list[AdaptationHistory] = []
        for h in all_history:
            try:
                adapted_at = datetime.fromisoformat(h.adapted_at)
                if adapted_at >= cutoff:
                    result.append(h)
            except (ValueError, TypeError):
                continue
        return result

    def get_success_rate(
        self,
        all_history: list[AdaptationHistory],
    ) -> float:
        """Calculate the success rate from history records.

        Success is defined as records with status COMPLETED and a positive
        outcome score.
        """
        if not all_history:
            return 0.0
        completed = sum(
            1 for h in all_history
            if h.status == DecisionStatus.COMPLETED
        )
        successful = sum(
            1 for h in all_history
            if h.status == DecisionStatus.COMPLETED and h.outcome_score > 0
        )
        return successful / max(completed, 1)
