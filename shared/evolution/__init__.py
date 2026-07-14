"""Evolution Engine — understands how GymOS evolves over time.

Consumes the Kernel and Capability Platform to answer:
- How much has GymOS evolved?
- Which RFC contributed the most?
- Which capability improved the fastest?
- What is required to reach v1.0?
- What is the predicted maturity after the next RFCs?

Usage:
    from shared.evolution import EvolutionOrchestrator
    engine = EvolutionOrchestrator()
    report = engine.generate_evolution_report()
    print(report)
"""

from __future__ import annotations

from dataclasses import dataclass, field

from shared.evolution.capability_history import (
    compute_capability_velocities,
    compute_evolution_velocity,
    compute_rfc_contributions,
    find_fastest_capability,
    find_slowest_capability,
)
from shared.evolution.evolution_engine import (
    EvolutionChain,
    EvolutionSummary,
    EvolutionVelocity,
    RfcContribution,
)
from shared.evolution.forecast import (
    estimate_remaining_work,
    forecast_capability,
    forecast_product_completion,
    forecast_release,
)
from shared.evolution.milestone_graph import build_milestone_progress
from shared.evolution.product_forecast import compute_product_completion
from shared.evolution.reports import (
    generate_evolution_report,
    generate_evolution_summary_report,
    generate_forecast_report,
    generate_json_evolution_report,
    generate_product_journey,
    generate_timeline_report,
    generate_version_report,
)
from shared.evolution.rfc_history import (
    compute_rfc_impact_scores,
    find_most_impactful_rfc,
)
from shared.evolution.timeline import (
    build_capability_growth_timeline,
    build_evolution_chain,
    build_evolution_summary,
    build_evolution_timeline,
    build_rfc_timeline,
    build_version_progress,
)
from shared.evolution.version_graph import build_version_readiness_trend
from shared.kernel.kernel_runtime import KernelRuntimeOrchestrator
from shared.kernel.kernel_state import create_default_state


@dataclass
class EvolutionOrchestrator:
    """Unified entry point for all evolution analysis."""

    kernel: KernelRuntimeOrchestrator = field(default_factory=KernelRuntimeOrchestrator)

    def get_product_completion(self):
        return compute_product_completion()

    def get_capability_velocities(self):
        return compute_capability_velocities(self.kernel.snapshots)

    def get_fastest_capability(self):
        return find_fastest_capability(self.get_capability_velocities())

    def get_slowest_capability(self):
        return find_slowest_capability(self.get_capability_velocities())

    def get_rfc_impacts(self):
        return compute_rfc_impact_scores(self.kernel.snapshots)

    def get_most_impactful_rfc(self):
        return find_most_impactful_rfc(self.get_rfc_impacts())

    def get_version_readiness_trends(self):
        return build_version_readiness_trend(self.kernel.snapshots)

    def get_evolution_timeline(self):
        state = create_default_state()
        rfcs = list(state.rfcs.values())
        releases = list(state.releases.values())
        return build_evolution_timeline(self.kernel.snapshots, rfcs, releases)

    def get_rfc_timeline(self):
        state = create_default_state()
        return build_rfc_timeline(list(state.rfcs.values()))

    def get_capability_growth_timeline(self):
        return build_capability_growth_timeline(self.kernel.snapshots)

    def get_milestones(self):
        return build_milestone_progress()

    def get_forecast(self):
        return forecast_product_completion(self.kernel.snapshots)

    def get_release_forecast(self, version: str = "0.6.0"):
        return forecast_release(version, self.kernel.snapshots)

    def get_capability_forecast(self, capability_id: str):
        return forecast_capability(capability_id, self.kernel.snapshots)

    def get_remaining_work(self):
        return estimate_remaining_work()

    def get_version_progress(self):
        return build_version_progress()

    def get_evolution_chain(self) -> EvolutionChain:
        return build_evolution_chain()

    def get_evolution_velocity(self) -> EvolutionVelocity:
        return compute_evolution_velocity(self.kernel.snapshots)

    def get_rfc_contributions(self) -> list[RfcContribution]:
        return compute_rfc_contributions(self.kernel.snapshots)

    def get_evolution_summary(self) -> EvolutionSummary:
        return build_evolution_summary(self.kernel.snapshots)

    # ── Reports ──────────────────────────────────────────────────────────────

    def generate_evolution_report(self) -> str:
        completion = self.get_product_completion()
        velocities = self.get_capability_velocities()
        rfc_impacts = self.get_rfc_impacts()
        trends = self.get_version_readiness_trends()
        timeline = self.get_evolution_timeline()
        forecast = self.get_forecast()
        remaining = self.get_remaining_work()
        milestones = self.get_milestones()

        return generate_evolution_report(
            completion, velocities, rfc_impacts, trends, timeline, forecast, remaining, milestones,
        )

    def generate_version_report(self) -> str:
        return generate_version_report(self.get_milestones())

    def generate_timeline_report(self) -> str:
        return generate_timeline_report(self.get_evolution_timeline())

    def generate_forecast_report(self) -> str:
        return generate_forecast_report(self.get_forecast(), self.get_remaining_work(), self.get_milestones())

    def generate_product_journey(self) -> str:
        return generate_product_journey(self.get_milestones())

    def generate_evolution_summary_report(self) -> str:
        return generate_evolution_summary_report(self.get_evolution_summary())

    def generate_json_report(self) -> dict:
        completion = self.get_product_completion()
        velocities = self.get_capability_velocities()
        rfc_impacts = self.get_rfc_impacts()
        trends = self.get_version_readiness_trends()
        forecast = self.get_forecast()
        remaining = self.get_remaining_work()
        milestones = self.get_milestones()

        return generate_json_evolution_report(
            completion, velocities, rfc_impacts, trends, forecast, remaining, milestones,
        )
