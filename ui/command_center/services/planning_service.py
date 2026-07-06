from __future__ import annotations

import logging
from typing import Any

from ui.command_center.models import (
    CurrentMesocycleData,
    WeeklyReviewData,
)

logger = logging.getLogger("command_center.services.planning")


class PlanningService:
    def __init__(self, db: Any = None, prog_mgr: Any = None) -> None:
        self._db = db
        self._prog_mgr = prog_mgr

    def fetch(self) -> dict:
        data = {
            "current_mesocycle": CurrentMesocycleData(),
            "weekly_review": WeeklyReviewData(),
        }
        try:
            if self._prog_mgr:
                active = getattr(self._prog_mgr, "get_active_program", lambda: None)()
                if active:
                    mesos = getattr(active, "mesocycles", [])
                    if mesos:
                        current = mesos[0]
                        data["current_mesocycle"] = CurrentMesocycleData(
                            name=getattr(current, "name", "Mesocycle"),
                            goal=getattr(current, "goal", ""),
                            phase=getattr(current, "phase", ""),
                            week=getattr(current, "current_week", 1),
                            total_weeks=getattr(current, "week_count", 4),
                            focus=getattr(current, "focus", ""),
                        )
            if self._db:
                vol = getattr(self._db, "get_volume_by_day", lambda d: [])(28)
                if vol:
                    data["weekly_review"] = WeeklyReviewData(
                        total_volume=sum(v.get("volume", 0) for v in vol[-7:]),
                        sessions_completed=len(vol),
                    )
        except Exception:
            logger.warning("PlanningService.fetch failed", exc_info=True)
        return data
