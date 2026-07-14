"""Planning Optimizer Repository — In-memory storage for optimization requests, results, and candidates."""

from __future__ import annotations

from shared.planning_optimizer.domain import (
    OptimizationCandidate,
    OptimizationRequest,
    OptimizationResult,
    OptimizerState,
)


class PlanningOptimizerRepository:
    """In-memory CRUD for optimization entities."""

    def __init__(self) -> None:
        self._requests: dict[str, OptimizationRequest] = {}
        self._results: dict[str, OptimizationResult] = {}
        self._candidates: dict[str, list[OptimizationCandidate]] = {}
        self._active_request_id: str = ""

    # ── Requests ──────────────────────────────────────────────────────

    def save_request(self, request: OptimizationRequest) -> None:
        self._requests[request.request_id] = request

    def find_request(self, request_id: str) -> OptimizationRequest | None:
        return self._requests.get(request_id)

    def list_requests(self) -> list[OptimizationRequest]:
        return list(self._requests.values())

    def delete_request(self, request_id: str) -> bool:
        if request_id in self._requests:
            del self._requests[request_id]
            return True
        return False

    # ── Results ───────────────────────────────────────────────────────

    def save_result(self, result: OptimizationResult) -> None:
        self._results[result.result_id] = result

    def find_result(self, result_id: str) -> OptimizationResult | None:
        return self._results.get(result_id)

    def find_result_by_request(self, request_id: str) -> OptimizationResult | None:
        for result in self._results.values():
            if result.request_id == request_id:
                return result
        return None

    def list_results(self) -> list[OptimizationResult]:
        return list(self._results.values())

    def delete_result(self, result_id: str) -> bool:
        if result_id in self._results:
            del self._results[result_id]
            return True
        return False

    # ── Candidates ────────────────────────────────────────────────────

    def save_candidates(
        self,
        request_id: str,
        candidates: list[OptimizationCandidate],
    ) -> None:
        self._candidates[request_id] = candidates

    def find_candidates(self, request_id: str) -> list[OptimizationCandidate]:
        return self._candidates.get(request_id, [])

    def delete_candidates(self, request_id: str) -> bool:
        if request_id in self._candidates:
            del self._candidates[request_id]
            return True
        return False

    # ── Active State ──────────────────────────────────────────────────

    def set_active_request(self, request_id: str) -> None:
        self._active_request_id = request_id

    def get_active_request_id(self) -> str | None:
        return self._active_request_id if self._active_request_id else None

    def get_state(self) -> OptimizerState:
        results = self.list_results()
        total_candidates = sum(
            len(cands) for cands in self._candidates.values()
        )
        all_scores = [r.final_score for r in results if r.final_score > 0]
        avg_score = sum(all_scores) / len(all_scores) if all_scores else 0.0
        best_score = max(all_scores) if all_scores else 0.0

        return OptimizerState(
            has_active_optimization=bool(self._active_request_id),
            active_request_id=self._active_request_id,
            optimization_count=len(results),
            total_candidates_generated=total_candidates,
            average_score=avg_score,
            best_score_ever=best_score,
        )

    # ── Lifecycle ─────────────────────────────────────────────────────

    def clear_all(self) -> None:
        self._requests.clear()
        self._results.clear()
        self._candidates.clear()
        self._active_request_id = ""
