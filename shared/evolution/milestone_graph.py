"""Milestone Graph — tracks progress toward key product milestones.

Stateless functions consuming Capability Platform and Kernel data.
"""

from __future__ import annotations

from dataclasses import dataclass

from shared.capabilities import registry as _cap_registry
from shared.capabilities.enums import CapabilityStatus
from shared.evolution.evolution_engine import JourneyMilestone


@dataclass(frozen=True)
class MilestoneProgress:
    """Progress toward a specific milestone."""
    label: str
    target_version: str
    description: str
    completion_percent: float
    capabilities_required: tuple[str, ...]
    capabilities_complete: int
    capabilities_total: int
    is_reached: bool


def build_milestone_progress() -> list[MilestoneProgress]:
    """Build progress data for all key product milestones."""
    caps = {c.capability_id: c for c in _cap_registry.list_all()}

    milestones = [
        JourneyMilestone(
            label="Platform Maturity",
            version="0.5.0",
            description="Core capabilities complete: training, nutrition, knowledge, events, product intelligence, capability platform",
            is_reached=False,
        ),
        JourneyMilestone(
            label="Recovery Intelligence",
            version="0.6.0",
            description="Recovery domain: sleep, HRV, soreness, deload scheduling",
            is_reached=False,
        ),
        JourneyMilestone(
            label="Decision Intelligence",
            version="0.7.0",
            description="Weekly review, recommendations, plateau detection",
            is_reached=False,
        ),
        JourneyMilestone(
            label="AI Coach",
            version="0.8.0",
            description="Personalized coaching, recommendations, nudges",
            is_reached=False,
        ),
        JourneyMilestone(
            label="Prediction Engine",
            version="0.9.0",
            description="Progress forecasting, goal timelines, what-if simulation",
            is_reached=False,
        ),
        JourneyMilestone(
            label="Personal OS",
            version="1.0.0",
            description="All core domains automated, adaptive programming, digital twin foundation",
            is_reached=False,
        ),
    ]

    results: list[MilestoneProgress] = []

    for m in milestones:
        # Map milestone to capabilities
        if m.version == "0.5.0":
            required = ("training-intelligence", "nutrition-intelligence", "knowledge-platform",
                       "event-platform", "product-intelligence", "capability-platform")
        elif m.version == "0.6.0":
            required = ("recovery-intelligence",)
        elif m.version == "0.7.0":
            required = ("decision-intelligence",)
        elif m.version == "0.8.0":
            required = ("ai-coach",)
        elif m.version == "0.9.0":
            required = ("prediction-engine",)
        elif m.version == "1.0.0":
            required = ("digital-twin",)
        else:
            required = ()

        complete_count = sum(1 for cid in required if cid in caps and caps[cid].status == CapabilityStatus.COMPLETE)
        total_count = len(required)
        pct = round((complete_count / total_count) * 100, 1) if total_count else 0.0

        results.append(MilestoneProgress(
            label=m.label,
            target_version=m.version,
            description=m.description,
            completion_percent=pct,
            capabilities_required=required,
            capabilities_complete=complete_count,
            capabilities_total=total_count,
            is_reached=complete_count == total_count and total_count > 0,
        ))

    return results
