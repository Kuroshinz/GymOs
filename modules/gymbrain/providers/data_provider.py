from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any


class DataProvider:
    """Consolidated provider that bridges GymBrain to external data sources.

    GymBrain never accesses databases or repositories directly.
    All data access goes through this provider, making GymBrain testable
    and decoupled from infrastructure.

    In production, the caller injects real implementations.
    In tests, the caller injects fake/mock implementations.
    """

    def __init__(
        self,
        exercise_repo: Any = None,
        muscle_repo: Any = None,
        program_repo: Any = None,
        knowledge_service: Any = None,
        db: Any = None,
        volume_engine: Any = None,
        pr_engine: Any = None,
        recovery_engine: Any = None,
        progression_engine: Any = None,
    ) -> None:
        self._exercise_repo = exercise_repo
        self._muscle_repo = muscle_repo
        self._program_repo = program_repo
        self._knowledge_service = knowledge_service
        self._db = db
        self._volume_engine = volume_engine
        self._pr_engine = pr_engine
        self._recovery_engine = recovery_engine
        self._progression_engine = progression_engine

    # ── Exercises ────────────────────────────────────────────────────

    def get_exercise(self, exercise_id: str) -> dict[str, Any] | None:
        if self._exercise_repo:
            ex = self._exercise_repo.get_by_id(exercise_id)
            return ex.to_dict() if hasattr(ex, "to_dict") else ex
        return None

    def get_exercise_by_name(self, name: str) -> dict[str, Any] | None:
        if self._exercise_repo:
            ex = self._exercise_repo.get_by_name(name)
            return ex.to_dict() if hasattr(ex, "to_dict") else ex
        return None

    def get_all_exercises(self) -> list[dict[str, Any]]:
        if self._exercise_repo:
            exercises = self._exercise_repo.get_all()
            return [e.to_dict() if hasattr(e, "to_dict") else e for e in exercises]
        return []

    def get_exercises_by_muscle(self, muscle_id: str) -> list[dict[str, Any]]:
        if self._exercise_repo:
            exercises = self._exercise_repo.get_by_muscle(muscle_id)
            return [e.to_dict() if hasattr(e, "to_dict") else e for e in exercises]
        return []

    def get_exercises_by_category(self, category: str) -> list[dict[str, Any]]:
        if self._exercise_repo:
            exercises = self._exercise_repo.get_by_category(category)
            return [e.to_dict() if hasattr(e, "to_dict") else e for e in exercises]
        return []

    # ── Muscles ──────────────────────────────────────────────────────

    def get_muscle(self, muscle_id: str) -> dict[str, Any] | None:
        if self._muscle_repo:
            m = self._muscle_repo.get_by_id(muscle_id)
            return m.to_dict() if hasattr(m, "to_dict") else m
        return None

    def get_all_muscles(self) -> list[dict[str, Any]]:
        if self._muscle_repo:
            muscles = self._muscle_repo.get_all()
            return [m.to_dict() if hasattr(m, "to_dict") else m for m in muscles]
        return []

    def get_muscles_by_group(self, group: str) -> list[dict[str, Any]]:
        if self._muscle_repo:
            muscles = self._muscle_repo.get_by_group(group)
            return [m.to_dict() if hasattr(m, "to_dict") else m for m in muscles]
        return []

    # ── Program ──────────────────────────────────────────────────────

    def get_program(self) -> dict[str, Any] | None:
        if self._program_repo:
            p = self._program_repo.get_program()
            return p.to_dict() if hasattr(p, "to_dict") else p
        return None

    def get_program_exercise_ids(self) -> list[str]:
        if self._program_repo:
            return self._program_repo.get_exercise_ids()
        return []

    def get_priority_muscles(self) -> list[str]:
        prog = self.get_program()
        if prog and isinstance(prog, dict):
            return prog.get("priority_muscles", [])
        return []

    # ── Sessions / DB ────────────────────────────────────────────────

    def list_sessions(self, limit: int = 50, offset: int = 0) -> list[Any]:
        if self._db:
            return self._db.list_sessions(limit=limit, offset=offset)
        return []

    def get_session(self, session_id: int) -> Any | None:
        if self._db:
            return self._db.get_session(session_id)
        return None

    def get_last_session_for_exercise(self, exercise_name: str) -> Any | None:
        if self._db:
            return self._db.get_last_session_for_exercise(exercise_name)
        return None

    def get_recent_sessions(self, days: int = 14) -> list[Any]:
        sessions = self.list_sessions(limit=100)
        cutoff = datetime.now() - timedelta(days=days)
        return [s for s in sessions if hasattr(s, "started_at") and s.started_at and s.started_at >= cutoff]

    def get_body_weight(self, date: datetime | None = None) -> Any | None:
        if self._db:
            return self._db.get_body_weight(date)
        return None

    def get_latest_body_weight(self) -> Any | None:
        if self._db:
            return self._db.get_latest_body_weight()
        return None

    def get_body_weight_history(self, days: int = 90) -> list[Any]:
        if self._db:
            return self._db.get_body_weight_history(days=days)
        return []

    def get_recent_volume(self, days: int = 7) -> float:
        if self._db:
            return self._db.get_recent_volume(days=days)
        return 0.0

    def get_volume_by_day(self, days: int = 90) -> list[dict[str, Any]]:
        if self._db:
            return self._db.get_volume_by_day(days=days)
        return []

    def get_streak(self) -> int:
        if self._db:
            return self._db.get_streak()
        return 0

    def get_total_workouts(self) -> int:
        if self._db:
            return self._db.get_total_workouts()
        return 0

    # ── Volume Engine ────────────────────────────────────────────────

    def calculate_effective_volume(self, exercise: Any, sets: list[Any]) -> list[Any]:
        if self._volume_engine:
            return self._volume_engine.calculate_effective_volume(exercise, sets)
        return []

    def calculate_total_weekly_volume(self, weekly_exercises: list[tuple[Any, list[Any]]]) -> dict[str, float]:
        if self._volume_engine:
            return self._volume_engine.calculate_total_weekly_volume(weekly_exercises)
        return {}

    # ── Engines ──────────────────────────────────────────────────────

    def detect_prs(self, session: Any) -> list[Any]:
        if self._pr_engine:
            return self._pr_engine.detect_prs(session)
        return []

    def analyse_session(self, session: Any) -> Any | None:
        if self._recovery_engine:
            return self._recovery_engine.analyse_session(session)
        return None

    def analyse_exercise(
        self, exercise_name: str, sets: list[Any], target_reps: str, acceptable_rir: int = 2
    ) -> Any | None:
        if self._progression_engine:
            return self._progression_engine.analyse_exercise(exercise_name, sets, target_reps, acceptable_rir)
        return None

    def get_progression_recommendation(self, exercise_name: str) -> Any | None:
        if self._progression_engine:
            return self._progression_engine.get_recommendation(exercise_name)
        return None
