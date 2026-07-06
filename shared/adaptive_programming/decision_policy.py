"""Deterministic, rule-based, evidence-driven decision policy."""

from __future__ import annotations

from shared.adaptive_programming.domain import (
    AdaptationScenario,
    AdaptiveConfig,
    AdaptiveContext,
    AdaptiveDecision,
    AdaptiveRecommendation,
    RecommendationPriority,
)


class AdaptiveDecisionPolicy:
    """Rule-based policy engine for evaluating, scoring, and safety-checking
    adaptive programming decisions."""

    @staticmethod
    def evaluate_recommendation(
        rec: AdaptiveRecommendation,
        context: AdaptiveContext,
        config: AdaptiveConfig,
        active_decisions: list[AdaptiveDecision],
    ) -> tuple[bool, str]:
        """Evaluate whether a recommendation should be approved.

        Rules are applied in order:
        1. REJECT if max concurrent adaptations exceeded.
        2. REJECT if compliance is too low.
        3. REJECT if same adaptation type is in cooldown.
        4. APPROVE unconditionally for CRITICAL priority.
        5. APPROVE if confidence >= 0.7 and expected_improvement > 0.
        6. Fall through to score-based approval.
        """
        if len(active_decisions) >= config.max_concurrent_adaptations:
            return False, (
                f"Max concurrent adaptations ({config.max_concurrent_adaptations}) "
                f"already active"
            )

        if context.compliance_rate < config.min_compliance_for_adaptation:
            return False, (
                f"Compliance rate {context.compliance_rate:.2f} below "
                f"minimum {config.min_compliance_for_adaptation:.2f}"
            )

        for ad in active_decisions:
            if ad.adaptation_type == rec.adaptation_type:
                return False, (
                    f"Adaptation type '{rec.adaptation_type.value}' is in cooldown; "
                    f"active decision {ad.decision_id} already in progress"
                )

        if rec.priority == RecommendationPriority.CRITICAL:
            return True, "CRITICAL priority — approved unconditionally"

        if rec.confidence >= 0.7 and rec.expected_improvement > 0:
            return True, (
                f"Confidence {rec.confidence:.2f} >= 0.7 and "
                f"expected improvement {rec.expected_improvement:.4f} > 0"
            )

        score = AdaptiveDecisionPolicy.score_recommendation(rec, context)
        threshold = 0.5
        if score >= threshold:
            return True, f"Score {score:.4f} >= {threshold}"
        return False, f"Score {score:.4f} < {threshold}"

    @staticmethod
    def score_recommendation(
        rec: AdaptiveRecommendation,
        context: AdaptiveContext,
    ) -> float:
        """Compute a composite score in [0, 1] for a recommendation."""
        components = (
            rec.confidence * 0.4
            + rec.expected_improvement * 0.3
            + (1 - abs(context.recovery_score - 0.5) * 2) * 0.15
            + context.compliance_rate * 0.15
        )
        return max(0.0, min(1.0, components))

    @staticmethod
    def should_rollback(
        decision: AdaptiveDecision,
        current_outcome: float,
    ) -> tuple[bool, str]:
        """Determine whether a previously approved decision should be rolled back.

        *current_outcome* is treated as the compliance rate after adaptation
        when checking the compliance threshold, or the raw outcome metric
        when checking for a significant drop.
        """
        outcome_drop = decision.score - current_outcome
        if outcome_drop > 0.2:
            return True, (
                f"Outcome dropped {outcome_drop:.4f} (> 0.2) from "
                f"{decision.score:.4f} to {current_outcome:.4f}"
            )

        if current_outcome < 0.5:
            return True, (
                f"Compliance/outcome {current_outcome:.4f} dropped below 0.5 "
                f"after adaptation"
            )

        return False, ""

    @staticmethod
    def check_safety(
        scenario: AdaptationScenario,
        config: AdaptiveConfig,
    ) -> tuple[bool, list[str]]:
        """Check whether a proposed scenario is safe to apply.

        Returns (is_safe, risk_factors).
        """
        risk_factors: list[str] = []

        volume_change = abs(scenario.proposed_value - scenario.current_value)
        if volume_change > config.max_volume_change_per_week:
            risk_factors.append(
                f"Volume change {volume_change:.2f} exceeds max "
                f"{config.max_volume_change_per_week:.2f} per week"
            )

        freq_change = abs(int(scenario.proposed_value - scenario.current_value))
        if freq_change > config.max_frequency_change_per_week:
            risk_factors.append(
                f"Frequency change {freq_change} exceeds max "
                f"{config.max_frequency_change_per_week} per week"
            )

        if scenario.score < config.safety_threshold:
            risk_factors.append(
                f"Scenario score {scenario.score:.4f} below safety threshold "
                f"{config.safety_threshold:.4f}"
            )

        return len(risk_factors) == 0, risk_factors
