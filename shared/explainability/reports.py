from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from shared.explainability.confidence import ConfidenceResult
from shared.explainability.counterfactual import Counterfactual
from shared.explainability.domain import ReportFormat
from shared.explainability.evidence import EvidenceGraph
from shared.explainability.impact_trace import ImpactTrace, ImpactTraceStore
from shared.explainability.reason_tree import ReasonChain, ReasonTree

logger = logging.getLogger("explainability.reports")


@dataclass
class ExplainabilityReport:
    report_id: str
    generated_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    report_type: str = "full"
    content: str | dict = field(default_factory=dict)
    format: str = "markdown"

    def to_dict(self) -> dict[str, Any]:
        return {
            "report_id": self.report_id,
            "generated_at": self.generated_at,
            "report_type": self.report_type,
            "content": self.content if isinstance(self.content, dict) else {"text": self.content},
            "format": self.format,
        }


class ExplainabilityReportGenerator:
    def __init__(self) -> None:
        self._reports: list[ExplainabilityReport] = []

    def generate_evidence_report(
        self,
        graph: EvidenceGraph,
        fmt: ReportFormat = ReportFormat.MARKDOWN,
    ) -> ExplainabilityReport:
        content = graph.to_dict() if fmt == ReportFormat.JSON else self._evidence_to_markdown(graph)
        report = ExplainabilityReport(
            report_id=self._next_id(),
            report_type="evidence",
            content=content,
            format=fmt.value,
        )
        self._reports.append(report)
        return report

    def generate_reason_report(
        self,
        tree: ReasonTree,
        fmt: ReportFormat = ReportFormat.MARKDOWN,
    ) -> ExplainabilityReport:
        content = tree.to_dict() if fmt == ReportFormat.JSON else self._reason_to_markdown(tree)
        report = ExplainabilityReport(
            report_id=self._next_id(),
            report_type="reason",
            content=content,
            format=fmt.value,
        )
        self._reports.append(report)
        return report

    def generate_chain_report(
        self,
        chain: ReasonChain,
        fmt: ReportFormat = ReportFormat.MARKDOWN,
    ) -> ExplainabilityReport:
        content = chain.to_dict() if fmt == ReportFormat.JSON else self._chain_to_markdown(chain)
        report = ExplainabilityReport(
            report_id=self._next_id(),
            report_type="chain",
            content=content,
            format=fmt.value,
        )
        self._reports.append(report)
        return report

    def generate_confidence_report(
        self,
        result: ConfidenceResult,
        fmt: ReportFormat = ReportFormat.MARKDOWN,
    ) -> ExplainabilityReport:
        if fmt == ReportFormat.JSON:
            content = result.to_dict()
        else:
            content = self._confidence_to_markdown(result)
        report = ExplainabilityReport(
            report_id=self._next_id(),
            report_type="confidence",
            content=content,
            format=fmt.value,
        )
        self._reports.append(report)
        return report

    def generate_counterfactual_report(
        self,
        counterfactuals: list[Counterfactual],
        fmt: ReportFormat = ReportFormat.MARKDOWN,
    ) -> ExplainabilityReport:
        if fmt == ReportFormat.JSON:
            content = [c.to_dict() for c in counterfactuals]
        else:
            content = self._counterfactual_to_markdown(counterfactuals)
        report = ExplainabilityReport(
            report_id=self._next_id(),
            report_type="counterfactual",
            content=content,
            format=fmt.value,
        )
        self._reports.append(report)
        return report

    def generate_impact_report(
        self,
        traces: ImpactTraceStore | list[ImpactTrace],
        fmt: ReportFormat = ReportFormat.MARKDOWN,
    ) -> ExplainabilityReport:
        trace_list = traces.get_all() if isinstance(traces, ImpactTraceStore) else traces
        if fmt == ReportFormat.JSON:
            content = [t.to_dict() for t in trace_list]
        else:
            content = self._impact_to_markdown(trace_list)
        report = ExplainabilityReport(
            report_id=self._next_id(),
            report_type="impact",
            content=content,
            format=fmt.value,
        )
        self._reports.append(report)
        return report

    def generate_full_report(
        self,
        graph: EvidenceGraph,
        tree: ReasonTree,
        confidence: ConfidenceResult,
        counterfactuals: list[Counterfactual],
        traces: ImpactTraceStore | list[ImpactTrace],
        fmt: ReportFormat = ReportFormat.MARKDOWN,
    ) -> ExplainabilityReport:
        if fmt == ReportFormat.JSON:
            content = {
                "evidence": graph.to_dict(),
                "reason_tree": tree.to_dict(),
                "confidence": confidence.to_dict(),
                "counterfactuals": [c.to_dict() for c in counterfactuals],
                "impact_traces": (
                    traces.to_dict() if isinstance(traces, ImpactTraceStore)
                    else [t.to_dict() for t in traces]
                ),
            }
        else:
            parts = [
                "# Explainability Platform Report",
                "",
                f"*Generated: {datetime.now(UTC).isoformat()}*",
                "",
                "---",
                "",
                "## Evidence Summary",
                self._evidence_to_markdown(graph),
                "",
                "## Reasoning Chains",
                self._reason_to_markdown(tree),
                "",
                "## Confidence Assessment",
                self._confidence_to_markdown(confidence),
                "",
                "## Counterfactual Alternatives",
                self._counterfactual_to_markdown(counterfactuals),
                "",
                "## Impact Traces",
                self._impact_to_markdown(
                    traces.get_all() if isinstance(traces, ImpactTraceStore) else traces
                ),
            ]
            content = "\n".join(parts)
        report = ExplainabilityReport(
            report_id=self._next_id(),
            report_type="full",
            content=content,
            format=fmt.value,
        )
        self._reports.append(report)
        return report

    def get_reports(self) -> list[ExplainabilityReport]:
        return list(self._reports)

    def get_reports_by_type(self, report_type: str) -> list[ExplainabilityReport]:
        return [r for r in self._reports if r.report_type == report_type]

    def clear_reports(self) -> None:
        self._reports.clear()

    def _next_id(self) -> str:
        import uuid
        return uuid.uuid4().hex[:12]

    def _evidence_to_markdown(self, graph: EvidenceGraph) -> str:
        lines = [
            f"- **Total evidence items**: {graph.size}",
            f"- **Sources**: {', '.join(sorted(s.label for s in graph.sources))}",
            f"- **Types**: {', '.join(sorted(t.label for t in graph.types))}",
            "",
            "### Evidence Items",
            "",
        ]
        for item in graph.get_all():
            lines.append(f"- **{item.label}** ({item.source.label}, {item.evidence_type.label})")
            lines.append(f"  - Confidence: {item.confidence:.2f}")
            lines.append(f"  - ID: `{item.evidence_id}`")
            if item.supporting_ids:
                lines.append(f"  - Supports: {', '.join(f'`{sid}`' for sid in item.supporting_ids)}")
        return "\n".join(lines) if graph.size > 0 else "No evidence collected."

    def _reason_to_markdown(self, tree: ReasonTree) -> str:
        lines = [
            f"- **Total nodes**: {tree.node_count}",
            f"- **Chains**: {tree.chain_count}",
            "",
        ]
        for chain in tree.get_all_chains():
            lines.append(f"### Chain: `{chain.chain_id}`")
            lines.append(f"- Confidence: {chain.overall_confidence:.2f}")
            lines.append(f"- Complete: {chain.is_complete}")
            lines.append("")
            for node in chain.nodes:
                prefix = "  " * (_CHAIN_ORDER.get(node.node_type, 99) if hasattr(node, 'node_type') else 0)
                lines.append(f"{prefix}- **{node.node_type.label}**: {node.label}")
                if node.description:
                    lines.append(f"{prefix}  {node.description}")
                lines.append(f"{prefix}  Confidence: {node.confidence:.2f}")
            lines.append("")
        if tree.chain_count == 0:
            lines.append("No reasoning chains built yet.")
        return "\n".join(lines)

    def _chain_to_markdown(self, chain: ReasonChain) -> str:
        lines = [
            f"## Reasoning Chain: `{chain.chain_id}`",
            "",
            f"- **Confidence**: {chain.overall_confidence:.2f}",
            f"- **Complete**: {chain.is_complete}",
            f"- **Nodes**: {chain.length}",
            "",
            "### Chain Path",
            "",
        ]
        for i, node in enumerate(chain.nodes):
            arrow = " → " if i < len(chain.nodes) - 1 else ""
            lines.append(f"{i + 1}. **{node.node_type.label}**: {node.label}{arrow}")
            if node.description:
                lines.append(f"   - {node.description}")
            lines.append(f"   - Confidence: {node.confidence:.2f}")
        return "\n".join(lines)

    def _confidence_to_markdown(self, result: ConfidenceResult) -> str:
        if not result.breakdown:
            return "No confidence data available."
        bd = result.breakdown
        lines = [
            f"### Overall Confidence: {result.overall:.2%}",
            "",
            "| Component | Score |",
            "|-----------|-------|",
            f"| Prediction | {bd.prediction:.2%} |",
            f"| Knowledge Quality | {bd.knowledge_quality:.2%} |",
            f"| Recovery Quality | {bd.recovery_quality:.2%} |",
            f"| Planning Certainty | {bd.planning_certainty:.2%} |",
            f"| Evidence Strength | {bd.evidence_strength:.2%} |",
            "",
            f"- **Strongest**: {bd.strongest[0]} ({bd.strongest[1]:.2%})",
            f"- **Weakest**: {bd.weakest[0]} ({bd.weakest[1]:.2%})",
            "",
            f"- Evidence count: {result.evidence_count}",
            f"- Source count: {result.source_count}",
        ]
        return "\n".join(lines)

    def _counterfactual_to_markdown(self, counterfactuals: list[Counterfactual]) -> str:
        if not counterfactuals:
            return "No counterfactuals generated."
        lines = [
            "| Action | Current | Proposed | Risk | Confidence | Safe |",
            "|--------|---------|----------|------|------------|------|",
        ]
        for cf in counterfactuals:
            safe = "✓" if cf.is_safe else "✗"
            lines.append(
                f"| {cf.action.label} | {cf.current_value or '—'} | "
                f"{cf.proposed_value or '—'} | {cf.risk:.0%} | "
                f"{cf.confidence:.0%} | {safe} |"
            )
        lines.append("")
        for cf in counterfactuals:
            lines.append(f"### {cf.action.label}")
            lines.append(f"- **Description**: {cf.description}")
            lines.append(f"- **Expected outcome**: {cf.expected_outcome}")
            lines.append(f"- **Risk**: {cf.risk_label} ({cf.risk:.0%})")
            lines.append(f"- **Confidence**: {cf.confidence:.0%}")
            lines.append("")
        return "\n".join(lines)

    def _impact_to_markdown(self, traces: list[ImpactTrace]) -> str:
        if not traces:
            return "No impact traces recorded."
        lines = [f"Total traces: {len(traces)}", ""]
        for trace in traces:
            lines.append(f"### Trace: `{trace.trace_id}`")
            nodes_str = " → ".join(f"**{n.node_type.label}**: {n.label}" for n in trace.nodes)
            lines.append(nodes_str)
            lines.append("")
        return "\n".join(lines)


_CHAIN_ORDER = {
    "intent": 0, "knowledge": 1, "recovery": 2,
    "prediction": 3, "decision": 4, "recommendation": 5,
}
