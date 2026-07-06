"""Kernel — GymOS Product Operating System.

The Kernel is the single runtime authority for product identity,
capability lifecycle, RFC lifecycle, release readiness, architecture
health, technical debt, and platform evolution.

It consumes the Capability Platform (shared/capabilities/) rather
than duplicating capability information.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto

from shared.version import APP_VERSION

# ── Product Lifecycle ────────────────────────────────────────────────────────

class ProductPhase(Enum):
    """Major product lifecycle phases."""
    ALPHA = auto()
    BETA = auto()
    STABLE = auto()
    MATURE = auto()


class RoadmapStage(Enum):
    """Stages within a product phase."""
    FOUNDATION = auto()
    GROWTH = auto()
    OPTIMIZATION = auto()
    EXPANSION = auto()


class ReleaseReadiness(Enum):
    """Release readiness score."""
    NOT_READY = auto()
    ALMOST_READY = auto()
    READY = auto()


class RfcStatus(Enum):
    """Status of an RFC."""
    DRAFT = auto()
    IN_REVIEW = auto()
    APPROVED = auto()
    IN_PROGRESS = auto()
    COMPLETE = auto()
    SUPERSEDED = auto()


class KernelSnapshotType(Enum):
    """Type of kernel snapshot."""
    MANUAL = auto()
    DAILY = auto()
    MILESTONE = auto()
    RELEASE = auto()


# ── Product Identity ─────────────────────────────────────────────────────────

@dataclass(frozen=True)
class ProductIdentity:
    """Immutable product identity."""
    name: str = "GymOS"
    description: str = "Personal Hypertrophy Operating System"
    version: str = APP_VERSION
    phase: ProductPhase = ProductPhase.ALPHA
    roadmap_stage: RoadmapStage = RoadmapStage.FOUNDATION
    current_milestone: str = "Platform Maturity"


# ── RFC Tracking ─────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class RfcRecord:
    """A recorded RFC in the product lifecycle."""
    rfc_id: str
    title: str
    status: RfcStatus
    description: str = ""
    depends_on: tuple[str, ...] = field(default_factory=tuple)
    created_at: str = ""
    completed_at: str = ""


# ── Release ──────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class Release:
    """A product release."""
    version: str
    name: str
    rfc_ids: tuple[str, ...] = field(default_factory=tuple)
    capabilities: tuple[str, ...] = field(default_factory=tuple)
    is_released: bool = False
    release_date: str = ""
    release_notes: str = ""


# ── Kernel Runtime ───────────────────────────────────────────────────────────

@dataclass(frozen=True)
class RuntimeMetrics:
    """Runtime-computed metrics for a single capability."""
    capability_id: str
    name: str
    runtime_maturity: float  # 0-100 weighted score
    architecture_score: float
    documentation_score: float
    test_score: float
    coverage_score: float
    completion_score: float
    debt_score: float
    dependency_health: float
    health_delta: float = 0.0  # change since last snapshot


@dataclass(frozen=True)
class KernelRuntime:
    """Current kernel runtime state."""
    version: str
    phase: ProductPhase
    roadmap_stage: RoadmapStage
    current_rfc: str
    next_rfc: str
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
    timestamp: str = ""


# ── Snapshot ─────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class KernelSnapshot:
    """Immutable snapshot of kernel state at a point in time."""
    timestamp: str
    snapshot_type: KernelSnapshotType
    runtime: KernelRuntime
    metrics: tuple[RuntimeMetrics, ...] = field(default_factory=tuple)
    overall_health: float = 0.0


# ── Trend ────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class TrendPoint:
    """A single data point in a trend line."""
    timestamp: str
    value: float
    label: str = ""


@dataclass(frozen=True)
class CapabilityTrend:
    """Trend data for a single capability over time."""
    capability_id: str
    name: str
    points: tuple[TrendPoint, ...] = field(default_factory=tuple)
    growth_rate: float = 0.0  # positive = improving, negative = declining


# ── Product Health ───────────────────────────────────────────────────────────

@dataclass(frozen=True)
class ProductHealth:
    """Multi-dimensional product health assessment."""
    overall: float
    architecture_health: float
    engineering_health: float
    knowledge_health: float
    capability_health: float
    documentation_health: float
    timestamp: str = ""


# ── Debt Registry ────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class DebtRegistryItem:
    """A technical debt item registered with the kernel."""
    debt_id: str
    title: str
    severity: str  # critical, high, medium, low
    owner: str
    affected_capability: str
    target_release: str
    status: str = "identified"  # identified, in_progress, resolved, accepted
    blocking: bool = False
    description: str = ""


# ── Release Readiness ────────────────────────────────────────────────────────

@dataclass(frozen=True)
class ReleaseReadinessResult:
    """Release readiness assessment."""
    version: str
    readiness: ReleaseReadiness
    score: float  # 0-100
    blockers: tuple[str, ...] = field(default_factory=tuple)
    blocker_count: int = 0
    capability_completion: float = 0.0
    documentation_score: float = 0.0
    test_score: float = 0.0
    health_score: float = 0.0
    debt_score: float = 0.0
    gaps: tuple[str, ...] = field(default_factory=tuple)
