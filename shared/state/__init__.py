"""Product State Engine — GymOS Runtime Self-Awareness Layer.

The Product State Engine continuously evaluates the product and determines
its current operational state by consuming the Capability Platform, Kernel,
Evolution Engine, and Product Knowledge Graph.

Usage:
    from shared.state import StateOrchestrator

    engine = StateOrchestrator()
    state = engine.get_current_state()
    print(f"Current state: {state.label}")
    print(f"Health: {state.overall_health}/100")
    print(f"Release readiness: {state.release_readiness}/100")

    # Get drift analysis
    drift = engine.get_drift()
    print(f"Overall drift: {drift.overall_drift}/100")

    # Get confidence assessment
    confidence = engine.get_confidence()
    print(f"Confidence: {confidence.overall}/100")

    # Generate reports
    state_report = engine.generate_report("state")
    print(state_report)
"""

from shared.state.confidence import ConfidenceResult, ConfidenceScorer
from shared.state.drift import DriftAnalyzer, DriftReport
from shared.state.evaluator import StateEvaluator
from shared.state.indicators import IndicatorSet, compute_indicators
from shared.state.reports import (
    generate_confidence_report,
    generate_drift_report,
    generate_release_confidence_report,
    generate_runtime_snapshot,
    generate_state_report,
)
from shared.state.runtime import StateOrchestrator
from shared.state.serializer import (
    confidence_to_dict,
    confidence_to_json,
    drift_to_dict,
    drift_to_json,
    snapshot_to_dict,
    snapshot_to_json,
    state_to_dict,
    state_to_json,
    transition_to_dict,
)
from shared.state.state import STATE_METADATA, ProductState, ProductStateType
from shared.state.transitions import (
    LEGAL_TRANSITIONS,
    TransitionEngine,
    TransitionRecord,
    TransitionType,
)

__all__ = (
    # State
    "ProductState",
    "ProductStateType",
    "STATE_METADATA",
    # Evaluator
    "StateEvaluator",
    # Transitions
    "TransitionEngine",
    "TransitionRecord",
    "TransitionType",
    "LEGAL_TRANSITIONS",
    # Drift
    "DriftAnalyzer",
    "DriftReport",
    # Confidence
    "ConfidenceScorer",
    "ConfidenceResult",
    # Indicators
    "IndicatorSet",
    "compute_indicators",
    # Runtime
    "StateOrchestrator",
    # Reports
    "generate_state_report",
    "generate_drift_report",
    "generate_confidence_report",
    "generate_runtime_snapshot",
    "generate_release_confidence_report",
    # Serializer
    "state_to_dict",
    "state_to_json",
    "drift_to_dict",
    "drift_to_json",
    "confidence_to_dict",
    "confidence_to_json",
    "transition_to_dict",
    "snapshot_to_dict",
    "snapshot_to_json",
)
