"""Shared fixtures for GymBrain tests."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any
from unittest.mock import MagicMock

import pytest

from modules.gymbrain.models.analysis import FatigueLevel, MuscleStatus
from modules.gymbrain.models.recommendations import Recommendation, RecommendationCategory, RecommendationPriority
from modules.gymbrain.providers.data_provider import DataProvider


# ── Fake data objects ──────────────────────────────────────────────

@dataclass
class FakeSet:
    set_number: int = 1
    weight_kg: float = 50.0
    reps: int = 10
    rir: float = 2.0
    completed: bool = True


@dataclass
class FakeExercise:
    name: str = "Bench Press"
    sets: list[FakeSet] = field(default_factory=lambda: [FakeSet() for _ in range(3)])
    sort_order: int = 1
    notes: str = ""


@dataclass
class FakeSession:
    id: int = 1
    day_name: str = "Push A"
    program_name: str = "PPL-UL"
    exercises: list[FakeExercise] = field(default_factory=lambda: [FakeExercise()])
    started_at: datetime = field(default_factory=lambda: datetime.now() - timedelta(days=1))
    completed_at: datetime = field(default_factory=lambda: datetime.now())
    notes: str = ""

    @property
    def duration_minutes(self) -> int:
        return 60

    @property
    def total_volume(self) -> float:
        return sum(
            sum(s.weight_kg * s.reps for s in e.sets)
            for e in self.exercises
        )

    @property
    def is_completed(self) -> bool:
        return True


@dataclass
class FakeBodyWeight:
    date: datetime = field(default_factory=datetime.now)
    weight_kg: float = 75.0
    notes: str = ""


@dataclass
class FakeFlag:
    flag_type: str = "rir_zero"
    severity: str = "warning"
    message: str = "RIR was 0 on multiple sets"
    exercise_name: str = "Bench Press"
    detail: str = ""


@dataclass
class FakeRecoveryReport:
    flags: list[FakeFlag] = field(default_factory=list)
    has_warnings: bool = False
    should_deload: bool = False


@dataclass
class FakeProgressionRec:
    exercise_name: str = "Bench Press"
    current_weight: float = 50.0
    current_reps: int = 10
    target_reps: str = "8-12"
    all_sets_at_top: bool = True
    should_increase: bool = True
    suggested_weight: float = 52.5
    suggested_reps: int = 8
    reason: str = "All target reps completed with RIR >= 2"


@dataclass
class FakePR:
    pr_type: str = "weight"
    exercise_name: str = "Bench Press"
    value: float = 52.5
    previous_value: float = 50.0
    improvement: float = 2.5
    label: str = "Bench Press: 52.5kg (+2.5kg)"


# ── Mock data builder ──────────────────────────────────────────────

class MockDataBuilder:
    """Builds mock data for GymBrain tests."""

    def __init__(self) -> None:
        self._exercise_data: dict[str, dict[str, Any]] = {}
        self._muscle_data: dict[str, dict[str, Any]] = {}
        self._sessions: list[FakeSession] = []
        self._body_weights: list[FakeBodyWeight] = []
        self._program_data: dict[str, Any] = {}
        self._pr_results: list[FakePR] = []
        self._recovery_results: dict[int, FakeRecoveryReport] = {}
        self._progression_results: dict[str, FakeProgressionRec] = {}

    def with_exercise(self, exercise_id: str, name: str, **overrides: Any) -> MockDataBuilder:
        data = {
            "id": exercise_id,
            "name": name,
            "category": "compound",
            "primary_muscles": ["upper_chest"],
            "secondary_muscles": ["front_delts", "triceps"],
            "hypertrophy_rep_range": "8-12",
            "muscle_contributions": [{"muscle_id": "upper_chest", "percentage": 60}],
            "equipment": "barbell",
            "movement_pattern": "push",
        }
        data.update(overrides)
        self._exercise_data[name.lower()] = data
        self._exercise_data[exercise_id] = data
        return self

    def with_muscle(self, muscle_id: str, display_name: str, **overrides: Any) -> MockDataBuilder:
        data = {
            "id": muscle_id,
            "display_name": display_name,
            "group": "chest",
            "weekly_volume_landmarks": {
                "mev": {"min_sets": 10, "max_sets": 15},
                "mav": {"min_sets": 15, "max_sets": 25},
                "mrv": {"min_sets": 25, "max_sets": 35},
            },
            "recommended_frequency": {
                "min_times_per_week": 2,
                "max_times_per_week": 3,
            },
            "recovery_characteristics": {
                "recovery_time_hours": 48,
                "fatigue_factor": 0.3,
            },
        }
        data.update(overrides)
        self._muscle_data[muscle_id] = data
        return self

    def with_session(self, session_id: int = 1, day_name: str = "Push A", exercises: list[FakeExercise] | None = None, days_ago: int = 1) -> MockDataBuilder:
        session = FakeSession(
            id=session_id,
            day_name=day_name,
            exercises=exercises or [FakeExercise()],
            started_at=datetime.now() - timedelta(days=days_ago),
        )
        self._sessions.append(session)
        return self

    def with_body_weight(self, weight_kg: float, days_ago: int = 0) -> MockDataBuilder:
        bw = FakeBodyWeight(
            date=datetime.now() - timedelta(days=days_ago),
            weight_kg=weight_kg,
        )
        self._body_weights.append(bw)
        return self

    def with_program(self, **overrides: Any) -> MockDataBuilder:
        data = {
            "name": "PPL-UL",
            "description": "Push Pull Legs Upper Lower",
            "days": [
                {"name": "Push A", "sort_order": 1, "exercises": []},
                {"name": "Pull A", "sort_order": 2, "exercises": []},
                {"name": "Legs A", "sort_order": 3, "exercises": []},
                {"name": "Upper B", "sort_order": 4, "exercises": []},
                {"name": "Lower B", "sort_order": 5, "exercises": []},
            ],
            "priority_muscles": ["upper_chest", "back_width", "quadriceps"],
            "version": "1.0",
            "goal": "hypertrophy",
            "experience_level": "intermediate",
        }
        data.update(overrides)
        self._program_data = data
        return self

    def with_pr(self, label: str = "Bench Press: 52.5kg (+2.5kg)") -> MockDataBuilder:
        self._pr_results.append(FakePR(label=label))
        return self

    def with_recovery(self, session_id: int, should_deload: bool = False, flags: list[FakeFlag] | None = None) -> MockDataBuilder:
        self._recovery_results[session_id] = FakeRecoveryReport(
            flags=flags or [],
            should_deload=should_deload,
            has_warnings=bool(flags),
        )
        return self

    def with_progression(self, exercise_name: str, should_increase: bool = True, suggested_weight: float = 52.5) -> MockDataBuilder:
        self._progression_results[exercise_name] = FakeProgressionRec(
            exercise_name=exercise_name,
            should_increase=should_increase,
            suggested_weight=suggested_weight,
        )
        return self

    def build(self) -> DataProvider:
        mock = MagicMock(spec=DataProvider)

        # Exercises
        mock.get_exercise_by_name.side_effect = lambda name: self._exercise_data.get(name.lower())
        mock.get_exercise.side_effect = lambda eid: self._exercise_data.get(eid)
        mock.get_all_exercises.return_value = [
            v for k, v in self._exercise_data.items() if v.get("name", "").lower() == k
        ] or list(self._exercise_data.values())

        def get_ex_by_muscle(muscle_id: str) -> list[dict[str, Any]]:
            return [v for v in self._exercise_data.values()
                    if isinstance(v, dict) and muscle_id in v.get("primary_muscles", [])]
        mock.get_exercises_by_muscle.side_effect = get_ex_by_muscle

        # Muscles
        mock.get_muscle.side_effect = lambda mid: self._muscle_data.get(mid)
        mock.get_all_muscles.return_value = list(self._muscle_data.values())

        def get_muscles_by_group(group: str) -> list[dict[str, Any]]:
            return [m for m in self._muscle_data.values() if isinstance(m, dict) and m.get("group") == group]
        mock.get_muscles_by_group.side_effect = get_muscles_by_group

        # Sessions
        mock.list_sessions.return_value = list(self._sessions)
        mock.get_session.side_effect = lambda sid: next((s for s in self._sessions if s.id == sid), None)
        mock.get_recent_sessions.return_value = [s for s in self._sessions if s.started_at >= datetime.now() - timedelta(days=14)]

        # Body weight
        mock.get_latest_body_weight.return_value = self._body_weights[-1] if self._body_weights else None
        mock.get_body_weight_history.return_value = list(self._body_weights)

        # Program
        mock.get_program.return_value = self._program_data
        mock.get_priority_muscles.return_value = self._program_data.get("priority_muscles", [])
        mock.get_program_exercise_ids.return_value = []

        # Volume
        def calc_weekly_volume(weekly_exercises: list[tuple[Any, list[Any]]]) -> dict[str, float]:
            result: dict[str, float] = {}
            for ex_data, sets in weekly_exercises:
                if isinstance(ex_data, dict):
                    primary = ex_data.get("primary_muscles", [])
                    contribs = ex_data.get("muscle_contributions", [])
                    if contribs:
                        for c in contribs:
                            mid = c.get("muscle_id", "")
                            pct = c.get("percentage", 100) / 100
                            result[mid] = result.get(mid, 0) + len(sets) * pct
                    else:
                        for m in primary:
                            result[m] = result.get(m, 0) + len(sets)
            return result
        mock.calculate_total_weekly_volume.side_effect = calc_weekly_volume

        mock.calculate_effective_volume.return_value = []
        mock.get_recent_volume.return_value = 15000.0
        mock.get_volume_by_day.return_value = [{"week": "2026-01", "volume": 15000} for _ in range(8)]

        # Engines
        mock.detect_prs.return_value = list(self._pr_results)
        mock.analyse_session.side_effect = lambda s: self._recovery_results.get(getattr(s, "id", 0))
        mock.get_progression_recommendation.side_effect = lambda name: self._progression_results.get(name)
        mock.analyse_exercise.return_value = None

        # Utilities
        mock.get_streak.return_value = 3
        mock.get_total_workouts.return_value = 50

        return mock


# ── Fixtures ───────────────────────────────────────────────────────

@pytest.fixture
def empty_provider() -> DataProvider:
    return MockDataBuilder().build()


@pytest.fixture
def basic_provider() -> DataProvider:
    return (
        MockDataBuilder()
        .with_exercise("bench_press", "Bench Press", category="compound")
        .with_exercise("incline_dbp", "Incline DB Press", category="compound")
        .with_muscle("upper_chest", "Upper Chest")
        .with_muscle("back_width", "Back Width")
        .with_muscle("quadriceps", "Quadriceps")
        .with_session(session_id=1, days_ago=1)
        .with_session(session_id=2, days_ago=3)
        .with_session(session_id=3, days_ago=5)
        .with_body_weight(75.0, days_ago=7)
        .with_body_weight(75.5, days_ago=3)
        .with_body_weight(76.0, days_ago=0)
        .with_program()
        .build()
    )


@pytest.fixture
def plateau_provider() -> DataProvider:
    """Provider where bench press has plateaued for 3+ weeks."""
    sets_50kg = [FakeSet(weight_kg=50, reps=10, rir=2) for _ in range(3)]
    exercises = [FakeExercise(name="Bench Press", sets=sets_50kg)]

    builder = (
        MockDataBuilder()
        .with_exercise("bench_press", "Bench Press", category="compound")
        .with_exercise("squat", "Squat", category="lower_compound")
        .with_muscle("upper_chest", "Upper Chest")
        .with_muscle("quadriceps", "Quadriceps")
        .with_program(priority_muscles=["upper_chest"])
        .with_body_weight(75.0, days_ago=21)
        .with_body_weight(75.0, days_ago=14)
        .with_body_weight(75.0, days_ago=7)
        .with_body_weight(75.0, days_ago=0)
    )

    for i in range(6):
        builder.with_session(session_id=i + 1, day_name="Push A", exercises=exercises, days_ago=i * 4)

    return builder.build()


@pytest.fixture
def fatigue_provider() -> DataProvider:
    """Provider with high fatigue indicators."""
    low_rir_sets = [FakeSet(weight_kg=50, reps=8, rir=0) for _ in range(8)]
    exercises = [FakeExercise(name="Bench Press", sets=low_rir_sets)]

    builder = (
        MockDataBuilder()
        .with_exercise("bench_press", "Bench Press", category="compound")
        .with_muscle("upper_chest", "Upper Chest")
        .with_program()
        .with_body_weight(75.0, days_ago=7)
        .with_body_weight(74.5, days_ago=0)
    )

    for i in range(10):
        builder.with_session(
            session_id=i + 1,
            day_name="Push A",
            exercises=exercises,
            days_ago=i,
        )
        flags = [FakeFlag(severity="critical", message=f"Critical flag {i}")]
        builder.with_recovery(session_id=i + 1, flags=flags)

    return builder.build()


@pytest.fixture
def progression_provider() -> DataProvider:
    """Provider where exercises are ready for progression."""
    sets_at_top = [FakeSet(weight_kg=50, reps=12, rir=2) for _ in range(3)]
    exercises = [FakeExercise(name="Bench Press", sets=sets_at_top)]

    return (
        MockDataBuilder()
        .with_exercise("bench_press", "Bench Press", category="compound")
        .with_muscle("upper_chest", "Upper Chest")
        .with_program()
        .with_session(session_id=1, days_ago=2, exercises=exercises)
        .with_session(session_id=2, days_ago=5, exercises=exercises)
        .with_progression("Bench Press", should_increase=True, suggested_weight=52.5)
        .build()
    )


@pytest.fixture
def decision_engine(basic_provider: DataProvider) -> Any:
    from modules.gymbrain.services.decision_engine import DecisionEngine
    engine = DecisionEngine(provider=basic_provider)
    return engine
