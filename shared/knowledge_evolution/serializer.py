"""Knowledge Evolution Serializer — Full round-trip serialization for domain models."""

from __future__ import annotations

from typing import Any

from shared.knowledge_evolution.domain import (
    ConfidenceLevel,
    ConflictSeverity,
    EvidenceType,
    EvolutionConfig,
    KnowledgeConfidence,
    KnowledgeConflict,
    KnowledgeDeprecation,
    KnowledgeEvidence,
    KnowledgeEvolutionReport,
    KnowledgeLifecycle,
    KnowledgeRecord,
    KnowledgeRevision,
    KnowledgeSnapshot,
    KnowledgeVersion,
    LifecycleStage,
    RevisionReason,
)

# ── Enum helpers ──────────────────────────────────────────────────────────


def _serialize_enum(value: Any) -> str | None:
    return value.value if value is not None else None


def _deserialize_enum(cls: type, value: str | None):
    if value is None:
        return None
    return cls(value)


# ── KnowledgeEvidence ─────────────────────────────────────────────────────


class KnowledgeEvidenceSerializer:

    @staticmethod
    def serialize(obj: KnowledgeEvidence) -> dict[str, Any]:
        return {
            "evidence_id": obj.evidence_id,
            "knowledge_id": obj.knowledge_id,
            "source": obj.source,
            "evidence_type": _serialize_enum(obj.evidence_type),
            "supports": obj.supports,
            "weight": obj.weight,
            "timestamp": obj.timestamp,
            "metadata": dict(obj.metadata),
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> KnowledgeEvidence:
        return KnowledgeEvidence(
            evidence_id=data.get("evidence_id", ""),
            knowledge_id=data.get("knowledge_id", ""),
            source=data.get("source", ""),
            evidence_type=_deserialize_enum(EvidenceType, data.get("evidence_type")),
            supports=data.get("supports", True),
            weight=data.get("weight", 1.0),
            timestamp=data.get("timestamp", ""),
            metadata=dict(data.get("metadata", {})),
        )


# ── KnowledgeConfidence ───────────────────────────────────────────────────


class KnowledgeConfidenceSerializer:

    @staticmethod
    def serialize(obj: KnowledgeConfidence) -> dict[str, Any]:
        return {
            "confidence_id": obj.confidence_id,
            "knowledge_id": obj.knowledge_id,
            "level": _serialize_enum(obj.level),
            "score": obj.score,
            "support_count": obj.support_count,
            "contradiction_count": obj.contradiction_count,
            "total_evidence": obj.total_evidence,
            "freshness_score": obj.freshness_score,
            "reliability_score": obj.reliability_score,
            "last_updated": obj.last_updated,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> KnowledgeConfidence:
        return KnowledgeConfidence(
            confidence_id=data.get("confidence_id", ""),
            knowledge_id=data.get("knowledge_id", ""),
            level=_deserialize_enum(ConfidenceLevel, data.get("level")),
            score=data.get("score", 0.0),
            support_count=data.get("support_count", 0),
            contradiction_count=data.get("contradiction_count", 0),
            total_evidence=data.get("total_evidence", 0),
            freshness_score=data.get("freshness_score", 0.0),
            reliability_score=data.get("reliability_score", 0.0),
            last_updated=data.get("last_updated", ""),
        )


# ── KnowledgeConflict ─────────────────────────────────────────────────────


class KnowledgeConflictSerializer:

    @staticmethod
    def serialize(obj: KnowledgeConflict) -> dict[str, Any]:
        return {
            "conflict_id": obj.conflict_id,
            "knowledge_id_a": obj.knowledge_id_a,
            "knowledge_id_b": obj.knowledge_id_b,
            "severity": _serialize_enum(obj.severity),
            "description": obj.description,
            "resolution": obj.resolution,
            "resolved": obj.resolved,
            "resolved_at": obj.resolved_at,
            "superseded_knowledge_id": obj.superseded_knowledge_id,
            "created_at": obj.created_at,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> KnowledgeConflict:
        return KnowledgeConflict(
            conflict_id=data.get("conflict_id", ""),
            knowledge_id_a=data.get("knowledge_id_a", ""),
            knowledge_id_b=data.get("knowledge_id_b", ""),
            severity=_deserialize_enum(ConflictSeverity, data.get("severity")),
            description=data.get("description", ""),
            resolution=data.get("resolution", ""),
            resolved=data.get("resolved", False),
            resolved_at=data.get("resolved_at", ""),
            superseded_knowledge_id=data.get("superseded_knowledge_id", ""),
            created_at=data.get("created_at", ""),
        )


# ── KnowledgeDeprecation ──────────────────────────────────────────────────


class KnowledgeDeprecationSerializer:

    @staticmethod
    def serialize(obj: KnowledgeDeprecation) -> dict[str, Any]:
        return {
            "deprecation_id": obj.deprecation_id,
            "knowledge_id": obj.knowledge_id,
            "reason": obj.reason,
            "superseded_by": obj.superseded_by,
            "deprecated_at": obj.deprecated_at,
            "author": obj.author,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> KnowledgeDeprecation:
        return KnowledgeDeprecation(
            deprecation_id=data.get("deprecation_id", ""),
            knowledge_id=data.get("knowledge_id", ""),
            reason=data.get("reason", ""),
            superseded_by=data.get("superseded_by", ""),
            deprecated_at=data.get("deprecated_at", ""),
            author=data.get("author", "system"),
        )


# ── KnowledgeRevision ─────────────────────────────────────────────────────


class KnowledgeRevisionSerializer:

    @staticmethod
    def serialize(obj: KnowledgeRevision) -> dict[str, Any]:
        return {
            "revision_id": obj.revision_id,
            "knowledge_id": obj.knowledge_id,
            "version": obj.version,
            "reason": _serialize_enum(obj.reason),
            "previous_score": obj.previous_score,
            "new_score": obj.new_score,
            "confidence_change": obj.confidence_change,
            "timestamp": obj.timestamp,
            "evidence_ids": list(obj.evidence_ids),
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> KnowledgeRevision:
        return KnowledgeRevision(
            revision_id=data.get("revision_id", ""),
            knowledge_id=data.get("knowledge_id", ""),
            version=data.get("version", ""),
            reason=_deserialize_enum(RevisionReason, data.get("reason")),
            previous_score=data.get("previous_score", 0.0),
            new_score=data.get("new_score", 0.0),
            confidence_change=data.get("confidence_change", 0.0),
            timestamp=data.get("timestamp", ""),
            evidence_ids=list(data.get("evidence_ids", [])),
        )


# ── KnowledgeRecord ───────────────────────────────────────────────────────


class KnowledgeRecordSerializer:

    @staticmethod
    def serialize(obj: KnowledgeRecord) -> dict[str, Any]:
        return {
            "knowledge_id": obj.knowledge_id,
            "domain": obj.domain,
            "statement": obj.statement,
            "confidence": KnowledgeConfidenceSerializer.serialize(obj.confidence),
            "evidence": [KnowledgeEvidenceSerializer.serialize(e) for e in obj.evidence],
            "lifecycle_stage": _serialize_enum(obj.lifecycle_stage),
            "created_at": obj.created_at,
            "updated_at": obj.updated_at,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> KnowledgeRecord:
        return KnowledgeRecord(
            knowledge_id=data.get("knowledge_id", ""),
            domain=data.get("domain", ""),
            statement=data.get("statement", ""),
            confidence=KnowledgeConfidenceSerializer.deserialize(data.get("confidence", {})),
            evidence=[KnowledgeEvidenceSerializer.deserialize(e) for e in data.get("evidence", [])],
            lifecycle_stage=_deserialize_enum(LifecycleStage, data.get("lifecycle_stage")),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
        )


# ── KnowledgeVersion ──────────────────────────────────────────────────────


class KnowledgeVersionSerializer:

    @staticmethod
    def serialize(obj: KnowledgeVersion) -> dict[str, Any]:
        return {
            "version_id": obj.version_id,
            "knowledge_id": obj.knowledge_id,
            "version": obj.version,
            "parent_version": obj.parent_version,
            "record": KnowledgeRecordSerializer.serialize(obj.record),
            "created_at": obj.created_at,
            "description": obj.description,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> KnowledgeVersion:
        return KnowledgeVersion(
            version_id=data.get("version_id", ""),
            knowledge_id=data.get("knowledge_id", ""),
            version=data.get("version", ""),
            parent_version=data.get("parent_version", ""),
            record=KnowledgeRecordSerializer.deserialize(data.get("record", {})),
            created_at=data.get("created_at", ""),
            description=data.get("description", ""),
        )


# ── KnowledgeSnapshot ─────────────────────────────────────────────────────


class KnowledgeSnapshotSerializer:

    @staticmethod
    def serialize(obj: KnowledgeSnapshot) -> dict[str, Any]:
        return {
            "snapshot_id": obj.snapshot_id,
            "version": obj.version,
            "records": [KnowledgeRecordSerializer.serialize(r) for r in obj.records],
            "conflicts": [KnowledgeConflictSerializer.serialize(c) for c in obj.conflicts],
            "created_at": obj.created_at,
            "description": obj.description,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> KnowledgeSnapshot:
        return KnowledgeSnapshot(
            snapshot_id=data.get("snapshot_id", ""),
            version=data.get("version", ""),
            records=[KnowledgeRecordSerializer.deserialize(r) for r in data.get("records", [])],
            conflicts=[KnowledgeConflictSerializer.deserialize(c) for c in data.get("conflicts", [])],
            created_at=data.get("created_at", ""),
            description=data.get("description", ""),
        )


# ── KnowledgeLifecycle ────────────────────────────────────────────────────


class KnowledgeLifecycleSerializer:

    @staticmethod
    def serialize(obj: KnowledgeLifecycle) -> dict[str, Any]:
        return {
            "lifecycle_id": obj.lifecycle_id,
            "knowledge_id": obj.knowledge_id,
            "current_stage": _serialize_enum(obj.current_stage),
            "previous_stage": _serialize_enum(obj.previous_stage),
            "changed_at": obj.changed_at,
            "reason": obj.reason,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> KnowledgeLifecycle:
        return KnowledgeLifecycle(
            lifecycle_id=data.get("lifecycle_id", ""),
            knowledge_id=data.get("knowledge_id", ""),
            current_stage=_deserialize_enum(LifecycleStage, data.get("current_stage")),
            previous_stage=_deserialize_enum(LifecycleStage, data.get("previous_stage")),
            changed_at=data.get("changed_at", ""),
            reason=data.get("reason", ""),
        )


# ── KnowledgeEvolutionReport ──────────────────────────────────────────────


class KnowledgeEvolutionReportSerializer:

    @staticmethod
    def serialize(obj: KnowledgeEvolutionReport) -> dict[str, Any]:
        return {
            "report_id": obj.report_id,
            "total_records": obj.total_records,
            "active_records": obj.active_records,
            "superseded_records": obj.superseded_records,
            "deprecated_records": obj.deprecated_records,
            "total_conflicts": obj.total_conflicts,
            "resolved_conflicts": obj.resolved_conflicts,
            "unresolved_conflicts": obj.unresolved_conflicts,
            "average_confidence": obj.average_confidence,
            "average_freshness": obj.average_freshness,
            "average_reliability": obj.average_reliability,
            "total_revisions": obj.total_revisions,
            "generated_at": obj.generated_at,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> KnowledgeEvolutionReport:
        return KnowledgeEvolutionReport(
            report_id=data.get("report_id", ""),
            total_records=data.get("total_records", 0),
            active_records=data.get("active_records", 0),
            superseded_records=data.get("superseded_records", 0),
            deprecated_records=data.get("deprecated_records", 0),
            total_conflicts=data.get("total_conflicts", 0),
            resolved_conflicts=data.get("resolved_conflicts", 0),
            unresolved_conflicts=data.get("unresolved_conflicts", 0),
            average_confidence=data.get("average_confidence", 0.0),
            average_freshness=data.get("average_freshness", 0.0),
            average_reliability=data.get("average_reliability", 0.0),
            total_revisions=data.get("total_revisions", 0),
            generated_at=data.get("generated_at", ""),
        )


# ── EvolutionConfig ───────────────────────────────────────────────────────


class EvolutionConfigSerializer:

    @staticmethod
    def serialize(obj: EvolutionConfig) -> dict[str, Any]:
        return {
            "base_weight": obj.base_weight,
            "freshness_half_life_days": obj.freshness_half_life_days,
            "min_evidence_for_confidence": obj.min_evidence_for_confidence,
            "conflict_threshold": obj.conflict_threshold,
            "deprecation_grace_period_days": obj.deprecation_grace_period_days,
            "max_conflict_resolution_attempts": obj.max_conflict_resolution_attempts,
            "enable_auto_evolution": obj.enable_auto_evolution,
            "enable_freshness_decay": obj.enable_freshness_decay,
            "enable_conflict_detection": obj.enable_conflict_detection,
            "enable_deprecation": obj.enable_deprecation,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> EvolutionConfig:
        return EvolutionConfig(
            base_weight=data.get("base_weight", 1.0),
            freshness_half_life_days=data.get("freshness_half_life_days", 30.0),
            min_evidence_for_confidence=data.get("min_evidence_for_confidence", 3),
            conflict_threshold=data.get("conflict_threshold", 0.3),
            deprecation_grace_period_days=data.get("deprecation_grace_period_days", 14),
            max_conflict_resolution_attempts=data.get("max_conflict_resolution_attempts", 3),
            enable_auto_evolution=data.get("enable_auto_evolution", True),
            enable_freshness_decay=data.get("enable_freshness_decay", True),
            enable_conflict_detection=data.get("enable_conflict_detection", True),
            enable_deprecation=data.get("enable_deprecation", True),
        )
