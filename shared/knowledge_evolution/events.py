"""Knowledge Evolution Events — Domain events for the knowledge evolution pipeline."""

from __future__ import annotations

from dataclasses import dataclass

from shared.events.event import DomainEvent


@dataclass
class EvidenceCollected(DomainEvent):
    source: str = "knowledge_evolution"
    evidence_id: str = ""
    knowledge_id: str = ""
    supports: bool = True
    weight: float = 1.0


@dataclass
class ConfidenceUpdated(DomainEvent):
    source: str = "knowledge_evolution"
    confidence_id: str = ""
    knowledge_id: str = ""
    new_score: float = 0.0
    old_score: float = 0.0


@dataclass
class ConflictDetected(DomainEvent):
    source: str = "knowledge_evolution"
    conflict_id: str = ""
    knowledge_id_a: str = ""
    knowledge_id_b: str = ""
    severity: str = ""


@dataclass
class ConflictResolved(DomainEvent):
    source: str = "knowledge_evolution"
    conflict_id: str = ""
    resolution: str = ""
    superseded_knowledge_id: str = ""


@dataclass
class KnowledgeRevised(DomainEvent):
    source: str = "knowledge_evolution"
    revision_id: str = ""
    knowledge_id: str = ""
    version: str = ""
    reason: str = ""


@dataclass
class KnowledgeDeprecated(DomainEvent):
    source: str = "knowledge_evolution"
    deprecation_id: str = ""
    knowledge_id: str = ""
    superseded_by: str = ""


@dataclass
class KnowledgeVersionPublished(DomainEvent):
    source: str = "knowledge_evolution"
    version_id: str = ""
    knowledge_id: str = ""
    version: str = ""
    parent_version: str = ""


@dataclass
class SnapshotCreated(DomainEvent):
    source: str = "knowledge_evolution"
    snapshot_id: str = ""
    version: str = ""
    record_count: int = 0


KNOWLEDGE_EVOLUTION_EVENT_REGISTRY: dict[str, type[DomainEvent]] = {
    "EvidenceCollected": EvidenceCollected,
    "ConfidenceUpdated": ConfidenceUpdated,
    "ConflictDetected": ConflictDetected,
    "ConflictResolved": ConflictResolved,
    "KnowledgeRevised": KnowledgeRevised,
    "KnowledgeDeprecated": KnowledgeDeprecated,
    "KnowledgeVersionPublished": KnowledgeVersionPublished,
    "SnapshotCreated": SnapshotCreated,
}
