"""Evolution Engine — Orchestrates the knowledge evolution pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime
from uuid import uuid4

from shared.knowledge_evolution.confidence import ConfidenceEngine
from shared.knowledge_evolution.conflict import ConflictEngine
from shared.knowledge_evolution.domain import (
    EvolutionConfig,
    KnowledgeConfidence,
    KnowledgeConflict,
    KnowledgeEvidence,
    KnowledgeRecord,
    KnowledgeRevision,
    KnowledgeSnapshot,
    KnowledgeVersion,
    LifecycleStage,
    RevisionReason,
)
from shared.knowledge_evolution.version_manager import VersionManager


def _generate_id() -> str:
    return uuid4().hex


@dataclass(frozen=True)
class EvolutionResult:
    records: list[KnowledgeRecord] = field(default_factory=list)
    versions: list[KnowledgeVersion] = field(default_factory=list)
    revisions: list[KnowledgeRevision] = field(default_factory=list)
    conflicts: list[KnowledgeConflict] = field(default_factory=list)
    snapshots: list[KnowledgeSnapshot] = field(default_factory=list)
    timestamp: str = ""


class EvolutionEngine:
    def __init__(self, config: EvolutionConfig | None = None):
        self.config = config or EvolutionConfig()
        self.confidence_engine = ConfidenceEngine(config=self.config)
        self.conflict_engine = ConflictEngine(config=self.config)
        self.version_manager = VersionManager()

    def collect_evidence(self, evidence: KnowledgeEvidence) -> KnowledgeEvidence:
        eid = evidence.evidence_id or _generate_id()
        ts = evidence.timestamp or datetime.now().isoformat()
        return replace(evidence, evidence_id=eid, timestamp=ts)

    def aggregate_evidence(
        self, knowledge_record: KnowledgeRecord
    ) -> KnowledgeRecord:
        return knowledge_record

    def recalculate_confidence(
        self, knowledge_record: KnowledgeRecord
    ) -> tuple[KnowledgeRecord, KnowledgeConfidence]:
        confidence = self.confidence_engine.compute_confidence(
            knowledge_record.knowledge_id,
            knowledge_record.evidence,
        )
        updated = replace(
            knowledge_record,
            confidence=confidence,
            updated_at=datetime.now().isoformat(),
        )
        return updated, confidence

    def detect_conflicts(
        self, records: list[KnowledgeRecord]
    ) -> list[KnowledgeConflict]:
        return self.conflict_engine.detect_conflicts(records)

    def resolve_conflicts(
        self,
        records: list[KnowledgeRecord],
        conflicts: list[KnowledgeConflict],
    ) -> tuple[list[KnowledgeRecord], list[KnowledgeConflict]]:
        record_map = {r.knowledge_id: r for r in records}
        output_records = list(records)
        resolved: list[KnowledgeConflict] = []

        for conflict in conflicts:
            if conflict.resolved:
                resolved.append(conflict)
                continue

            rec_a = record_map.get(conflict.knowledge_id_a)
            rec_b = record_map.get(conflict.knowledge_id_b)
            if rec_a is None or rec_b is None:
                resolved.append(conflict)
                continue

            superseded_id = (
                rec_a.knowledge_id
                if rec_a.confidence.score <= rec_b.confidence.score
                else rec_b.knowledge_id
            )

            resolved_conflict = replace(
                conflict,
                resolved=True,
                resolved_at=datetime.now().isoformat(),
                superseded_knowledge_id=superseded_id,
            )
            resolved.append(resolved_conflict)

            for i, rec in enumerate(output_records):
                if rec.knowledge_id == superseded_id:
                    output_records[i] = replace(
                        rec,
                        lifecycle_stage=LifecycleStage.SUPERSEDED,
                        updated_at=datetime.now().isoformat(),
                    )

        return output_records, resolved

    def create_revision(
        self,
        knowledge_record: KnowledgeRecord,
        reason: RevisionReason,
    ) -> KnowledgeRevision:
        return KnowledgeRevision(
            revision_id=_generate_id(),
            knowledge_id=knowledge_record.knowledge_id,
            version=knowledge_record.updated_at or datetime.now().isoformat(),
            reason=reason,
            previous_score=knowledge_record.confidence.score,
            new_score=knowledge_record.confidence.score,
            confidence_change=0.0,
            timestamp=datetime.now().isoformat(),
            evidence_ids=[e.evidence_id for e in knowledge_record.evidence],
        )

    def deprecate_obsolete(
        self,
        records: list[KnowledgeRecord],
        deprecated_ids: list[str],
    ) -> list[KnowledgeRecord]:
        result = list(records)
        now = datetime.now().isoformat()
        for i, rec in enumerate(result):
            if rec.knowledge_id in deprecated_ids:
                result[i] = replace(
                    rec,
                    lifecycle_stage=LifecycleStage.DEPRECATED,
                    updated_at=now,
                )
        return result

    def publish_version(
        self,
        knowledge_record: KnowledgeRecord,
        parent_version: str,
    ) -> tuple[KnowledgeVersion, KnowledgeRecord]:
        version = self.version_manager.create_version(knowledge_record, parent_version)
        return version, knowledge_record

    def evolve_all(
        self,
        records: list[KnowledgeRecord],
        deprecated_ids: list[str] | None = None,
    ) -> EvolutionResult:
        deprecated_ids = deprecated_ids or []
        timestamp = datetime.now().isoformat()

        aggregated = [self.aggregate_evidence(r) for r in records]

        updated: list[KnowledgeRecord] = []
        for rec in aggregated:
            u, _ = self.recalculate_confidence(rec)
            updated.append(u)

        conflicts = self.detect_conflicts(updated)
        updated, resolved_conflicts = self.resolve_conflicts(updated, conflicts)
        updated = self.deprecate_obsolete(updated, deprecated_ids)

        revisions: list[KnowledgeRevision] = []
        for orig, curr in zip(aggregated, updated, strict=True):
            if orig.confidence.score != curr.confidence.score:
                revisions.append(
                    self.create_revision(curr, RevisionReason.CONFIDENCE_UPDATE)
                )
            if orig.lifecycle_stage != curr.lifecycle_stage:
                if curr.lifecycle_stage == LifecycleStage.DEPRECATED:
                    revisions.append(
                        self.create_revision(curr, RevisionReason.DEPRECATION)
                    )
                elif curr.lifecycle_stage == LifecycleStage.SUPERSEDED:
                    revisions.append(
                        self.create_revision(curr, RevisionReason.CONFLICT_RESOLUTION)
                    )

        versions: list[KnowledgeVersion] = []
        for rec in updated:
            v, _ = self.publish_version(rec, "")
            versions.append(v)

        snapshot = KnowledgeSnapshot(
            snapshot_id=_generate_id(),
            version=timestamp,
            records=updated,
            conflicts=resolved_conflicts,
            created_at=timestamp,
            description="Auto-evolution snapshot",
        )

        return EvolutionResult(
            records=updated,
            versions=versions,
            revisions=revisions,
            conflicts=resolved_conflicts,
            snapshots=[snapshot],
            timestamp=timestamp,
        )
