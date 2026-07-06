from __future__ import annotations

import logging
from typing import Any

from ui.command_center.models import PredictionSummaryData

logger = logging.getLogger("command_center.services.prediction")


class PredictionService:
    def __init__(self, prediction_service: Any = None) -> None:
        self._prediction_service = prediction_service

    def fetch(self) -> dict:
        data = {
            "prediction_summary": PredictionSummaryData(),
            "predictions": [],
        }
        try:
            if self._prediction_service:
                summary = getattr(self._prediction_service, "get_summary", lambda: None)()
                if summary:
                    preds = getattr(summary, "predictions", []) or getattr(summary, "forecasts", [])
                    items = []
                    for p in preds[:4]:
                        items.append({
                            "value": getattr(p, "predicted_value", str(getattr(p, "value", "--"))),
                            "probability": f"Probability: {getattr(p, 'probability', 0.0):.0%}",
                            "confidence": f"Confidence: {getattr(p, 'confidence', 0.0):.0%}",
                            "trend": getattr(p, "trend", "stable"),
                        })
                    data["prediction_summary"] = PredictionSummaryData(
                        predictions=items,
                        accuracy=getattr(summary, "accuracy", 0.0),
                        trend=getattr(summary, "trend", "stable"),
                    )
        except Exception:
            logger.warning("PredictionService.fetch failed", exc_info=True)
        return data
