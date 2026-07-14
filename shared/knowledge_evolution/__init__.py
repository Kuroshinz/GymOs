"""Knowledge Evolution Orchestrator — Unified facade for evidence-driven, self-evolving knowledge.

Usage:
    from shared.knowledge_evolution import KnowledgeEvolutionOrchestrator

    orch = KnowledgeEvolutionOrchestrator()
    orch.add_evidence(evidence)
    result = orch.evolve()
    print(orch.get_state())
"""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime
from typing import Any

from shared.knowledge_evolution.confidence import ConfidenceEngine
from shared.knowledge_evolution.conflict import ConflictEngine
from shared.knowledge_evolution.domain import (
    CONFIDENCE_LEVEL_LABELS,
    CONFLICT_SEVERITY_LABELS,
    EVIDENCE_TYPE_LABELS,
    LIFECYCLE_STAGE_LABELS,
    REVISION_REASON_LABELS,
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
from shared.knowledge_evolution.evolution_engine import EvolutionEngine, EvolutionResult
from shared.knowledge_evolution.metrics import EvolutionMetricsResult, KnowledgeEvolutionMetrics
from shared.knowledge_evolution.query import KnowledgeEvolutionQuery
from shared.knowledge_evolution.reports import EvolutionReportGenerator
from shared.knowledge_evolution.repository import KnowledgeEvolutionRepository
from shared.knowledge_evolution.serializer import (
    EvolutionConfigSerializer,
    KnowledgeConfidenceSerializer,
    KnowledgeConflictSerializer,
    KnowledgeDeprecationSerializer,
    KnowledgeEvidenceSerializer,
    KnowledgeEvolutionReportSerializer,
    KnowledgeLifecycleSerializer,
    KnowledgeRecordSerializer,
    KnowledgeRevisionSerializer,
    KnowledgeSnapshotSerializer,
    KnowledgeVersionSerializer,
)
from shared.knowledge_evolution.version_manager import VersionManager


class KnowledgeEvolutionOrchestrator:
    """Unified entry point for all knowledge evolution operations.

    Wraps EvolutionEngine, ConfidenceEngine, ConflictEngine, VersionManager,
    KnowledgeEvolutionMetrics, EvolutionReportGenerator, KnowledgeEvolutionRepository,
    and KnowledgeEvolutionQuery behind a single facade.
    """

    def __init__(
        self,
        config: EvolutionConfig | None = None,
    ) -> None:
        self.config = config or EvolutionConfig()
        self.engine = EvolutionEngine(config)
        self.repository = KnowledgeEvolutionRepository()
        self.report_generator = EvolutionReportGenerator()
        self.metrics_engine = KnowledgeEvolutionMetrics()
        self.query = KnowledgeEvolutionQuery()
        self._pending_evidence: dict[str, list[KnowledgeEvidence]] = {}

    # ── Evidence ────────────────────────────────────────────────────────

    def add_evidence(
        self,
        evidence: KnowledgeEvidence,
    ) -> KnowledgeEvidence:
        collected = self.engine.collect_evidence(evidence)
        kid = collected.knowledge_id
        if kid:
            self._pending_evidence.setdefault(kid, []).append(collected)
            existing = self.repository.get_record(kid)
            if existing is not None:
                updated = replace(
                    existing,
                    evidence=list(existing.evidence) + [collected],
                    updated_at=datetime.now().isoformat(),
                )
                self.repository.store_record(updated)
        return collected

    # ── Records ─────────────────────────────────────────────────────────

    def add_record(self, record: KnowledgeRecord) -> None:
        self.repository.store_record(record)

    def get_record(self, knowledge_id: str) -> KnowledgeRecord | None:
        return self.repository.get_record(knowledge_id)

    def list_records(self) -> list[KnowledgeRecord]:
        return self.repository.list_records()

    def list_records_by_domain(self, domain: str) -> list[KnowledgeRecord]:
        return self.repository.list_records_by_domain(domain)

    # ── Evolution ──────────────────────────────────────────────────────

    def evolve(
        self,
        deprecated_ids: list[str] | None = None,
    ) -> EvolutionResult:
        records = self.repository.list_records()
        result = self.engine.evolve_all(records, deprecated_ids)

        for rec in result.records:
            self.repository.store_record(rec)
        for ver in result.versions:
            self.repository.store_version(ver)
        for rev in result.revisions:
            self.repository.store_revision(rev)
        for con in result.conflicts:
            self.repository.store_conflict(con)
        for snap in result.snapshots:
            self.repository.store_snapshot(snap)

        self._pending_evidence.clear()
        return result

    # ── Query Methods ──────────────────────────────────────────────────

    def get_latest_version(
        self,
        knowledge_id: str,
    ) -> KnowledgeVersion | None:
        versions = self.repository.get_versions_for_knowledge(knowledge_id)
        return self.query.get_latest_version(knowledge_id, versions)

    def get_historical_version(
        self,
        knowledge_id: str,
        target_version: str,
    ) -> KnowledgeVersion | None:
        versions = self.repository.get_versions_for_knowledge(knowledge_id)
        return self.query.get_historical_version(knowledge_id, target_version, versions)

    def get_confidence_timeline(
        self,
        knowledge_id: str,
    ) -> list[tuple[str, float]]:
        versions = self.repository.get_versions_for_knowledge(knowledge_id)
        return self.query.get_confidence_timeline(knowledge_id, versions)

    def get_evidence_history(
        self,
        knowledge_id: str,
    ) -> list[KnowledgeEvidence]:
        records = self.repository.list_records()
        return self.query.get_evidence_history(knowledge_id, records)

    def get_conflict_history(
        self,
        knowledge_id: str,
    ) -> list[KnowledgeConflict]:
        conflicts = self.repository.list_conflicts()
        return self.query.get_conflict_history(knowledge_id, conflicts)

    def query_by_domain(
        self,
        domain: str,
    ) -> list[KnowledgeRecord]:
        return self.query.query_by_domain(domain, self.repository.list_records())

    def query_by_confidence(
        self,
        min_score: float,
    ) -> list[KnowledgeRecord]:
        return self.query.query_by_confidence(min_score, self.repository.list_records())

    def query_by_lifecycle(
        self,
        stage: LifecycleStage,
    ) -> list[KnowledgeRecord]:
        return self.query.query_by_lifecycle(stage, self.repository.list_records())

    def query_active_records(self) -> list[KnowledgeRecord]:
        return self.query.query_active_records(self.repository.list_records())

    # ── Reports ────────────────────────────────────────────────────────

    def generate_evolution_report(self) -> str:
        return self.report_generator.generate_evolution_report(
            records=self.repository.list_records(),
            conflicts=self.repository.list_conflicts(),
            versions=list(self.repository._versions.values()),
            revisions=[
                r
                for revisions in self.repository._revisions.values()
                for r in revisions
            ],
            snapshots=self.repository.list_snapshots(),
        )

    def generate_confidence_report(self) -> str:
        return self.report_generator.generate_confidence_report(
            self.repository.list_records(),
        )

    def generate_conflict_report(self) -> str:
        return self.report_generator.generate_conflict_report(
            self.repository.list_conflicts(),
        )

    def generate_lifecycle_report(self) -> str:
        return self.report_generator.generate_lifecycle_report(
            self.repository.list_records(),
        )

    # ── Metrics ────────────────────────────────────────────────────────

    def compute_metrics(self) -> EvolutionMetricsResult:
        return self.metrics_engine.compute_metrics(
            records=self.repository.list_records(),
            conflicts=self.repository.list_conflicts(),
            versions=list(self.repository._versions.values()),
        )

    # ── Version History ────────────────────────────────────────────────

    def get_version_history(
        self,
        knowledge_id: str,
    ) -> list[KnowledgeVersion]:
        return self.repository.get_versions_for_knowledge(knowledge_id)

    # ── State ──────────────────────────────────────────────────────────

    def get_state(self) -> dict[str, Any]:
        records = self.repository.list_records()
        conflicts = self.repository.list_conflicts()
        versions = list(self.repository._versions.values())
        snapshots = self.repository.list_snapshots()
        return {
            "total_records": len(records),
            "total_versions": len(versions),
            "total_conflicts": len(conflicts),
            "unresolved_conflicts": sum(1 for c in conflicts if not c.resolved),
            "total_snapshots": len(snapshots),
            "pending_evidence_count": sum(len(v) for v in self._pending_evidence.values()),
            "domains": list({r.domain for r in records}),
            "active_records": sum(1 for r in records if r.lifecycle_stage == LifecycleStage.ACTIVE),
            "deprecated_records": sum(1 for r in records if r.lifecycle_stage == LifecycleStage.DEPRECATED),
        }

    # ── Serialization ─────────────────────────────────────────────────

    def to_dict(self) -> dict[str, Any]:
        return {
            "config": EvolutionConfigSerializer.serialize(self.config),
            "records": [
                KnowledgeRecordSerializer.serialize(r)
                for r in self.repository.list_records()
            ],
            "versions": [
                KnowledgeVersionSerializer.serialize(v)
                for v in self.repository._versions.values()
            ],
            "conflicts": [
                KnowledgeConflictSerializer.serialize(c)
                for c in self.repository.list_conflicts()
            ],
            "snapshots": [
                KnowledgeSnapshotSerializer.serialize(s)
                for s in self.repository.list_snapshots()
            ],
            "revisions": {
                kid: [KnowledgeRevisionSerializer.serialize(r) for r in revs]
                for kid, revs in self.repository._revisions.items()
            },
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> KnowledgeEvolutionOrchestrator:
        config = EvolutionConfigSerializer.deserialize(data.get("config", {}))
        orch = cls(config=config)
        for r_data in data.get("records", []):
            orch.repository.store_record(KnowledgeRecordSerializer.deserialize(r_data))
        for v_data in data.get("versions", []):
            orch.repository.store_version(KnowledgeVersionSerializer.deserialize(v_data))
        for c_data in data.get("conflicts", []):
            orch.repository.store_conflict(KnowledgeConflictSerializer.deserialize(c_data))
        for s_data in data.get("snapshots", []):
            orch.repository.store_snapshot(KnowledgeSnapshotSerializer.deserialize(s_data))
        for _kid, revs_data in data.get("revisions", {}).items():
            for r_data in revs_data:
                orch.repository.store_revision(KnowledgeRevisionSerializer.deserialize(r_data))
        return orch

    # ── Clear ──────────────────────────────────────────────────────────

    def clear_all(self) -> None:
        self.repository.clear_all()
        self._pending_evidence.clear()


__all__ = (
    # Orchestrator
    "KnowledgeEvolutionOrchestrator",

    # Engine
    "EvolutionEngine",
    "EvolutionResult",

    # Confidence
    "ConfidenceEngine",

    # Conflict
    "ConflictEngine",

    # Version Manager
    "VersionManager",

    # Metrics
    "KnowledgeEvolutionMetrics",
    "EvolutionMetricsResult",

    # Reports
    "EvolutionReportGenerator",

    # Repository
    "KnowledgeEvolutionRepository",

    # Query
    "KnowledgeEvolutionQuery",

    # Domain Config
    "EvolutionConfig",

    # Domain Enums
    "EvidenceType",
    "ConfidenceLevel",
    "ConflictSeverity",
    "LifecycleStage",
    "RevisionReason",

    # Domain Label Dicts
    "EVIDENCE_TYPE_LABELS",
    "CONFIDENCE_LEVEL_LABELS",
    "CONFLICT_SEVERITY_LABELS",
    "LIFECYCLE_STAGE_LABELS",
    "REVISION_REASON_LABELS",

    # Domain Models
    "KnowledgeEvidence",
    "KnowledgeConfidence",
    "KnowledgeConflict",
    "KnowledgeDeprecation",
    "KnowledgeRecord",
    "KnowledgeRevision",
    "KnowledgeVersion",
    "KnowledgeSnapshot",
    "KnowledgeLifecycle",
    "KnowledgeEvolutionReport",

    # Serializers
    "KnowledgeEvidenceSerializer",
    "KnowledgeConfidenceSerializer",
    "KnowledgeConflictSerializer",
    "KnowledgeDeprecationSerializer",
    "KnowledgeRecordSerializer",
    "KnowledgeRevisionSerializer",
    "KnowledgeVersionSerializer",
    "KnowledgeSnapshotSerializer",
    "KnowledgeLifecycleSerializer",
    "KnowledgeEvolutionReportSerializer",
    "EvolutionConfigSerializer",
)
