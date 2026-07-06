"""Product State — strongly typed product states for GymOS self-awareness.

Defines 9 canonical product states, each with confidence, risk, blockers,
active capabilities, architecture health, documentation health, technical
debt, release readiness, and timestamp.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any


class ProductStateType(Enum):
    """Canonical product states for the GymOS Product State Engine."""

    BOOTSTRAPPING = auto()       # Initial state: core being built
    GROWING = auto()             # Active capability development
    STABLE = auto()              # All core capabilities complete
    OPTIMIZING = auto()          # Performance/quality improvements
    REFACTORING = auto()         # Architecture/tech debt reduction
    BLOCKED = auto()             # Blocked by external dependencies
    RELEASE_CANDIDATE = auto()   # Ready for release evaluation
    READY_FOR_RELEASE = auto()   # Release criteria met
    MAINTENANCE = auto()         # Bug fixes, minor improvements


# Human-readable labels and descriptions for each state
STATE_METADATA: dict[ProductStateType, dict[str, str]] = {
    ProductStateType.BOOTSTRAPPING: {
        "label": "Bootstrapping",
        "description": "Initial product development — core infrastructure and foundational capabilities being built.",
        "color": "blue",
    },
    ProductStateType.GROWING: {
        "label": "Growing",
        "description": "Active development — new capabilities being added, rapid feature expansion.",
        "color": "green",
    },
    ProductStateType.STABLE: {
        "label": "Stable",
        "description": "Core capabilities complete, product is reliable and production-ready.",
        "color": "teal",
    },
    ProductStateType.OPTIMIZING: {
        "label": "Optimizing",
        "description": "Performance tuning, quality improvements, test coverage increases.",
        "color": "purple",
    },
    ProductStateType.REFACTORING: {
        "label": "Refactoring",
        "description": "Architecture improvements, technical debt reduction, code quality.",
        "color": "orange",
    },
    ProductStateType.BLOCKED: {
        "label": "Blocked",
        "description": "Development blocked by external dependencies, critical issues, or missing capabilities.",
        "color": "red",
    },
    ProductStateType.RELEASE_CANDIDATE: {
        "label": "Release Candidate",
        "description": "Feature-complete, undergoing release validation and testing.",
        "color": "yellow",
    },
    ProductStateType.READY_FOR_RELEASE: {
        "label": "Ready for Release",
        "description": "All release criteria met, ready for production deployment.",
        "color": "bright_green",
    },
    ProductStateType.MAINTENANCE: {
        "label": "Maintenance",
        "description": "Bug fixes, minor improvements, no major feature development.",
        "color": "gray",
    },
}


@dataclass(frozen=True)
class ProductState:
    """Complete description of the product's current operational state.

    Every field is computed from canonical sources (Capability Platform, Kernel,
    Evolution Engine, Product Knowledge Graph) — never entered manually.
    """

    # Identity
    state_type: ProductStateType
    timestamp: str = ""

    # Confidence & risk
    confidence: float = 0.0       # 0-100: how confident are we in this assessment
    risk_score: float = 0.0       # 0-100: overall product risk
    drift_score: float = 0.0      # 0-100: how much has drifted from ideal

    # Capability metrics
    active_capabilities: int = 0
    total_capabilities: int = 0
    capabilities_complete: int = 0
    capabilities_in_progress: int = 0
    capabilities_not_started: int = 0
    capabilities_blocked: int = 0

    # Health dimensions
    architecture_health: float = 0.0  # 0-100
    documentation_health: float = 0.0  # 0-100
    test_health: float = 0.0  # 0-100
    overall_health: float = 0.0  # 0-100

    # Technical debt
    technical_debt: int = 0
    blocking_debt: int = 0
    debt_pressure: float = 0.0  # 0-100: how much debt is impeding progress

    # Release
    release_readiness: float = 0.0  # 0-100
    release_blockers: tuple[str, ...] = field(default_factory=tuple)

    # Momentum
    product_momentum: float = 0.0  # -100 to 100: positive = improving

    # Blockers
    blockers: tuple[str, ...] = field(default_factory=tuple)

    # State reasoning
    primary_reason: str = ""  # Why we determined this state
    supporting_factors: tuple[str, ...] = field(default_factory=tuple)

    @property
    def completion_percent(self) -> float:
        """Overall completion percentage."""
        if self.total_capabilities == 0:
            return 0.0
        return round((self.capabilities_complete / self.total_capabilities) * 100, 1)

    @property
    def is_healthy(self) -> bool:
        return self.overall_health >= 50.0

    @property
    def is_blocked(self) -> bool:
        return self.state_type == ProductStateType.BLOCKED or len(self.blockers) > 0

    @property
    def is_releasable(self) -> bool:
        return self.state_type in (
            ProductStateType.RELEASE_CANDIDATE,
            ProductStateType.READY_FOR_RELEASE,
        )

    @property
    def label(self) -> str:
        return STATE_METADATA[self.state_type]["label"]

    @property
    def description(self) -> str:
        return STATE_METADATA[self.state_type]["description"]

    def to_dict(self) -> dict[str, Any]:
        return {
            "state_type": self.state_type.name.lower(),
            "label": self.label,
            "timestamp": self.timestamp,
            "confidence": self.confidence,
            "risk_score": self.risk_score,
            "drift_score": self.drift_score,
            "active_capabilities": self.active_capabilities,
            "total_capabilities": self.total_capabilities,
            "capabilities_complete": self.capabilities_complete,
            "capabilities_in_progress": self.capabilities_in_progress,
            "capabilities_not_started": self.capabilities_not_started,
            "capabilities_blocked": self.capabilities_blocked,
            "architecture_health": self.architecture_health,
            "documentation_health": self.documentation_health,
            "test_health": self.test_health,
            "overall_health": self.overall_health,
            "technical_debt": self.technical_debt,
            "blocking_debt": self.blocking_debt,
            "debt_pressure": self.debt_pressure,
            "release_readiness": self.release_readiness,
            "release_blockers": list(self.release_blockers),
            "product_momentum": self.product_momentum,
            "blockers": list(self.blockers),
            "primary_reason": self.primary_reason,
            "supporting_factors": list(self.supporting_factors),
            "completion_percent": self.completion_percent,
            "is_healthy": self.is_healthy,
            "is_blocked": self.is_blocked,
            "is_releasable": self.is_releasable,
        }
