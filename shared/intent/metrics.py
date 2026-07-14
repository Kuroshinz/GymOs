from __future__ import annotations

from dataclasses import dataclass, field

from shared.intent.domain import UserIntent
from shared.intent.scorer import IntentScorer
from shared.intent.validator import IntentValidator


@dataclass
class IntentHealthScore:
    overall: float = 0.0
    completeness: float = 0.0
    consistency: float = 0.0
    confidence: float = 0.0
    stability: float = 0.0
    alignment: float = 0.0

    def __post_init__(self) -> None:
        self.overall = round(
            self.completeness * 0.25 +
            self.consistency * 0.25 +
            self.confidence * 0.20 +
            self.stability * 0.15 +
            self.alignment * 0.15,
            2,
        )


@dataclass
class IntentMetrics:
    total_intents: int = 0
    active_intents: int = 0
    archived_intents: int = 0
    avg_score: float = 0.0
    avg_completeness: float = 0.0
    avg_consistency: float = 0.0
    avg_confidence: float = 0.0
    avg_stability: float = 0.0
    total_conflicts: int = 0
    resolved_conflicts: int = 0
    unresolved_conflicts: int = 0
    total_goals: int = 0
    total_constraints: int = 0
    version_count: int = 0
    health: IntentHealthScore = field(default_factory=IntentHealthScore)

    @staticmethod
    def compute(intents: list[UserIntent], scorer: IntentScorer, validator: IntentValidator) -> IntentMetrics:
        if not intents:
            return IntentMetrics()

        total = len(intents)
        active = sum(1 for i in intents if i.status.value == "active")
        archived = sum(1 for i in intents if i.status.value == "archived")

        scores = [scorer.score(i) for i in intents]
        completenesses = [scorer.completeness(i) for i in intents]
        consistencies = [scorer.consistency(i) for i in intents]
        confidences = [scorer.confidence(i) for i in intents]
        stabilities = [scorer.stability(i) for i in intents]

        all_conflicts = [c for i in intents for c in i.conflicts]
        resolved = sum(1 for c in all_conflicts if c.is_resolved)
        unresolved = len(all_conflicts) - resolved

        total_goals = sum(len(i.goals) for i in intents)
        total_constraints = sum(len(i.constraints) for i in intents)

        def avg(vals): return sum(vals) / len(vals) if vals else 0.0

        health = IntentHealthScore(
            completeness=round(avg(completenesses), 2),
            consistency=round(avg(consistencies), 2),
            confidence=round(avg(confidences), 2),
            stability=round(avg(stabilities), 2),
            alignment=round(avg([scorer._score_alignment(i) for i in intents]), 2),
        )

        return IntentMetrics(
            total_intents=total,
            active_intents=active,
            archived_intents=archived,
            avg_score=round(avg(scores), 2),
            avg_completeness=health.completeness,
            avg_consistency=health.consistency,
            avg_confidence=health.confidence,
            avg_stability=health.stability,
            total_conflicts=len(all_conflicts),
            resolved_conflicts=resolved,
            unresolved_conflicts=unresolved,
            total_goals=total_goals,
            total_constraints=total_constraints,
            version_count=1,
            health=health,
        )

    @staticmethod
    def health_score(intent: UserIntent, scorer: IntentScorer) -> IntentHealthScore:
        return IntentHealthScore(
            completeness=scorer.completeness(intent),
            consistency=scorer.consistency(intent),
            confidence=scorer.confidence(intent),
            stability=scorer.stability(intent),
            alignment=scorer._score_alignment(intent),
        )
