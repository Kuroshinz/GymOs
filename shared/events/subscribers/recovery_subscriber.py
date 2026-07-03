"""Recovery Engine subscriber — analyses recovery on workout completion."""

import logging

from shared.events.domain_events import (
    DomainEvent,
    RecoveryScoreUpdated,
    WorkoutCompleted,
)
from shared.events.publisher import Publisher
from shared.events.subscriber import Subscriber

logger = logging.getLogger("nexus.events.subscribers.recovery")


class RecoverySubscriber(Subscriber):
    """Listens for WorkoutCompleted and updates recovery scores."""

    def __init__(self, bus=None, recovery_engine=None):
        super().__init__(bus)
        self._recovery_engine = recovery_engine
        self._publisher = Publisher(self._bus)

    def handled_events(self) -> list[type[DomainEvent]]:
        return [WorkoutCompleted]

    def handle(self, event: DomainEvent) -> None:
        if not isinstance(event, WorkoutCompleted):
            return
        logger.info("Recovery analysis for workout %s", event.workout_id)
        if self._recovery_engine:
            try:
                result = self._recovery_engine.analyse_by_workout_id(event.workout_id)
                self._publisher.publish(RecoveryScoreUpdated(
                    score=result.get("score", 100.0),
                    flags=result.get("flags", []),
                    session_id=event.workout_id,
                    correlation_id=event.correlation_id,
                ))
            except Exception:
                logger.exception("Recovery analysis failed for workout %s", event.workout_id)
