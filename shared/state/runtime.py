"""State Runtime — orchestrates the Product State Engine lifecycle.

The StateOrchestrator is the unified entry point for consuming product state.
It coordinates the evaluator, drift analyzer, confidence scorer, and transition engine.
"""

from __future__ import annotations

from dataclasses import dataclass, field

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
from shared.state.state import ProductState
from shared.state.transitions import TransitionEngine, TransitionRecord


@dataclass
class StateOrchestrator:
    """Unified entry point for all product state analysis.

    Usage:
        engine = StateOrchestrator()
        state = engine.get_current_state()
        print(state.label)  # "Growing"
        print(state.primary_reason)
    """

    evaluator: StateEvaluator = field(default_factory=StateEvaluator)
    drift_analyzer: DriftAnalyzer = field(default_factory=DriftAnalyzer)
    confidence_scorer: ConfidenceScorer = field(default_factory=ConfidenceScorer)
    transition_engine: TransitionEngine = field(default_factory=TransitionEngine)

    _last_state: ProductState | None = None

    def get_current_state(self) -> ProductState:
        """Evaluate and return the current product state."""
        state = self.evaluator.evaluate()
        self._track_transition(state)
        return state

    def get_indicators(self) -> IndicatorSet:
        """Return the current set of product indicators."""
        return compute_indicators()

    def get_drift(self) -> DriftReport:
        """Return the current drift analysis."""
        return self.drift_analyzer.analyze()

    def get_confidence(self) -> ConfidenceResult:
        """Return the current confidence assessment."""
        return self.confidence_scorer.score()

    def get_transition_history(self) -> list[TransitionRecord]:
        """Return all recorded transitions."""
        return self.transition_engine.get_history()

    def get_runtime_snapshot(self) -> dict:
        """Return a complete runtime snapshot as a dictionary."""
        state = self.get_current_state()
        drift = self.drift_analyzer.analyze()
        confidence = self.confidence_scorer.score()
        return {
            "state": state.to_dict(),
            "drift": {
                "overall_drift": drift.overall_drift,
                "architecture_drift": drift.architecture_drift,
                "documentation_drift": drift.documentation_drift,
                "capability_drift": drift.capability_drift,
                "knowledge_drift": drift.knowledge_drift,
                "rfc_drift": drift.rfc_drift,
            },
            "confidence": {
                "overall": confidence.overall,
                "state_confidence": confidence.state_confidence,
                "release_confidence": confidence.release_confidence,
            },
        }

    def generate_report(self, report_type: str = "state") -> str:
        """Generate a report by type.

        Supported types: state, drift, confidence, runtime, release
        """
        state = self.get_current_state()
        drift = self.drift_analyzer.analyze()
        confidence = self.confidence_scorer.score()

        report_map = {
            "state": lambda: generate_state_report(state),
            "drift": lambda: generate_drift_report(drift),
            "confidence": lambda: generate_confidence_report(confidence),
            "runtime": lambda: generate_runtime_snapshot(state, drift, confidence),
            "release": lambda: generate_release_confidence_report(state, confidence),
        }
        generator = report_map.get(report_type)
        if generator is None:
            return f"Unknown report type: {report_type}. Supported: {', '.join(report_map.keys())}"
        return generator()

    def _track_transition(self, new_state: ProductState) -> None:
        """Track state transitions automatically."""
        if self._last_state is not None and self._last_state.state_type != new_state.state_type:
            reason = self.transition_engine.generate_transition_reason(
                self._last_state.state_type, new_state.state_type,
            )
            self.transition_engine.record_transition(
                from_state=self._last_state.state_type,
                to_state=new_state.state_type,
                reason=reason,
                confidence=new_state.confidence,
            )
        self._last_state = new_state
