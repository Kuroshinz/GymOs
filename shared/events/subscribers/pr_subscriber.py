"""PR Engine subscriber — detects personal records on workout completion."""

import logging

from shared.events.domain_events import (
    DomainEvent,
    PersonalRecordUnlocked,
    SetCompleted,
    WorkoutCompleted,
)
from shared.events.event_bus import get_event_bus
from shared.events.publisher import Publisher
from shared.events.subscriber import Subscriber

logger = logging.getLogger("nexus.events.subscribers.pr")


class PRSubscriber(Subscriber):
    """Listens for SetCompleted events and detects potential PRs."""

    def __init__(self, bus=None, pr_engine=None):
        super().__init__(bus)
        self._pr_engine = pr_engine
        self._publisher = Publisher(self._bus)

    def handled_events(self) -> list[type[DomainEvent]]:
        return [WorkoutCompleted]

    def handle(self, event: DomainEvent) -> None:
        if not isinstance(event, WorkoutCompleted):
            return
        logger.info("PR check triggered for workout %s", event.workout_id)
        if self._pr_engine:
            try:
                prs = self._pr_engine.detect_prs_by_workout_id(event.workout_id)
                for pr in prs:
                    self._publisher.publish(PersonalRecordUnlocked(
                        exercise_id=pr.get("exercise_id", ""),
                        exercise_name=pr.get("exercise_name", ""),
                        pr_type=pr.get("pr_type", "weight"),
                        value=pr.get("value", 0),
                        previous_value=pr.get("previous_value"),
                        correlation_id=event.correlation_id,
                    ))
            except Exception:
                logger.exception("PR detection failed for workout %s", event.workout_id)
