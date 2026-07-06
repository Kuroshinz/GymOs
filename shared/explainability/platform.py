from __future__ import annotations

import logging
from typing import Any

from shared.events.event import DomainEvent
from shared.explainability.confidence import ConfidenceEngine
from shared.explainability.counterfactual import CounterfactualEngine
from shared.explainability.domain import ReportFormat
from shared.explainability.evidence import EvidenceGraph, EvidenceItem
from shared.explainability.impact_trace import ImpactTraceStore
from shared.explainability.reason_tree import ReasonTree
from shared.explainability.reports import ExplainabilityReport, ExplainabilityReportGenerator

logger = logging.getLogger("explainability.platform")


class ExplainabilityPlatform:
    def __init__(self) -> None:
        self.evidence = EvidenceGraph()
        self.reason_tree = ReasonTree()
        self.confidence = ConfidenceEngine()
        self.counterfactual = CounterfactualEngine()
        self.impact_traces = ImpactTraceStore()
        self.reports = ExplainabilityReportGenerator()

    def collect_event(self, event: DomainEvent) -> None:
        item = self.evidence.add_from_event(event)
        if item is not None:
            logger.debug("Collected evidence '%s' from event '%s'", item.evidence_id, event.event_name)

    def add_evidence(self, item: EvidenceItem) -> None:
        self.evidence.add_evidence(item)

    def explain_recommendation(self, recommendation_id: str) -> dict[str, Any]:
        chain = self.reason_tree.build_chain(recommendation_id)
        if chain is None:
            return {"error": f"Recommendation '{recommendation_id}' not found in reason tree"}

        evidence_items = []
        for node in chain.nodes:
            for eid in node.evidence_ids:
                item = self.evidence.get_evidence(eid)
                if item is not None:
                    evidence_items.append(item)

        confidence_result = self.confidence.aggregate(evidence_items)

        return {
            "chain": chain.to_dict(),
            "confidence": confidence_result.to_dict(),
            "evidence_count": len(evidence_items),
            "trace_id": chain.chain_id,
        }

    def generate_full_report(
        self,
        fmt: ReportFormat = ReportFormat.MARKDOWN,
    ) -> ExplainabilityReport:
        all_evidence = self.evidence.get_all()
        confidence_result = self.confidence.aggregate(all_evidence)
        counterfactuals = self.counterfactual.get_history()

        return self.reports.generate_full_report(
            graph=self.evidence,
            tree=self.reason_tree,
            confidence=confidence_result,
            counterfactuals=counterfactuals,
            traces=self.impact_traces,
            fmt=fmt,
        )

    def generate_evidence_report(self, fmt: ReportFormat = ReportFormat.MARKDOWN) -> ExplainabilityReport:
        return self.reports.generate_evidence_report(self.evidence, fmt)

    def generate_reason_report(self, fmt: ReportFormat = ReportFormat.MARKDOWN) -> ExplainabilityReport:
        return self.reports.generate_reason_report(self.reason_tree, fmt)

    def generate_confidence_report(self, fmt: ReportFormat = ReportFormat.MARKDOWN) -> ExplainabilityReport:
        items = self.evidence.get_all()
        result = self.confidence.aggregate(items)
        return self.reports.generate_confidence_report(result, fmt)

    def generate_counterfactual_report(self, fmt: ReportFormat = ReportFormat.MARKDOWN) -> ExplainabilityReport:
        return self.reports.generate_counterfactual_report(self.counterfactual.get_history(), fmt)

    def generate_impact_report(self, fmt: ReportFormat = ReportFormat.MARKDOWN) -> ExplainabilityReport:
        return self.reports.generate_impact_report(self.impact_traces, fmt)

    def clear_all(self) -> None:
        self.evidence.clear()
        self.reason_tree.clear()
        self.confidence.clear_results()
        self.counterfactual.clear_history()
        self.impact_traces.clear()
        self.reports.clear_reports()
        logger.info("Explainability platform cleared")
