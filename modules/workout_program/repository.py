"""ProgramRepository — CRUD operations for workout programs in the database."""

import uuid

from sqlalchemy import create_engine, func, select, update
from sqlalchemy.orm import Session

from modules.workout.infrastructure.models import (
    DayExerciseModel,
    WorkoutDayModel,
    WorkoutProgramModel,
)
from modules.workout_program.domain import ProgramDay, ProgramExercise, WorkoutProgram


class ProgramRepository:
    def __init__(self, db_path: str):
        self._engine = create_engine(f"sqlite:///{db_path}")

    def _get_session(self) -> Session:
        return Session(self._engine)

    # ─── Create ──────────────────────────────────────────────

    def save(self, program: WorkoutProgram) -> str:
        program_id = uuid.uuid4().hex[:36]
        with self._get_session() as session:
            prog_model = WorkoutProgramModel(
                id=program_id,
                name=program.name,
                description=program.description,
            )
            for d_idx, day in enumerate(program.days):
                day_model = WorkoutDayModel(
                    id=uuid.uuid4().hex[:36],
                    program_id=program_id,
                    name=day.name,
                    sort_order=d_idx,
                    notes=day.notes,
                )
                for e_idx, ex in enumerate(day.exercises):
                    ex_model = DayExerciseModel(
                        id=uuid.uuid4().hex[:36],
                        workout_day_id=day_model.id,
                        name=ex.name,
                        target_sets=ex.target_sets,
                        target_reps=ex.target_reps,
                        sort_order=e_idx,
                        muscle_group=ex.muscle_group or "",
                        exercise_id=ex.exercise_id or "",
                        notes=ex.notes,
                    )
                    day_model.day_exercises.append(ex_model)
                prog_model.days.append(day_model)
            session.add(prog_model)
            session.commit()
        return program_id

    # ─── Read ────────────────────────────────────────────────

    def get_all(self) -> list[dict]:
        with self._get_session() as session:
            stmt = select(WorkoutProgramModel).order_by(WorkoutProgramModel.name)
            models = session.execute(stmt).scalars().all()
            return [self._model_to_dict(m) for m in models]

    def get_by_id(self, program_id: str) -> WorkoutProgram | None:
        with self._get_session() as session:
            model = session.get(WorkoutProgramModel, program_id)
            if model is None:
                return None
            return self._model_to_domain(model)

    def get_by_name(self, name: str) -> WorkoutProgram | None:
        with self._get_session() as session:
            stmt = select(WorkoutProgramModel).where(WorkoutProgramModel.name == name)
            model = session.execute(stmt).scalars().first()
            if model is None:
                return None
            return self._model_to_domain(model)

    def get_active(self) -> WorkoutProgram | None:
        with self._get_session() as session:
            stmt = (
                select(WorkoutProgramModel)
                .where(WorkoutProgramModel.is_active.is_(True))
            )
            model = session.execute(stmt).scalars().first()
            if model is None:
                return None
            return self._model_to_domain(model)

    def name_exists(self, name: str) -> bool:
        with self._get_session() as session:
            stmt = select(func.count(WorkoutProgramModel.id)).where(
                WorkoutProgramModel.name == name
            )
            count = session.execute(stmt).scalar() or 0
            return count > 0

    def count(self) -> int:
        with self._get_session() as session:
            return session.execute(select(func.count(WorkoutProgramModel.id))).scalar() or 0

    # ─── Activate ────────────────────────────────────────────

    def activate(self, program_id: str) -> None:
        with self._get_session() as session:
            session.execute(
                update(WorkoutProgramModel)
                .where(WorkoutProgramModel.is_active.is_(True))
                .values(is_active=False)
            )
            session.execute(
                update(WorkoutProgramModel)
                .where(WorkoutProgramModel.id == program_id)
                .values(is_active=True)
            )
            session.commit()

    def deactivate_all(self) -> None:
        with self._get_session() as session:
            session.execute(
                update(WorkoutProgramModel)
                .values(is_active=False)
            )
            session.commit()

    # ─── Delete ──────────────────────────────────────────────

    def delete(self, program_id: str) -> bool:
        with self._get_session() as session:
            model = session.get(WorkoutProgramModel, program_id)
            if model is None:
                return False
            session.delete(model)
            session.commit()
            return True

    def ensure_single_active(self) -> None:
        with self._get_session() as session:
            active_count = (
                session.execute(
                    select(func.count(WorkoutProgramModel.id))
                    .where(WorkoutProgramModel.is_active.is_(True))
                ).scalar() or 0
            )
            if active_count > 1:
                all_active = session.execute(
                    select(WorkoutProgramModel)
                    .where(WorkoutProgramModel.is_active.is_(True))
                    .order_by(WorkoutProgramModel.created_at)
                ).scalars().all()
                for model in all_active[1:]:
                    model.is_active = False
                session.commit()

    def get_active_id(self) -> str | None:
        with self._get_session() as session:
            stmt = (
                select(WorkoutProgramModel.id)
                .where(WorkoutProgramModel.is_active.is_(True))
                .limit(1)
            )
            result = session.execute(stmt).scalar()
            return result

    # ─── Mapping helpers ─────────────────────────────────────

    def _model_to_domain(self, model: WorkoutProgramModel) -> WorkoutProgram:
        days: list[ProgramDay] = []
        for d in model.days:
            exercises: list[ProgramExercise] = []
            for e in d.day_exercises:
                exercises.append(ProgramExercise(
                    name=e.name,
                    target_sets=e.target_sets,
                    target_reps=e.target_reps or "10",
                    muscle_group=e.muscle_group or "",
                    exercise_id=e.exercise_id or "",
                    sort_order=e.sort_order,
                    notes=e.notes or "",
                ))
            days.append(ProgramDay(
                name=d.name,
                sort_order=d.sort_order,
                exercises=exercises,
                notes=d.notes or "",
            ))
        return WorkoutProgram(
            name=model.name,
            description=model.description or "",
            days=days,
        )

    def _model_to_dict(self, model: WorkoutProgramModel) -> dict:
        return {
            "id": model.id,
            "name": model.name,
            "description": model.description or "",
            "is_active": model.is_active or False,
            "day_count": len(model.days),
            "exercise_count": sum(len(d.day_exercises) for d in model.days),
        }

    def dispose(self) -> None:
        self._engine.dispose()
