"""Production DataProvider — real repository-backed implementation.

Wires GymDatabase, knowledge repositories, and workout engines
into the DataProvider interface consumed by GymBrain.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from modules.gymbrain.providers.data_provider import DataProvider
from modules.workout.infrastructure.repository import GymDatabase


class ProductionDataProvider(DataProvider):
    """DataProvider backed by a real GymDatabase and knowledge repositories.

    All exercise/muscle lookups go through ExerciseRepository/MuscleRepository
    (loaded from knowledge YAML files). All session data goes through GymDatabase
    (the SQLite training log). Rule evaluation never touches infrastructure directly.
    """

    def __init__(
        self,
        db: GymDatabase,
        exercise_repo: Any = None,
        muscle_repo: Any = None,
        program_repo: Any = None,
        knowledge_service: Any = None,
        volume_engine: Any = None,
        pr_engine: Any = None,
        recovery_engine: Any = None,
        progression_engine: Any = None,
    ) -> None:
        super().__init__(
            exercise_repo=exercise_repo,
            muscle_repo=muscle_repo,
            program_repo=program_repo,
            knowledge_service=knowledge_service,
            db=db,
            volume_engine=volume_engine,
            pr_engine=pr_engine,
            recovery_engine=recovery_engine,
            progression_engine=progression_engine,
        )
        self._db = db

    # ─── Exercises ────────────────────────────────────────────────

    def get_exercise(self, exercise_id: str) -> dict[str, Any] | None:
        if not self._exercise_repo:
            return None
        try:
            ex = self._exercise_repo.get_by_id(exercise_id)
            return getattr(ex, "raw", ex) if ex else None
        except Exception:
            return None

    def get_exercise_by_name(self, name: str) -> dict[str, Any] | None:
        if not self._exercise_repo:
            return None
        try:
            ex = self._exercise_repo.get_by_name(name)
            return getattr(ex, "raw", ex) if ex else None
        except Exception:
            return None

    def get_all_exercises(self) -> list[dict[str, Any]]:
        if not self._exercise_repo:
            return []
        try:
            exercises = self._exercise_repo.get_all()
            if isinstance(exercises, dict):
                return [getattr(v, "raw", v) for v in exercises.values()]
            return [getattr(e, "raw", e) for e in exercises]
        except Exception:
            return []

    def get_exercises_by_muscle(self, muscle_id: str) -> list[dict[str, Any]]:
        if not self._exercise_repo:
            return []
        try:
            exercises = self._exercise_repo.get_by_muscle(muscle_id)
            if isinstance(exercises, dict):
                return [getattr(v, "raw", v) for v in exercises.values()]
            return [getattr(e, "raw", e) for e in exercises]
        except Exception:
            return []

    def get_exercises_by_category(self, category: str) -> list[dict[str, Any]]:
        if not self._exercise_repo:
            return []
        try:
            exercises = self._exercise_repo.get_by_category(category)
            if isinstance(exercises, dict):
                return [getattr(v, "raw", v) for v in exercises.values()]
            return [getattr(e, "raw", e) for e in exercises]
        except Exception:
            return []

    # ─── Muscles ──────────────────────────────────────────────────

    def get_muscle(self, muscle_id: str) -> dict[str, Any] | None:
        if not self._muscle_repo:
            return None
        try:
            m = self._muscle_repo.get_by_id(muscle_id)
            return getattr(m, "raw", m) if m else None
        except Exception:
            return None

    def get_all_muscles(self) -> list[dict[str, Any]]:
        if not self._muscle_repo:
            return []
        try:
            muscles = self._muscle_repo.get_all()
            if isinstance(muscles, dict):
                return [getattr(v, "raw", v) for v in muscles.values()]
            return [getattr(m, "raw", m) for m in muscles]
        except Exception:
            return []

    def get_muscles_by_group(self, group: str) -> list[dict[str, Any]]:
        if not self._muscle_repo:
            return []
        try:
            muscles = self._muscle_repo.get_by_group(group)
            if isinstance(muscles, dict):
                return [getattr(v, "raw", v) for v in muscles.values()]
            return [getattr(m, "raw", m) for m in muscles]
        except Exception:
            return []

    # ─── Program ──────────────────────────────────────────────────

    def get_program(self) -> dict[str, Any] | None:
        if not self._program_repo:
            return None
        try:
            p = self._program_repo.get_program()
            return getattr(p, "raw", p) if p else None
        except Exception:
            return None

    def get_program_exercise_ids(self) -> list[str]:
        if not self._program_repo:
            return []
        try:
            return list(self._program_repo.get_exercise_ids())
        except Exception:
            return []

    def get_priority_muscles(self) -> list[str]:
        prog = self.get_program()
        if prog is None:
            return []
        if isinstance(prog, dict):
            return prog.get("priority_muscles", [])
        return list(getattr(prog, "priority_muscles", []))

    # ─── Sessions / DB ────────────────────────────────────────────

    def list_sessions(self, limit: int = 50, offset: int = 0) -> list[Any]:
        try:
            return self._db.list_sessions(limit=limit, offset=offset)
        except Exception:
            return []

    def get_session(self, session_id: int) -> Any | None:
        try:
            return self._db.get_session(session_id)
        except Exception:
            return None

    def get_last_session_for_exercise(self, exercise_name: str) -> Any | None:
        try:
            return self._db.get_last_session_for_exercise(exercise_name)
        except Exception:
            return None

    def get_recent_sessions(self, days: int = 14) -> list[Any]:
        try:
            sessions = self._db.list_sessions(limit=100)
            cutoff = datetime.now() - timedelta(days=days)
            return [s for s in sessions if hasattr(s, "started_at") and s.started_at and s.started_at >= cutoff]
        except Exception:
            return []

    def get_body_weight(self, date: datetime | None = None) -> Any | None:
        try:
            return self._db.get_body_weight(date)
        except Exception:
            return None

    def get_latest_body_weight(self) -> Any | None:
        try:
            return self._db.get_latest_body_weight()
        except Exception:
            return None

    def get_body_weight_history(self, days: int = 90) -> list[Any]:
        try:
            return self._db.get_body_weight_history(days=days)
        except Exception:
            return []

    def get_recent_volume(self, days: int = 7) -> float:
        try:
            return self._db.get_recent_volume(days=days)
        except Exception:
            return 0.0

    def get_volume_by_day(self, days: int = 90) -> list[dict[str, Any]]:
        try:
            return self._db.get_volume_by_day(days=days)
        except Exception:
            return []

    def get_streak(self) -> int:
        try:
            return self._db.get_streak()
        except Exception:
            return 0

    def get_total_workouts(self) -> int:
        try:
            return self._db.get_total_workouts()
        except Exception:
            return 0

    # ─── Volume Engine ────────────────────────────────────────────
    #
    # Note: VolumeEngine expects (ExerciseData, int) for sets, but
    # GymBrain passes (ExerciseData, list[SessionSet]). We bridge
    # by passing len(sets) as the set count.

    def calculate_effective_volume(self, exercise: Any, sets: list[Any]) -> list[Any]:
        if not self._volume_engine:
            return []
        try:
            return self._volume_engine.calculate_effective_volume(exercise, len(sets))
        except Exception:
            return []

    def calculate_total_weekly_volume(self, weekly_exercises: list[tuple[Any, list[Any]]]) -> dict[str, float]:
        if not self._volume_engine:
            return {}
        try:
            converted = [(ex, len(sets)) for ex, sets in weekly_exercises]
            return self._volume_engine.calculate_total_weekly_volume(converted)
        except Exception:
            return {}

    # ─── Engines ──────────────────────────────────────────────────

    def detect_prs(self, session: Any) -> list[Any]:
        if not self._pr_engine:
            return []
        try:
            return self._pr_engine.detect_prs(session)
        except Exception:
            return []

    def analyse_session(self, session: Any) -> Any | None:
        if not self._recovery_engine:
            return None
        try:
            return self._recovery_engine.analyse_session(session)
        except Exception:
            return None

    def analyse_exercise(
        self, exercise_name: str, sets: list[Any], target_reps: str, acceptable_rir: int = 2
    ) -> Any | None:
        if not self._progression_engine:
            return None
        try:
            return self._progression_engine.analyse_exercise(exercise_name, sets, target_reps, acceptable_rir)
        except Exception:
            return None

    def get_progression_recommendation(self, exercise_name: str) -> Any | None:
        if not self._progression_engine:
            return None
        try:
            return self._progression_engine.get_recommendation(exercise_name)
        except Exception:
            return None
