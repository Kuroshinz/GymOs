from __future__ import annotations

import logging
from typing import Any

from ui.command_center.models import CommandCenterData
from ui.command_center.services.adaptive_service import AdaptiveService
from ui.command_center.services.analytics_service import AnalyticsService
from ui.command_center.services.knowledge_service import KnowledgeService
from ui.command_center.services.mission_service import MissionService
from ui.command_center.services.planning_service import PlanningService
from ui.command_center.services.prediction_service import PredictionService
from ui.command_center.services.recovery_service import RecoveryService
from ui.command_center.services.system_service import SystemService

logger = logging.getLogger("command_center.service")


class CommandCenterService:
    def __init__(
        self,
        db: Any = None,
        prog_mgr: Any = None,
        decision_engine: Any = None,
        pr_engine: Any = None,
        nutrition_service: Any = None,
        recovery_service: Any = None,
        prediction_service: Any = None,
        capability_registry: Any = None,
    ) -> None:
        self._mission = MissionService(db=db, prog_mgr=prog_mgr, decision_engine=decision_engine)
        self._planning = PlanningService(db=db, prog_mgr=prog_mgr)
        self._prediction = PredictionService(prediction_service=prediction_service)
        self._recovery = RecoveryService(recovery_service=recovery_service)
        self._knowledge = KnowledgeService()
        self._adaptive = AdaptiveService()
        self._analytics = AnalyticsService(db=db, pr_engine=pr_engine, nutrition_service=nutrition_service)
        self._system = SystemService(capability_registry=capability_registry)

    def fetch_all(self) -> CommandCenterData:
        data = CommandCenterData()
        try:
            data.mission = self._mission.fetch()
        except Exception:
            logger.exception("Command Center: mission service failed")
        try:
            data.planning = self._planning.fetch()
        except Exception:
            logger.exception("Command Center: planning service failed")
        try:
            data.prediction = self._prediction.fetch()
        except Exception:
            logger.exception("Command Center: prediction service failed")
        try:
            data.recovery = self._recovery.fetch()
        except Exception:
            logger.exception("Command Center: recovery service failed")
        try:
            data.knowledge = self._knowledge.fetch()
        except Exception:
            logger.exception("Command Center: knowledge service failed")
        try:
            data.adaptive = self._adaptive.fetch()
        except Exception:
            logger.exception("Command Center: adaptive service failed")
        try:
            data.analytics = self._analytics.fetch()
        except Exception:
            logger.exception("Command Center: analytics service failed")
        try:
            data.system = self._system.fetch()
        except Exception:
            logger.exception("Command Center: system service failed")
        return data

    def refresh_section(self, data: CommandCenterData, section: str) -> None:
        try:
            if section == "mission":
                data.mission = self._mission.fetch()
            elif section == "planning":
                data.planning = self._planning.fetch()
            elif section == "prediction":
                data.prediction = self._prediction.fetch()
            elif section == "recovery":
                data.recovery = self._recovery.fetch()
            elif section == "knowledge":
                data.knowledge = self._knowledge.fetch()
            elif section == "adaptive":
                data.adaptive = self._adaptive.fetch()
            elif section == "analytics":
                data.analytics = self._analytics.fetch()
            elif section == "system":
                data.system = self._system.fetch()
        except Exception:
            logger.exception("Command Center: refresh section %s failed", section)
