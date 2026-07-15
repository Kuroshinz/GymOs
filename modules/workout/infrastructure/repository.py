"""GymOS database repository — single source of truth for all DB operations."""

import uuid
from datetime import datetime, timedelta

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from modules.workout.domain import (
    BodyWeight,
    PreviousSessionData,
    SessionExercise,
    SessionSet,
    WorkoutSession,
)

from .models import (
    BodyWeightModel,
    DayExerciseModel,
    GoalConfigModel,
    SessionExerciseModel,
    SessionSetModel,
    WorkoutDayModel,
    WorkoutProgramModel,
    WorkoutSessionModel,
)
from .program_loader import ProgramLoader


class GymDatabase:
    """Unified database gateway for all GymOS data."""

    def __init__(self, db_path: str = "data/gymos.db"):
        self._db_path = db_path
        self._engine = create_engine(f"sqlite:///{db_path}")

    def _get_session(self) -> Session:
        return Session(self._engine)

    # ─── Seed ───────────────────────────────────────────────

    def seed_if_empty(self) -> bool:
        """Seed default PPL-UL program if no programs exist. Returns True if seeded."""
        with self._get_session() as session:
            count = session.execute(select(func.count(WorkoutProgramModel.id))).scalar()
            if count and count > 0:
                return False

        loader = ProgramLoader()
        program_data = loader.load()
        self._seed_program(program_data)
        return True

    def _seed_program(self, program_data: dict) -> WorkoutProgramModel:
        with self._get_session() as session:
            prog = WorkoutProgramModel(
                id=uuid.uuid4().hex[:36],
                name=program_data["name"],
                description=program_data.get("description", ""),
            )
            for d_idx, day_data in enumerate(program_data["days"]):
                day = WorkoutDayModel(
                    id=uuid.uuid4().hex[:36],
                    program_id=prog.id,
                    name=day_data["name"],
                    sort_order=d_idx,
                )
                for e_idx, ex_data in enumerate(day_data["exercises"]):
                    ex = DayExerciseModel(
                        id=uuid.uuid4().hex[:36],
                        workout_day_id=day.id,
                        name=ex_data["name"],
                        target_sets=ex_data.get("target_sets", 3),
                        target_reps=ex_data.get("target_reps", "10"),
                        sort_order=e_idx,
                        muscle_group=ex_data.get("muscle_group", ""),
                    )
                    day.day_exercises.append(ex)
                prog.days.append(day)
            session.add(prog)
            session.commit()
            return prog

    # ─── Programs ───────────────────────────────────────────

    def get_programs(self) -> list[dict]:
        """Get all workout programs with their days and exercises."""
        with self._get_session() as session:
            stmt = select(WorkoutProgramModel).order_by(WorkoutProgramModel.name)
            models = session.execute(stmt).scalars().all()
            return [self._program_to_dict(m) for m in models]

    def get_program_days(self, program_name: str = "PPL-UL") -> list[dict]:
        """Get all days for a program with their exercises."""
        with self._get_session() as session:
            stmt = (
                select(WorkoutProgramModel)
                .where(WorkoutProgramModel.name == program_name)
            )
            prog = session.execute(stmt).scalars().first()
            if not prog:
                return []
            return self._program_to_dict(prog).get("days", [])

    def _program_to_dict(self, model: WorkoutProgramModel) -> dict:
        return {
            "id": model.id,
            "name": model.name,
            "description": model.description or "",
            "days": [
                {
                    "id": d.id,
                    "name": d.name,
                    "sort_order": d.sort_order,
                    "exercises": [
                        {
                            "id": e.id,
                            "name": e.name,
                            "target_sets": e.target_sets,
                            "target_reps": e.target_reps or "10",
                            "sort_order": e.sort_order,
                            "muscle_group": e.muscle_group or "",
                        }
                        for e in d.day_exercises
                    ],
                }
                for d in model.days
            ],
        }

    # ─── Sessions ────────────────────────────────────────────

    def save_session(self, session_data: WorkoutSession) -> WorkoutSession:
        """Save a workout session (create or update)."""
        session_id = session_data.id or uuid.uuid4().hex[:36]
        with self._get_session() as db_session:
            existing = db_session.get(WorkoutSessionModel, session_id)

            if existing:
                # Update existing
                existing.completed_at = session_data.completed_at
                existing.notes = session_data.notes

                # Delete old exercises/sets
                for ex in existing.exercises:
                    db_session.delete(ex)
                existing.exercises.clear()
            else:
                # Create new
                existing = WorkoutSessionModel(
                    id=session_id,
                    day_name=session_data.day_name,
                    program_name=session_data.program_name,
                    started_at=session_data.started_at or datetime.now(),
                    completed_at=session_data.completed_at,
                    notes=session_data.notes,
                )
                db_session.add(existing)

            # Add exercises and sets
            for s_idx, ex in enumerate(session_data.exercises):
                ex_model = SessionExerciseModel(
                    id=uuid.uuid4().hex[:36],
                    session_id=session_id,
                    name=ex.name,
                    sort_order=s_idx,
                    notes=ex.notes,
                )
                for s, set_data in enumerate(ex.sets):
                    set_model = SessionSetModel(
                        id=uuid.uuid4().hex[:36],
                        exercise_id=ex_model.id,
                        set_number=s + 1,
                        weight_kg=set_data.weight_kg,
                        reps=set_data.reps,
                        rir=set_data.rir,
                        completed=set_data.completed,
                    )
                    ex_model.sets.append(set_model)
                existing.exercises.append(ex_model)

            db_session.commit()
            session_data.id = session_id
            return session_data

    def get_session(self, session_id: str) -> WorkoutSession | None:
        """Get a single workout session."""
        with self._get_session() as session:
            model = session.get(WorkoutSessionModel, session_id)
            if model is None:
                return None
            return self._session_model_to_domain(model)

    def list_sessions(self, limit: int = 20, offset: int = 0) -> list[WorkoutSession]:
        """List workout sessions most recent first."""
        with self._get_session() as session:
            stmt = (
                select(WorkoutSessionModel)
                .order_by(WorkoutSessionModel.started_at.desc())
                .offset(offset)
                .limit(limit)
            )
            models = session.execute(stmt).scalars().all()
            return [self._session_model_to_domain(m) for m in models]

    def delete_session(self, session_id: str) -> None:
        """Delete a workout session."""
        with self._get_session() as session:
            model = session.get(WorkoutSessionModel, session_id)
            if model:
                session.delete(model)
                session.commit()

    def _session_model_to_domain(self, model: WorkoutSessionModel) -> WorkoutSession:
        exercises = []
        for ex_model in model.exercises:
            sets = [
                SessionSet(
                    set_number=s.set_number,
                    weight_kg=s.weight_kg or 0.0,
                    reps=s.reps or 0,
                    rir=s.rir,
                    completed=s.completed,
                )
                for s in ex_model.sets
            ]
            exercises.append(SessionExercise(
                name=ex_model.name,
                sets=sets,
                sort_order=ex_model.sort_order,
                notes=ex_model.notes or "",
            ))
        return WorkoutSession(
            id=model.id,
            day_name=model.day_name,
            program_name=model.program_name,
            exercises=exercises,
            started_at=model.started_at,
            completed_at=model.completed_at,
            notes=model.notes or "",
        )

    def get_last_session_for_exercise(self, exercise_name: str) -> PreviousSessionData | None:
        """Get the most recent session data for a given exercise."""
        with self._get_session() as db_session:
            stmt = (
                select(SessionExerciseModel)
                .join(WorkoutSessionModel, SessionExerciseModel.session_id == WorkoutSessionModel.id)
                .where(SessionExerciseModel.name == exercise_name)
                .where(WorkoutSessionModel.completed_at.isnot(None))
                .order_by(WorkoutSessionModel.started_at.desc())
                .limit(1)
            )
            result = db_session.execute(stmt).scalars().first()
            if result is None:
                return None

            session = db_session.get(WorkoutSessionModel, result.session_id)
            date_str = ""
            if session and session.started_at:
                date_str = session.started_at.strftime("%Y-%m-%d")

            return PreviousSessionData(
                exercise_name=exercise_name,
                sets=[
                    {"weight": s.weight_kg, "reps": s.reps, "rir": s.rir}
                    for s in result.sets
                ],
                date=date_str,
            )

    # ─── Stats ──────────────────────────────────────────────

    def get_streak(self) -> int:
        """Calculate current workout streak (consecutive days with completed session)."""
        with self._get_session() as session:
            stmt = (
                select(WorkoutSessionModel.started_at)
                .where(WorkoutSessionModel.completed_at.isnot(None))
                .order_by(WorkoutSessionModel.started_at.desc())
            )
            dates = session.execute(stmt).scalars().all()
            if not dates:
                return 0

            streak = 0
            today = datetime.now().date()
            check_date = today

            for dt in dates:
                if dt is None:
                    continue
                d = dt.date()
                if d == check_date:
                    streak += 1
                    check_date = d - timedelta(days=1)
                elif d < check_date:
                    break
                # d > check_date means same day, skip
            return streak

    def get_total_workouts(self) -> int:
        """Get total number of completed workouts."""
        with self._get_session() as session:
            stmt = select(func.count(WorkoutSessionModel.id)).where(
                WorkoutSessionModel.completed_at.isnot(None)
            )
            return session.execute(stmt).scalar() or 0

    def get_recent_volume(self, days: int = 7) -> float:
        """Get total training volume for the last N days."""
        with self._get_session() as session:
            cutoff = datetime.now() - timedelta(days=days)
            stmt = (
                select(WorkoutSessionModel)
                .where(WorkoutSessionModel.completed_at.isnot(None))
                .where(WorkoutSessionModel.started_at >= cutoff)
            )
            models = session.execute(stmt).scalars().all()
            total = 0.0
            for m in models:
                for ex in m.exercises:
                    for s in ex.sets:
                        if s.completed and s.weight_kg and s.reps:
                            total += s.weight_kg * s.reps
            return total

    def get_volume_by_day(self, days: int = 90) -> list[dict]:
        """Get weekly volume data for charting."""
        with self._get_session() as session:
            cutoff = datetime.now() - timedelta(days=days)
            stmt = (
                select(WorkoutSessionModel)
                .where(WorkoutSessionModel.completed_at.isnot(None))
                .where(WorkoutSessionModel.started_at >= cutoff)
                .order_by(WorkoutSessionModel.started_at)
            )
            models = session.execute(stmt).scalars().all()

            # Group by week
            weekly: dict[str, float] = {}
            for m in models:
                if m.started_at:
                    week_key = m.started_at.strftime("%Y-W%V")
                    vol = sum(
                        s.weight_kg * s.reps
                        for ex in m.exercises
                        for s in ex.sets
                        if s.completed and s.weight_kg and s.reps
                    )
                    weekly[week_key] = weekly.get(week_key, 0) + vol

            return sorted(
                [{"week": k, "volume": v} for k, v in weekly.items()],
                key=lambda x: x["week"],
            )

    # ─── Body Weight ─────────────────────────────────────────

    def save_body_weight(self, weight: BodyWeight) -> BodyWeight:
        """Save a body weight entry."""
        weight_id = weight.id or uuid.uuid4().hex[:36]
        with self._get_session() as session:
            existing = session.get(BodyWeightModel, weight_id)
            if existing:
                existing.date = weight.date
                existing.weight_kg = weight.weight_kg
                existing.notes = weight.notes
            else:
                model = BodyWeightModel(
                    id=weight_id,
                    date=weight.date,
                    weight_kg=weight.weight_kg,
                    notes=weight.notes,
                )
                session.add(model)
            session.commit()
            weight.id = weight_id
            return weight

    def get_body_weight(self, date: str) -> BodyWeight | None:
        """Get body weight for a specific date."""
        with self._get_session() as session:
            stmt = select(BodyWeightModel).where(BodyWeightModel.date == date)
            model = session.execute(stmt).scalars().first()
            if model is None:
                return None
            return BodyWeight(
                id=model.id,
                date=model.date,
                weight_kg=model.weight_kg,
                notes=model.notes or "",
            )

    def get_body_weight_history(self, days: int = 90) -> list[BodyWeight]:
        """Get body weight history for charting."""
        with self._get_session() as session:
            cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            stmt = (
                select(BodyWeightModel)
                .where(BodyWeightModel.date >= cutoff)
                .order_by(BodyWeightModel.date)
            )
            models = session.execute(stmt).scalars().all()
            return [
                BodyWeight(id=m.id, date=m.date, weight_kg=m.weight_kg, notes=m.notes or "")
                for m in models
            ]

    def get_latest_body_weight(self) -> BodyWeight | None:
        """Get the most recent body weight entry."""
        with self._get_session() as session:
            stmt = (
                select(BodyWeightModel)
                .order_by(BodyWeightModel.date.desc())
                .limit(1)
            )
            model = session.execute(stmt).scalars().first()
            if model is None:
                return None
            return BodyWeight(
                id=model.id,
                date=model.date,
                weight_kg=model.weight_kg,
                notes=model.notes or "",
            )

    # ─── Goal Config ─────────────────────────────────────────

    def get_goal_config(self) -> tuple[float, int]:
        """Get the stored goal configuration.

        Returns:
            Tuple of (target_weight_kg, target_calorie_surplus).
            Defaults to (72.0, 300) if no config exists.
        """
        with self._get_session() as session:
            model = session.get(GoalConfigModel, "default")
            if model is None:
                return (72.0, 300)
            return (model.target_weight_kg, model.target_calorie_surplus)

    def save_goal_config(
        self, target_weight_kg: float, target_calorie_surplus: int = 300
    ) -> None:
        """Save or update the goal configuration (upsert single row)."""
        with self._get_session() as session:
            model = session.get(GoalConfigModel, "default")
            if model is None:
                model = GoalConfigModel(
                    id="default",
                    target_weight_kg=target_weight_kg,
                    target_calorie_surplus=target_calorie_surplus,
                )
                session.add(model)
            else:
                model.target_weight_kg = target_weight_kg
                model.target_calorie_surplus = target_calorie_surplus
                model.updated_at = datetime.now()
            session.commit()

    # ─── Cleanup ────────────────────────────────────────────

    def dispose(self) -> None:
        self._engine.dispose()
