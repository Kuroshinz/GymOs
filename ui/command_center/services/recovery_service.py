from __future__ import annotations

import logging
from typing import Any

from ui.command_center.models import RecoveryOverviewData, TrainingReadinessData

logger = logging.getLogger("command_center.services.recovery")


class RecoveryService:
    def __init__(self, recovery_service: Any = None) -> None:
        self._recovery_service = recovery_service

    def fetch(self) -> dict:
        data = {
            "recovery_overview": RecoveryOverviewData(),
            "training_readiness": TrainingReadinessData(),
        }
        try:
            if self._recovery_service:
                snap = getattr(self._recovery_service, "get_snapshot", lambda: None)()
                if snap:
                    data["recovery_overview"] = RecoveryOverviewData(
                        score=getattr(snap, "recovery_score", 0.0),
                        level=getattr(snap, "recovery_level", ""),
                        sleep_score=getattr(snap, "sleep_score", 0.0),
                        stress_score=getattr(snap, "stress_score", 0.0),
                        fatigue_score=getattr(snap, "fatigue_score", 0.0),
                        flags=getattr(snap, "flags", []),
                    )
                    data["training_readiness"] = TrainingReadinessData(
                        readiness=getattr(snap, "readiness", "unknown"),
                        score=getattr(snap, "recovery_score", 0.0),
                        limiting_factor=getattr(snap, "limiting_factor", ""),
                    )
        except Exception:
            logger.warning("RecoveryService.fetch failed", exc_info=True)
        return data
