from __future__ import annotations

import logging
from typing import Any

from PySide6.QtCore import QObject, Signal

from ui.command_center.models import CommandCenterData
from ui.command_center.services.command_center_service import CommandCenterService

logger = logging.getLogger("command_center.controller")


class CommandCenterController(QObject):
    data_updated = Signal(CommandCenterData)

    def __init__(
        self,
        db: Any = None,
        decision_engine: Any = None,
        pr_engine: Any = None,
        prog_mgr: Any = None,
        nutrition_service: Any = None,
        recovery_service: Any = None,
        prediction_service: Any = None,
        capability_registry: Any = None,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._service = CommandCenterService(
            db=db,
            prog_mgr=prog_mgr,
            decision_engine=decision_engine,
            pr_engine=pr_engine,
            nutrition_service=nutrition_service,
            recovery_service=recovery_service,
            prediction_service=prediction_service,
            capability_registry=capability_registry,
        )
        self._last_data: CommandCenterData = CommandCenterData()
        self._event_bus = None
        self._subscribed = False
        self._subscribe_to_events()

    @property
    def last_data(self) -> CommandCenterData:
        return self._last_data

    def _subscribe_to_events(self) -> None:
        if self._subscribed:
            return
        try:
            from shared.events.event_bus import get_event_bus

            self._event_bus = get_event_bus()
            self._event_bus.subscribe("WorkoutCompleted", self._on_workout_completed)
            self._event_bus.subscribe("RecoveryUpdated", self._on_recovery_updated)
            self._event_bus.subscribe("RecoveryScoreChanged", self._on_recovery_updated)
            self._event_bus.subscribe("PredictionUpdated", self._on_prediction_updated)
            self._event_bus.subscribe("PatternMined", self._on_knowledge_updated)
            self._event_bus.subscribe("ConfidenceUpdated", self._on_knowledge_updated)
            self._event_bus.subscribe("KnowledgeVersionPublished", self._on_knowledge_updated)
            self._event_bus.subscribe("ContextUpdated", self._on_adaptive_updated)
            self._event_bus.subscribe("RecommendationGenerated", self._on_adaptive_updated)
            self._event_bus.subscribe("DecisionApproved", self._on_adaptive_updated)
            self._event_bus.subscribe("DecisionRejected", self._on_adaptive_updated)
            self._event_bus.subscribe("PlanActivated", self._on_planning_updated)
            self._event_bus.subscribe("ProgramActivated", self._on_planning_updated)
            self._event_bus.subscribe("ProgramImported", self._on_planning_updated)
            self._subscribed = True
            logger.info("CommandCenterController subscribed to domain events")
        except Exception:
            logger.debug("Event bus not available — live updates disabled")

    def _on_workout_completed(self, event: Any) -> None:
        self.refresh_section("mission")
        self.refresh_section("analytics")

    def _on_recovery_updated(self, event: Any) -> None:
        self.refresh_section("recovery")

    def _on_prediction_updated(self, event: Any) -> None:
        self.refresh_section("prediction")

    def _on_knowledge_updated(self, event: Any) -> None:
        self.refresh_section("knowledge")

    def _on_adaptive_updated(self, event: Any) -> None:
        self.refresh_section("adaptive")

    def _on_planning_updated(self, event: Any) -> None:
        self.refresh_section("planning")

    def refresh(self) -> CommandCenterData:
        data = self._service.fetch_all()
        self._last_data = data
        self.data_updated.emit(data)
        return data

    def refresh_section(self, section: str) -> None:
        data = self._last_data
        self._service.refresh_section(data, section)
        self.data_updated.emit(data)
