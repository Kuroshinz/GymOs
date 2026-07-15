"""TrainingDataProvider — production-ready training data access with @safe error handling.

Extends DataProvider with all training-domain methods (exercises, muscles,
sessions, program, volume, engines) wrapped in the ``@safe`` decorator
instead of manual try/except blocks.

Consumed by ProductionDataProvider (via inheritance) which adds nutrition
and recovery providers on top.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from modules.gymbrain.providers.data_provider import DataProvider
from modules.gymbrain.providers.decorators import safe


class TrainingDataProvider(DataProvider):
    """Training-domain DataProvider with @safe error handling.

    All exercise/muscle/session/program/volume/engine methods are wrapped
    with ``@safe``, eliminating repetitive try/except + logger boilerplate.

    Inherits nutrition_provider / recovery_provider properties from DataProvider.
    """

    # ─── Exercises ────────────────────────────────────────────────

    @safe(default=None)
    def get_exercise(self, exercise_id: str) -> dict[str, Any] | None:
        if not self._exercise_repo:
            return None
        ex = self._exercise_repo.get_by_id(exercise_id)
        return getattr(ex, "raw", ex) if ex else None

    @safe(default=None)
    def get_exercise_by_name(self, name: str) -> dict[str, Any] | None:
        if not self._exercise_repo:
            return None
        ex = self._exercise_repo.get_by_name(name)
        return getattr(ex, "raw", ex) if ex else None

    @safe(default=[])
    def get_all_exercises(self) -> list[dict[str, Any]]:
        if not self._exercise_repo:
            return []
        exercises = self._exercise_repo.get_all()
        if isinstance(exercises, dict):
            return [getattr(v, "raw", v) for v in exercises.values()]
        return [getattr(e, "raw", e) for e in exercises]

    @safe(default=[])
    def get_exercises_by_muscle(self, muscle_id: str) -> list[dict[str, Any]]:
        if not self._exercise_repo:
            return []
        exercises = self._exercise_repo.get_by_muscle(muscle_id)
        if isinstance(exercises, dict):
            return [getattr(v, "raw", v) for v in exercises.values()]
        return [getattr(e, "raw", e) for e in exercises]

    @safe(default=[])
    def get_exercises_by_category(self, category: str) -> list[dict[str, Any]]:
        if not self._exercise_repo:
            return []
        exercises = self._exercise_repo.get_by_category(category)
        if isinstance(exercises, dict):
            return [getattr(v, "raw", v) for v in exercises.values()]
        return [getattr(e, "raw", e) for e in exercises]

    # ─── Muscles ──────────────────────────────────────────────────

    @safe(default=None)
    def get_muscle(self, muscle_id: str) -> dict[str, Any] | None:
        if not self._muscle_repo:
            return None
        m = self._muscle_repo.get_by_id(muscle_id)
        return getattr(m, "raw", m) if m else None

    @safe(default=[])
    def get_all_muscles(self) -> list[dict[str, Any]]:
        if not self._muscle_repo:
            return []
        muscles = self._muscle_repo.get_all()
        if isinstance(muscles, dict):
            return [getattr(v, "raw", v) for v in muscles.values()]
        return [getattr(m, "raw", m) for m in muscles]

    @safe(default=[])
    def get_muscles_by_group(self, group: str) -> list[dict[str, Any]]:
        if not self._muscle_repo:
            return []
        muscles = self._muscle_repo.get_by_group(group)
        if isinstance(muscles, dict):
            return [getattr(v, "raw", v) for v in muscles.values()]
        return [getattr(m, "raw", m) for m in muscles]

    # ─── Program ──────────────────────────────────────────────────

    @safe(default=None)
    def get_program(self) -> dict[str, Any] | None:
        if not self._program_repo:
            return None
        p = self._program_repo.get_program()
        return getattr(p, "raw", p) if p else None

    @safe(default=[])
    def get_program_exercise_ids(self) -> list[str]:
        if not self._program_repo:
            return []
        return list(self._program_repo.get_exercise_ids())

    def get_priority_muscles(self) -> list[str]:
        """Returns priority muscles from the current program."""
        prog = self.get_program()
        if prog is None:
            return []
        if isinstance(prog, dict):
            return prog.get("priority_muscles", [])
        return list(getattr(prog, "priority_muscles", []))

    # ─── Sessions / DB ────────────────────────────────────────────

    @safe(default=[])
    def list_sessions(self, limit: int = 50, offset: int = 0) -> list[Any]:
        return self._db.list_sessions(limit=limit, offset=offset)

    @safe(default=None)
    def get_session(self, session_id: int) -> Any | None:
        return self._db.get_session(session_id)

    @safe(default=None)
    def get_last_session_for_exercise(self, exercise_name: str) -> Any | None:
        return self._db.get_last_session_for_exercise(exercise_name)

    @safe(default=[])
    def get_recent_sessions(self, days: int = 14) -> list[Any]:
        sessions = self._db.list_sessions(limit=100)
        cutoff = datetime.now() - timedelta(days=days)
        return [s for s in sessions if hasattr(s, "started_at") and s.started_at and s.started_at >= cutoff]

    @safe(default=None)
    def get_body_weight(self, date: datetime | None = None) -> Any | None:
        return self._db.get_body_weight(date)

    @safe(default=None)
    def get_latest_body_weight(self) -> Any | None:
        return self._db.get_latest_body_weight()

    @safe(default=[])
    def get_body_weight_history(self, days: int = 90) -> list[Any]:
        return self._db.get_body_weight_history(days=days)

    @safe(default=0.0)
    def get_recent_volume(self, days: int = 7) -> float:
        return self._db.get_recent_volume(days=days)

    @safe(default=[])
    def get_volume_by_day(self, days: int = 90) -> list[dict[str, Any]]:
        return self._db.get_volume_by_day(days=days)

    @safe(default=0)
    def get_streak(self) -> int:
        return self._db.get_streak()

    @safe(default=0)
    def get_total_workouts(self) -> int:
        return self._db.get_total_workouts()

    # ─── Volume Engine ────────────────────────────────────────────

    @safe(default=[])
    def calculate_effective_volume(self, exercise: Any, sets: list[Any]) -> list[Any]:
        if not self._volume_engine:
            return []
        return self._volume_engine.calculate_effective_volume(exercise, len(sets))

    @safe(default={})
    def calculate_total_weekly_volume(
        self, weekly_exercises: list[tuple[Any, list[Any]]]
    ) -> dict[str, float]:
        if not self._volume_engine:
            return {}
        converted = [(ex, len(sets)) for ex, sets in weekly_exercises]
        return self._volume_engine.calculate_total_weekly_volume(converted)

    # ─── Engines ──────────────────────────────────────────────────

    @safe(default=[])
    def detect_prs(self, session: Any) -> list[Any]:
        if not self._pr_engine:
            return []
        return self._pr_engine.detect_prs(session)

    @safe(default=None)
    def analyse_session(self, session: Any) -> Any | None:
        if not self._recovery_engine:
            return None
        return self._recovery_engine.analyse_session(session)

    @safe(default=None)
    def analyse_exercise(
        self, exercise_name: str, sets: list[Any], target_reps: str, acceptable_rir: int = 2
    ) -> Any | None:
        if not self._progression_engine:
            return None
        return self._progression_engine.analyse_exercise(exercise_name, sets, target_reps, acceptable_rir)

    @safe(default=None)
    def get_progression_recommendation(self, exercise_name: str) -> Any | None:
        if not self._progression_engine:
            return None
        return self._progression_engine.get_recommendation(exercise_name)

    # ─── Goal Config ────────────────────────────────────────────────

    @safe(default=(72.0, 300))
    def get_goal_config(self) -> tuple[float, int]:
        """Get the stored goal configuration (target_weight_kg, target_calorie_surplus)."""
        return self._db.get_goal_config()

    def save_goal_config(
        self, target_weight_kg: float, target_calorie_surplus: int = 300
    ) -> None:
        """Persist the user's goal configuration."""
        if not self._db:
            return
        self._db.save_goal_config(
            target_weight_kg=target_weight_kg,
            target_calorie_surplus=target_calorie_surplus,
        )
