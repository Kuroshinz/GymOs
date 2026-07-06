"""Planning Optimizer Metrics — Aggregate metrics across optimization runs."""

from __future__ import annotations

from dataclasses import dataclass

from shared.planning_optimizer.domain import OptimizationResult


@dataclass
class OptimizerMetrics:
    total_optimizations: int = 0
    total_candidates_generated: int = 0
    total_feasible_candidates: int = 0
    total_generations_run: int = 0
    average_best_score: float = 0.0
    best_score_ever: float = 0.0
    average_success_rate: float = 0.0
    average_duration_seconds: float = 0.0
    best_result_id: str = ""

    @property
    def overall_efficiency(self) -> float:
        if self.total_candidates_generated == 0:
            return 0.0
        return self.total_feasible_candidates / self.total_candidates_generated

    @property
    def average_generations_per_run(self) -> float:
        if self.total_optimizations == 0:
            return 0.0
        return self.total_generations_run / self.total_optimizations


class OptimizerMetricsCollector:
    """Collects and computes aggregate optimization metrics."""

    def __init__(self) -> None:
        self._results: list[OptimizationResult] = []

    def record(self, result: OptimizationResult) -> None:
        self._results.append(result)

    def compute(self) -> OptimizerMetrics:
        if not self._results:
            return OptimizerMetrics()

        total_candidates = sum(len(r.all_candidates) for r in self._results)
        total_feasible = sum(r.feasible_count for r in self._results)
        total_generations = sum(r.total_generations for r in self._results)
        best_score = max((r.final_score for r in self._results), default=0.0)
        avg_score = sum(r.final_score for r in self._results) / len(self._results)
        avg_success = sum(r.success_rate for r in self._results) / len(self._results)
        avg_duration = sum(r.duration_seconds for r in self._results) / len(self._results)

        best_result = max(self._results, key=lambda r: r.final_score, default=None)

        return OptimizerMetrics(
            total_optimizations=len(self._results),
            total_candidates_generated=total_candidates,
            total_feasible_candidates=total_feasible,
            total_generations_run=total_generations,
            average_best_score=avg_score,
            best_score_ever=best_score,
            average_success_rate=avg_success,
            average_duration_seconds=avg_duration,
            best_result_id=best_result.result_id if best_result else "",
        )
