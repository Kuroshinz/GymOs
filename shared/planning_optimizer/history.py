"""Planning Optimizer History — Tracking optimization runs, snapshots, and changes."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from shared.planning_optimizer.domain import OptimizationHistoryEntry, OptimizationResult


@dataclass
class OptimizationSnapshot:
    snapshot_id: str = ""
    request_id: str = ""
    result: OptimizationResult | None = None
    timestamp: str = ""
    description: str = ""


class PlanningOptimizerHistory:
    """Records optimization history: snapshots, changes, and adherence."""

    def __init__(self) -> None:
        self._snapshots: dict[str, list[OptimizationSnapshot]] = {}
        self._entries: dict[str, list[OptimizationHistoryEntry]] = {}

    def record_snapshot(
        self,
        request_id: str,
        result: OptimizationResult,
        description: str = "",
    ) -> None:
        import uuid
        snapshot = OptimizationSnapshot(
            snapshot_id=f"snap_{uuid.uuid4().hex[:12]}",
            request_id=request_id,
            result=result,
            timestamp=datetime.now().isoformat(),
            description=description,
        )
        if request_id not in self._snapshots:
            self._snapshots[request_id] = []
        self._snapshots[request_id].append(snapshot)

    def get_snapshots(self, request_id: str) -> list[OptimizationSnapshot]:
        return self._snapshots.get(request_id, [])

    def record_entry(
        self,
        request_id: str,
        action: str,
        details: str = "",
        previous_best_score: float = 0.0,
        new_best_score: float = 0.0,
    ) -> None:
        import uuid
        entry = OptimizationHistoryEntry(
            entry_id=f"entry_{uuid.uuid4().hex[:12]}",
            request_id=request_id,
            action=action,
            timestamp=datetime.now().isoformat(),
            details=details,
            previous_best_score=previous_best_score,
            new_best_score=new_best_score,
        )
        if request_id not in self._entries:
            self._entries[request_id] = []
        self._entries[request_id].append(entry)

    def get_entries(self, request_id: str) -> list[OptimizationHistoryEntry]:
        return self._entries.get(request_id, [])

    def get_latest_result(self, request_id: str) -> OptimizationResult | None:
        snapshots = self._snapshots.get(request_id, [])
        if not snapshots:
            return None
        return snapshots[-1].result

    def clear(self, request_id: str) -> None:
        self._snapshots.pop(request_id, None)
        self._entries.pop(request_id, None)

    def clear_all(self) -> None:
        self._snapshots.clear()
        self._entries.clear()
