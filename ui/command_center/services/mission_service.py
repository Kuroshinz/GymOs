from __future__ import annotations

import logging
from typing import Any

from ui.command_center.models import (
    IntentData,
    MissionData,
    TrainingReadinessData,
)

logger = logging.getLogger("command_center.services.mission")


class MissionService:
    def __init__(
        self,
        db: Any = None,
        prog_mgr: Any = None,
        decision_engine: Any = None,
    ) -> None:
        self._db = db
        self._prog_mgr = prog_mgr
        self._engine = decision_engine

    def fetch(self) -> dict:
        data = {
            "mission": MissionData(),
            "intent": IntentData(),
            "training_readiness": TrainingReadinessData(),
            "adaptive_timeline": [],
            "decision_timeline_items": [],
        }
        try:
            if self._prog_mgr:
                active = getattr(self._prog_mgr, "get_active_program", lambda: None)()
                if active:
                    data["mission"] = MissionData(
                        title=getattr(active, "name", "Today's Workout"),
                        type=getattr(active, "split_style", ""),
                        estimated_duration=getattr(active, "estimated_duration", 60),
                    )
            if self._engine:
                goal = getattr(self._engine, "get_goal_progress", lambda: None)()
                if goal:
                    data["intent"] = IntentData(
                        current_goal=getattr(goal, "goal_type", ""),
                        progress_percent=getattr(goal, "progress_percent", 0.0),
                        weekly_rate=getattr(goal, "weekly_rate", 0.0),
                        adherence=getattr(goal, "adherence", 0.0),
                    )
        except Exception:
            logger.warning("MissionService.fetch failed", exc_info=True)
        return data
