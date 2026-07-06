"""Drift Analyzer — detects and quantifies product drift across multiple dimensions.

Drift types:
- Architecture Drift: variance in architecture health across capabilities
- Documentation Drift: gaps between documentation scores and targets
- Capability Drift: capabilities falling behind their target maturity
- Knowledge Drift: gaps in knowledge coverage
- RFC Drift: RFCs not progressing as expected
"""

from __future__ import annotations

from dataclasses import dataclass

from shared.capabilities import registry as _cap_registry
from shared.capabilities.enums import CapabilityMaturity
from shared.capabilities.health import calculate_health, score_documentation
from shared.kernel.kernel import RfcStatus
from shared.kernel.kernel_state import create_default_state


@dataclass(frozen=True)
class DriftReport:
    """Complete drift analysis for the product."""

    architecture_drift: float = 0.0    # 0-100
    documentation_drift: float = 0.0   # 0-100
    capability_drift: float = 0.0      # 0-100
    knowledge_drift: float = 0.0       # 0-100
    rfc_drift: float = 0.0             # 0-100
    overall_drift: float = 0.0         # 0-100
    details: tuple[str, ...] = ()


class DriftAnalyzer:
    """Analyzes product drift across multiple dimensions.

    Stateless — every call computes fresh from canonical sources.
    """

    def analyze(self) -> DriftReport:
        """Compute drift across all dimensions."""
        caps = _cap_registry.list_all()

        arch_drift = self._compute_architecture_drift(caps)
        doc_drift = self._compute_documentation_drift(caps)
        cap_drift = self._compute_capability_drift(caps)
        knl_drift = self._compute_knowledge_drift(caps)
        rfc_drift = self._compute_rfc_drift()

        details = self._collect_details(arch_drift, doc_drift, cap_drift, knl_drift, rfc_drift)

        overall = round(
            arch_drift * 0.25 + doc_drift * 0.20 + cap_drift * 0.30 + knl_drift * 0.10 + rfc_drift * 0.15,
            1,
        )

        return DriftReport(
            architecture_drift=round(arch_drift, 1),
            documentation_drift=round(doc_drift, 1),
            capability_drift=round(cap_drift, 1),
            knowledge_drift=round(knl_drift, 1),
            rfc_drift=round(rfc_drift, 1),
            overall_drift=round(overall, 1),
            details=tuple(details),
        )

    def _compute_architecture_drift(self, caps: list) -> float:
        """Architecture drift: variance in architecture scores across capabilities."""
        if len(caps) < 2:
            return 0.0
        scores = [calculate_health(c).architecture for c in caps]
        avg = sum(scores) / len(scores)
        variance = sum((s - avg) ** 2 for s in scores) / len(scores)
        return min(variance / 25.0, 100.0)

    def _compute_documentation_drift(self, caps: list) -> float:
        """Documentation drift: average gap between doc score and target (80)."""
        if not caps:
            return 0.0
        target = 80.0
        gaps = [max(0.0, target - score_documentation(c)) for c in caps]
        return sum(gaps) / len(gaps)

    def _compute_capability_drift(self, caps: list) -> float:
        """Capability drift: capabilities that haven't reached target maturity."""
        if not caps:
            return 0.0
        levels = list(CapabilityMaturity)
        total_gap = 0.0
        for c in caps:
            current_idx = levels.index(c.current_maturity)
            target_idx = levels.index(c.target_maturity)
            if target_idx > 0:
                gap = (target_idx - current_idx) / target_idx * 100.0
                total_gap += gap
        return min(total_gap / len(caps), 100.0)

    def _compute_knowledge_drift(self, caps: list) -> float:
        """Knowledge drift: capabilities with missing documentation or knowledge."""
        if not caps:
            return 0.0
        missing = sum(1 for c in caps if not c.documentation_links)
        return (missing / len(caps)) * 100.0

    def _compute_rfc_drift(self) -> float:
        """RFC drift: RFCs stuck in DRAFT or IN_REVIEW for too long."""
        state = create_default_state()
        rfcs = list(state.rfcs.values())
        if not rfcs:
            return 0.0
        stuck = sum(1 for r in rfcs if r.status in (RfcStatus.DRAFT,))
        return (stuck / len(rfcs)) * 100.0

    def _collect_details(
        self, arch: float, doc: float, cap: float, knl: float, rfc: float
    ) -> list[str]:
        details: list[str] = []
        thresholds = {
            "Architecture": (arch, 30.0),
            "Documentation": (doc, 30.0),
            "Capability": (cap, 30.0),
            "Knowledge": (knl, 30.0),
            "RFC": (rfc, 30.0),
        }
        for name, (score, threshold) in thresholds.items():
            if score > threshold:
                details.append(f"{name} drift elevated: {score:.1f}/100")
            else:
                details.append(f"{name} drift normal: {score:.1f}/100")
        return details
