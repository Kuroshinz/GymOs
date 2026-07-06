"""Knowledge Evolution Repository — Append-only, immutable, versioned knowledge store."""

from __future__ import annotations

from shared.knowledge_evolution.domain import (
    KnowledgeConflict,
    KnowledgeRecord,
    KnowledgeRevision,
    KnowledgeSnapshot,
    KnowledgeVersion,
)


class KnowledgeEvolutionRepository:
    """Append-only, immutable, versioned repository for knowledge evolution.

    Records are stored by ``knowledge_id`` (latest version overwrites). All
    other entities are append-only — once written they are never mutated.
    """

    def __init__(self) -> None:
        self._records: dict[str, KnowledgeRecord] = {}
        self._versions: dict[str, KnowledgeVersion] = {}
        self._conflicts: dict[str, KnowledgeConflict] = {}
        self._revisions: dict[str, list[KnowledgeRevision]] = {}
        self._snapshots: dict[str, KnowledgeSnapshot] = {}

    # ── Records ────────────────────────────────────────────────────────

    def store_record(self, record: KnowledgeRecord) -> None:
        self._records[record.knowledge_id] = record

    def get_record(self, knowledge_id: str) -> KnowledgeRecord | None:
        return self._records.get(knowledge_id)

    def list_records(self) -> list[KnowledgeRecord]:
        return list(self._records.values())

    def list_records_by_domain(self, domain: str) -> list[KnowledgeRecord]:
        return [r for r in self._records.values() if r.domain == domain]

    # ── Versions ───────────────────────────────────────────────────────

    def store_version(self, version: KnowledgeVersion) -> None:
        self._versions[version.version_id] = version

    def get_version(self, version_id: str) -> KnowledgeVersion | None:
        return self._versions.get(version_id)

    def get_versions_for_knowledge(
        self, knowledge_id: str
    ) -> list[KnowledgeVersion]:
        return [
            v
            for v in self._versions.values()
            if v.knowledge_id == knowledge_id
        ]

    # ── Conflicts ──────────────────────────────────────────────────────

    def store_conflict(self, conflict: KnowledgeConflict) -> None:
        self._conflicts[conflict.conflict_id] = conflict

    def get_conflict(self, conflict_id: str) -> KnowledgeConflict | None:
        return self._conflicts.get(conflict_id)

    def list_conflicts(self) -> list[KnowledgeConflict]:
        return list(self._conflicts.values())

    def list_unresolved_conflicts(self) -> list[KnowledgeConflict]:
        return [c for c in self._conflicts.values() if not c.resolved]

    # ── Revisions ──────────────────────────────────────────────────────

    def store_revision(self, revision: KnowledgeRevision) -> None:
        self._revisions.setdefault(revision.knowledge_id, []).append(revision)

    def get_revisions_for_knowledge(
        self, knowledge_id: str
    ) -> list[KnowledgeRevision]:
        return list(self._revisions.get(knowledge_id, []))

    # ── Snapshots ──────────────────────────────────────────────────────

    def store_snapshot(self, snapshot: KnowledgeSnapshot) -> None:
        self._snapshots[snapshot.snapshot_id] = snapshot

    def get_snapshot(self, snapshot_id: str) -> KnowledgeSnapshot | None:
        return self._snapshots.get(snapshot_id)

    def list_snapshots(self) -> list[KnowledgeSnapshot]:
        return list(self._snapshots.values())

    # ── Lifecycle ──────────────────────────────────────────────────────

    def clear_all(self) -> None:
        self._records.clear()
        self._versions.clear()
        self._conflicts.clear()
        self._revisions.clear()
        self._snapshots.clear()
