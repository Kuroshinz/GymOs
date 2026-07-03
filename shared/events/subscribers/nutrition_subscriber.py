"""Nutrition subscriber — invalidates GymBrain cache on meal/nutrition events."""

from __future__ import annotations

import logging
from typing import Any

from shared.events.domain_events import MealLogged, NutritionUpdated, MacroTargetChanged
from shared.events.subscriber import Subscriber

logger = logging.getLogger("nexus.events.subscribers.nutrition")


class NutritionSubscriber(Subscriber):
    """Invalidates GymBrain analysis cache when nutrition data changes.

    Subscribes to:
      - MealLogged: a meal was logged
      - NutritionUpdated: bulk nutrition data changed
      - MacroTargetChanged: macro targets were updated
    """

    def __init__(self, bus: Any = None, decision_engine: Any = None) -> None:
        self._engine = decision_engine
        super().__init__(bus)

    def handled_events(self) -> list[type]:
        return [MealLogged, NutritionUpdated, MacroTargetChanged]

    def handle(self, event: Any) -> None:
        if not self._engine:
            logger.debug("No DecisionEngine wired — skipping cache invalidation")
            return

        event_name = type(event).__name__
        logger.debug("NutritionSubscriber handling %s", event_name)

        try:
            self._engine.invalidate_cache("nutrition_analysis")
            self._engine.invalidate_cache("recommendations")
            logger.debug("Invalidated nutrition analysis and recommendations cache")
        except Exception:
            logger.exception("Failed to invalidate cache on %s", event_name)
