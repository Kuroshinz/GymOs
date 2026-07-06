"""State Serializer — serializes Product State Engine data to/from dict and JSON."""

from __future__ import annotations

import json
from typing import Any

from shared.state.confidence import ConfidenceResult
from shared.state.drift import DriftReport
from shared.state.state import ProductState
from shared.state.transitions import TransitionRecord


def state_to_dict(state: ProductState) -> dict[str, Any]:
    """Serialize a ProductState to a dictionary."""
    return state.to_dict()


def state_to_json(state: ProductState, indent: int = 2) -> str:
    """Serialize a ProductState to a JSON string."""
    return json.dumps(state_to_dict(state), indent=indent)


def drift_to_dict(drift: DriftReport) -> dict[str, Any]:
    """Serialize a DriftReport to a dictionary."""
    return {
        "architecture_drift": drift.architecture_drift,
        "documentation_drift": drift.documentation_drift,
        "capability_drift": drift.capability_drift,
        "knowledge_drift": drift.knowledge_drift,
        "rfc_drift": drift.rfc_drift,
        "overall_drift": drift.overall_drift,
        "details": list(drift.details),
    }


def drift_to_json(drift: DriftReport, indent: int = 2) -> str:
    return json.dumps(drift_to_dict(drift), indent=indent)


def confidence_to_dict(confidence: ConfidenceResult) -> dict[str, Any]:
    """Serialize a ConfidenceResult to a dictionary."""
    return {
        "state_confidence": confidence.state_confidence,
        "release_confidence": confidence.release_confidence,
        "data_quality": confidence.data_quality,
        "coverage_confidence": confidence.coverage_confidence,
        "timestamp_confidence": confidence.timestamp_confidence,
        "overall": confidence.overall,
        "factors": list(confidence.factors),
    }


def confidence_to_json(confidence: ConfidenceResult, indent: int = 2) -> str:
    return json.dumps(confidence_to_dict(confidence), indent=indent)


def transition_to_dict(record: TransitionRecord) -> dict[str, Any]:
    """Serialize a TransitionRecord to a dictionary."""
    return {
        "from_state": record.from_state.name.lower(),
        "to_state": record.to_state.name.lower(),
        "transition_type": record.transition_type.name.lower(),
        "timestamp": record.timestamp,
        "reason": record.reason,
        "confidence": record.confidence,
    }


def snapshot_to_dict(
    state: ProductState, drift: DriftReport, confidence: ConfidenceResult,
    transitions: list[TransitionRecord] | None = None,
) -> dict[str, Any]:
    """Serialize a complete runtime snapshot to a dictionary."""
    data: dict[str, Any] = {
        "state": state_to_dict(state),
        "drift": drift_to_dict(drift),
        "confidence": confidence_to_dict(confidence),
    }
    if transitions:
        data["transitions"] = [transition_to_dict(t) for t in transitions]
    return data


def snapshot_to_json(
    state: ProductState, drift: DriftReport, confidence: ConfidenceResult,
    transitions: list[TransitionRecord] | None = None,
    indent: int = 2,
) -> str:
    """Serialize a complete runtime snapshot to a JSON string."""
    return json.dumps(snapshot_to_dict(state, drift, confidence, transitions), indent=indent)
