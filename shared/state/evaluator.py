"""State Evaluator — evaluates the current product state from canonical data.

Consumes ONLY: Capability Platform, Kernel, Evolution Engine, Product Knowledge Graph.
Never duplicates information.
"""

from __future__ import annotations

from datetime import UTC, datetime

from shared.state.indicators import IndicatorSet, compute_indicators
from shared.state.state import STATE_METADATA, ProductState, ProductStateType


class StateEvaluator:
    """Evaluates the current product state from canonical indicators.

    Stateless — every call to evaluate() computes fresh from source data.
    """

    def evaluate(self) -> ProductState:
        """Compute the current product state from all indicator data."""
        indicators = compute_indicators()
        state_type = self._determine_state(indicators)
        primary_reason, supporting = self._determine_reasoning(state_type, indicators)
        drift_score = self._compute_drift_score(indicators)
        debt_pressure = self._compute_debt_pressure(indicators)

        return ProductState(
            state_type=state_type,
            timestamp=datetime.now(UTC).isoformat(),
            confidence=indicators.overall_health,
            risk_score=indicators.risk_score,
            drift_score=drift_score,
            active_capabilities=indicators.total_capabilities - indicators.not_started,
            total_capabilities=indicators.total_capabilities,
            capabilities_complete=indicators.complete,
            capabilities_in_progress=indicators.in_progress,
            capabilities_not_started=indicators.not_started,
            capabilities_blocked=indicators.blocked,
            architecture_health=indicators.architecture_health,
            documentation_health=indicators.documentation_health,
            test_health=indicators.test_health,
            overall_health=indicators.overall_health,
            technical_debt=indicators.total_debt,
            blocking_debt=indicators.blocking_debt,
            debt_pressure=debt_pressure,
            release_readiness=indicators.release_readiness,
            release_blockers=indicators.release_blockers,
            product_momentum=indicators.product_momentum,
            blockers=indicators.blockers,
            primary_reason=primary_reason,
            supporting_factors=tuple(supporting),
        )

    def evaluate_from_indicators(self, indicators: IndicatorSet) -> ProductState:
        """Evaluate state from pre-computed indicators (for testing)."""
        state_type = self._determine_state(indicators)
        primary_reason, supporting = self._determine_reasoning(state_type, indicators)
        drift_score = self._compute_drift_score(indicators)
        debt_pressure = self._compute_debt_pressure(indicators)

        return ProductState(
            state_type=state_type,
            timestamp=datetime.now(UTC).isoformat(),
            confidence=indicators.overall_health,
            risk_score=indicators.risk_score,
            drift_score=drift_score,
            active_capabilities=indicators.total_capabilities - indicators.not_started,
            total_capabilities=indicators.total_capabilities,
            capabilities_complete=indicators.complete,
            capabilities_in_progress=indicators.in_progress,
            capabilities_not_started=indicators.not_started,
            capabilities_blocked=indicators.blocked,
            architecture_health=indicators.architecture_health,
            documentation_health=indicators.documentation_health,
            test_health=indicators.test_health,
            overall_health=indicators.overall_health,
            technical_debt=indicators.total_debt,
            blocking_debt=indicators.blocking_debt,
            debt_pressure=debt_pressure,
            release_readiness=indicators.release_readiness,
            release_blockers=indicators.release_blockers,
            product_momentum=indicators.product_momentum,
            blockers=indicators.blockers,
            primary_reason=primary_reason,
            supporting_factors=tuple(supporting),
        )

    def _determine_state(self, indicators: IndicatorSet) -> ProductStateType:
        """Determine the current product state from indicators using decision rules.

        Rules are ordered from most specific to least specific.
        """
        # BLOCKED: high blocking debt or many blockers
        if indicators.blocking_debt >= 3 or len(indicators.blockers) >= 2:
            return ProductStateType.BLOCKED

        # READY_FOR_RELEASE: very high health and readiness
        if indicators.overall_health >= 85 and indicators.release_readiness >= 90:
            return ProductStateType.READY_FOR_RELEASE

        # MAINTENANCE: near-complete capabilities, no new work
        if indicators.complete >= indicators.total_capabilities * 0.8 and indicators.not_started == 0:
            return ProductStateType.MAINTENANCE

        # RELEASE_CANDIDATE: high health, high readiness, capabilities mostly complete
        if (indicators.overall_health >= 70 and indicators.release_readiness >= 70
                and indicators.completion_percent >= 80):
            return ProductStateType.RELEASE_CANDIDATE

        # OPTIMIZING: high health but low active development
        if indicators.overall_health >= 50 and indicators.in_progress == 0 and indicators.not_started <= 2:
            return ProductStateType.OPTIMIZING

        # STABLE: high health, most capabilities complete
        if (indicators.overall_health >= 60 and indicators.completion_percent >= 70
                and indicators.in_progress <= 3):
            return ProductStateType.STABLE

        # REFACTORING: high debt, reasonable health
        if indicators.total_debt >= 10 and indicators.overall_health >= 30:
            return ProductStateType.REFACTORING

        # GROWING: active capability development
        if indicators.in_progress > 0 and indicators.completion_percent >= 30:
            return ProductStateType.GROWING

        # BOOTSTRAPPING: early stage, few capabilities complete
        return ProductStateType.BOOTSTRAPPING

    def _determine_reasoning(
        self, state_type: ProductStateType, indicators: IndicatorSet
    ) -> tuple[str, list[str]]:
        """Generate human-readable reasoning for the state determination."""
        reasons: list[str] = []

        reasons.append(f"Overall health: {indicators.overall_health}/100")
        reasons.append(f"Capabilities: {indicators.complete}/{indicators.total_capabilities} complete")
        reasons.append(f"Release readiness: {indicators.release_readiness}/100")

        if indicators.blocking_debt > 0:
            reasons.append(f"Blocking debt items: {indicators.blocking_debt}")
        if indicators.total_debt > 0:
            reasons.append(f"Total technical debt: {indicators.total_debt} items")
        if indicators.product_momentum != 0:
            reasons.append(f"Product momentum: {indicators.product_momentum:+.1f}")

        label = STATE_METADATA[state_type]["label"]
        primary = f"Product is in {label} state based on health={indicators.overall_health}, completion={indicators.completion_percent}%, readiness={indicators.release_readiness}"

        return primary, reasons

    def _compute_drift_score(self, indicators: IndicatorSet) -> float:
        """Compute a drift score based on variance between health dimensions."""
        scores = [indicators.architecture_health, indicators.documentation_health,
                  indicators.test_health, indicators.capability_health]
        if not scores:
            return 0.0
        avg = sum(scores) / len(scores)
        variance = sum((s - avg) ** 2 for s in scores) / len(scores)
        # Normalize: max variance is ~2500 (100^2), so divide by 25 for 0-100
        drift = min(variance / 25.0, 100.0)
        return round(drift, 1)

    def _compute_debt_pressure(self, indicators: IndicatorSet) -> float:
        """Compute debt pressure: how much technical debt impedes progress."""
        if indicators.total_capabilities == 0:
            return 0.0
        debt_ratio = indicators.total_debt / max(indicators.total_capabilities, 1)
        blocking_ratio = indicators.blocking_debt / max(indicators.total_debt, 1)
        pressure = min(debt_ratio * 20.0 + blocking_ratio * 50.0, 100.0)
        return round(pressure, 1)
