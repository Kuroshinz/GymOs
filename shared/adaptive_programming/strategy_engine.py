"""Adaptation Strategy Engine — 8 adaptation strategies for long-term training adaptation."""

from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from shared.adaptive_programming.domain import (
    AdaptationType,
    AdaptiveConfig,
    AdaptiveContext,
    AdaptiveRecommendation,
    AdaptiveStrategy,
    RecommendationPriority,
    StrategyPhase,
)


def _generate_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


class AdaptationStrategyEngine:
    """Evaluates adaptation strategies and produces recommendations."""

    def _score_confidence(self, evidence_count: int) -> float:
        if evidence_count >= 4:
            return 0.95
        if evidence_count >= 3:
            return 0.8
        if evidence_count >= 2:
            return 0.6
        if evidence_count >= 1:
            return 0.4
        return 0.1

    def _build_recommendation(
        self,
        adaptation_type: AdaptationType,
        suggested_value: float,
        current_value: float,
        priority: RecommendationPriority,
        confidence: float,
        expected_improvement: float,
        reason: str,
        evidence: list[str],
    ) -> AdaptiveRecommendation:
        return AdaptiveRecommendation(
            recommendation_id=_generate_id("rec"),
            adaptation_type=adaptation_type,
            suggested_value=suggested_value,
            current_value=current_value,
            priority=priority,
            confidence=confidence,
            expected_improvement=expected_improvement,
            reason=reason,
            supporting_evidence=evidence,
            created_at=datetime.now().isoformat(),
        )

    def adapt_volume(
        self,
        strategy: AdaptiveStrategy,
        context: AdaptiveContext,
        config: AdaptiveConfig,
    ) -> AdaptiveRecommendation | None:
        evidence: list[str] = []
        should_increase = (
            context.recovery_score > config.min_recovery_for_volume_increase
            and context.compliance_rate > config.min_compliance_for_adaptation
            and context.progress_percentage > 0.5
        )
        should_decrease = (
            context.recovery_score < 0.4 or context.compliance_rate < 0.5
        )

        if should_increase:
            factor = min(
                (context.recovery_score - 0.6) / 0.4,
                (context.compliance_rate - 0.7) / 0.3,
                (context.progress_percentage - 0.5) / 0.5,
            )
            factor = max(0.1, min(1.0, factor))
            change = strategy.current_volume * config.max_volume_change_per_week * factor
            suggested = strategy.current_volume + change
            evidence = ["High recovery score", "Good compliance rate", "Positive progress"]
            priority = RecommendationPriority.MEDIUM
            confidence = self._score_confidence(len(evidence))
            expected_improvement = change / strategy.current_volume if strategy.current_volume > 0 else 0.05

            return self._build_recommendation(
                adaptation_type=AdaptationType.VOLUME,
                suggested_value=round(suggested, 2),
                current_value=strategy.current_volume,
                priority=priority,
                confidence=confidence,
                expected_improvement=round(expected_improvement, 4),
                reason=(
                    f"Increase volume by {factor * 100:.0f}% due to favorable "
                    f"recovery ({context.recovery_score:.2f}), "
                    f"compliance ({context.compliance_rate:.2f}), "
                    f"and progress ({context.progress_percentage:.2f})"
                ),
                evidence=evidence,
            )

        if should_decrease:
            factor = 0.5
            if context.recovery_score < 0.3:
                factor = 1.0
            elif context.recovery_score < 0.4:
                factor = 0.75
            change = strategy.current_volume * config.max_volume_change_per_week * factor
            suggested = strategy.current_volume - change
            if context.recovery_score < 0.4:
                evidence.append(f"Low recovery score ({context.recovery_score:.2f})")
            if context.compliance_rate < 0.5:
                evidence.append(f"Low compliance rate ({context.compliance_rate:.2f})")
            priority = RecommendationPriority.HIGH
            confidence = self._score_confidence(len(evidence))
            expected_improvement = -change / strategy.current_volume if strategy.current_volume > 0 else -0.05

            return self._build_recommendation(
                adaptation_type=AdaptationType.VOLUME,
                suggested_value=round(suggested, 2),
                current_value=strategy.current_volume,
                priority=priority,
                confidence=confidence,
                expected_improvement=round(expected_improvement, 4),
                reason=(
                    f"Decrease volume by {factor * 100:.0f}% due to "
                    f"{'low recovery' if context.recovery_score < 0.4 else ''}"
                    f"{' and ' if context.recovery_score < 0.4 and context.compliance_rate < 0.5 else ''}"
                    f"{'low compliance' if context.compliance_rate < 0.5 else ''}"
                ),
                evidence=evidence,
            )

        return None

    def adapt_frequency(
        self,
        strategy: AdaptiveStrategy,
        context: AdaptiveContext,
        config: AdaptiveConfig,
    ) -> AdaptiveRecommendation | None:
        evidence: list[str] = []

        if context.recovery_score > 0.7 and context.progress_percentage > 0.6:
            suggested = strategy.current_frequency + 1
            evidence = [
                f"High recovery ({context.recovery_score:.2f})",
                f"Good progress ({context.progress_percentage:.2f})",
            ]
            priority = RecommendationPriority.MEDIUM
            confidence = self._score_confidence(len(evidence))
            return self._build_recommendation(
                adaptation_type=AdaptationType.FREQUENCY,
                suggested_value=float(suggested),
                current_value=float(strategy.current_frequency),
                priority=priority,
                confidence=confidence,
                expected_improvement=0.1,
                reason=f"Increase frequency from {strategy.current_frequency} to {suggested} due to strong recovery and progress",
                evidence=evidence,
            )

        if context.fatigue_level > 0.7:
            suggested = max(1, strategy.current_frequency - 1)
            evidence = [f"High fatigue level ({context.fatigue_level:.2f})"]
            priority = RecommendationPriority.MEDIUM
            confidence = self._score_confidence(len(evidence))
            return self._build_recommendation(
                adaptation_type=AdaptationType.FREQUENCY,
                suggested_value=float(suggested),
                current_value=float(strategy.current_frequency),
                priority=priority,
                confidence=confidence,
                expected_improvement=0.05,
                reason=f"Decrease frequency from {strategy.current_frequency} to {suggested} due to high fatigue",
                evidence=evidence,
            )

        return None

    def adapt_exercise_substitution(
        self,
        strategy: AdaptiveStrategy,
        context: AdaptiveContext,
        config: AdaptiveConfig,
    ) -> AdaptiveRecommendation | None:
        evidence: list[str] = []
        plateau_detected = context.prediction_progress < 0.2 and context.weeks_into_phase >= 3

        if context.recovery_score < 0.4:
            evidence.append(f"Low recovery ({context.recovery_score:.2f})")
        if plateau_detected:
            evidence.append("Progress plateau detected")

        if not evidence:
            return None

        priority = RecommendationPriority.MEDIUM
        confidence = self._score_confidence(len(evidence))
        return self._build_recommendation(
            adaptation_type=AdaptationType.EXERCISE_SUBSTITUTION,
            suggested_value=1.0,
            current_value=0.0,
            priority=priority,
            confidence=confidence,
            expected_improvement=0.15,
            reason=f"Exercise substitution recommended: {', '.join(evidence)}",
            evidence=evidence,
        )

    def adapt_mesocycle(
        self,
        strategy: AdaptiveStrategy,
        context: AdaptiveContext,
        config: AdaptiveConfig,
    ) -> AdaptiveRecommendation | None:
        if context.knowledge_confidence < 0.5:
            evidence = [f"Low knowledge confidence ({context.knowledge_confidence:.2f})"]
            priority = RecommendationPriority.MEDIUM
            confidence = self._score_confidence(len(evidence))
            return self._build_recommendation(
                adaptation_type=AdaptationType.MESOCYCLE_ADJUSTMENT,
                suggested_value=1.0,
                current_value=0.0,
                priority=priority,
                confidence=confidence,
                expected_improvement=0.1,
                reason="Restructure mesocycle due to low prediction confidence",
                evidence=evidence,
            )

        if context.knowledge_confidence > 0.8:
            evidence = [f"High knowledge confidence ({context.knowledge_confidence:.2f})"]
            priority = RecommendationPriority.MEDIUM
            confidence = self._score_confidence(len(evidence))
            return self._build_recommendation(
                adaptation_type=AdaptationType.MESOCYCLE_ADJUSTMENT,
                suggested_value=0.0,
                current_value=0.0,
                priority=priority,
                confidence=confidence,
                expected_improvement=0.0,
                reason="Maintain current mesocycle structure — high prediction confidence",
                evidence=evidence,
            )

        return None

    def adapt_progression(
        self,
        strategy: AdaptiveStrategy,
        context: AdaptiveContext,
        config: AdaptiveConfig,
    ) -> AdaptiveRecommendation | None:
        if context.knowledge_confidence < 0.5:
            evidence = [f"Low knowledge confidence ({context.knowledge_confidence:.2f})"]
            priority = RecommendationPriority.MEDIUM
            confidence = self._score_confidence(len(evidence))
            return self._build_recommendation(
                adaptation_type=AdaptationType.PROGRESSION_ADJUSTMENT,
                suggested_value=1.0,
                current_value=0.0,
                priority=priority,
                confidence=confidence,
                expected_improvement=0.1,
                reason="Adjust progression scheme due to low knowledge confidence",
                evidence=evidence,
            )

        if context.knowledge_confidence > 0.8 and context.optimization_insight_score > 0.7:
            evidence = [
                f"High knowledge confidence ({context.knowledge_confidence:.2f})",
                f"Strong optimization insight ({context.optimization_insight_score:.2f})",
            ]
            priority = RecommendationPriority.MEDIUM
            confidence = self._score_confidence(len(evidence))
            return self._build_recommendation(
                adaptation_type=AdaptationType.PROGRESSION_ADJUSTMENT,
                suggested_value=0.0,
                current_value=0.0,
                priority=priority,
                confidence=confidence,
                expected_improvement=0.0,
                reason="Maintain current progression scheme — high knowledge confidence",
                evidence=evidence,
            )

        return None

    def adapt_deload_timing(
        self,
        strategy: AdaptiveStrategy,
        context: AdaptiveContext,
        config: AdaptiveConfig,
    ) -> AdaptiveRecommendation | None:
        evidence: list[str] = []

        if context.fatigue_level > 0.7:
            evidence.append(f"Elevated fatigue ({context.fatigue_level:.2f})")
        if context.recovery_score < 0.3:
            evidence.append(f"Low recovery ({context.recovery_score:.2f})")

        if not evidence:
            return None

        priority = RecommendationPriority.HIGH
        confidence = self._score_confidence(len(evidence))
        return self._build_recommendation(
            adaptation_type=AdaptationType.DELOAD_TIMING,
            suggested_value=1.0,
            current_value=0.0,
            priority=priority,
            confidence=confidence,
            expected_improvement=0.2,
            reason=f"Deload recommended: {', '.join(evidence)}",
            evidence=evidence,
        )

    def adapt_nutrition_target(
        self,
        strategy: AdaptiveStrategy,
        context: AdaptiveContext,
        config: AdaptiveConfig,
    ) -> AdaptiveRecommendation | None:
        phase = context.current_phase
        evidence: list[str] = []

        if phase == StrategyPhase.PEAK:
            suggested = 1.0
            reason = "Increase nutrition support for peak phase performance"
            evidence = ["Peak phase — increased nutritional demands"]
        elif phase == StrategyPhase.DEVELOPMENT:
            suggested = 0.5
            reason = "Maintain nutrition support during development phase"
            evidence = ["Development phase — steady nutritional requirements"]
        elif phase == StrategyPhase.DELOAD:
            suggested = 0.8
            reason = "Adjust nutrition for recovery during deload phase"
            evidence = ["Deload phase — recovery-focused nutrition"]
        elif phase == StrategyPhase.INITIATION:
            suggested = 0.3
            reason = "Baseline nutrition support during initiation phase"
            evidence = ["Initiation phase — establishing baseline nutrition"]
        elif phase == StrategyPhase.TRANSITION:
            suggested = 0.6
            reason = "Adjust nutrition during transition phase"
            evidence = ["Transition phase — adjusting nutritional strategy"]
        elif phase == StrategyPhase.MAINTENANCE:
            suggested = 0.4
            reason = "Maintain nutrition during maintenance phase"
            evidence = ["Maintenance phase — steady nutritional support"]
        else:
            return None

        priority = RecommendationPriority.MEDIUM
        confidence = self._score_confidence(len(evidence))
        return self._build_recommendation(
            adaptation_type=AdaptationType.NUTRITION_TARGET,
            suggested_value=suggested,
            current_value=0.0,
            priority=priority,
            confidence=confidence,
            expected_improvement=0.08,
            reason=reason,
            evidence=evidence,
        )

    def adapt_goal_reprioritization(
        self,
        strategy: AdaptiveStrategy,
        context: AdaptiveContext,
        config: AdaptiveConfig,
    ) -> AdaptiveRecommendation | None:
        evidence: list[str] = []
        progress_stagnant = context.progress_percentage < 0.1 and context.weeks_into_phase >= 2
        prediction_stagnant = context.prediction_progress < 0.1

        if progress_stagnant:
            evidence.append(f"Stagnant progress ({context.progress_percentage:.2f}) for {context.weeks_into_phase} weeks")
        if prediction_stagnant:
            evidence.append(f"Low prediction progress ({context.prediction_progress:.2f})")

        if not evidence:
            return None

        priority = RecommendationPriority.HIGH
        confidence = self._score_confidence(len(evidence))
        return self._build_recommendation(
            adaptation_type=AdaptationType.GOAL_REPRIORITIZATION,
            suggested_value=1.0,
            current_value=0.0,
            priority=priority,
            confidence=confidence,
            expected_improvement=0.25,
            reason=f"Goal reprioritization recommended: {', '.join(evidence)}",
            evidence=evidence,
        )

    def evaluate_all_strategies(
        self,
        strategy: AdaptiveStrategy,
        context: AdaptiveContext,
        config: AdaptiveConfig,
    ) -> list[AdaptiveRecommendation]:
        results: list[AdaptiveRecommendation | None] = [
            self.adapt_volume(strategy, context, config),
            self.adapt_frequency(strategy, context, config),
            self.adapt_exercise_substitution(strategy, context, config),
            self.adapt_mesocycle(strategy, context, config),
            self.adapt_progression(strategy, context, config),
            self.adapt_deload_timing(strategy, context, config),
            self.adapt_nutrition_target(strategy, context, config),
            self.adapt_goal_reprioritization(strategy, context, config),
        ]
        return [r for r in results if r is not None]
