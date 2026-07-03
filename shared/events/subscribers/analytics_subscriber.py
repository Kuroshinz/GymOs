"""Analytics subscriber — logs events for analytics and reporting."""

import logging

from shared.events.domain_events import (
    BodyWeightUpdated,
    DomainEvent,
    ExerciseCompleted,
    ExerciseKnowledgeUpdated,
    MealLogged,
    PersonalRecordUnlocked,
    ProgramActivated,
    ProgramImported,
    RecoveryScoreUpdated,
    SetCompleted,
    WorkoutCompleted,
    WorkoutStarted,
)
from shared.events.subscriber import Subscriber

logger = logging.getLogger("nexus.events.subscribers.analytics")


class AnalyticsSubscriber(Subscriber):
    """Records all domain events for analytics and reporting.

    Provides query methods for aggregating event data.
    """

    def __init__(self, bus=None):
        super().__init__(bus)
        self._event_log: list[DomainEvent] = []

    def handled_events(self) -> list[type[DomainEvent]]:
        return [
            WorkoutStarted,
            WorkoutCompleted,
            SetCompleted,
            ExerciseCompleted,
            ProgramImported,
            ProgramActivated,
            BodyWeightUpdated,
            PersonalRecordUnlocked,
            RecoveryScoreUpdated,
            MealLogged,
            ExerciseKnowledgeUpdated,
        ]

    def handle(self, event: DomainEvent) -> None:
        self._event_log.append(event)
        if isinstance(event, WorkoutCompleted):
            logger.info("Analytics: workout %.1f min, %.0f kg volume", event.duration_minutes, event.total_volume_kg)
        elif isinstance(event, PersonalRecordUnlocked):
            logger.info("Analytics: PR — %s %s", event.exercise_name, event.pr_type)
        elif isinstance(event, MealLogged):
            logger.info("Analytics: meal %.0f cal", event.calories)

    def get_workout_count(self) -> int:
        return sum(1 for e in self._event_log if isinstance(e, WorkoutCompleted))

    def get_pr_count(self) -> int:
        return sum(1 for e in self._event_log if isinstance(e, PersonalRecordUnlocked))

    def get_total_volume(self) -> float:
        return sum(e.total_volume_kg for e in self._event_log if isinstance(e, WorkoutCompleted))

    def clear_log(self) -> None:
        self._event_log.clear()
