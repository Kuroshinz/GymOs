"""Planning Optimizer Engine — Generates, mutates, evaluates, ranks, and selects optimal training plans."""

from __future__ import annotations

import copy
import json
import random
import uuid
from datetime import datetime
from typing import Any

from shared.planning_optimizer.domain import (
    CandidateStatus,
    OptimizationCandidate,
    OptimizationRequest,
    OptimizationResult,
    OptimizerConfig,
    OptimizerStatus,
)
from shared.planning_optimizer.simulation import SimulationPipeline


def _generate_id(prefix: str = "opt") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


class OptimizationEngine:
    """Evolutionary optimization engine for training plans.

    Generates a population of candidate plans, evaluates them against
    objectives and constraints, then evolves the population through
    selection, crossover, and mutation over multiple generations.
    """

    def __init__(
        self,
        config: OptimizerConfig = OptimizerConfig(),
    ) -> None:
        self.config = config
        self._simulation = SimulationPipeline()
        self._rng = random.Random(42)

    def optimize(
        self,
        request: OptimizationRequest,
    ) -> OptimizationResult:
        """Run the full optimization from a request."""
        base_plan = json.loads(request.base_plan_json) if request.base_plan_json else {}
        start_time = datetime.now()

        request.status = OptimizerStatus.RUNNING

        population = self._initialize_population(
            base_plan, request, request.population_size
        )

        for generation in range(request.max_generations):
            evaluated = self._evaluate_population(population, request)

            ranked = self._rank_population(evaluated)

            best_score = ranked[0].scores.overall if ranked else 0.0

            if self._check_convergence(ranked, generation):
                population = [json.loads(c.macrocycle_json) for c in ranked if c.macrocycle_json] or population
                break

            new_population = self._create_next_generation(
                ranked, request, generation + 1
            )
            population = new_population

        final_population = self._evaluate_population(population, request)
        final_ranked = self._rank_population(final_population)

        duration = (datetime.now() - start_time).total_seconds()

        return self._simulation.compute_result(
            request_id=request.request_id,
            all_candidates=final_ranked,
            total_generations=request.max_generations,
            duration_seconds=duration,
            completed_at=datetime.now().isoformat(),
        )

    def _initialize_population(
        self,
        base_plan: dict[str, Any],
        request: OptimizationRequest,
        size: int,
    ) -> list[dict[str, Any]]:
        population: list[dict[str, Any]] = []
        for i in range(size):
            candidate = copy.deepcopy(base_plan) if base_plan else self._create_base_plan(request)
            self._mutate_plan(candidate, request.mutation_rate)
            population.append(candidate)
        return population

    def _create_base_plan(self, request: OptimizationRequest) -> dict[str, Any]:
        return {
            "total_sets": 0,
            "total_weeks": 12,
            "total_sessions": 0,
            "sessions_per_week": 4,
            "mesocycles": [],
            "weeks": [],
        }

    def _evaluate_population(
        self,
        population: list[dict[str, Any]],
        request: OptimizationRequest,
    ) -> list[OptimizationCandidate]:
        return [
            self._simulation.run(p, request.objectives, request.constraints)
            for p in population
        ]

    def _rank_population(
        self,
        candidates: list[OptimizationCandidate],
    ) -> list[OptimizationCandidate]:
        feasible = [c for c in candidates if c.is_feasible]
        infeasible = [c for c in candidates if not c.is_feasible]

        feasible.sort(key=lambda c: c.scores.overall, reverse=True)
        infeasible.sort(key=lambda c: c.scores.overall, reverse=True)

        for i, c in enumerate(feasible):
            c = OptimizationCandidate(
                candidate_id=c.candidate_id,
                macrocycle_json=c.macrocycle_json,
                scores=c.scores,
                mutations=c.mutations,
                generation=c.generation,
                rank=i + 1,
                status=CandidateStatus.SELECTED if i == 0 else CandidateStatus.ACTIVE,
                constraint_violations=c.constraint_violations,
                is_feasible=c.is_feasible,
            )
            feasible[i] = c

        for i, c in enumerate(infeasible):
            c = OptimizationCandidate(
                candidate_id=c.candidate_id,
                macrocycle_json=c.macrocycle_json,
                scores=c.scores,
                mutations=c.mutations,
                generation=c.generation,
                rank=len(feasible) + i + 1,
                status=CandidateStatus.INFEASIBLE,
                constraint_violations=c.constraint_violations,
                is_feasible=c.is_feasible,
            )
            infeasible[i] = c

        return feasible + infeasible

    def _check_convergence(
        self,
        ranked: list[OptimizationCandidate],
        generation: int,
    ) -> bool:
        if not self.config.enable_early_stop:
            return False
        if generation < self.config.max_stall_generations:
            return False
        recent = ranked[:max(5, len(ranked) // 4)]
        if len(recent) < 2:
            return False
        scores = [c.scores.overall for c in recent]
        return max(scores) - min(scores) <= self.config.convergence_threshold

    def _create_next_generation(
        self,
        ranked: list[OptimizationCandidate],
        request: OptimizationRequest,
        next_generation: int,
    ) -> list[dict[str, Any]]:
        population_size = len(ranked)
        new_population: list[dict[str, Any]] = []

        elite_count = max(1, int(population_size * request.elite_ratio))
        for c in ranked[:elite_count]:
            plan = json.loads(c.macrocycle_json)
            new_population.append(plan)

        while len(new_population) < population_size:
            parent_a = self._tournament_select(ranked)
            parent_b = self._tournament_select(ranked)

            if self._rng.random() < request.crossover_rate:
                child = self._crossover(
                    json.loads(parent_a.macrocycle_json),
                    json.loads(parent_b.macrocycle_json),
                )
            else:
                child = copy.deepcopy(json.loads(parent_a.macrocycle_json))

            if self._rng.random() < request.mutation_rate:
                self._mutate_plan(child, request.mutation_rate)
                child_mutations = parent_a.mutations + ["mutated"]
            else:
                child_mutations = parent_a.mutations

            if self.config.enable_diversity_maintenance and self._rng.random() < 0.1:
                self._mutate_plan(child, 0.5)

            new_population.append(child)

        return new_population

    def _tournament_select(
        self,
        candidates: list[OptimizationCandidate],
        tournament_size: int = 3,
    ) -> OptimizationCandidate:
        pool = [c for c in candidates if c.is_feasible] or candidates
        actual_size = min(tournament_size, len(pool))
        if actual_size == 0:
            return candidates[0] if candidates else OptimizationCandidate()
        tournament = self._rng.sample(pool, actual_size)
        return max(tournament, key=lambda c: c.scores.overall)

    def _crossover(
        self,
        parent_a: dict[str, Any],
        parent_b: dict[str, Any],
    ) -> dict[str, Any]:
        child: dict[str, Any] = {}

        for key in set(list(parent_a.keys()) + list(parent_b.keys())):
            if key in ("mesocycles", "weeks"):
                child[key] = self._crossover_list(
                    parent_a.get(key, []),
                    parent_b.get(key, []),
                )
            elif isinstance(parent_a.get(key), (int, float)):
                child[key] = self._rng.choice([parent_a.get(key, 0), parent_b.get(key, 0)])
            else:
                child[key] = self._rng.choice([
                    parent_a.get(key),
                    parent_b.get(key),
                ])

        return child

    def _crossover_list(
        self,
        list_a: list[Any],
        list_b: list[Any],
    ) -> list[Any]:
        if not list_a or not list_b:
            return list_a or list_b
        split = self._rng.randint(0, min(len(list_a), len(list_b)))
        return list_a[:split] + list_b[split:]

    def _mutate_plan(
        self,
        plan: dict[str, Any],
        mutation_rate: float,
    ) -> None:
        if self._rng.random() < mutation_rate:
            current = plan.get("sessions_per_week")
            if current is None:
                current = 4
            plan["sessions_per_week"] = self._mutate_value(
                current, 1, 7
            )
        if self._rng.random() < mutation_rate:
            current = plan.get("total_weeks")
            if current is None:
                current = 12
            plan["total_weeks"] = self._mutate_value(
                current, 4, 52
            )
        if self._rng.random() < mutation_rate:
            total_sets = plan.get("total_sets", 0)
            if total_sets is None:
                total_sets = 0
            total_weeks = plan.get("total_weeks", 1)
            if total_weeks is None or total_weeks == 0:
                total_weeks = 1
            avg_sets = total_sets / total_weeks
            new_avg = self._mutate_value(avg_sets, 10, 200)
            plan["total_sets"] = int(new_avg * total_weeks)

        mesocycles = plan.get("mesocycles", [])
        if mesocycles is None:
            mesocycles = []
        for meso in mesocycles:
            if self._rng.random() < mutation_rate:
                current = meso.get("week_count", 4)
                if current is None:
                    current = 4
                meso["week_count"] = self._mutate_value(
                    current, 2, 8
                )
            if self._rng.random() < mutation_rate:
                current_goal = meso.get("goal", "hypertrophy")
                goals = ["hypertrophy", "strength", "endurance", "conditioning"]
                if current_goal in goals:
                    remaining = [g for g in goals if g != current_goal]
                    meso["goal"] = self._rng.choice(remaining)
            if self._rng.random() < mutation_rate * 0.5:
                meso["has_deload"] = not meso.get("has_deload", False)

    def _mutate_value(self, current: float, min_val: float, max_val: float) -> float:
        delta = (self._rng.random() - 0.5) * (max_val - min_val) * 0.2
        return max(min_val, min(max_val, current + delta))


class PlanMutator:
    """Stateless plan mutation operations.

    Each mutation is a pure function that returns a modified copy.
    """

    @staticmethod
    def mutate_sessions_per_week(
        plan_data: dict[str, Any],
        min_sessions: int = 1,
        max_sessions: int = 7,
    ) -> dict[str, Any]:
        result = copy.deepcopy(plan_data)
        current = result.get("sessions_per_week", 4)
        adjustments = [-1, 1]
        new_val = max(min_sessions, min(max_sessions, current + random.choice(adjustments)))
        result["sessions_per_week"] = new_val
        return result

    @staticmethod
    def mutate_total_weeks(
        plan_data: dict[str, Any],
        min_weeks: int = 4,
        max_weeks: int = 52,
    ) -> dict[str, Any]:
        result = copy.deepcopy(plan_data)
        current = result.get("total_weeks", 12)
        adjustments = [-4, -2, 2, 4]
        new_val = max(min_weeks, min(max_weeks, current + random.choice(adjustments)))
        result["total_weeks"] = new_val
        return result

    @staticmethod
    def mutate_total_sets(
        plan_data: dict[str, Any],
        min_avg_sets: int = 10,
        max_avg_sets: int = 200,
    ) -> dict[str, Any]:
        result = copy.deepcopy(plan_data)
        total_weeks = max(result.get("total_weeks", 1), 1)
        current_total = result.get("total_sets", 0)
        current_avg = current_total / total_weeks
        adjustment = random.uniform(-20, 20)
        new_avg = max(min_avg_sets, min(max_avg_sets, current_avg + adjustment))
        result["total_sets"] = int(new_avg * total_weeks)
        return result

    @staticmethod
    def mutate_mesocycle_goal(
        plan_data: dict[str, Any],
    ) -> dict[str, Any]:
        result = copy.deepcopy(plan_data)
        mesocycles = result.get("mesocycles", [])
        if not mesocycles:
            return result
        idx = random.randint(0, len(mesocycles) - 1)
        current = mesocycles[idx].get("goal", "hypertrophy")
        goals = ["hypertrophy", "strength", "endurance", "conditioning"]
        available = [g for g in goals if g != current]
        mesocycles[idx]["goal"] = random.choice(available)
        return result

    @staticmethod
    def mutate_mesocycle_weeks(
        plan_data: dict[str, Any],
    ) -> dict[str, Any]:
        result = copy.deepcopy(plan_data)
        mesocycles = result.get("mesocycles", [])
        if not mesocycles:
            return result
        idx = random.randint(0, len(mesocycles) - 1)
        current = mesocycles[idx].get("week_count", 4)
        adjustments = [-1, 1]
        new_val = max(2, min(8, current + random.choice(adjustments)))
        mesocycles[idx]["week_count"] = new_val
        return result

    @staticmethod
    def apply_random_mutation(
        plan_data: dict[str, Any],
    ) -> dict[str, Any]:
        mutations = [
            PlanMutator.mutate_sessions_per_week,
            PlanMutator.mutate_total_weeks,
            PlanMutator.mutate_total_sets,
            PlanMutator.mutate_mesocycle_goal,
            PlanMutator.mutate_mesocycle_weeks,
        ]
        mutator = random.choice(mutations)
        return mutator(plan_data)
