"""Optimization Knowledge History — Versioned, append-only knowledge history with audit trail."""

from __future__ import annotations

from datetime import datetime

from shared.optimization_knowledge.domain import (
    KnowledgeConfig,
    OptimizationKnowledge,
)


def _int_id(prefix: str = "hist") -> str:
    import uuid
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


class KnowledgeHistory:
    """Maintains versioned knowledge history with snapshot capabilities."""

    def __init__(self, config: KnowledgeConfig = KnowledgeConfig()) -> None:
        self.config = config
        self._entries: list[KnowledgeHistoryEntry] = []
        self._snapshots: dict[str, OptimizationKnowledge] = {}

    def record_version(
        self,
        knowledge: OptimizationKnowledge,
        reason: str = "knowledge extraction",
    ) -> KnowledgeHistoryEntry:
        entry = KnowledgeHistoryEntry(
            entry_id=_int_id(),
            version=knowledge.version,
            parent_version=knowledge.parent_version,
            reason=reason,
            timestamp=datetime.now().isoformat(),
            pattern_count=len(knowledge.patterns),
            insight_count=len(knowledge.insights),
            rule_count=len(knowledge.rules),
            recommendation_count=len(knowledge.recommendations),
        )
        self._entries.append(entry)
        return entry

    def create_snapshot(
        self,
        knowledge: OptimizationKnowledge,
    ) -> str:
        import copy
        import uuid
        snapshot_id = f"snap_{uuid.uuid4().hex[:12]}"
        self._snapshots[snapshot_id] = copy.deepcopy(knowledge)
        return snapshot_id

    def get_snapshot(self, snapshot_id: str) -> OptimizationKnowledge | None:
        return self._snapshots.get(snapshot_id)

    def list_snapshots(self) -> list[str]:
        return list(self._snapshots.keys())

    def get_history(self) -> list[KnowledgeHistoryEntry]:
        return list(self._entries)

    def get_version_history(self, version: str) -> list[KnowledgeHistoryEntry]:
        return [e for e in self._entries if e.version == version]

    def clear(self) -> None:
        self._entries.clear()
        self._snapshots.clear()

    def get_entry_count(self) -> int:
        return len(self._entries)


class KnowledgeHistoryEntry:
    """A single entry in the knowledge version history."""

    def __init__(
        self,
        entry_id: str,
        version: str,
        parent_version: str,
        reason: str,
        timestamp: str,
        pattern_count: int = 0,
        insight_count: int = 0,
        rule_count: int = 0,
        recommendation_count: int = 0,
    ) -> None:
        self.entry_id = entry_id
        self.version = version
        self.parent_version = parent_version
        self.reason = reason
        self.timestamp = timestamp
        self.pattern_count = pattern_count
        self.insight_count = insight_count
        self.rule_count = rule_count
        self.recommendation_count = recommendation_count

    def to_dict(self) -> dict:
        return {
            "entry_id": self.entry_id,
            "version": self.version,
            "parent_version": self.parent_version,
            "reason": self.reason,
            "timestamp": self.timestamp,
            "pattern_count": self.pattern_count,
            "insight_count": self.insight_count,
            "rule_count": self.rule_count,
            "recommendation_count": self.recommendation_count,
        }

    @classmethod
    def from_dict(cls, data: dict) -> KnowledgeHistoryEntry:
        return cls(
            entry_id=data["entry_id"],
            version=data["version"],
            parent_version=data["parent_version"],
            reason=data["reason"],
            timestamp=data["timestamp"],
            pattern_count=data.get("pattern_count", 0),
            insight_count=data.get("insight_count", 0),
            rule_count=data.get("rule_count", 0),
            recommendation_count=data.get("recommendation_count", 0),
        )
