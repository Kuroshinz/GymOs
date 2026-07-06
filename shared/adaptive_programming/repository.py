"""Adaptive Programming Repository — Append-only, immutable, in-memory store."""

from __future__ import annotations

from shared.adaptive_programming.domain import (
    AdaptationHistory,
    AdaptationSnapshot,
    AdaptationType,
    AdaptiveDecision,
    AdaptivePlan,
    DecisionStatus,
)


class AdaptiveProgrammingRepository:
    """In-memory repository for adaptive programming data.

    Plans are stored by ``plan_id`` (latest overwrites). All other entities
    are append-only — once written they are never mutated.
    """

    def __init__(self) -> None:
        self._plans: dict[str, AdaptivePlan] = {}
        self._decisions: dict[str, AdaptiveDecision] = {}
        self._history: dict[str, AdaptationHistory] = {}
        self._snapshots: dict[str, AdaptationSnapshot] = {}

    # ── Plans ───────────────────────────────────────────────────────────

    def store_plan(self, plan: AdaptivePlan) -> None:
        self._plans[plan.plan_id] = plan

    def get_plan(self, plan_id: str) -> AdaptivePlan | None:
        return self._plans.get(plan_id)

    def list_plans(self) -> list[AdaptivePlan]:
        return list(self._plans.values())

    # ── Decisions ───────────────────────────────────────────────────────

    def store_decision(self, decision: AdaptiveDecision) -> None:
        self._decisions[decision.decision_id] = decision

    def get_decision(self, decision_id: str) -> AdaptiveDecision | None:
        return self._decisions.get(decision_id)

    def list_decisions(self) -> list[AdaptiveDecision]:
        return list(self._decisions.values())

    def list_decisions_by_type(
        self, adaptation_type: AdaptationType
    ) -> list[AdaptiveDecision]:
        return [
            d for d in self._decisions.values()
            if d.adaptation_type == adaptation_type
        ]

    def list_decisions_by_status(
        self, status: DecisionStatus
    ) -> list[AdaptiveDecision]:
        return [
            d for d in self._decisions.values()
            if d.status == status
        ]

    # ── History ─────────────────────────────────────────────────────────

    def store_history(self, history: AdaptationHistory) -> None:
        self._history[history.history_id] = history

    def get_history(self, history_id: str) -> AdaptationHistory | None:
        return self._history.get(history_id)

    def list_history(self) -> list[AdaptationHistory]:
        return list(self._history.values())

    # ── Snapshots ───────────────────────────────────────────────────────

    def store_snapshot(self, snapshot: AdaptationSnapshot) -> None:
        self._snapshots[snapshot.snapshot_id] = snapshot

    def get_snapshot(self, snapshot_id: str) -> AdaptationSnapshot | None:
        return self._snapshots.get(snapshot_id)

    def list_snapshots(self) -> list[AdaptationSnapshot]:
        return list(self._snapshots.values())

    # ── Lifecycle ───────────────────────────────────────────────────────

    def clear_all(self) -> None:
        self._plans.clear()
        self._decisions.clear()
        self._history.clear()
        self._snapshots.clear()
