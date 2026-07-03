from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any
from uuid import uuid4


class RecommendationCategory(Enum):
    TRAINING = "training"
    NUTRITION = "nutrition"
    RECOVERY = "recovery"
    PROGRESSION = "progression"
    TECHNIQUE = "technique"
    EXERCISE_ORDER = "exercise_order"
    DELOAD = "deload"
    PROGRAM_ADJUSTMENT = "program_adjustment"
    CONSISTENCY = "consistency"
    EXERCISE_SELECTION = "exercise_selection"
    VOLUME = "volume"
    FREQUENCY = "frequency"


class RecommendationPriority(Enum):
    CRITICAL = 90
    HIGH = 70
    MEDIUM = 50
    LOW = 30
    INFO = 10


@dataclass
class RecommendationAction:
    type: str
    params: dict[str, Any] = field(default_factory=dict)
    display: str = ""


@dataclass
class RecommendationEvidence:
    data_points: list[str] = field(default_factory=list)
    rule_name: str = ""
    confidence: float = 0.0


@dataclass
class Recommendation:
    id: str = field(default_factory=lambda: uuid4().hex[:12])
    category: RecommendationCategory = RecommendationCategory.TRAINING
    priority: int = RecommendationPriority.MEDIUM.value
    title: str = ""
    description: str = ""
    reason: str = ""
    confidence: float = 0.0
    evidence: list[str] = field(default_factory=list)
    action: RecommendationAction | None = None
    rule_name: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: datetime | None = None

    def __post_init__(self: Recommendation) -> None:
        if self.expires_at is None:
            self.expires_at = self.created_at + timedelta(days=7)

    def is_expired(self: Recommendation) -> bool:
        return datetime.now() > self.expires_at if self.expires_at else False

    def to_dict(self: Recommendation) -> dict[str, Any]:
        return {
            "id": self.id,
            "category": self.category.value,
            "priority": self.priority,
            "title": self.title,
            "description": self.description,
            "reason": self.reason,
            "confidence": self.confidence,
            "evidence": self.evidence,
            "action": {
                "type": self.action.type,
                "params": self.action.params,
                "display": self.action.display,
            } if self.action else None,
            "rule_name": self.rule_name,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
        }
