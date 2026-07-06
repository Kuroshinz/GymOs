"""Evolution Engine — understands how GymOS evolves over time.

Answers:
- How much has GymOS evolved?
- Which RFC contributed the most?
- Which capability improved the fastest?
- What is required to reach v1.0?
- What is the predicted maturity after the next RFCs?
- How are RFCs, capabilities, milestones, and versions linked?

Consumes the Kernel and Capability Platform.
Does NOT duplicate them.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# ── Evolution Metrics ───────────────────────────────────────────────────────

@dataclass(frozen=True)
class ProductCompletion:
    """Product-wide completion metrics."""
    total_capabilities: int = 0
    complete: int = 0
    in_progress: int = 0
    not_started: int = 0
    completion_percent: float = 0.0
    estimated_remaining_work: float = 0.0  # in arbitrary units


@dataclass(frozen=True)
class CapabilityVelocity:
    """Velocity of a single capability's evolution."""
    capability_id: str = ""
    name: str = ""
    maturity_gain: float = 0.0  # maturity points gained
    time_periods: int = 0
    velocity: float = 0.0  # maturity gain per period
    growth_rate: float = 0.0  # percentage growth


@dataclass(frozen=True)
class RfcImpactScore:
    """Impact score of an RFC on the product."""
    rfc_id: str = ""
    title: str = ""
    health_delta: float = 0.0  # change in overall health
    capabilities_affected: int = 0
    capabilities_completed: int = 0
    maturity_gain: float = 0.0
    impact_score: float = 0.0  # composite score


@dataclass(frozen=True)
class VersionReadinessTrend:
    """Trend of readiness scores across versions."""
    version: str = ""
    readiness_score: float = 0.0
    trend_direction: str = "stable"  # improving, declining, stable
    delta: float = 0.0


@dataclass(frozen=True)
class EstimatedRemainingWork:
    """Estimated work remaining to reach targets."""
    total_capabilities: int = 0
    remaining: int = 0
    estimated_sprints: int = 0
    estimated_weeks: int = 0
    confidence: str = "medium"  # low, medium, high


# ── Timelines ───────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class TimelineEntry:
    """A single entry on any timeline."""
    timestamp: str = ""
    event_type: str = ""  # rfc, release, milestone, capability_change
    label: str = ""
    description: str = ""
    value: float = 0.0


@dataclass(frozen=True)
class EvolutionTimeline:
    """Complete evolution timeline for the product."""
    entries: tuple[TimelineEntry, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class RfcTimeline:
    """Timeline of RFC events."""
    entries: tuple[TimelineEntry, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class CapabilityGrowthTimeline:
    """Timeline of capability growth."""
    entries: tuple[TimelineEntry, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class VersionProgress:
    """Progress data for a single version."""
    version: str = ""
    total_capabilities: int = 0
    complete: int = 0
    completion_percent: float = 0.0
    health_score: float = 0.0


# ── Forecasts ───────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class CapabilityForecast:
    """Predicted future state of a single capability."""
    capability_id: str = ""
    name: str = ""
    current_maturity: float = 0.0
    predicted_maturity: float = 0.0
    sprints_to_target: int = 0
    confidence: str = "medium"


@dataclass(frozen=True)
class ReleaseForecast:
    """Predicted readiness for a future release."""
    target_version: str = ""
    predicted_readiness_score: float = 0.0
    predicted_completion_percent: float = 0.0
    estimated_sprints_remaining: int = 0
    blockers_remaining: int = 0
    confidence: str = "medium"


@dataclass(frozen=True)
class ProductCompletionForecast:
    """Predicted completion trajectory for the product."""
    current_completion: float = 0.0
    predicted_completion_next_rfc: float = 0.0
    predicted_completion_v1: float = 0.0
    sprints_to_v1: int = 0
    estimated_health_at_v1: float = 0.0
    confidence: str = "medium"


# ── Reports ──────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class EvolutionReport:
    """Complete evolution report."""
    product_completion: ProductCompletion = field(default_factory=ProductCompletion)
    capability_velocities: tuple[CapabilityVelocity, ...] = field(default_factory=tuple)
    rfc_impacts: tuple[RfcImpactScore, ...] = field(default_factory=tuple)
    version_trends: tuple[VersionReadinessTrend, ...] = field(default_factory=tuple)
    timelines: EvolutionTimeline = field(default_factory=EvolutionTimeline)
    forecast: ProductCompletionForecast = field(default_factory=ProductCompletionForecast)
    remaining_work: EstimatedRemainingWork = field(default_factory=EstimatedRemainingWork)


@dataclass(frozen=True)
class JourneyMilestone:
    """A milestone on the product journey."""
    label: str = ""
    version: str = ""
    description: str = ""
    is_reached: bool = False


# ── Evolution Velocity ──────────────────────────────────────────────────────

@dataclass(frozen=True)
class EvolutionVelocity:
    """Velocity of the entire product evolution over a period."""
    period_label: str = ""
    maturity_delta: float = 0.0
    capabilities_completed: int = 0
    rfc_impact_sum: float = 0.0
    velocity_score: float = 0.0


@dataclass(frozen=True)
class RfcContribution:
    """An RFC's contribution to overall product evolution."""
    rfc_id: str = ""
    rfc_title: str = ""
    status: str = ""
    capabilities_affected: int = 0
    maturity_contribution: float = 0.0
    completion_contribution: float = 0.0
    contribution_percent: float = 0.0


# ── Evolution Chain (RFC → Capability → Milestone → Version) ───────────────

@dataclass(frozen=True)
class EvolutionChainLink:
    """A single link in the RFC → Capability → Milestone → Version chain."""
    rfc_id: str = ""
    rfc_title: str = ""
    rfc_status: str = ""
    capability_id: str = ""
    capability_name: str = ""
    capability_status: str = ""
    capability_maturity: str = ""
    milestone_label: str = ""
    milestone_version: str = ""
    version_name: str = ""
    version_is_released: bool = False


@dataclass(frozen=True)
class EvolutionChain:
    """Complete RFC → Capability → Milestone → Version chain."""
    links: tuple[EvolutionChainLink, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class EvolutionSummary:
    """Comprehensive summary of all evolution data."""
    total_rfcs: int = 0
    completed_rfcs: int = 0
    total_capabilities: int = 0
    completed_capabilities: int = 0
    total_milestones: int = 0
    reached_milestones: int = 0
    total_versions: int = 0
    released_versions: int = 0
    overall_evolution_progress: float = 0.0
    evolution_velocity: EvolutionVelocity = field(default_factory=EvolutionVelocity)
    fastest_capability: str = ""
    slowest_capability: str = ""
    most_impactful_rfc: str = ""
