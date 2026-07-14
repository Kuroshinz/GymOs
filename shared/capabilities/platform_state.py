"""Platform State — aggregate view of the entire GymOS platform.

Answers: version, health, progress, blockers, capability count, maturity.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from shared.capabilities.enums import CapabilityStatus
from shared.capabilities.health import calculate_health
from shared.capabilities.registry import CapabilityRegistry
from shared.capabilities.roadmap import GapAnalysis, RoadmapSummary, analyze_gaps, summarize_roadmap


@dataclass(frozen=True)
class PlatformState:
    """Complete description of the GymOS platform at a point in time."""
    current_version: str
    current_milestone: str
    total_capabilities: int
    capabilities_complete: int
    capabilities_in_progress: int
    capabilities_not_started: int
    capabilities_blocked: int
    overall_health: float
    weakest_capability: str
    strongest_capability: str
    total_technical_debt: int
    blocking_debt: int
    roadmap: RoadmapSummary
    gaps: tuple[GapAnalysis, ...] = field(default_factory=tuple)


def compute_platform_state(registry: CapabilityRegistry) -> PlatformState:
    """Compute the complete platform state from the capability registry."""
    caps = registry.list_all()
    total = len(caps)
    complete = sum(1 for c in caps if c.status == CapabilityStatus.COMPLETE)
    in_progress = sum(1 for c in caps if c.status == CapabilityStatus.IN_PROGRESS)
    not_started = sum(1 for c in caps if c.status == CapabilityStatus.NOT_STARTED)
    blocked = sum(1 for c in caps if c.status == CapabilityStatus.BLOCKED)

    # Overall health: average of all capability health scores
    overall_health = sum(calculate_health(c).overall for c in caps) / len(caps) if caps else 0.0

    # Weakest/strongest by health
    weakest = ""
    strongest = ""
    if caps:
        health_scores = [(c, calculate_health(c).overall) for c in caps]
        weakest = min(health_scores, key=lambda x: x[1])[0].name
        strongest = max(health_scores, key=lambda x: x[1])[0].name

    # Total technical debt
    total_debt = sum(c.technical_debt.total_items for c in caps)
    blocking_debt = sum(c.technical_debt.critical + c.technical_debt.high for c in caps)

    roadmap = summarize_roadmap(registry)
    gaps = tuple(analyze_gaps(registry))

    return PlatformState(
        current_version="0.5.0",
        current_milestone="Platform Maturity",
        total_capabilities=total,
        capabilities_complete=complete,
        capabilities_in_progress=in_progress,
        capabilities_not_started=not_started,
        capabilities_blocked=blocked,
        overall_health=round(overall_health, 1),
        weakest_capability=weakest,
        strongest_capability=strongest,
        total_technical_debt=total_debt,
        blocking_debt=blocking_debt,
        roadmap=roadmap,
        gaps=gaps,
    )
