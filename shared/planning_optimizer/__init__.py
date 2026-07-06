"""Planning Optimizer — Intelligent multi-objective optimization for training plans.

Usage:
    from shared.planning_optimizer import PlanningOptimizerOrchestrator

    orch = PlanningOptimizerOrchestrator()
    result = orch.optimize_from_plan(macrocycle_json)
    print(result.best_score_summary)
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from typing import Any, Optional

from shared.planning_optimizer.constraints import ConstraintChecker
from shared.planning_optimizer.domain import (
    CandidateStatus,
    ConstraintType,
    ObjectiveType,
    OptimizationCandidate,
    OptimizationConstraint,
    OptimizationHistoryEntry,
    OptimizationObjective,
    OptimizationReport,
    OptimizationRequest,
    OptimizationResult,
    OptimizationScore,
    OptimizerConfig,
    OptimizerState,
    OptimizerStatus,
)
from shared.planning_optimizer.engine import OptimizationEngine, PlanMutator
from shared.planning_optimizer.events import PLANNING_OPTIMIZER_EVENT_REGISTRY
from shared.planning_optimizer.history import PlanningOptimizerHistory
from shared.planning_optimizer.metrics import OptimizerMetrics, OptimizerMetricsCollector
from shared.planning_optimizer.objectives import ObjectiveScorer
from shared.planning_optimizer.reports import PlanningOptimizerReports
from shared.planning_optimizer.repository import PlanningOptimizerRepository
from shared.planning_optimizer.scoring import CompositeScorer
from shared.planning_optimizer.serializer import PlanningOptimizerSerializer
from shared.planning_optimizer.simulation import SimulationPipeline


def _generate_id(prefix: str = "opt") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


class PlanningOptimizerOrchestrator:
    """Unified entry point for all planning optimization operations.

    Provides a single facade over the OptimizationEngine, SimulationPipeline,
    CompositeScorer, MetricsCollector, Repository, Serializer, History, and Reports.
    """

    def __init__(
        self,
        config: OptimizerConfig = OptimizerConfig(),
    ) -> None:
        self.config = config
        self.engine = OptimizationEngine(config)
        self.repository = PlanningOptimizerRepository()
        self.serializer = PlanningOptimizerSerializer()
        self.history = PlanningOptimizerHistory()
        self.reports = PlanningOptimizerReports()
        self.metrics_collector = OptimizerMetricsCollector()
        self._simulation = SimulationPipeline()

    # ── Optimization ──────────────────────────────────────────────────

    def optimize(
        self,
        request: OptimizationRequest,
    ) -> OptimizationResult:
        request.status = OptimizerStatus.RUNNING
        self.repository.save_request(request)

        result = self.engine.optimize(request)

        self.repository.save_result(result)
        self.repository.save_candidates(request.request_id, result.all_candidates)
        self.history.record_snapshot(request.request_id, result, "Optimization completed")
        self.metrics_collector.record(result)

        return result

    def optimize_from_plan(
        self,
        macrocycle_json: str,
        objectives: list[OptimizationObjective] | None = None,
        constraints: list[OptimizationConstraint] | None = None,
        population_size: int | None = None,
        max_generations: int | None = None,
    ) -> OptimizationResult:
        request = OptimizationRequest(
            request_id=_generate_id("req"),
            base_plan_json=macrocycle_json,
            objectives=objectives or [
                OptimizationObjective(
                    objective_type=ObjectiveType.MAXIMIZE_HYPERTROPHY,
                    weight=1.0,
                    is_primary=True,
                ),
                OptimizationObjective(
                    objective_type=ObjectiveType.MINIMIZE_FATIGUE,
                    weight=0.7,
                ),
                OptimizationObjective(
                    objective_type=ObjectiveType.MAXIMIZE_ADHERENCE,
                    weight=0.8,
                ),
            ],
            constraints=constraints or [
                OptimizationConstraint(
                    constraint_type=ConstraintType.FREQUENCY,
                    max_value=6.0,
                    min_value=3.0,
                ),
                OptimizationConstraint(
                    constraint_type=ConstraintType.SAFETY,
                    max_value=120.0,
                ),
            ],
            population_size=population_size or self.config.default_population_size,
            max_generations=max_generations or self.config.default_max_generations,
            mutation_rate=self.config.default_mutation_rate,
            crossover_rate=self.config.default_crossover_rate,
            elite_ratio=self.config.default_elite_ratio,
            status=OptimizerStatus.PENDING,
            created_at=datetime.now().isoformat(),
        )
        return self.optimize(request)

    # ── Evaluation ────────────────────────────────────────────────────

    def evaluate_plan(
        self,
        plan_data: dict[str, Any],
        objectives: list[OptimizationObjective] | None = None,
        constraints: list[OptimizationConstraint] | None = None,
    ) -> OptimizationScore:
        objs = objectives or [
            OptimizationObjective(objective_type=ObjectiveType.MAXIMIZE_HYPERTROPHY, weight=1.0),
        ]
        cons = constraints or []
        return CompositeScorer.score(plan_data, objs, cons)

    def check_constraints(
        self,
        plan_data: dict[str, Any],
        constraints: list[OptimizationConstraint] | None = None,
    ) -> tuple[bool, list[str], int]:
        cons = constraints or []
        return ConstraintChecker.check_all(plan_data, cons)

    def simulate_plan(
        self,
        plan_data: dict[str, Any],
        objectives: list[OptimizationObjective] | None = None,
        constraints: list[OptimizationConstraint] | None = None,
    ) -> OptimizationCandidate:
        objs = objectives or [
            OptimizationObjective(objective_type=ObjectiveType.MAXIMIZE_HYPERTROPHY, weight=1.0),
        ]
        cons = constraints or []
        return self._simulation.run(plan_data, objs, cons)

    # ── Mutation ──────────────────────────────────────────────────────

    def mutate_plan(self, plan_data: dict[str, Any]) -> dict[str, Any]:
        return PlanMutator.apply_random_mutation(plan_data)

    # ── Requests ──────────────────────────────────────────────────────

    def create_request(
        self,
        base_plan_json: str = "",
        objectives: list[dict[str, Any]] | None = None,
        constraints: list[dict[str, Any]] | None = None,
        population_size: int = 20,
        max_generations: int = 10,
    ) -> OptimizationRequest:
        request = OptimizationRequest(
            request_id=_generate_id("req"),
            base_plan_json=base_plan_json,
            objectives=[
                self.serializer.objective_from_dict(o) if isinstance(o, dict) else o
                for o in (objectives or [])
            ] or [
                OptimizationObjective(
                    objective_type=ObjectiveType.MAXIMIZE_HYPERTROPHY,
                    weight=1.0,
                    is_primary=True,
                ),
            ],
            constraints=[
                self.serializer.constraint_from_dict(c) if isinstance(c, dict) else c
                for c in (constraints or [])
            ],
            population_size=population_size,
            max_generations=max_generations,
            status=OptimizerStatus.PENDING,
            created_at=datetime.now().isoformat(),
        )
        self.repository.save_request(request)
        return request

    def get_request(self, request_id: str) -> OptimizationRequest | None:
        return self.repository.find_request(request_id)

    def list_requests(self) -> list[OptimizationRequest]:
        return self.repository.list_requests()

    def delete_request(self, request_id: str) -> bool:
        self.history.clear(request_id)
        self.repository.delete_candidates(request_id)
        return self.repository.delete_request(request_id)

    # ── Results ───────────────────────────────────────────────────────

    def get_result(self, result_id: str) -> OptimizationResult | None:
        return self.repository.find_result(result_id)

    def get_result_by_request(self, request_id: str) -> OptimizationResult | None:
        return self.repository.find_result_by_request(request_id)

    def list_results(self) -> list[OptimizationResult]:
        return self.repository.list_results()

    # ── Candidates ────────────────────────────────────────────────────

    def get_best_candidate(self, request_id: str) -> OptimizationCandidate | None:
        candidates = self.repository.find_candidates(request_id)
        feasible = [c for c in candidates if c.is_feasible]
        if not feasible:
            return None
        return max(feasible, key=lambda c: c.scores.overall)

    def get_candidates(self, request_id: str) -> list[OptimizationCandidate]:
        return self.repository.find_candidates(request_id)

    # ── Metrics ───────────────────────────────────────────────────────

    def get_metrics(self) -> OptimizerMetrics:
        return self.metrics_collector.compute()

    # ── History ───────────────────────────────────────────────────────

    def get_snapshots(self, request_id: str):
        return self.history.get_snapshots(request_id)

    def get_history(self, request_id: str) -> list[OptimizationHistoryEntry]:
        return self.history.get_entries(request_id)

    # ── Reports ───────────────────────────────────────────────────────

    def optimization_report(self, result_id: str) -> str:
        result = self.repository.find_result(result_id)
        if result is None:
            return "No result found."
        return self.reports.generate_optimization_report(result)

    def candidate_report(self, candidate_id: str, request_id: str) -> str:
        candidates = self.repository.find_candidates(request_id)
        for c in candidates:
            if c.candidate_id == candidate_id:
                return self.reports.generate_candidate_report(c)
        return "Candidate not found."

    def metrics_report(self) -> str:
        metrics = self.get_metrics()
        return self.reports.generate_metrics_report(metrics)

    def summary_report(
        self,
        result_id: str | None = None,
    ) -> str:
        result = None
        if result_id:
            result = self.repository.find_result(result_id)
        metrics = self.get_metrics()
        return self.reports.generate_summary_report(result, metrics)

    # ── State ─────────────────────────────────────────────────────────

    def get_state(self) -> OptimizerState:
        return self.repository.get_state()

    # ── Serialization ─────────────────────────────────────────────────

    def request_to_json(self, request: OptimizationRequest) -> str:
        return json.dumps(self.serializer.request_to_dict(request))

    def request_from_json(self, json_str: str) -> OptimizationRequest:
        return self.serializer.request_from_dict(json.loads(json_str))

    def result_to_json(self, result: OptimizationResult) -> str:
        return json.dumps(self.serializer.result_to_dict(result))

    def result_from_json(self, json_str: str) -> OptimizationResult:
        return self.serializer.result_from_dict(json.loads(json_str))

    # ── Integration Helpers ───────────────────────────────────────────

    def get_objective_defaults(self) -> dict[str, Any]:
        return {
            obj_type.value: obj_type.default_weight
            for obj_type in ObjectiveType
        }


__all__ = (
    # Orchestrator
    "PlanningOptimizerOrchestrator",

    # Engine
    "OptimizationEngine",
    "PlanMutator",

    # Simulation
    "SimulationPipeline",

    # Scoring
    "CompositeScorer",

    # Objectives
    "ObjectiveScorer",
    "ObjectiveType",
    "OptimizationObjective",

    # Constraints
    "ConstraintChecker",
    "ConstraintType",
    "OptimizationConstraint",

    # Domain
    "OptimizationRequest",
    "OptimizationResult",
    "OptimizationCandidate",
    "OptimizationScore",
    "OptimizationHistoryEntry",
    "OptimizationReport",
    "OptimizerConfig",
    "OptimizerState",
    "CandidateStatus",
    "OptimizerStatus",

    # Metrics
    "OptimizerMetrics",
    "OptimizerMetricsCollector",

    # Reports
    "PlanningOptimizerReports",

    # Repository
    "PlanningOptimizerRepository",

    # Serializer
    "PlanningOptimizerSerializer",

    # History
    "PlanningOptimizerHistory",

    # Events
    "PLANNING_OPTIMIZER_EVENT_REGISTRY",
)
