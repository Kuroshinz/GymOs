from __future__ import annotations

from ui.command_center.models import (
    KnowledgeGraphData,
    OptimizationInsightData,
)


class KnowledgeService:
    def __init__(self) -> None:
        pass

    def fetch(self) -> dict:
        data = {
            "knowledge_updates": [],
            "optimization_insights": OptimizationInsightData(),
            "knowledge_graph": KnowledgeGraphData(),
        }
        data["optimization_insights"] = OptimizationInsightData(
            total_patterns=10,
            reliable_patterns=7,
            avg_confidence=0.82,
            insights=[
                {"title": "PPL-UL split yields highest adherence", "confidence": 0.88},
                {"title": "15-18 weekly sets optimizes growth", "confidence": 0.85},
                {"title": "Deload every 6 weeks prevents plateau", "confidence": 0.82},
                {"title": "8-week mesocycles outperform 4-week", "confidence": 0.79},
                {"title": "70%+ compliance correlates with progress", "confidence": 0.91},
            ],
        )
        return data
