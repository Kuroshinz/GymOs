"""Volume Engine subscriber — updates effective volume on workout completion."""

import logging

from shared.events.domain_events import DomainEvent, WorkoutCompleted
from shared.events.subscriber import Subscriber

logger = logging.getLogger("nexus.events.subscribers.volume")


class VolumeSubscriber(Subscriber):
    """Listens for WorkoutCompleted and updates volume analytics."""

    def __init__(self, bus=None, volume_analytics=None):
        super().__init__(bus)
        self._volume_analytics = volume_analytics

    def handled_events(self) -> list[type[DomainEvent]]:
        return [WorkoutCompleted]

    def handle(self, event: DomainEvent) -> None:
        if not isinstance(event, WorkoutCompleted):
            return
        logger.info("Volume update for workout %s", event.workout_id)
        if self._volume_analytics:
            try:
                self._volume_analytics.record_workout_volume(event.workout_id, event.total_volume_kg, event.exercise_count)
            except Exception:
                logger.exception("Volume update failed for workout %s", event.workout_id)
