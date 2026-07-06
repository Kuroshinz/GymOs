"""Recovery subscriber — recomputes recovery scores on workout completion."""

import logging
from datetime import datetime

from shared.events.domain_events import (
    DomainEvent,
    RecoveryUpdated,
    WorkoutCompleted,
)
from shared.events.publisher import Publisher
from shared.events.subscriber import Subscriber

logger = logging.getLogger("nexus.events.subscribers.recovery")


class RecoverySubscriber(Subscriber):
    """Listens for WorkoutCompleted and recomputes recovery scores.

    Uses the RecoveryService to compute updated recovery metrics
    and publishes RecoveryUpdated events for cache invalidation.
    """

    def __init__(self, bus=None, recovery_service=None):
        super().__init__(bus)
        self._recovery_service = recovery_service
        self._publisher = Publisher(self._bus)

    def handled_events(self) -> list[type[DomainEvent]]:
        return [WorkoutCompleted]

    def handle(self, event: DomainEvent) -> None:
        if not isinstance(event, WorkoutCompleted):
            return
        logger.info("Recomputing recovery after workout %s", event.workout_id)
        if not self._recovery_service:
            return
        try:
            target_date = datetime.now().strftime("%Y-%m-%d")
            score = self._recovery_service.compute_and_save_score(target_date)
            self._publisher.publish(RecoveryUpdated(
                date=target_date,
                update_type="score",
                recovery_score=score.overall_score if score else 0.0,
                correlation_id=event.correlation_id,
            ))
        except Exception:
            logger.exception("Recovery computation failed for workout %s", event.workout_id)
