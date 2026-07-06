"""Capability enums — maturity levels, statuses, risk levels, and priorities."""

from __future__ import annotations

from enum import Enum, auto


class CapabilityMaturity(Enum):
    """Maturity level of a capability."""
    CONCEPT = auto()        # Idea exists, no implementation
    DESIGN = auto()         # Architecture designed, no code
    FOUNDATION = auto()     # Basic scaffolding in place
    IMPLEMENTED = auto()    # Core functionality works
    STABLE = auto()         # Production-ready, tested, documented
    ADVANCED = auto()       # Exceeds basic requirements, optimized
    OPTIMIZED = auto()      # Performance-tuned, self-monitoring
    SELF_EVOLVING = auto()  # Self-improving, adaptive (v1.0+ goal)


class CapabilityStatus(Enum):
    """Current development status."""
    NOT_STARTED = auto()
    IN_PROGRESS = auto()
    COMPLETE = auto()
    BLOCKED = auto()
    DEPRECATED = auto()


class RiskLevel(Enum):
    """Risk level associated with a capability or debt item."""
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
    CRITICAL = auto()


class CapabilityPriority(Enum):
    """Priority level for capability completion."""
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
    CRITICAL = auto()


class DebtSeverity(Enum):
    """Severity of a technical debt item."""
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
    CRITICAL = auto()


class MilestoneType(Enum):
    """Type of milestone."""
    FEATURE = auto()
    ARCHITECTURE = auto()
    QUALITY = auto()
    PLATFORM = auto()
    RESEARCH = auto()
