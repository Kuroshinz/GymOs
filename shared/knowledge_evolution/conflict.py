"""Knowledge Evolution Conflicts — Conflict detection, resolution, and ranking."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from shared.knowledge_evolution.domain import (
    ConflictSeverity,
    EvolutionConfig,
    KnowledgeConflict,
    KnowledgeRecord,
)


class ConflictEngine:
    """Detects, resolves, and ranks knowledge conflicts."""

    def __init__(self, config: EvolutionConfig | None = None) -> None:
        self.config = config or EvolutionConfig()

    # ── Public API ───────────────────────────────────────────────────────

    def detect_conflicts(
        self, records: list[KnowledgeRecord]
    ) -> list[KnowledgeConflict]:
        """Find all conflicting record pairs within the same domain.

        Two records conflict when both have ``total_evidence >=
        min_evidence_for_confidence`` and their confidence scores lie on
        opposite sides of 0.5 (one >= 0.5, the other < 0.5).
        """
        if not self.config.enable_conflict_detection:
            return []

        grouped: dict[str, list[KnowledgeRecord]] = {}
        for r in records:
            grouped.setdefault(r.domain, []).append(r)

        conflicts: list[KnowledgeConflict] = []
        for _domain, domain_records in grouped.items():
            limit = self.config.min_evidence_for_confidence
            for i in range(len(domain_records)):
                for j in range(i + 1, len(domain_records)):
                    a = domain_records[i]
                    b = domain_records[j]
                    if not self._sides_opposed(a.confidence.score, b.confidence.score):
                        continue
                    if a.confidence.total_evidence < limit:
                        continue
                    if b.confidence.total_evidence < limit:
                        continue
                    conflicts.append(self._build_conflict(a, b))

        return conflicts

    def resolve_conflict(
        self,
        conflict: KnowledgeConflict,
        resolution: str,
        superseded_id: str,
    ) -> KnowledgeConflict:
        """Return a resolved copy of *conflict*."""
        now = datetime.now(UTC).isoformat()
        return KnowledgeConflict(
            conflict_id=conflict.conflict_id,
            knowledge_id_a=conflict.knowledge_id_a,
            knowledge_id_b=conflict.knowledge_id_b,
            severity=conflict.severity,
            description=conflict.description,
            resolution=resolution,
            resolved=True,
            resolved_at=now,
            superseded_knowledge_id=superseded_id,
            created_at=conflict.created_at,
        )

    @staticmethod
    def rank_competing_evidence(
        record_a: KnowledgeRecord,
        record_b: KnowledgeRecord,
    ) -> tuple[KnowledgeRecord, KnowledgeRecord]:
        """Rank two records by total evidence weight, returning (winner, loser)."""
        weight_a = sum(e.weight for e in record_a.evidence)
        weight_b = sum(e.weight for e in record_b.evidence)
        if weight_a >= weight_b:
            return record_a, record_b
        return record_b, record_a

    @staticmethod
    def generate_resolution_report(
        conflicts: list[KnowledgeConflict],
    ) -> str:
        """Produce a human-readable summary of all conflicts."""
        if not conflicts:
            return "No conflicts found."

        lines = ["=== Conflict Resolution Report ===", ""]
        for idx, c in enumerate(conflicts, start=1):
            status = "Resolved" if c.resolved else "Unresolved"
            lines.append(f"Conflict #{idx}: {c.conflict_id}")
            lines.append(f"  Knowledge A    : {c.knowledge_id_a}")
            lines.append(f"  Knowledge B    : {c.knowledge_id_b}")
            lines.append(f"  Severity        : {c.severity.label}")
            lines.append(f"  Status          : {status}")
            lines.append(f"  Description     : {c.description}")
            if c.resolution:
                lines.append(f"  Resolution      : {c.resolution}")
            if c.superseded_knowledge_id:
                lines.append(f"  Superseded      : {c.superseded_knowledge_id}")
            if c.resolved_at:
                lines.append(f"  Resolved At     : {c.resolved_at}")
            lines.append(f"  Created At      : {c.created_at}")
            lines.append("")
        return "\n".join(lines)

    # ── Internal helpers ────────────────────────────────────────────────

    @staticmethod
    def _sides_opposed(score_a: float, score_b: float) -> bool:
        return (score_a >= 0.5) != (score_b >= 0.5)

    def _determine_severity(self, score_diff: float) -> ConflictSeverity:
        if score_diff >= 0.6:
            return ConflictSeverity.CRITICAL
        if score_diff >= 0.4:
            return ConflictSeverity.MAJOR
        if score_diff >= 0.2:
            return ConflictSeverity.MODERATE
        return ConflictSeverity.MINOR

    def _build_conflict(
        self, a: KnowledgeRecord, b: KnowledgeRecord
    ) -> KnowledgeConflict:
        score_diff = abs(a.confidence.score - b.confidence.score)
        severity = self._determine_severity(score_diff)
        now = datetime.now(UTC).isoformat()
        return KnowledgeConflict(
            conflict_id=str(uuid4()),
            knowledge_id_a=a.knowledge_id,
            knowledge_id_b=b.knowledge_id,
            severity=severity,
            description=(
                f"Conflict between '{a.statement}' and "
                f"'{b.statement}' in domain '{a.domain}'"
            ),
            created_at=now,
        )
