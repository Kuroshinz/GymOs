"""Dashboard subscriber — updates dashboard state from events."""

import logging
from typing import Any

from shared.events.domain_events import (
    BodyWeightUpdated,
    DomainEvent,
    PersonalRecordUnlocked,
    ProgramActivated,
    RecommendationsUpdated,
    WorkoutCompleted,
)
from shared.events.subscriber import Subscriber

logger = logging.getLogger("nexus.events.subscribers.dashboard")


class DashboardSubscriber(Subscriber):
    """Listens for events that affect the dashboard and updates accordingly."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._latest_recommendations: list[dict] = []

    def handled_events(self) -> list[type[DomainEvent]]:
        return [WorkoutCompleted, PersonalRecordUnlocked, BodyWeightUpdated, ProgramActivated, RecommendationsUpdated]

    @property
    def latest_recommendations(self) -> list[dict]:
        return list(self._latest_recommendations)

    def handle(self, event: DomainEvent) -> None:
        if isinstance(event, RecommendationsUpdated):
            self._latest_recommendations = event.recommendations
            logger.info("Dashboard: %d recommendations updated via %s", event.recommendation_count, event.triggered_by)
        elif isinstance(event, WorkoutCompleted):
            logger.debug("Dashboard: workout %s completed (%d sets)", event.workout_id, event.total_sets)
        elif isinstance(event, PersonalRecordUnlocked):
            logger.info("Dashboard: new PR — %s %s: %.1f %s", event.exercise_name, event.pr_type, event.value, event.unit)
        elif isinstance(event, BodyWeightUpdated):
            logger.debug("Dashboard: body weight updated to %.1f kg", event.weight_kg)
        elif isinstance(event, ProgramActivated):
            logger.info("Dashboard: program activated — %s %s", event.program_name, event.version)
