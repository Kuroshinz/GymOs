"""Knowledge Evolution Domain — Evidence-driven, versioned, self-evolving knowledge models.

All models are frozen dataclasses for immutability. Enums have @property label methods.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

# ── Label Constants ─────────────────────────────────────────────────────

EVIDENCE_TYPE_LABELS: dict[str, str] = {
    "optimization_result": "Optimization Result",
    "prediction_outcome": "Prediction Outcome",
    "recovery_observation": "Recovery Observation",
    "nutrition_observation": "Nutrition Observation",
    "decision_outcome": "Decision Outcome",
    "user_feedback": "User Feedback",
    "external_research": "External Research",
}

CONFIDENCE_LEVEL_LABELS: dict[str, str] = {
    "very_low": "Very Low",
    "low": "Low",
    "medium": "Medium",
    "high": "High",
    "very_high": "Very High",
}

CONFLICT_SEVERITY_LABELS: dict[str, str] = {
    "minor": "Minor",
    "moderate": "Moderate",
    "major": "Major",
    "critical": "Critical",
}

LIFECYCLE_STAGE_LABELS: dict[str, str] = {
    "draft": "Draft",
    "active": "Active",
    "superseded": "Superseded",
    "deprecated": "Deprecated",
    "archived": "Archived",
}

REVISION_REASON_LABELS: dict[str, str] = {
    "new_evidence": "New Evidence",
    "confidence_update": "Confidence Update",
    "conflict_resolution": "Conflict Resolution",
    "deprecation": "Deprecation",
    "manual_revision": "Manual Revision",
}


# ── Enums ──────────────────────────────────────────────────────────────


class EvidenceType(Enum):
    OPTIMIZATION_RESULT = "optimization_result"
    PREDICTION_OUTCOME = "prediction_outcome"
    RECOVERY_OBSERVATION = "recovery_observation"
    NUTRITION_OBSERVATION = "nutrition_observation"
    DECISION_OUTCOME = "decision_outcome"
    USER_FEEDBACK = "user_feedback"
    EXTERNAL_RESEARCH = "external_research"

    @property
    def label(self) -> str:
        return EVIDENCE_TYPE_LABELS[self.value]


class ConfidenceLevel(Enum):
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"

    @property
    def label(self) -> str:
        return CONFIDENCE_LEVEL_LABELS[self.value]

    @property
    def numeric_value(self) -> float:
        return {
            ConfidenceLevel.VERY_LOW: 0.1,
            ConfidenceLevel.LOW: 0.3,
            ConfidenceLevel.MEDIUM: 0.5,
            ConfidenceLevel.HIGH: 0.7,
            ConfidenceLevel.VERY_HIGH: 0.9,
        }[self]


class ConflictSeverity(Enum):
    MINOR = "minor"
    MODERATE = "moderate"
    MAJOR = "major"
    CRITICAL = "critical"

    @property
    def label(self) -> str:
        return CONFLICT_SEVERITY_LABELS[self.value]


class LifecycleStage(Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    SUPERSEDED = "superseded"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"

    @property
    def label(self) -> str:
        return LIFECYCLE_STAGE_LABELS[self.value]


class RevisionReason(Enum):
    NEW_EVIDENCE = "new_evidence"
    CONFIDENCE_UPDATE = "confidence_update"
    CONFLICT_RESOLUTION = "conflict_resolution"
    DEPRECATION = "deprecation"
    MANUAL_REVISION = "manual_revision"

    @property
    def label(self) -> str:
        return REVISION_REASON_LABELS[self.value]


# ── Domain Models ──────────────────────────────────────────────────────


@dataclass(frozen=True)
class KnowledgeEvidence:
    """A single piece of evidence supporting or contradicting knowledge."""
    evidence_id: str = ""
    knowledge_id: str = ""
    source: str = ""
    evidence_type: EvidenceType = EvidenceType.OPTIMIZATION_RESULT
    supports: bool = True
    weight: float = 1.0
    timestamp: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class KnowledgeConfidence:
    """Bayesian-style confidence metrics for a knowledge record."""
    confidence_id: str = ""
    knowledge_id: str = ""
    level: ConfidenceLevel = ConfidenceLevel.VERY_LOW
    score: float = 0.0
    support_count: int = 0
    contradiction_count: int = 0
    total_evidence: int = 0
    freshness_score: float = 0.0
    reliability_score: float = 0.0
    last_updated: str = ""


@dataclass(frozen=True)
class KnowledgeConflict:
    """A detected conflict between two knowledge records."""
    conflict_id: str = ""
    knowledge_id_a: str = ""
    knowledge_id_b: str = ""
    severity: ConflictSeverity = ConflictSeverity.MINOR
    description: str = ""
    resolution: str = ""
    resolved: bool = False
    resolved_at: str = ""
    superseded_knowledge_id: str = ""
    created_at: str = ""


@dataclass(frozen=True)
class KnowledgeDeprecation:
    """Records the deprecation of a knowledge record."""
    deprecation_id: str = ""
    knowledge_id: str = ""
    reason: str = ""
    superseded_by: str = ""
    deprecated_at: str = ""
    author: str = "system"


@dataclass(frozen=True)
class KnowledgeRevision:
    """An immutable revision of a knowledge record."""
    revision_id: str = ""
    knowledge_id: str = ""
    version: str = ""
    reason: RevisionReason = RevisionReason.NEW_EVIDENCE
    previous_score: float = 0.0
    new_score: float = 0.0
    confidence_change: float = 0.0
    timestamp: str = ""
    evidence_ids: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class KnowledgeRecord:
    """A single piece of knowledge with its evidence trail."""
    knowledge_id: str = ""
    domain: str = ""
    statement: str = ""
    confidence: KnowledgeConfidence = field(default_factory=KnowledgeConfidence)
    evidence: list[KnowledgeEvidence] = field(default_factory=list)
    lifecycle_stage: LifecycleStage = LifecycleStage.DRAFT
    created_at: str = ""
    updated_at: str = ""

    @property
    def is_active(self) -> bool:
        return self.lifecycle_stage == LifecycleStage.ACTIVE

    @property
    def evidence_count(self) -> int:
        return len(self.evidence)

    @property
    def support_evidence_count(self) -> int:
        return sum(1 for e in self.evidence if e.supports)

    @property
    def contradiction_evidence_count(self) -> int:
        return sum(1 for e in self.evidence if not e.supports)


@dataclass(frozen=True)
class KnowledgeVersion:
    """A versioned snapshot of a knowledge record."""
    version_id: str = ""
    knowledge_id: str = ""
    version: str = ""
    parent_version: str = ""
    record: KnowledgeRecord = field(default_factory=KnowledgeRecord)
    created_at: str = ""
    description: str = ""


@dataclass(frozen=True)
class KnowledgeSnapshot:
    """A point-in-time snapshot of all knowledge."""
    snapshot_id: str = ""
    version: str = ""
    records: list[KnowledgeRecord] = field(default_factory=list)
    conflicts: list[KnowledgeConflict] = field(default_factory=list)
    created_at: str = ""
    description: str = ""


@dataclass(frozen=True)
class KnowledgeLifecycle:
    """Tracks the lifecycle of a knowledge record."""
    lifecycle_id: str = ""
    knowledge_id: str = ""
    current_stage: LifecycleStage = LifecycleStage.DRAFT
    previous_stage: LifecycleStage = LifecycleStage.DRAFT
    changed_at: str = ""
    reason: str = ""


@dataclass(frozen=True)
class KnowledgeEvolutionReport:
    """A comprehensive evolution report for knowledge."""
    report_id: str = ""
    total_records: int = 0
    active_records: int = 0
    superseded_records: int = 0
    deprecated_records: int = 0
    total_conflicts: int = 0
    resolved_conflicts: int = 0
    unresolved_conflicts: int = 0
    average_confidence: float = 0.0
    average_freshness: float = 0.0
    average_reliability: float = 0.0
    total_revisions: int = 0
    generated_at: str = ""


# ── Configuration ──────────────────────────────────────────────────────


@dataclass(frozen=True)
class EvolutionConfig:
    base_weight: float = 1.0
    freshness_half_life_days: float = 30.0
    min_evidence_for_confidence: int = 3
    conflict_threshold: float = 0.3
    deprecation_grace_period_days: int = 14
    max_conflict_resolution_attempts: int = 3
    enable_auto_evolution: bool = True
    enable_freshness_decay: bool = True
    enable_conflict_detection: bool = True
    enable_deprecation: bool = True
