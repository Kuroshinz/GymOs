from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from shared.intent.domain import UserIntent
from shared.intent.repository import IntentRepository
from shared.intent.scorer import IntentScorer
from shared.intent.validator import IntentValidator


@dataclass
class IntentState:
    current_intent: UserIntent | None = None
    intent_count: int = 0
    active_count: int = 0
    last_updated: str = ""
    has_active_intent: bool = False
    score: float = 0.0
    errors: int = 0
    warnings: int = 0

    @staticmethod
    def build(repo: IntentRepository, scorer: IntentScorer, validator: IntentValidator) -> IntentState:
        active = repo.list_active()
        total = repo.count()
        current = active[0] if active else None
        now = datetime.now().isoformat()

        state = IntentState(
            current_intent=current,
            intent_count=total,
            active_count=len(active),
            last_updated=now,
            has_active_intent=current is not None,
        )

        if current:
            state.score = scorer.score(current)
            v = validator.validate(current)
            state.errors = v.error_count
            state.warnings = v.warning_count

        return state

    @staticmethod
    def snapshot(repo: IntentRepository, scorer: IntentScorer, validator: IntentValidator) -> dict:
        state = IntentState.build(repo, scorer, validator)
        return {
            "timestamp": state.last_updated,
            "intent_count": state.intent_count,
            "active_count": state.active_count,
            "has_active_intent": state.has_active_intent,
            "score": state.score,
            "errors": state.errors,
            "warnings": state.warnings,
            "current_intent_id": state.current_intent.intent_id if state.current_intent else None,
        }
