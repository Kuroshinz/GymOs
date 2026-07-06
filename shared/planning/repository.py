"""Planning Repository — in-memory storage for macrocycles, plans, and history.

Provides CRUD operations for all planning entities.
"""

from __future__ import annotations

from datetime import datetime

from shared.planning.domain import (
    Macrocycle,
    Mesocycle,
    Microcycle,
    PlanningState,
    PlanProgress,
    SessionPlan,
    WeekPlan,
)


class PlanningRepository:
    """In-memory repository for planning data."""

    def __init__(self) -> None:
        self._macrocycles: dict[str, Macrocycle] = {}
        self._mesocycles: dict[str, Mesocycle] = {}
        self._microcycles: dict[str, Microcycle] = {}
        self._weeks: dict[str, WeekPlan] = {}
        self._sessions: dict[str, SessionPlan] = {}
        self._progress: dict[str, PlanProgress] = {}
        self._active_macrocycle_id: str | None = None

    # ── Macrocycle operations ──────────────────────────────────

    def save_macrocycle(self, macrocycle: Macrocycle) -> Macrocycle:
        self._macrocycles[macrocycle.macrocycle_id] = macrocycle
        for meso in macrocycle.mesocycles:
            self.save_mesocycle(meso)
        return macrocycle

    def find_macrocycle(self, macrocycle_id: str) -> Macrocycle | None:
        return self._macrocycles.get(macrocycle_id)

    def delete_macrocycle(self, macrocycle_id: str) -> bool:
        macro = self._macrocycles.pop(macrocycle_id, None)
        if macro is None:
            return False
        if self._active_macrocycle_id == macrocycle_id:
            self._active_macrocycle_id = None
        return True

    def list_macrocycles(self) -> list[Macrocycle]:
        return list(self._macrocycles.values())

    def count_macrocycles(self) -> int:
        return len(self._macrocycles)

    def has_data(self) -> bool:
        return len(self._macrocycles) > 0

    # ── Mesocycle operations ───────────────────────────────────

    def save_mesocycle(self, mesocycle: Mesocycle) -> Mesocycle:
        self._mesocycles[mesocycle.mesocycle_id] = mesocycle
        for micro in mesocycle.microcycles:
            self.save_microcycle(micro)
        return mesocycle

    def find_mesocycle(self, mesocycle_id: str) -> Mesocycle | None:
        return self._mesocycles.get(mesocycle_id)

    def list_mesocycles(self) -> list[Mesocycle]:
        return list(self._mesocycles.values())

    def list_mesocycles_for_macrocycle(self, macrocycle_id: str) -> list[Mesocycle]:
        macro = self.find_macrocycle(macrocycle_id)
        if macro is None:
            return []
        return [m for m in self._mesocycles.values()
                if m.mesocycle_id in (mm.mesocycle_id for mm in macro.mesocycles)]

    # ── Microcycle operations ──────────────────────────────────

    def save_microcycle(self, microcycle: Microcycle) -> Microcycle:
        self._microcycles[microcycle.microcycle_id] = microcycle
        for week in microcycle.weeks:
            self.save_week(week)
        return microcycle

    def find_microcycle(self, microcycle_id: str) -> Microcycle | None:
        return self._microcycles.get(microcycle_id)

    # ── Week operations ────────────────────────────────────────

    def save_week(self, week: WeekPlan) -> WeekPlan:
        week_key = f"week_{week.week_number}"
        self._weeks[week_key] = week
        for session in week.sessions:
            self.save_session(session)
        return week

    def find_week(self, week_number: int) -> WeekPlan | None:
        return self._weeks.get(f"week_{week_number}")

    def list_weeks(self) -> list[WeekPlan]:
        return list(self._weeks.values())

    # ── Session operations ─────────────────────────────────────

    def save_session(self, session: SessionPlan) -> SessionPlan:
        self._sessions[session.session_id] = session
        return session

    def find_session(self, session_id: str) -> SessionPlan | None:
        return self._sessions.get(session_id)

    def list_sessions(self) -> list[SessionPlan]:
        return list(self._sessions.values())

    # ── Progress operations ────────────────────────────────────

    def save_progress(self, macrocycle_id: str, progress: PlanProgress) -> None:
        self._progress[macrocycle_id] = progress

    def find_progress(self, macrocycle_id: str) -> PlanProgress | None:
        return self._progress.get(macrocycle_id)

    # ── Active plan operations ─────────────────────────────────

    def set_active_macrocycle(self, macrocycle_id: str) -> bool:
        if macrocycle_id in self._macrocycles:
            self._active_macrocycle_id = macrocycle_id
            return True
        return False

    def get_active_macrocycle(self) -> Macrocycle | None:
        if self._active_macrocycle_id is None:
            return None
        return self.find_macrocycle(self._active_macrocycle_id)

    def get_active_macrocycle_id(self) -> str | None:
        return self._active_macrocycle_id

    def clear_active(self) -> None:
        self._active_macrocycle_id = None

    # ── State operations ───────────────────────────────────────

    def get_state(self) -> PlanningState:
        active = self.get_active_macrocycle()
        progress = None
        if active:
            progress = self.find_progress(active.macrocycle_id)
        return PlanningState(
            has_active_plan=active is not None,
            active_macrocycle_id=active.macrocycle_id if active else "",
            plan_count=self.count_macrocycles(),
            active_plan_progress=progress,
            last_updated=datetime.now().isoformat(),
            current_phase=active.mesocycles[0].phase if active and active.mesocycles else None,
        )

    # ── Bulk operations ────────────────────────────────────────

    def clear(self) -> None:
        self._macrocycles.clear()
        self._mesocycles.clear()
        self._microcycles.clear()
        self._weeks.clear()
        self._sessions.clear()
        self._progress.clear()
        self._active_macrocycle_id = None

    def get_all_sessions(self) -> list[SessionPlan]:
        return list(self._sessions.values())

    def get_all_weeks(self) -> list[WeekPlan]:
        return list(self._weeks.values())

    def get_all_microcycles(self) -> list[Microcycle]:
        return list(self._microcycles.values())
