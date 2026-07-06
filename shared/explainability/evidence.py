from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from shared.events.event import DomainEvent
from shared.explainability.domain import EvidenceSource, EvidenceType

logger = logging.getLogger("explainability.evidence")


@dataclass
class EvidenceItem:
    evidence_id: str
    source: EvidenceSource
    evidence_type: EvidenceType
    label: str
    value: Any = None
    confidence: float = 0.0
    supporting_ids: list[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    metadata: dict = field(default_factory=dict)


class EvidenceGraph:
    def __init__(self, max_items: int = 10000) -> None:
        self._items: dict[str, EvidenceItem] = {}
        self._max_items = max_items

    def add_evidence(self, item: EvidenceItem) -> None:
        self._items[item.evidence_id] = item
        if len(self._items) > self._max_items:
            oldest = min(self._items.keys(), key=lambda k: self._items[k].timestamp)
            self._items.pop(oldest, None)

    def add_from_event(self, event: DomainEvent) -> EvidenceItem | None:
        source = self._detect_source(event)
        if source is None:
            return None
        evidence_type = self._detect_type(event)
        item = EvidenceItem(
            evidence_id=uuid.uuid4().hex[:12],
            source=source,
            evidence_type=evidence_type,
            label=event.event_name or event.__class__.__name__,
            value=event.to_dict(),
            timestamp=event.timestamp.isoformat() if hasattr(event.timestamp, "isoformat") else str(event.timestamp),
            metadata={"correlation_id": event.correlation_id, "event_id": event.event_id},
        )
        self._items[item.evidence_id] = item
        if len(self._items) > self._max_items:
            oldest = min(self._items.keys(), key=lambda k: self._items[k].timestamp)
            self._items.pop(oldest, None)
        return item

    def _detect_source(self, event: DomainEvent) -> EvidenceSource | None:
        name = event.event_name or ""
        if any(k in name for k in ("decision", "recommendation", "rule")):
            return EvidenceSource.DECISION_ENGINE
        if any(k in name for k in ("prediction", "forecast", "plateau", "eta")):
            return EvidenceSource.PREDICTION
        if any(k in name for k in ("recovery", "readiness", "deload", "fatigue")):
            return EvidenceSource.RECOVERY
        if any(k in name for k in ("plan", "macrocycle", "mesocycle", "session", "allocation")):
            return EvidenceSource.PLANNING
        if any(k in name for k in ("intent", "goal", "preference")):
            return EvidenceSource.INTENT
        if any(k in name for k in ("knowledge", "evidence", "confidence", "conflict", "version")):
            return EvidenceSource.KNOWLEDGE
        if any(k in name for k in ("adaptive", "adaptation", "scenario", "strategy")):
            return EvidenceSource.ADAPTIVE
        if any(k in name for k in ("optimization", "candidate", "generation", "experience", "pattern", "insight")):
            return EvidenceSource.OPTIMIZATION
        return None

    def _detect_type(self, event: DomainEvent) -> EvidenceType:
        name = event.event_name or ""
        if any(k in name for k in ("recommendation", "suggestion")):
            return EvidenceType.RECOMMENDATION
        if any(k in name for k in ("prediction", "forecast", "eta")):
            return EvidenceType.PREDICTION
        if any(k in name for k in ("score", "rating", "metric")):
            return EvidenceType.SCORE
        if any(k in name for k in ("analysis", "review", "report")):
            return EvidenceType.ANALYSIS
        if any(k in name for k in ("constraint", "violation")):
            return EvidenceType.CONSTRAINT
        if any(k in name for k in ("rule", "policy")):
            return EvidenceType.RULE
        if any(k in name for k in ("pattern",)):
            return EvidenceType.PATTERN
        if any(k in name for k in ("insight",)):
            return EvidenceType.INSIGHT
        if any(k in name for k in ("decision", "approved", "rejected", "rollback")):
            return EvidenceType.DECISION
        if any(k in name for k in ("goal", "intent")):
            return EvidenceType.GOAL
        return EvidenceType.ANALYSIS

    def get_evidence(self, evidence_id: str) -> EvidenceItem | None:
        return self._items.get(evidence_id)

    def query(
        self,
        source: EvidenceSource | None = None,
        evidence_type: EvidenceType | None = None,
        min_confidence: float = 0.0,
    ) -> list[EvidenceItem]:
        result = list(self._items.values())
        if source is not None:
            result = [i for i in result if i.source == source]
        if evidence_type is not None:
            result = [i for i in result if i.evidence_type == evidence_type]
        if min_confidence > 0.0:
            result = [i for i in result if i.confidence >= min_confidence]
        return result

    def get_all(self) -> list[EvidenceItem]:
        return list(self._items.values())

    def get_by_source(self, source: EvidenceSource) -> list[EvidenceItem]:
        return [i for i in self._items.values() if i.source == source]

    def get_by_type(self, evidence_type: EvidenceType) -> list[EvidenceItem]:
        return [i for i in self._items.values() if i.evidence_type == evidence_type]

    def clear(self) -> None:
        self._items.clear()

    @property
    def size(self) -> int:
        return len(self._items)

    @property
    def sources(self) -> set[EvidenceSource]:
        return {i.source for i in self._items.values()}

    @property
    def types(self) -> set[EvidenceType]:
        return {i.evidence_type for i in self._items.values()}

    def to_dict(self) -> dict[str, Any]:
        return {
            "size": self.size,
            "sources": [s.value for s in self.sources],
            "types": [t.value for t in self.types],
            "items": [
                {
                    "evidence_id": i.evidence_id,
                    "source": i.source.value,
                    "evidence_type": i.evidence_type.value,
                    "label": i.label,
                    "value": i.value,
                    "confidence": i.confidence,
                    "supporting_ids": i.supporting_ids,
                    "timestamp": i.timestamp,
                    "metadata": i.metadata,
                }
                for i in self._items.values()
            ],
        }
