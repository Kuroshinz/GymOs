"""Planning History — tracks plan versions, changes, and historical data."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from shared.planning.domain import Macrocycle
from shared.planning.metrics import PlanningMetricsScorer, PlanQuality


@dataclass
class PlanSnapshot:
    macrocycle: Macrocycle
    quality: PlanQuality
    timestamp: str = ""
    snapshot_version: str = ""
    change_description: str = ""


@dataclass
class PlanChange:
    macrocycle_id: str = ""
    timestamp: str = ""
    change_type: str = ""
    field_changed: str = ""
    old_value: str = ""
    new_value: str = ""
    description: str = ""


@dataclass
class PlanningHistoryEntry:
    macrocycle_id: str = ""
    name: str = ""
    created_at: str = ""
    updated_at: str = ""
    completed_at: str = ""
    version_count: int = 0
    is_active: bool = False
    is_completed: bool = False
    quality_scores: list[float] = field(default_factory=list)
    adherence_rates: list[float] = field(default_factory=list)


class PlanningHistory:
    """Tracks plan history, versions, and changes over time."""

    def __init__(self) -> None:
        self._snapshots: dict[str, list[PlanSnapshot]] = {}
        self._changes: dict[str, list[PlanChange]] = {}
        self._entries: dict[str, PlanningHistoryEntry] = {}
        self._scorer = PlanningMetricsScorer()

    def record_snapshot(
        self,
        macrocycle: Macrocycle,
        description: str = "",
    ) -> PlanSnapshot:
        quality = self._scorer.score_plan_quality(macrocycle)
        snapshot = PlanSnapshot(
            macrocycle=macrocycle,
            quality=quality,
            timestamp=datetime.now().isoformat(),
            snapshot_version=f"v{len(self._snapshots.get(macrocycle.macrocycle_id, [])) + 1}",
            change_description=description,
        )
        self._snapshots.setdefault(macrocycle.macrocycle_id, []).append(snapshot)
        self._update_entry(macrocycle, quality)
        return snapshot

    def record_change(
        self,
        macrocycle_id: str,
        change_type: str,
        field_changed: str,
        old_value: str,
        new_value: str,
        description: str = "",
    ) -> PlanChange:
        change = PlanChange(
            macrocycle_id=macrocycle_id,
            timestamp=datetime.now().isoformat(),
            change_type=change_type,
            field_changed=field_changed,
            old_value=old_value,
            new_value=new_value,
            description=description or f"{change_type}: {field_changed}",
        )
        self._changes.setdefault(macrocycle_id, []).append(change)
        entry = self._entries.get(macrocycle_id)
        if entry:
            self._entries[macrocycle_id] = PlanningHistoryEntry(
                macrocycle_id=entry.macrocycle_id,
                name=entry.name,
                created_at=entry.created_at,
                updated_at=change.timestamp,
                completed_at=entry.completed_at,
                version_count=entry.version_count + 1,
                is_active=entry.is_active,
                is_completed=entry.is_completed,
                quality_scores=entry.quality_scores,
                adherence_rates=entry.adherence_rates,
            )
        return change

    def get_snapshots(self, macrocycle_id: str) -> list[PlanSnapshot]:
        return list(self._snapshots.get(macrocycle_id, []))

    def get_changes(self, macrocycle_id: str) -> list[PlanChange]:
        return list(self._changes.get(macrocycle_id, []))

    def get_entry(self, macrocycle_id: str) -> PlanningHistoryEntry | None:
        return self._entries.get(macrocycle_id)

    def list_entries(self) -> list[PlanningHistoryEntry]:
        return list(self._entries.values())

    def list_completed(self) -> list[PlanningHistoryEntry]:
        return [e for e in self._entries.values() if e.is_completed]

    def list_active(self) -> list[PlanningHistoryEntry]:
        return [e for e in self._entries.values() if e.is_active and not e.is_completed]

    def mark_completed(self, macrocycle_id: str) -> PlanningHistoryEntry | None:
        entry = self._entries.get(macrocycle_id)
        if entry is None:
            return None
        self._entries[macrocycle_id] = PlanningHistoryEntry(
            macrocycle_id=entry.macrocycle_id,
            name=entry.name,
            created_at=entry.created_at,
            updated_at=entry.updated_at,
            completed_at=datetime.now().isoformat(),
            version_count=entry.version_count,
            is_active=False,
            is_completed=True,
            quality_scores=entry.quality_scores,
            adherence_rates=entry.adherence_rates,
        )
        return self._entries[macrocycle_id]

    def record_adherence(self, macrocycle_id: str, adherence_rate: float) -> None:
        entry = self._entries.get(macrocycle_id)
        if entry is None:
            return
        self._entries[macrocycle_id] = PlanningHistoryEntry(
            macrocycle_id=entry.macrocycle_id,
            name=entry.name,
            created_at=entry.created_at,
            updated_at=datetime.now().isoformat(),
            completed_at=entry.completed_at,
            version_count=entry.version_count,
            is_active=entry.is_active,
            is_completed=entry.is_completed,
            quality_scores=entry.quality_scores,
            adherence_rates=entry.adherence_rates + [adherence_rate],
        )

    def clear(self) -> None:
        self._snapshots.clear()
        self._changes.clear()
        self._entries.clear()

    def has_data(self) -> bool:
        return len(self._entries) > 0

    def _update_entry(self, macrocycle: Macrocycle, quality: PlanQuality) -> None:
        now = datetime.now().isoformat()
        existing = self._entries.get(macrocycle.macrocycle_id)
        if existing:
            self._entries[macrocycle.macrocycle_id] = PlanningHistoryEntry(
                macrocycle_id=existing.macrocycle_id,
                name=existing.name,
                created_at=existing.created_at,
                updated_at=now,
                completed_at=existing.completed_at,
                version_count=existing.version_count + 1,
                is_active=True,
                is_completed=existing.is_completed,
                quality_scores=existing.quality_scores + [quality.overall],
                adherence_rates=existing.adherence_rates,
            )
        else:
            self._entries[macrocycle.macrocycle_id] = PlanningHistoryEntry(
                macrocycle_id=macrocycle.macrocycle_id,
                name=macrocycle.name,
                created_at=now,
                updated_at=now,
                version_count=1,
                is_active=True,
                quality_scores=[quality.overall],
            )
