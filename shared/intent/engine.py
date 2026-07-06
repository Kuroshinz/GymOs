from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from shared.intent.builder import IntentBuilder
from shared.intent.domain import IntentSnapshot, UserIntent
from shared.intent.merger import ConflictResolver, IntentMerger
from shared.intent.scorer import IntentScorer
from shared.intent.validator import IntentValidator, ValidationResult
from shared.intent.versioner import IntentVersioner


@dataclass
class IntentEngine:
    builder: IntentBuilder = field(default_factory=IntentBuilder)
    merger: IntentMerger = field(default_factory=IntentMerger)
    resolver: ConflictResolver = field(default_factory=ConflictResolver)
    versioner: IntentVersioner = field(default_factory=IntentVersioner)
    scorer: IntentScorer = field(default_factory=IntentScorer)
    validator: IntentValidator = field(default_factory=IntentValidator)

    def build(self, config: dict[str, Any]) -> UserIntent:
        return self.builder.build(config)

    def merge(self, base: UserIntent, override: UserIntent) -> UserIntent:
        return self.merger.merge(base, override)

    def resolve(self, intent: UserIntent, auto_resolve: bool = True) -> UserIntent:
        return self.resolver.resolve(intent, auto_resolve=auto_resolve)

    def detect_conflicts(self, intent: UserIntent) -> list:
        return self.resolver.detect(intent)

    def validate(self, intent: UserIntent) -> ValidationResult:
        return self.validator.validate(intent)

    def score(self, intent: UserIntent) -> float:
        return self.scorer.score(intent)

    def save_version(self, intent: UserIntent, description: str = "") -> IntentSnapshot:
        scored = UserIntent(
            intent_id=intent.intent_id, version=intent.version, status=intent.status,
            created_at=intent.created_at, updated_at=intent.updated_at,
            goals=intent.goals, constraints=intent.constraints,
            timeline=intent.timeline, equipment=intent.equipment,
            lifestyle=intent.lifestyle, compliance=intent.compliance,
            risk_tolerance=intent.risk_tolerance,
            training=intent.training, nutrition=intent.nutrition,
            recovery=intent.recovery, adaptive=intent.adaptive,
            priorities=intent.priorities, conflicts=intent.conflicts,
        )
        return self.versioner.save_version(scored, description)

    def get_history(self, intent_id: str) -> list[IntentSnapshot]:
        return self.versioner.get_history(intent_id)

    def rollback(self, intent_id: str, version: str) -> UserIntent | None:
        return self.versioner.rollback(intent_id, version)

    def build_and_score(self, config: dict[str, Any]) -> tuple[UserIntent, float, ValidationResult]:
        intent = self.build(config)
        scored = self.resolve(intent)
        score = self.scorer.score(scored)
        validation = self.validator.validate(scored)
        return scored, score, validation

    def full_pipeline(self, config: dict[str, Any], auto_resolve: bool = True) -> tuple[UserIntent, float, ValidationResult, list]:
        intent = self.build(config)
        resolved = self.resolver.resolve(intent, auto_resolve=auto_resolve)
        score = self.scorer.score(resolved)
        validation = self.validator.validate(resolved)
        conflicts = self.resolver.detect(resolved)
        return resolved, score, validation, conflicts
