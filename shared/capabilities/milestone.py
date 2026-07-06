"""Milestone model — tracking progress toward capability goals."""

from __future__ import annotations

from dataclasses import dataclass, field

from shared.capabilities.enums import MilestoneType


@dataclass(frozen=True)
class Milestone:
    """A milestone on the capability roadmap."""
    name: str
    description: str
    milestone_type: MilestoneType = MilestoneType.FEATURE
    version: str = ""
    is_required_for_v1: bool = False
    depends_on: tuple[str, ...] = field(default_factory=tuple)
    estimated_effort: str = ""  # e.g., "2 weeks", "1 sprint"

    @property
    def key(self) -> str:
        return self.name.lower().replace(" ", "_")


@dataclass(frozen=True)
class RoadmapPhase:
    """A phase on the capability roadmap."""
    name: str
    description: str
    target_version: str
    milestones: tuple[Milestone, ...] = field(default_factory=tuple)
    is_complete: bool = False


@dataclass(frozen=True)
class CapabilityRoadmap:
    """Complete roadmap for a capability."""
    phases: tuple[RoadmapPhase, ...] = field(default_factory=tuple)
    blocking_issues: tuple[str, ...] = field(default_factory=tuple)
