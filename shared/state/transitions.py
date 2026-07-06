"""State Transitions — determines legal transitions between product states.

Defines which state transitions are allowed, generates transition reasons,
and maintains transition history.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum, auto

from shared.state.state import STATE_METADATA, ProductStateType


class TransitionType(Enum):
    """Type of state transition."""

    NATURAL = auto()       # Normal progression (e.g., BOOTSTRAPPING → GROWING)
    REGRESSION = auto()    # Moving backward (e.g., STABLE → BLOCKED)
    PROMOTION = auto()     # Moving forward toward release (e.g., RELEASE_CANDIDATE → READY_FOR_RELEASE)
    SIDEWAYS = auto()      # Moving sideways (e.g., OPTIMIZING → REFACTORING)


@dataclass(frozen=True)
class TransitionRecord:
    """A recorded state transition."""

    from_state: ProductStateType
    to_state: ProductStateType
    transition_type: TransitionType
    timestamp: str = ""
    reason: str = ""
    confidence: float = 0.0


# Legal transitions: (from_state, to_state) pairs that are allowed
LEGAL_TRANSITIONS: set[tuple[ProductStateType, ProductStateType]] = {
    # Bootstrapping → ...
    (ProductStateType.BOOTSTRAPPING, ProductStateType.GROWING),
    (ProductStateType.BOOTSTRAPPING, ProductStateType.REFACTORING),
    (ProductStateType.BOOTSTRAPPING, ProductStateType.BLOCKED),

    # Growing → ...
    (ProductStateType.GROWING, ProductStateType.STABLE),
    (ProductStateType.GROWING, ProductStateType.OPTIMIZING),
    (ProductStateType.GROWING, ProductStateType.REFACTORING),
    (ProductStateType.GROWING, ProductStateType.BLOCKED),

    # Stable → ...
    (ProductStateType.STABLE, ProductStateType.OPTIMIZING),
    (ProductStateType.STABLE, ProductStateType.REFACTORING),
    (ProductStateType.STABLE, ProductStateType.RELEASE_CANDIDATE),
    (ProductStateType.STABLE, ProductStateType.MAINTENANCE),
    (ProductStateType.STABLE, ProductStateType.GROWING),
    (ProductStateType.STABLE, ProductStateType.BLOCKED),

    # Optimizing → ...
    (ProductStateType.OPTIMIZING, ProductStateType.STABLE),
    (ProductStateType.OPTIMIZING, ProductStateType.REFACTORING),
    (ProductStateType.OPTIMIZING, ProductStateType.RELEASE_CANDIDATE),
    (ProductStateType.OPTIMIZING, ProductStateType.GROWING),

    # Refactoring → ...
    (ProductStateType.REFACTORING, ProductStateType.STABLE),
    (ProductStateType.REFACTORING, ProductStateType.OPTIMIZING),
    (ProductStateType.REFACTORING, ProductStateType.GROWING),
    (ProductStateType.REFACTORING, ProductStateType.BLOCKED),

    # Blocked → ...
    (ProductStateType.BLOCKED, ProductStateType.GROWING),
    (ProductStateType.BLOCKED, ProductStateType.REFACTORING),
    (ProductStateType.BLOCKED, ProductStateType.STABLE),

    # Release Candidate → ...
    (ProductStateType.RELEASE_CANDIDATE, ProductStateType.READY_FOR_RELEASE),
    (ProductStateType.RELEASE_CANDIDATE, ProductStateType.BLOCKED),
    (ProductStateType.RELEASE_CANDIDATE, ProductStateType.STABLE),
    (ProductStateType.RELEASE_CANDIDATE, ProductStateType.OPTIMIZING),

    # Ready for Release → ...
    (ProductStateType.READY_FOR_RELEASE, ProductStateType.MAINTENANCE),
    (ProductStateType.READY_FOR_RELEASE, ProductStateType.RELEASE_CANDIDATE),
    (ProductStateType.READY_FOR_RELEASE, ProductStateType.STABLE),

    # Maintenance → ...
    (ProductStateType.MAINTENANCE, ProductStateType.GROWING),
    (ProductStateType.MAINTENANCE, ProductStateType.OPTIMIZING),
    (ProductStateType.MAINTENANCE, ProductStateType.REFACTORING),
    (ProductStateType.MAINTENANCE, ProductStateType.BLOCKED),
}


class TransitionEngine:
    """Determines legal transitions between product states.

    Maintains transition history for analysis.
    """

    def __init__(self) -> None:
        self._history: list[TransitionRecord] = []

    def is_legal(self, from_state: ProductStateType, to_state: ProductStateType) -> bool:
        """Check if a transition between two states is legal."""
        return (from_state, to_state) in LEGAL_TRANSITIONS

    def get_legal_transitions(self, from_state: ProductStateType) -> list[ProductStateType]:
        """Get all legal target states from a given state."""
        return [to for (frm, to) in LEGAL_TRANSITIONS if frm == from_state]

    def record_transition(
        self,
        from_state: ProductStateType,
        to_state: ProductStateType,
        reason: str = "",
        confidence: float = 0.0,
    ) -> TransitionRecord:
        """Record a new transition. Returns the record."""
        record = TransitionRecord(
            from_state=from_state,
            to_state=to_state,
            transition_type=self._classify_transition(from_state, to_state),
            timestamp=datetime.now(UTC).isoformat(),
            reason=reason,
            confidence=confidence,
        )
        self._history.append(record)
        return record

    def get_history(self) -> list[TransitionRecord]:
        """Get all recorded transitions."""
        return list(self._history)

    def get_last_transition(self) -> TransitionRecord | None:
        """Get the most recent transition."""
        if not self._history:
            return None
        return self._history[-1]

    def clear_history(self) -> None:
        """Clear all transition history."""
        self._history.clear()

    def generate_transition_reason(
        self,
        from_state: ProductStateType,
        to_state: ProductStateType,
        indicators: object = None,
    ) -> str:
        """Generate a human-readable reason for a transition."""
        if not self.is_legal(from_state, to_state):
            return f"Illegal transition: {STATE_METADATA[from_state]['label']} → {STATE_METADATA[to_state]['label']}"

        frm_label = STATE_METADATA[from_state]["label"]
        to_label = STATE_METADATA[to_state]["label"]

        progression_reasons = {
            (ProductStateType.BOOTSTRAPPING, ProductStateType.GROWING):
                "Core infrastructure complete, beginning active capability development.",
            (ProductStateType.GROWING, ProductStateType.STABLE):
                "Active development complete, product is now stable.",
            (ProductStateType.STABLE, ProductStateType.RELEASE_CANDIDATE):
                "All release criteria met, entering release validation.",
            (ProductStateType.RELEASE_CANDIDATE, ProductStateType.READY_FOR_RELEASE):
                "Release validation passed, ready for production deployment.",
        }

        reason = progression_reasons.get((from_state, to_state), "")
        if reason:
            return reason

        regression_reasons = {
            (ProductStateType.GROWING, ProductStateType.BLOCKED):
                "Critical blockers detected, development paused.",
            (ProductStateType.STABLE, ProductStateType.BLOCKED):
                "Regressions or critical issues detected.",
        }

        reason = regression_reasons.get((from_state, to_state), "")
        if reason:
            return reason

        return f"Transitioning from {frm_label} to {to_label}."

    @staticmethod
    def _classify_transition(from_state: ProductStateType, to_state: ProductStateType) -> TransitionType:
        """Classify the type of transition."""
        # Forward progression
        forward = [
            (ProductStateType.BOOTSTRAPPING, ProductStateType.GROWING),
            (ProductStateType.GROWING, ProductStateType.STABLE),
            (ProductStateType.STABLE, ProductStateType.RELEASE_CANDIDATE),
            (ProductStateType.RELEASE_CANDIDATE, ProductStateType.READY_FOR_RELEASE),
        ]
        if (from_state, to_state) in forward:
            return TransitionType.PROMOTION

        # Regression (moving to BLOCKED or BOOTSTRAPPING)
        if to_state in (ProductStateType.BLOCKED,) or (
            from_state not in (ProductStateType.BOOTSTRAPPING, ProductStateType.BLOCKED)
            and to_state in (ProductStateType.BOOTSTRAPPING,)
        ):
            return TransitionType.REGRESSION

        return TransitionType.NATURAL
