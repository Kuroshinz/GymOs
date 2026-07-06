"""Evolution Report Generator — Human-readable reports for knowledge evolution."""

from __future__ import annotations

from datetime import datetime

from shared.knowledge_evolution.domain import (
    KnowledgeConflict,
    KnowledgeRecord,
    KnowledgeRevision,
    KnowledgeSnapshot,
    KnowledgeVersion,
    LifecycleStage,
)
from shared.knowledge_evolution.metrics import KnowledgeEvolutionMetrics


class EvolutionReportGenerator:
    """Generates formatted text reports for knowledge evolution data."""

    def __init__(self) -> None:
        self._metrics = KnowledgeEvolutionMetrics()

    # ── Public API ──────────────────────────────────────────────────────

    def generate_evolution_report(
        self,
        records: list[KnowledgeRecord],
        conflicts: list[KnowledgeConflict],
        versions: list[KnowledgeVersion],
        revisions: list[KnowledgeRevision],
        snapshots: list[KnowledgeSnapshot],
    ) -> str:
        """Comprehensive evolution report covering all dimensions."""
        evo = self._metrics.compute_metrics(records, conflicts, versions)
        now = datetime.now().isoformat()

        lines: list[str] = []
        lines.append("=== Evolution Report ===")
        lines.append(f"Generated: {now}")
        lines.append(f"Total snapshots: {len(snapshots)}")
        lines.append("")

        # ── Overview ──
        lines.append("--- Overview ---")
        lines.append(f"Total records      : {evo.total_records}")
        lines.append(f"Active             : {evo.active_records}")
        lines.append(f"Superseded         : {evo.superseded_records}")
        lines.append(f"Deprecated         : {evo.deprecated_records}")
        lines.append(f"Archived           : {evo.archived_records}")
        lines.append(f"Total versions     : {len(versions)}")
        lines.append(f"Total revisions    : {len(revisions)}")
        lines.append("")

        # ── Confidence ──
        lines.append("--- Confidence ---")
        lines.append(f"Average score      : {evo.average_confidence:.4f}")
        lines.append(f"Average freshness  : {evo.average_freshness:.4f}")
        lines.append(f"Average reliability: {evo.average_reliability:.4f}")
        lines.append(f"Knowledge freshness: {evo.knowledge_freshness:.4f}")
        lines.append(f"Confidence growth  : {evo.confidence_growth:.4f}")
        lines.append("")

        # ── Conflicts ──
        lines.append("--- Conflicts ---")
        lines.append(f"Total conflicts    : {evo.total_conflicts}")
        lines.append(f"Resolved           : {evo.resolved_conflicts}")
        lines.append(f"Unresolved         : {evo.unresolved_conflicts}")
        lines.append(f"Conflict rate      : {evo.conflict_rate:.4f}")
        lines.append("")

        # ── Revisions ──
        lines.append("--- Revisions ---")
        lines.append(f"Total revisions    : {len(revisions)}")
        lines.append(f"Revision frequency : {evo.revision_frequency:.4f}")
        if revisions:
            by_reason: dict[str, int] = {}
            for r in revisions:
                by_reason[r.reason.label] = by_reason.get(r.reason.label, 0) + 1
            lines.append("By reason:")
            for reason_label, count in sorted(by_reason.items()):
                lines.append(f"  {reason_label:<25}: {count}")
        lines.append("")

        # ── Stability & Volatility ──
        lines.append("--- Stability ---")
        lines.append(f"Knowledge stability : {evo.knowledge_stability:.4f}")
        lines.append(f"Knowledge volatility: {evo.knowledge_volatility:.4f}")
        lines.append("")

        # ── Snapshots ──
        lines.append("--- Snapshots ---")
        lines.append(f"Total snapshots     : {len(snapshots)}")
        if snapshots:
            lines.append("Recent snapshots:")
            for s in sorted(snapshots, key=lambda x: x.created_at, reverse=True)[:5]:
                lines.append(f"  {s.snapshot_id}: v{s.version} ({s.created_at})")
        lines.append("")

        return "\n".join(lines)

    def generate_confidence_report(
        self,
        records: list[KnowledgeRecord],
    ) -> str:
        """Confidence status for all knowledge records."""
        lines: list[str] = []
        lines.append("=== Confidence Report ===")
        lines.append(f"Total records: {len(records)}")
        lines.append("")

        if not records:
            lines.append("No records to report.")
            lines.append("")
            return "\n".join(lines)

        # ── Distribution by level ──
        lines.append("--- Distribution by Level ---")
        level_counts: dict[str, int] = {}
        for r in records:
            level_counts[r.confidence.level.label] = (
                level_counts.get(r.confidence.level.label, 0) + 1
            )
        for level_label in ["Very Low", "Low", "Medium", "High", "Very High"]:
            count = level_counts.get(level_label, 0)
            bar = "#" * count if count else ""
            lines.append(f"  {level_label:<12}: {count:>4}  {bar}")
        lines.append("")

        # ── Record details ──
        lines.append("--- Record Details ---")
        sorted_records = sorted(
            records, key=lambda r: r.confidence.score, reverse=True
        )
        header = f"{'ID':<40} {'Score':>7} {'Level':<12} {'Support':>7} {'Contra':>7} {'Fresh':>7} {'Reliab':>7}"
        lines.append(header)
        lines.append("-" * len(header))
        for r in sorted_records:
            c = r.confidence
            lines.append(
                f"{r.knowledge_id:<40} {c.score:>7.4f} {c.level.label:<12} "
                f"{c.support_count:>7} {c.contradiction_count:>7} "
                f"{c.freshness_score:>7.4f} {c.reliability_score:>7.4f}"
            )
        lines.append("")

        return "\n".join(lines)

    def generate_conflict_report(
        self,
        conflicts: list[KnowledgeConflict],
    ) -> str:
        """Conflict resolution status for all detected conflicts."""
        lines: list[str] = []
        lines.append("=== Conflict Report ===")
        lines.append(f"Total conflicts: {len(conflicts)}")
        lines.append("")

        if not conflicts:
            lines.append("No conflicts to report.")
            lines.append("")
            return "\n".join(lines)

        resolved = sum(1 for c in conflicts if c.resolved)
        unresolved = len(conflicts) - resolved
        lines.append(f"Resolved          : {resolved}")
        lines.append(f"Unresolved        : {unresolved}")
        lines.append("")

        # ── Severity distribution ──
        lines.append("--- Severity Distribution ---")
        severity_counts: dict[str, int] = {}
        unresolved_severity: dict[str, int] = {}
        for c in conflicts:
            sev = c.severity.label
            severity_counts[sev] = severity_counts.get(sev, 0) + 1
            if not c.resolved:
                unresolved_severity[sev] = unresolved_severity.get(sev, 0) + 1
        for sev_label in ["Minor", "Moderate", "Major", "Critical"]:
            total = severity_counts.get(sev_label, 0)
            unreso = unresolved_severity.get(sev_label, 0)
            bar = "#" * total if total else ""
            unresolved_tag = f" ({unreso} unresolved)" if unreso else ""
            lines.append(f"  {sev_label:<12}: {total:>4}{unresolved_tag}  {bar}")
        lines.append("")

        # ── Unresolved conflict details ──
        unresolved_conflicts = [c for c in conflicts if not c.resolved]
        if unresolved_conflicts:
            lines.append("--- Unresolved Conflicts ---")
            for idx, c in enumerate(unresolved_conflicts, start=1):
                lines.append(f"  #{idx}: {c.conflict_id}")
                lines.append(f"    A: {c.knowledge_id_a}")
                lines.append(f"    B: {c.knowledge_id_b}")
                lines.append(f"    Severity : {c.severity.label}")
                lines.append(f"    Desc     : {c.description}")
                lines.append(f"    Created  : {c.created_at}")
                lines.append("")

        # ── Resolved conflict details ──
        resolved_conflicts = [c for c in conflicts if c.resolved]
        if resolved_conflicts:
            lines.append("--- Resolved Conflicts ---")
            for idx, c in enumerate(resolved_conflicts, start=1):
                lines.append(f"  #{idx}: {c.conflict_id}")
                lines.append(f"    A: {c.knowledge_id_a}")
                lines.append(f"    B: {c.knowledge_id_b}")
                lines.append(f"    Severity  : {c.severity.label}")
                lines.append(f"    Resolution: {c.resolution}")
                if c.superseded_knowledge_id:
                    lines.append(f"    Superseded: {c.superseded_knowledge_id}")
                lines.append(f"    Resolved  : {c.resolved_at}")
                lines.append("")

        return "\n".join(lines)

    def generate_lifecycle_report(
        self,
        records: list[KnowledgeRecord],
    ) -> str:
        """Lifecycle stage distribution for all knowledge records."""
        lines: list[str] = []
        lines.append("=== Lifecycle Report ===")
        lines.append(f"Total records: {len(records)}")
        lines.append("")

        if not records:
            lines.append("No records to report.")
            lines.append("")
            return "\n".join(lines)

        # ── Stage distribution ──
        lines.append("--- Stage Distribution ---")
        stage_counts: dict[str, int] = {}
        for r in records:
            stage_counts[r.lifecycle_stage.label] = (
                stage_counts.get(r.lifecycle_stage.label, 0) + 1
            )
        for stage_label in ["Draft", "Active", "Superseded", "Deprecated", "Archived"]:
            count = stage_counts.get(stage_label, 0)
            pct = count / len(records) * 100 if records else 0.0
            bar = "#" * count if count else ""
            lines.append(f"  {stage_label:<12}: {count:>4} ({pct:>5.1f}%)  {bar}")
        lines.append("")

        # ── Records by stage ──
        for stage in LifecycleStage:
            stage_records = [
                r for r in records if r.lifecycle_stage == stage
            ]
            if not stage_records:
                continue
            lines.append(f"--- {stage.label} Records ---")
            for r in stage_records:
                confidence_tag = f"[{r.confidence.level.label}]" if r.confidence else ""
                evidence_tag = f"ev:{r.evidence_count}" if r.evidence else ""
                tags = " ".join(t for t in (confidence_tag, evidence_tag) if t)
                lines.append(
                    f"  {r.knowledge_id:<40} {r.statement[:60]:<62} {tags}"
                )
            lines.append("")

        return "\n".join(lines)
