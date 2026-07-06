"""Planning Optimizer Serializer — Dict/JSON serialization for all optimization domain models."""

from __future__ import annotations

from typing import Any

from shared.planning_optimizer.domain import (
    CandidateStatus,
    ConstraintType,
    ObjectiveType,
    OptimizationCandidate,
    OptimizationConstraint,
    OptimizationHistoryEntry,
    OptimizationObjective,
    OptimizationRequest,
    OptimizationResult,
    OptimizationScore,
    OptimizerConfig,
    OptimizerState,
    OptimizerStatus,
)


class PlanningOptimizerSerializer:
    """Full dict/JSON round-trip for all optimization domain models."""

    @staticmethod
    def objective_to_dict(obj: OptimizationObjective) -> dict[str, Any]:
        return {
            "objective_type": obj.objective_type.value,
            "weight": obj.weight,
            "target_value": obj.target_value,
            "is_primary": obj.is_primary,
        }

    @staticmethod
    def objective_from_dict(data: dict[str, Any]) -> OptimizationObjective:
        return OptimizationObjective(
            objective_type=ObjectiveType(data.get("objective_type", "maximize_hypertrophy")),
            weight=data.get("weight", 1.0),
            target_value=data.get("target_value"),
            is_primary=data.get("is_primary", False),
        )

    @staticmethod
    def constraint_to_dict(c: OptimizationConstraint) -> dict[str, Any]:
        return {
            "constraint_type": c.constraint_type.value,
            "max_value": c.max_value,
            "min_value": c.min_value,
            "value": c.value,
            "is_hard": c.is_hard,
            "description": c.description,
        }

    @staticmethod
    def constraint_from_dict(data: dict[str, Any]) -> OptimizationConstraint:
        return OptimizationConstraint(
            constraint_type=ConstraintType(data.get("constraint_type", "time")),
            max_value=data.get("max_value"),
            min_value=data.get("min_value"),
            value=data.get("value"),
            is_hard=data.get("is_hard", True),
            description=data.get("description", ""),
        )

    @staticmethod
    def score_to_dict(score: OptimizationScore) -> dict[str, Any]:
        return {
            "scientific_score": score.scientific_score,
            "recovery_score": score.recovery_score,
            "hypertrophy_score": score.hypertrophy_score,
            "compliance_score": score.compliance_score,
            "risk_score": score.risk_score,
            "overall": score.overall,
        }

    @staticmethod
    def score_from_dict(data: dict[str, Any]) -> OptimizationScore:
        return OptimizationScore(
            scientific_score=data.get("scientific_score", 0.0),
            recovery_score=data.get("recovery_score", 0.0),
            hypertrophy_score=data.get("hypertrophy_score", 0.0),
            compliance_score=data.get("compliance_score", 0.0),
            risk_score=data.get("risk_score", 0.0),
            overall=data.get("overall", 0.0),
        )

    @staticmethod
    def candidate_to_dict(candidate: OptimizationCandidate) -> dict[str, Any]:
        return {
            "candidate_id": candidate.candidate_id,
            "macrocycle_json": candidate.macrocycle_json,
            "scores": PlanningOptimizerSerializer.score_to_dict(candidate.scores),
            "mutations": candidate.mutations,
            "generation": candidate.generation,
            "rank": candidate.rank,
            "status": candidate.status.value,
            "constraint_violations": candidate.constraint_violations,
            "is_feasible": candidate.is_feasible,
        }

    @staticmethod
    def candidate_from_dict(data: dict[str, Any]) -> OptimizationCandidate:
        return OptimizationCandidate(
            candidate_id=data.get("candidate_id", ""),
            macrocycle_json=data.get("macrocycle_json", ""),
            scores=PlanningOptimizerSerializer.score_from_dict(data.get("scores", {})),
            mutations=data.get("mutations", []),
            generation=data.get("generation", 0),
            rank=data.get("rank", 0),
            status=CandidateStatus(data.get("status", "active")),
            constraint_violations=data.get("constraint_violations", []),
            is_feasible=data.get("is_feasible", True),
        )

    @staticmethod
    def request_to_dict(request: OptimizationRequest) -> dict[str, Any]:
        return {
            "request_id": request.request_id,
            "base_plan_json": request.base_plan_json,
            "objectives": [PlanningOptimizerSerializer.objective_to_dict(o) for o in request.objectives],
            "constraints": [PlanningOptimizerSerializer.constraint_to_dict(c) for c in request.constraints],
            "population_size": request.population_size,
            "max_generations": request.max_generations,
            "mutation_rate": request.mutation_rate,
            "crossover_rate": request.crossover_rate,
            "elite_ratio": request.elite_ratio,
            "status": request.status.value,
            "created_at": request.created_at,
        }

    @staticmethod
    def request_from_dict(data: dict[str, Any]) -> OptimizationRequest:
        return OptimizationRequest(
            request_id=data.get("request_id", ""),
            base_plan_json=data.get("base_plan_json", ""),
            objectives=[
                PlanningOptimizerSerializer.objective_from_dict(o)
                for o in data.get("objectives", [])
            ],
            constraints=[
                PlanningOptimizerSerializer.constraint_from_dict(c)
                for c in data.get("constraints", [])
            ],
            population_size=data.get("population_size", 20),
            max_generations=data.get("max_generations", 10),
            mutation_rate=data.get("mutation_rate", 0.2),
            crossover_rate=data.get("crossover_rate", 0.5),
            elite_ratio=data.get("elite_ratio", 0.1),
            status=OptimizerStatus(data.get("status", "pending")),
            created_at=data.get("created_at", ""),
        )

    @staticmethod
    def result_to_dict(result: OptimizationResult) -> dict[str, Any]:
        return {
            "result_id": result.result_id,
            "request_id": result.request_id,
            "best_candidate": (
                PlanningOptimizerSerializer.candidate_to_dict(result.best_candidate)
                if result.best_candidate else None
            ),
            "all_candidates": [
                PlanningOptimizerSerializer.candidate_to_dict(c)
                for c in result.all_candidates
            ],
            "final_score": result.final_score,
            "total_generations": result.total_generations,
            "total_evaluated": result.total_evaluated,
            "feasible_count": result.feasible_count,
            "status": result.status.value,
            "duration_seconds": result.duration_seconds,
            "completed_at": result.completed_at,
        }

    @staticmethod
    def result_from_dict(data: dict[str, Any]) -> OptimizationResult:
        return OptimizationResult(
            result_id=data.get("result_id", ""),
            request_id=data.get("request_id", ""),
            best_candidate=(
                PlanningOptimizerSerializer.candidate_from_dict(data["best_candidate"])
                if data.get("best_candidate") else None
            ),
            all_candidates=[
                PlanningOptimizerSerializer.candidate_from_dict(c)
                for c in data.get("all_candidates", [])
            ],
            final_score=data.get("final_score", 0.0),
            total_generations=data.get("total_generations", 0),
            total_evaluated=data.get("total_evaluated", 0),
            feasible_count=data.get("feasible_count", 0),
            status=OptimizerStatus(data.get("status", "pending")),
            duration_seconds=data.get("duration_seconds", 0.0),
            completed_at=data.get("completed_at", ""),
        )

    @staticmethod
    def history_entry_to_dict(entry: OptimizationHistoryEntry) -> dict[str, Any]:
        return {
            "entry_id": entry.entry_id,
            "request_id": entry.request_id,
            "action": entry.action,
            "timestamp": entry.timestamp,
            "details": entry.details,
            "previous_best_score": entry.previous_best_score,
            "new_best_score": entry.new_best_score,
        }

    @staticmethod
    def history_entry_from_dict(data: dict[str, Any]) -> OptimizationHistoryEntry:
        return OptimizationHistoryEntry(
            entry_id=data.get("entry_id", ""),
            request_id=data.get("request_id", ""),
            action=data.get("action", ""),
            timestamp=data.get("timestamp", ""),
            details=data.get("details", ""),
            previous_best_score=data.get("previous_best_score", 0.0),
            new_best_score=data.get("new_best_score", 0.0),
        )

    @staticmethod
    def state_to_dict(state: OptimizerState) -> dict[str, Any]:
        return {
            "has_active_optimization": state.has_active_optimization,
            "active_request_id": state.active_request_id,
            "optimization_count": state.optimization_count,
            "last_run_at": state.last_run_at,
            "total_candidates_generated": state.total_candidates_generated,
            "last_result": (
                PlanningOptimizerSerializer.result_to_dict(state.last_result)
                if state.last_result else None
            ),
            "average_score": state.average_score,
            "best_score_ever": state.best_score_ever,
        }

    @staticmethod
    def state_from_dict(data: dict[str, Any]) -> OptimizerState:
        return OptimizerState(
            has_active_optimization=data.get("has_active_optimization", False),
            active_request_id=data.get("active_request_id", ""),
            optimization_count=data.get("optimization_count", 0),
            last_run_at=data.get("last_run_at", ""),
            total_candidates_generated=data.get("total_candidates_generated", 0),
            last_result=(
                PlanningOptimizerSerializer.result_from_dict(data["last_result"])
                if data.get("last_result") else None
            ),
            average_score=data.get("average_score", 0.0),
            best_score_ever=data.get("best_score_ever", 0.0),
        )

    @staticmethod
    def config_to_dict(config: OptimizerConfig) -> dict[str, Any]:
        return {
            "default_population_size": config.default_population_size,
            "default_max_generations": config.default_max_generations,
            "default_mutation_rate": config.default_mutation_rate,
            "default_crossover_rate": config.default_crossover_rate,
            "default_elite_ratio": config.default_elite_ratio,
            "max_candidates": config.max_candidates,
            "convergence_threshold": config.convergence_threshold,
            "max_stall_generations": config.max_stall_generations,
            "enable_early_stop": config.enable_early_stop,
            "enable_diversity_maintenance": config.enable_diversity_maintenance,
            "enable_constraint_penalty": config.enable_constraint_penalty,
            "constraint_penalty_factor": config.constraint_penalty_factor,
        }

    @staticmethod
    def config_from_dict(data: dict[str, Any]) -> OptimizerConfig:
        return OptimizerConfig(
            default_population_size=data.get("default_population_size", 20),
            default_max_generations=data.get("default_max_generations", 10),
            default_mutation_rate=data.get("default_mutation_rate", 0.2),
            default_crossover_rate=data.get("default_crossover_rate", 0.5),
            default_elite_ratio=data.get("default_elite_ratio", 0.1),
            max_candidates=data.get("max_candidates", 500),
            convergence_threshold=data.get("convergence_threshold", 0.01),
            max_stall_generations=data.get("max_stall_generations", 3),
            enable_early_stop=data.get("enable_early_stop", True),
            enable_diversity_maintenance=data.get("enable_diversity_maintenance", True),
            enable_constraint_penalty=data.get("enable_constraint_penalty", True),
            constraint_penalty_factor=data.get("constraint_penalty_factor", 0.3),
        )
