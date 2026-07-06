from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("command_center.services.analytics")


class AnalyticsService:
    def __init__(
        self,
        db: Any = None,
        pr_engine: Any = None,
        nutrition_service: Any = None,
    ) -> None:
        self._db = db
        self._pr_engine = pr_engine
        self._nutrition_service = nutrition_service

    def fetch(self) -> dict:
        data = {
            "volume_trend": [],
            "nutrition_data": {},
            "prs": [],
            "compliance": 0.0,
        }
        try:
            if self._db:
                vol = getattr(self._db, "get_volume_by_day", lambda d: [])(28)
                data["volume_trend"] = vol
            if self._pr_engine:
                prs = getattr(self._pr_engine, "get_latest_prs", lambda l: [])(5)
                data["prs"] = prs
            if self._nutrition_service:
                summary = getattr(self._nutrition_service, "get_summary", lambda: None)()
                if summary:
                    data["nutrition_data"] = summary
        except Exception:
            logger.warning("AnalyticsService.fetch failed", exc_info=True)
        return data
