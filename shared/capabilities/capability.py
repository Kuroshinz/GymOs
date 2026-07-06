"""Capability model — the core dataclass for every GymOS subsystem."""

from __future__ import annotations

from dataclasses import dataclass, field

from shared.capabilities.enums import (
    CapabilityMaturity,
    CapabilityPriority,
    CapabilityStatus,
    RiskLevel,
)
from shared.capabilities.metrics import CompletionMetrics, HealthScore
from shared.capabilities.milestone import CapabilityRoadmap
from shared.capabilities.technical_debt import TechnicalDebtSummary


@dataclass(frozen=True)
class Capability:
    """A describable subsystem of GymOS with maturity, health, and roadmap."""

    # Identity
    capability_id: str
    name: str
    description: str
    category: str  # training, nutrition, recovery, intelligence, platform, experience

    # Ownership
    owner: str = "platform"

    # Maturity
    status: CapabilityStatus = CapabilityStatus.NOT_STARTED
    version_introduced: str = ""
    target_version: str = ""

    current_maturity: CapabilityMaturity = CapabilityMaturity.CONCEPT
    target_maturity: CapabilityMaturity = CapabilityMaturity.STABLE

    # Health
    health: HealthScore = field(default_factory=lambda: HealthScore(overall=0.0))
    completion: CompletionMetrics = field(default_factory=lambda: CompletionMetrics(current_percent=0.0, target_percent=100.0))
    technical_debt: TechnicalDebtSummary = field(default_factory=TechnicalDebtSummary)

    # Dependencies
    dependencies: tuple[str, ...] = field(default_factory=tuple)
    blocked_by: tuple[str, ...] = field(default_factory=tuple)
    used_by: tuple[str, ...] = field(default_factory=tuple)

    # Planning
    roadmap: CapabilityRoadmap = field(default_factory=CapabilityRoadmap)
    risk_level: RiskLevel = RiskLevel.LOW
    priority: CapabilityPriority = CapabilityPriority.MEDIUM

    # Documentation
    documentation_links: tuple[str, ...] = field(default_factory=tuple)
    last_review: str = ""
    last_updated: str = ""
