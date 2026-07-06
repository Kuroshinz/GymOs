from __future__ import annotations

from shared.intent.domain import (
    IntentConflictSeverity,
    UserIntent,
)
from shared.intent.merger import ConflictResolver


class IntentScorer:
    @staticmethod
    def score(intent: UserIntent) -> float:
        if not intent.goals:
            return 0.0
        completeness = IntentScorer._score_completeness(intent)
        consistency = IntentScorer._score_consistency(intent)
        confidence = IntentScorer._score_confidence(intent)
        stability = IntentScorer._score_stability(intent)
        alignment = IntentScorer._score_alignment(intent)
        return round(
            completeness * 0.25 +
            consistency * 0.25 +
            confidence * 0.20 +
            stability * 0.15 +
            alignment * 0.15,
            2,
        )

    @staticmethod
    def _score_completeness(intent: UserIntent) -> float:
        checks = [
            bool(intent.goals),
            bool(intent.training.style),
            bool(intent.nutrition.approach),
            intent.timeline.sessions_per_week > 0,
            intent.recovery.sleep_target > 0,
            intent.lifestyle.occupation_hours_per_week > 0,
            intent.compliance.training_compliance_rate > 0,
        ]
        return sum(checks) / len(checks)

    @staticmethod
    def _score_consistency(intent: UserIntent) -> float:
        conflicts = ConflictResolver.detect(intent)
        if not conflicts:
            return 1.0
        penalty = sum({
            IntentConflictSeverity.LOW: 0.1,
            IntentConflictSeverity.MEDIUM: 0.2,
            IntentConflictSeverity.HIGH: 0.35,
            IntentConflictSeverity.CRITICAL: 0.5,
        }[c.severity] for c in conflicts)
        return max(0.0, 1.0 - penalty)

    @staticmethod
    def _score_confidence(intent: UserIntent) -> float:
        scores: list[float] = []
        if intent.compliance.training_compliance_rate > 0:
            scores.append(min(1.0, intent.compliance.training_compliance_rate + 0.1))
        if intent.compliance.nutrition_compliance_rate > 0:
            scores.append(min(1.0, intent.compliance.nutrition_compliance_rate + 0.1))
        if intent.compliance.recovery_compliance_rate > 0:
            scores.append(min(1.0, intent.compliance.recovery_compliance_rate + 0.1))
        if intent.compliance.streak_days > 0:
            scores.append(min(1.0, intent.compliance.streak_days / 90.0))
        return sum(scores) / len(scores) if scores else 0.3

    @staticmethod
    def _score_stability(intent: UserIntent) -> float:
        resolved = sum(1 for c in intent.conflicts if c.is_resolved)
        total = len(intent.conflicts)
        if total == 0:
            return 0.9
        return resolved / total

    @staticmethod
    def _score_alignment(intent: UserIntent) -> float:
        if not intent.goals:
            return 0.0
        primary = intent.goals[0]
        if intent.nutrition.approach.value == "lean_bulk" and primary.goal_type.value == "hypertrophy" or intent.nutrition.approach.value == "cut" and primary.goal_type.value == "weight":
            alignment = 0.9
        else:
            alignment = 0.5
        if intent.training.style.value == "ppl_ul" and primary.goal_type.value == "hypertrophy":
            alignment += 0.05
        return min(1.0, alignment)

    @staticmethod
    def completeness(intent: UserIntent) -> float:
        return IntentScorer._score_completeness(intent)

    @staticmethod
    def consistency(intent: UserIntent) -> float:
        return IntentScorer._score_consistency(intent)

    @staticmethod
    def confidence(intent: UserIntent) -> float:
        return IntentScorer._score_confidence(intent)

    @staticmethod
    def stability(intent: UserIntent) -> float:
        return IntentScorer._score_stability(intent)
