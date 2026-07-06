"""Planning Optimizer Events — Domain events for the optimization pipeline."""

from __future__ import annotations

from dataclasses import dataclass

from shared.events.event import DomainEvent


@dataclass
class OptimizationRequested(DomainEvent):
    source: str = "planning_optimizer"
    request_id: str = ""
    objectives_count: int = 0
    constraints_count: int = 0
    population_size: int = 0


@dataclass
class OptimizationStarted(DomainEvent):
    source: str = "planning_optimizer"
    request_id: str = ""
    total_iterations: int = 0


@dataclass
class CandidateGenerated(DomainEvent):
    source: str = "planning_optimizer"
    request_id: str = ""
    candidate_id: str = ""
    generation: int = 0
    population_size: int = 0


@dataclass
class CandidateEvaluated(DomainEvent):
    source: str = "planning_optimizer"
    request_id: str = ""
    candidate_id: str = ""
    overall_score: float = 0.0
    is_feasible: bool = True


@dataclass
class GenerationCompleted(DomainEvent):
    source: str = "planning_optimizer"
    request_id: str = ""
    generation: int = 0
    best_score: float = 0.0
    average_score: float = 0.0
    feasible_count: int = 0


@dataclass
class OptimizationCompleted(DomainEvent):
    source: str = "planning_optimizer"
    request_id: str = ""
    best_score: float = 0.0
    total_generations: int = 0
    total_evaluated: int = 0
    feasible_count: int = 0


@dataclass
class OptimizationFailed(DomainEvent):
    source: str = "planning_optimizer"
    request_id: str = ""
    reason: str = ""


@dataclass
class OptimizationConstraintViolated(DomainEvent):
    source: str = "planning_optimizer"
    request_id: str = ""
    candidate_id: str = ""
    constraint_type: str = ""
    violation_detail: str = ""


PLANNING_OPTIMIZER_EVENT_REGISTRY: dict[str, type[DomainEvent]] = {
    "OptimizationRequested": OptimizationRequested,
    "OptimizationStarted": OptimizationStarted,
    "CandidateGenerated": CandidateGenerated,
    "CandidateEvaluated": CandidateEvaluated,
    "GenerationCompleted": GenerationCompleted,
    "OptimizationCompleted": OptimizationCompleted,
    "OptimizationFailed": OptimizationFailed,
    "OptimizationConstraintViolated": OptimizationConstraintViolated,
}
