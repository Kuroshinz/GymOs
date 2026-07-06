"""Knowledge Evolution Query — Query helpers for knowledge evolution domain models."""

from __future__ import annotations

from shared.knowledge_evolution.domain import (
    KnowledgeConflict,
    KnowledgeEvidence,
    KnowledgeRecord,
    KnowledgeVersion,
    LifecycleStage,
)


def _parse_semver(version: str) -> tuple[int, ...]:
    """Parse a semantic version string into a comparable tuple of ints."""
    cleaned = version.lstrip("v")
    return tuple(int(p) for p in cleaned.split("."))


class KnowledgeEvolutionQuery:
    """Stateless query methods for the knowledge evolution domain."""

    @staticmethod
    def get_latest_version(
        knowledge_id: str,
        versions: list[KnowledgeVersion],
    ) -> KnowledgeVersion | None:
        """Return the latest version for a record (highest parsed semver)."""
        matching = [v for v in versions if v.knowledge_id == knowledge_id]
        if not matching:
            return None
        return max(matching, key=lambda v: _parse_semver(v.version))

    @staticmethod
    def get_historical_version(
        knowledge_id: str,
        target_version: str,
        versions: list[KnowledgeVersion],
    ) -> KnowledgeVersion | None:
        """Return a specific historical version for a record."""
        for v in versions:
            if v.knowledge_id == knowledge_id and v.version == target_version:
                return v
        return None

    @staticmethod
    def get_confidence_timeline(
        knowledge_id: str,
        versions: list[KnowledgeVersion],
    ) -> list[tuple[str, float]]:
        """Return (version, confidence_score) pairs sorted by version."""
        pairs = [
            (v.version, v.record.confidence.score)
            for v in versions
            if v.knowledge_id == knowledge_id
        ]
        pairs.sort(key=lambda p: _parse_semver(p[0]))
        return pairs

    @staticmethod
    def get_evidence_history(
        knowledge_id: str,
        records: list[KnowledgeRecord],
    ) -> list[KnowledgeEvidence]:
        """Return all evidence for a record across all versions."""
        result: list[KnowledgeEvidence] = []
        seen: set[str] = set()
        for r in records:
            if r.knowledge_id == knowledge_id:
                for e in r.evidence:
                    if e.evidence_id not in seen:
                        seen.add(e.evidence_id)
                        result.append(e)
        return result

    @staticmethod
    def get_conflict_history(
        knowledge_id: str,
        conflicts: list[KnowledgeConflict],
    ) -> list[KnowledgeConflict]:
        """Return all conflicts involving a record."""
        return [
            c
            for c in conflicts
            if c.knowledge_id_a == knowledge_id or c.knowledge_id_b == knowledge_id
        ]

    @staticmethod
    def query_by_domain(
        domain: str,
        records: list[KnowledgeRecord],
    ) -> list[KnowledgeRecord]:
        """Filter records by domain."""
        return [r for r in records if r.domain == domain]

    @staticmethod
    def query_by_confidence(
        min_score: float,
        records: list[KnowledgeRecord],
    ) -> list[KnowledgeRecord]:
        """Filter records by minimum confidence score."""
        return [r for r in records if r.confidence.score >= min_score]

    @staticmethod
    def query_by_lifecycle(
        stage: LifecycleStage,
        records: list[KnowledgeRecord],
    ) -> list[KnowledgeRecord]:
        """Filter records by lifecycle stage."""
        return [r for r in records if r.lifecycle_stage == stage]

    @staticmethod
    def query_active_records(
        records: list[KnowledgeRecord],
    ) -> list[KnowledgeRecord]:
        """Return only ACTIVE records."""
        return [r for r in records if r.lifecycle_stage == LifecycleStage.ACTIVE]
