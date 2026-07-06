"""GymBrain subscriber — triggers recommendation evaluation on domain events.

When a training-relevant event occurs (workout completed, program changed,
body weight updated), this subscriber builds a production DecisionEngine,
evaluates all rules, and publishes a RecommendationsUpdated event.
"""

from __future__ import annotations

import logging
from typing import Any

from shared.events.domain_events import (
    BodyWeightUpdated,
    ExerciseKnowledgeUpdated,
    ProgramActivated,
    RecommendationsUpdated,
    WorkoutCompleted,
)

logger = logging.getLogger("nexus.events.subscribers.gymbrain")


class GymBrainSubscriber:
    """Listens for training events and publishes GymBrain recommendations.

    On each relevant event, fresh recommendations are generated via
    DecisionEngine.evaluate_rules() and published as RecommendationsUpdated.
    """

    def __init__(self, bus: Any = None, db: Any = None) -> None:
        self._bus = bus
        self._db = db
        self._engine: Any = None
        if bus:
            bus.subscribe_class(WorkoutCompleted, self._on_workout_completed)
            bus.subscribe_class(ProgramActivated, self._on_program_changed)
            bus.subscribe_class(BodyWeightUpdated, self._on_body_weight)
            bus.subscribe_class(ExerciseKnowledgeUpdated, self._on_knowledge)

    def _ensure_engine(self) -> Any:
        if self._engine is None and self._db is not None:
            from modules.gymbrain.services.decision_engine import DecisionEngine
            self._engine = DecisionEngine.from_production(db=self._db)
        return self._engine

    def _evaluate_and_publish(self, trigger: str) -> None:
        engine = self._ensure_engine()
        if engine is None:
            logger.warning("GymBrainSubscriber: no db available, skipping evaluation")
            return
        try:
            recs = engine.evaluate_rules()
            event = RecommendationsUpdated(
                triggered_by=trigger,
                recommendation_count=len(recs),
                recommendations=[r.to_dict() if hasattr(r, "to_dict") else {"title": r.title} for r in recs],
            )
            if self._bus:
                self._bus.publish(event)
            logger.info("GymBrain: %d recommendations published (triggered by %s)", len(recs), trigger)
        except Exception:
            logger.exception("GymBrainSubscriber: recommendation evaluation failed for %s", trigger)

    def _on_workout_completed(self, event: WorkoutCompleted) -> None:
        logger.debug("GymBrain: workout %s completed — evaluating recommendations", event.workout_id)
        self._evaluate_and_publish("workout_completed")

    def _on_program_changed(self, event: ProgramActivated) -> None:
        logger.debug("GymBrain: program changed to %s — invalidating cache", event.program_name)
        engine = self._ensure_engine()
        if engine:
            engine.invalidate_cache()
        self._evaluate_and_publish("program_changed")

    def _on_body_weight(self, event: BodyWeightUpdated) -> None:
        logger.debug("GymBrain: body weight updated to %.1f kg — evaluating recommendations", event.weight_kg)
        engine = self._ensure_engine()
        if engine:
            engine.invalidate_cache("recovery_status")
        self._evaluate_and_publish("body_weight_updated")

    def _on_knowledge(self, event: ExerciseKnowledgeUpdated) -> None:
        logger.debug("GymBrain: knowledge updated for %s — invalidating cache", event.exercise_id)
        engine = self._ensure_engine()
        if engine:
            engine.invalidate_cache()
        self._evaluate_and_publish("knowledge_updated")
