"""Roadmap Engine — generates roadmap summaries, gap analysis, and version targeting."""

from __future__ import annotations

from dataclasses import dataclass, field

from shared.capabilities.enums import CapabilityMaturity, CapabilityStatus
from shared.capabilities.registry import CapabilityRegistry


@dataclass(frozen=True)
class RoadmapSummary:
    """High-level roadmap summary for the platform."""
    current_version: str
    next_version: str
    target_version: str
    capabilities_in_progress: int
    capabilities_not_started: int
    capabilities_complete: int
    capabilities_blocked: int
    blocking_issues: tuple[str, ...] = field(default_factory=tuple)
    unmet_milestones: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class GapAnalysis:
    """Analysis of gaps between current and target states."""
    capability_id: str
    name: str
    current_maturity: CapabilityMaturity
    target_maturity: CapabilityMaturity
    maturity_gap: int
    health_score: float
    is_blocked: bool


def summarize_roadmap(registry: CapabilityRegistry) -> RoadmapSummary:
    """Generate a roadmap summary from all registered capabilities."""
    capabilities = registry.list_all()
    in_progress = sum(1 for c in capabilities if c.status == CapabilityStatus.IN_PROGRESS)
    not_started = sum(1 for c in capabilities if c.status == CapabilityStatus.NOT_STARTED)
    complete = sum(1 for c in capabilities if c.status == CapabilityStatus.COMPLETE)
    blocked = sum(1 for c in capabilities if c.status == CapabilityStatus.BLOCKED)

    blocking_issues: list[str] = []
    for cap in capabilities:
        if cap.blocked_by:
            blocking_issues.append(f"{cap.name} blocked by: {', '.join(cap.blocked_by)}")
        if cap.status == CapabilityStatus.BLOCKED:
            blocking_issues.append(f"{cap.name} is blocked")

    unmet: list[str] = []
    for cap in capabilities:
        levels = list(CapabilityMaturity)
        try:
            if levels.index(cap.current_maturity) < levels.index(cap.target_maturity):
                unmet.append(f"{cap.name}: {cap.current_maturity.name} → {cap.target_maturity.name}")
        except ValueError:
            unmet.append(f"{cap.name}: maturity level unknown")

    return RoadmapSummary(
        current_version="0.5.0",
        next_version="0.6.0",
        target_version="1.0.0",
        capabilities_in_progress=in_progress,
        capabilities_not_started=not_started,
        capabilities_complete=complete,
        capabilities_blocked=blocked,
        blocking_issues=tuple(blocking_issues),
        unmet_milestones=tuple(unmet),
    )


def analyze_gaps(registry: CapabilityRegistry) -> list[GapAnalysis]:
    """Analyze maturity gaps for all capabilities."""
    levels = list(CapabilityMaturity)
    results: list[GapAnalysis] = []

    for cap in registry.list_all():
        try:
            current_idx = levels.index(cap.current_maturity)
            target_idx = levels.index(cap.target_maturity)
            gap = target_idx - current_idx
        except ValueError:
            gap = 0

        results.append(GapAnalysis(
            capability_id=cap.capability_id,
            name=cap.name,
            current_maturity=cap.current_maturity,
            target_maturity=cap.target_maturity,
            maturity_gap=max(gap, 0),
            health_score=cap.health.overall,
            is_blocked=cap.status == CapabilityStatus.BLOCKED,
        ))

    return sorted(results, key=lambda g: (-g.maturity_gap, g.health_score))
