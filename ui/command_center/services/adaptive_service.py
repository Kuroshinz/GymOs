from __future__ import annotations

import logging

from ui.command_center.models import AdaptiveTimelineItem, DecisionTimelineItem

logger = logging.getLogger("command_center.services.adaptive")


class AdaptiveService:
    def __init__(self) -> None:
        pass

    def fetch(self) -> dict:
        data = {
            "adaptive_timeline": [],
            "adaptive_timeline_items": [],
            "decision_timeline": [],
            "decision_timeline_items": [],
        }
        try:
            data["adaptive_timeline_items"] = [
                AdaptiveTimelineItem(
                    date="Week 1", adaptation_type="Volume",
                    previous_value="12 sets", new_value="14 sets",
                    reason="Recovery score above threshold", status="approved",
                    score=0.85,
                ),
                AdaptiveTimelineItem(
                    date="Week 3", adaptation_type="Frequency",
                    previous_value="4x/week", new_value="5x/week",
                    reason="Compliance > 80%", status="approved",
                    score=0.78,
                ),
                AdaptiveTimelineItem(
                    date="Week 5", adaptation_type="Deload Timing",
                    previous_value="Week 8", new_value="Week 6",
                    reason="Fatigue accumulation detected", status="pending",
                    score=0.72,
                ),
            ]
            data["decision_timeline_items"] = [
                DecisionTimelineItem(
                    date="Week 1", decision_type="Volume Increase",
                    outcome="approved", confidence=0.85, impact="+15% volume",
                ),
                DecisionTimelineItem(
                    date="Week 3", decision_type="Frequency Increase",
                    outcome="approved", confidence=0.78, impact="+1 session/week",
                ),
                DecisionTimelineItem(
                    date="Week 4", decision_type="Exercise Substitution",
                    outcome="rejected", confidence=0.45, impact="Insufficient evidence",
                ),
            ]
        except Exception:
            logger.warning("AdaptiveService.fetch failed", exc_info=True)
        return data
