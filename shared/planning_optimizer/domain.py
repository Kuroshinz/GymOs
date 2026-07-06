"""Planning Optimizer Domain — Optimization request, candidate, score, objective, constraint, history, and report models."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

# ── Enums ──────────────────────────────────────────────────────────────


class OptimizerStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"

    @property
    def label(self) -> str:
        return {
            OptimizerStatus.PENDING: "Pending",
            OptimizerStatus.RUNNING: "Running",
            OptimizerStatus.COMPLETED: "Completed",
            OptimizerStatus.FAILED: "Failed",
            OptimizerStatus.PARTIAL: "Partial",
        }[self]


class ObjectiveType(Enum):
    MAXIMIZE_HYPERTROPHY = "maximize_hypertrophy"
    MINIMIZE_FATIGUE = "minimize_fatigue"
    MAXIMIZE_RECOVERY = "maximize_recovery"
    MAXIMIZE_ADHERENCE = "maximize_adherence"
    MINIMIZE_PLATEAU_RISK = "minimize_plateau_risk"
    MINIMIZE_INJURY_RISK = "minimize_injury_risk"
    MAXIMIZE_STRENGTH = "maximize_strength"
    MAXIMIZE_ENDURANCE = "maximize_endurance"
    BALANCE_VOLUME = "balance_volume"
    MAXIMIZE_PROGRESSION = "maximize_progression"

    @property
    def label(self) -> str:
        return {
            ObjectiveType.MAXIMIZE_HYPERTROPHY: "Maximize Hypertrophy",
            ObjectiveType.MINIMIZE_FATIGUE: "Minimize Fatigue",
            ObjectiveType.MAXIMIZE_RECOVERY: "Maximize Recovery",
            ObjectiveType.MAXIMIZE_ADHERENCE: "Maximize Adherence",
            ObjectiveType.MINIMIZE_PLATEAU_RISK: "Minimize Plateau Risk",
            ObjectiveType.MINIMIZE_INJURY_RISK: "Minimize Injury Risk",
            ObjectiveType.MAXIMIZE_STRENGTH: "Maximize Strength",
            ObjectiveType.MAXIMIZE_ENDURANCE: "Maximize Endurance",
            ObjectiveType.BALANCE_VOLUME: "Balance Volume",
            ObjectiveType.MAXIMIZE_PROGRESSION: "Maximize Progression",
        }[self]

    @property
    def default_weight(self) -> float:
        return {
            ObjectiveType.MAXIMIZE_HYPERTROPHY: 1.0,
            ObjectiveType.MINIMIZE_FATIGUE: 0.8,
            ObjectiveType.MAXIMIZE_RECOVERY: 0.7,
            ObjectiveType.MAXIMIZE_ADHERENCE: 0.9,
            ObjectiveType.MINIMIZE_PLATEAU_RISK: 0.6,
            ObjectiveType.MINIMIZE_INJURY_RISK: 0.8,
            ObjectiveType.MAXIMIZE_STRENGTH: 0.8,
            ObjectiveType.MAXIMIZE_ENDURANCE: 0.6,
            ObjectiveType.BALANCE_VOLUME: 0.5,
            ObjectiveType.MAXIMIZE_PROGRESSION: 0.7,
        }[self]


class ConstraintType(Enum):
    EQUIPMENT = "equipment"
    FREQUENCY = "frequency"
    TIME = "time"
    RECOVERY = "recovery"
    INTENT = "intent"
    NUTRITION = "nutrition"
    SAFETY = "safety"
    EXPERIENCE = "experience"
    INJURY = "injury"
    SCHEDULE = "schedule"

    @property
    def label(self) -> str:
        return {
            ConstraintType.EQUIPMENT: "Equipment",
            ConstraintType.FREQUENCY: "Frequency",
            ConstraintType.TIME: "Time",
            ConstraintType.RECOVERY: "Recovery",
            ConstraintType.INTENT: "Intent",
            ConstraintType.NUTRITION: "Nutrition",
            ConstraintType.SAFETY: "Safety",
            ConstraintType.EXPERIENCE: "Experience",
            ConstraintType.INJURY: "Injury",
            ConstraintType.SCHEDULE: "Schedule",
        }[self]


class CandidateStatus(Enum):
    ACTIVE = "active"
    DOMINATED = "dominated"
    INFEASIBLE = "infeasible"
    SELECTED = "selected"

    @property
    def label(self) -> str:
        return {
            CandidateStatus.ACTIVE: "Active",
            CandidateStatus.DOMINATED: "Dominated",
            CandidateStatus.INFEASIBLE: "Infeasible",
            CandidateStatus.SELECTED: "Selected",
        }[self]


# ── Core Domain Models ─────────────────────────────────────────────────


@dataclass(frozen=True)
class OptimizationObjective:
    objective_type: ObjectiveType = ObjectiveType.MAXIMIZE_HYPERTROPHY
    weight: float = 1.0
    target_value: float | None = None
    is_primary: bool = False

    @property
    def is_maximization(self) -> bool:
        return self.objective_type in {
            ObjectiveType.MAXIMIZE_HYPERTROPHY,
            ObjectiveType.MAXIMIZE_RECOVERY,
            ObjectiveType.MAXIMIZE_ADHERENCE,
            ObjectiveType.MAXIMIZE_STRENGTH,
            ObjectiveType.MAXIMIZE_ENDURANCE,
            ObjectiveType.MAXIMIZE_PROGRESSION,
            ObjectiveType.BALANCE_VOLUME,
        }

    @property
    def name(self) -> str:
        return self.objective_type.label


@dataclass(frozen=True)
class OptimizationConstraint:
    constraint_type: ConstraintType = ConstraintType.TIME
    max_value: float | None = None
    min_value: float | None = None
    value: Any | None = None
    is_hard: bool = True
    description: str = ""

    def is_satisfied(self, candidate_value: float) -> bool:
        if self.max_value is not None and candidate_value > self.max_value:
            return False
        if self.min_value is not None and candidate_value < self.min_value:
            return False
        return True


@dataclass(frozen=True)
class OptimizationScore:
    scientific_score: float = 0.0
    recovery_score: float = 0.0
    hypertrophy_score: float = 0.0
    compliance_score: float = 0.0
    risk_score: float = 0.0
    overall: float = 0.0

    @property
    def is_viable(self) -> bool:
        return self.overall >= 0.3

    @property
    def is_optimal(self) -> bool:
        return self.overall >= 0.8

    @property
    def component_scores(self) -> dict[str, float]:
        return {
            "scientific": self.scientific_score,
            "recovery": self.recovery_score,
            "hypertrophy": self.hypertrophy_score,
            "compliance": self.compliance_score,
            "risk": self.risk_score,
        }


@dataclass(frozen=True)
class OptimizationCandidate:
    candidate_id: str = ""
    macrocycle_json: str = ""
    scores: OptimizationScore = field(default_factory=OptimizationScore)
    mutations: list[str] = field(default_factory=list)
    generation: int = 0
    rank: int = 0
    status: CandidateStatus = CandidateStatus.ACTIVE
    constraint_violations: list[str] = field(default_factory=list)
    is_feasible: bool = True

    @property
    def score_summary(self) -> str:
        return f"Candidate {self.candidate_id[:8]} — Gen {self.generation} — Score {self.scores.overall:.2f}"

    @property
    def violation_count(self) -> int:
        return len(self.constraint_violations)


@dataclass
class OptimizationRequest:
    request_id: str = ""
    base_plan_json: str = ""
    objectives: list[OptimizationObjective] = field(default_factory=list)
    constraints: list[OptimizationConstraint] = field(default_factory=list)
    population_size: int = 20
    max_generations: int = 10
    mutation_rate: float = 0.2
    crossover_rate: float = 0.5
    elite_ratio: float = 0.1
    status: OptimizerStatus = OptimizerStatus.PENDING
    created_at: str = ""

    @property
    def primary_objective(self) -> OptimizationObjective | None:
        for obj in self.objectives:
            if obj.is_primary:
                return obj
        return self.objectives[0] if self.objectives else None

    @property
    def total_iterations(self) -> int:
        return self.population_size * self.max_generations


@dataclass
class OptimizationResult:
    result_id: str = ""
    request_id: str = ""
    best_candidate: OptimizationCandidate | None = None
    all_candidates: list[OptimizationCandidate] = field(default_factory=list)
    final_score: float = 0.0
    total_generations: int = 0
    total_evaluated: int = 0
    feasible_count: int = 0
    status: OptimizerStatus = OptimizerStatus.PENDING
    duration_seconds: float = 0.0
    completed_at: str = ""

    @property
    def success_rate(self) -> float:
        if not self.all_candidates:
            return 0.0
        return self.feasible_count / len(self.all_candidates)

    @property
    def best_score_summary(self) -> str:
        if self.best_candidate is None:
            return "No solution found."
        return (
            f"Best: {self.best_candidate.scores.overall:.2f} "
            f"(Sci:{self.best_candidate.scores.scientific_score:.2f} "
            f"Rec:{self.best_candidate.scores.recovery_score:.2f} "
            f"Hype:{self.best_candidate.scores.hypertrophy_score:.2f} "
            f"Comp:{self.best_candidate.scores.compliance_score:.2f} "
            f"Risk:{self.best_candidate.scores.risk_score:.2f})"
        )

    @property
    def score_improvement(self) -> float:
        if not self.all_candidates:
            return 0.0
        first_gen = [c for c in self.all_candidates if c.generation == 0]
        last_gen = [c for c in self.all_candidates if c.generation == self.total_generations - 1]
        if not first_gen or not last_gen:
            return 0.0
        initial = max(c.scores.overall for c in first_gen)
        final = max(c.scores.overall for c in last_gen)
        return final - initial


@dataclass
class OptimizationHistoryEntry:
    entry_id: str = ""
    request_id: str = ""
    action: str = ""
    timestamp: str = ""
    details: str = ""
    previous_best_score: float = 0.0
    new_best_score: float = 0.0

    @property
    def score_delta(self) -> float:
        return self.new_best_score - self.previous_best_score


@dataclass
class OptimizationReport:
    report_id: str = ""
    request_id: str = ""
    summary: str = ""
    best_score: float = 0.0
    total_candidates: int = 0
    feasible_candidates: int = 0
    total_generations: int = 0
    top_objectives: list[str] = field(default_factory=list)
    top_constraints: list[str] = field(default_factory=list)
    duration_seconds: float = 0.0
    recommendation: str = ""
    generated_at: str = ""


# ── Configuration ──────────────────────────────────────────────────────


@dataclass(frozen=True)
class OptimizerConfig:
    default_population_size: int = 20
    default_max_generations: int = 10
    default_mutation_rate: float = 0.2
    default_crossover_rate: float = 0.5
    default_elite_ratio: float = 0.1
    max_candidates: int = 500
    convergence_threshold: float = 0.01
    max_stall_generations: int = 3
    enable_early_stop: bool = True
    enable_diversity_maintenance: bool = True
    enable_constraint_penalty: bool = True
    constraint_penalty_factor: float = 0.3


# ── Aggregate Models ───────────────────────────────────────────────────


@dataclass
class OptimizerState:
    has_active_optimization: bool = False
    active_request_id: str = ""
    optimization_count: int = 0
    last_run_at: str = ""
    total_candidates_generated: int = 0
    last_result: OptimizationResult | None = None
    average_score: float = 0.0
    best_score_ever: float = 0.0
