"""Dashboard controller — orchestrates data flow and event subscriptions.

On refresh(), fetches all data via DashboardDataService and emits
data_updated with a DashboardData payload. Widgets connected to
this signal update their display.

Automatically subscribes to domain events for live updates:
  - WorkoutCompleted → refreshes workout, volume, recovery, PRs
  - BodyWeightUpdated → refreshes header, goal progress
  - RecommendationsUpdated → refreshes recommendations
  - ProgramActivated → full refresh
"""

from __future__ import annotations

import logging
from typing import Any

from PySide6.QtCore import QObject, Signal

from ui.dashboard.dashboard_models import DashboardData
from ui.dashboard.dashboard_services.dashboard_data_service import DashboardDataService

logger = logging.getLogger("nexus.dashboard.controller")


class DashboardController(QObject):
    """Orchestrates dashboard data flow.

    On refresh(), fetches all data via DashboardDataService and emits
    data_updated with a DashboardData payload. Widgets connected to
    this signal update their display.

    Automatically subscribes to domain events for live updates.
    """

    data_updated = Signal(DashboardData)

    def __init__(
        self,
        db: Any = None,
        decision_engine: Any = None,
        pr_engine: Any = None,
        prog_mgr: Any = None,
        nutrition_service: Any = None,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._db = db
        self._engine = decision_engine
        self._pr_engine = pr_engine
        self._prog_mgr = prog_mgr
        self._nutrition_service = nutrition_service
        self._data_service = DashboardDataService(
            db=db,
            decision_engine=decision_engine,
            pr_engine=pr_engine,
            prog_mgr=prog_mgr,
            nutrition_service=nutrition_service,
        )
        self._last_data: DashboardData = DashboardData()
        self._event_bus = None
        self._subscribed = False
        self._subscribe_to_events()

    @property
    def last_data(self) -> DashboardData:
        return self._last_data

    # ─── Event Subscriptions ──────────────────────────────────

    def _subscribe_to_events(self) -> None:
        """Subscribe to domain events for live dashboard updates."""
        if self._subscribed:
            return
        try:
            from shared.events.event_bus import get_event_bus

            self._event_bus = get_event_bus()
            self._event_bus.subscribe("WorkoutCompleted", self._on_workout_completed)
            self._event_bus.subscribe("BodyWeightUpdated", self._on_body_weight_updated)
            self._event_bus.subscribe("RecommendationsUpdated", self._on_recommendations_updated)
            self._event_bus.subscribe("ExerciseKnowledgeUpdated", self._on_knowledge_updated)
            self._event_bus.subscribe("ProgramActivated", self._on_program_activated)
            self._event_bus.subscribe("ProgramImported", self._on_program_activated)
            self._event_bus.subscribe("MealLogged", self._on_nutrition_updated)
            self._event_bus.subscribe("NutritionUpdated", self._on_nutrition_updated)
            self._event_bus.subscribe("RecoveryUpdated", self._on_recovery_updated)
            self._event_bus.subscribe("RecoveryScoreChanged", self._on_recovery_updated)
            self._event_bus.subscribe("ReadinessChanged", self._on_recovery_updated)
            self._subscribed = True
            logger.info("DashboardController subscribed to domain events")
        except Exception:
            logger.debug("Event bus not available — live updates disabled")

    def _on_workout_completed(self, event: Any) -> None:
        """Refresh workout, volume, recovery, and PRs after a workout."""
        try:
            data = self._last_data
            self._data_service.refresh_section(data, "workout")
            self._data_service.refresh_section(data, "recovery")
            self._data_service.refresh_section(data, "prs")
            self._data_service.refresh_section(data, "volume")
            self._data_service.refresh_section(data, "priority_muscles")
            self.data_updated.emit(data)
        except Exception:
            self.refresh()

    def _on_body_weight_updated(self, event: Any) -> None:
        """Refresh weight-related sections."""
        try:
            data = self._last_data
            self._data_service.refresh_section(data, "weight")
            self._data_service.refresh_section(data, "goal_progress")
            self.data_updated.emit(data)
        except Exception:
            self.refresh()

    def _on_recommendations_updated(self, event: Any) -> None:
        """Refresh recommendations."""
        try:
            data = self._last_data
            self._data_service.refresh_section(data, "recommendations")
            self.data_updated.emit(data)
        except Exception:
            self.refresh()

    def _on_knowledge_updated(self, event: Any) -> None:
        """Refresh when exercise knowledge is updated."""
        try:
            if self._engine:
                self._engine.invalidate_cache()
            self.refresh()
        except Exception:
            self.refresh()

    def _on_program_activated(self, event: Any) -> None:
        """Full refresh when program changes."""
        try:
            if self._engine:
                self._engine.invalidate_cache()
        except Exception:
            pass
        self.refresh()

    def _on_nutrition_updated(self, event: Any) -> None:
        """Refresh nutrition section and recommendations when nutrition data changes."""
        try:
            data = self._last_data
            self._data_service.refresh_section(data, "nutrition")
            if self._engine:
                self._engine.invalidate_cache("recommendations")
                self._data_service.refresh_section(data, "recommendations")
            self.data_updated.emit(data)
        except Exception:
            self.refresh()

    def _on_recovery_updated(self, event: Any) -> None:
        """Refresh recovery section when recovery data changes."""
        try:
            data = self._last_data
            self._data_service.refresh_section(data, "recovery")
            if self._engine:
                self._engine.invalidate_cache("recovery_status")
                self._data_service.refresh_section(data, "recommendations")
            self.data_updated.emit(data)
        except Exception:
            self.refresh()

    # ─── Data Flow ────────────────────────────────────────────

    def refresh(self) -> DashboardData:
        """Fetch fresh data and emit data_updated signal."""
        data = self._data_service.fetch_all()
        self._last_data = data
        self.data_updated.emit(data)
        return data

    def refresh_section(self, section: str) -> None:
        """Refresh a single dashboard section without full reload."""
        data = self._last_data
        self._data_service.refresh_section(data, section)
        self.data_updated.emit(data)
