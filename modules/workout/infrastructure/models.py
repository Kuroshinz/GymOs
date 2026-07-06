"""SQLAlchemy ORM models for GymOS database."""

import os
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class WorkoutProgramModel(Base):
    __tablename__ = "workout_programs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)
    is_active: Mapped[bool | None] = mapped_column(Boolean(), default=False)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(), default=datetime.now)

    days: Mapped[list["WorkoutDayModel"]] = relationship(
        "WorkoutDayModel", back_populates="program",
        cascade="all, delete-orphan",
        order_by="WorkoutDayModel.sort_order",
    )


class WorkoutDayModel(Base):
    __tablename__ = "workout_days"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    program_id: Mapped[str] = mapped_column(String(36), ForeignKey("workout_programs.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer(), default=0)
    notes: Mapped[str | None] = mapped_column(Text(), nullable=True)

    program: Mapped["WorkoutProgramModel"] = relationship("WorkoutProgramModel", back_populates="days")
    day_exercises: Mapped[list["DayExerciseModel"]] = relationship(
        "DayExerciseModel", back_populates="workout_day",
        cascade="all, delete-orphan",
        order_by="DayExerciseModel.sort_order",
    )
    sessions: Mapped[list["WorkoutSessionModel"]] = relationship(
        "WorkoutSessionModel", back_populates="workout_day",
    )


class DayExerciseModel(Base):
    """Template exercise within a workout day (target sets/reps)."""
    __tablename__ = "day_exercises"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    workout_day_id: Mapped[str] = mapped_column(String(36), ForeignKey("workout_days.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    target_sets: Mapped[int] = mapped_column(Integer(), default=3)
    target_reps: Mapped[str | None] = mapped_column(String(20), nullable=True)  # e.g., "8-12"
    sort_order: Mapped[int] = mapped_column(Integer(), default=0)
    muscle_group: Mapped[str | None] = mapped_column(String(50), nullable=True)
    exercise_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text(), nullable=True)

    workout_day: Mapped["WorkoutDayModel"] = relationship("WorkoutDayModel", back_populates="day_exercises")


class WorkoutSessionModel(Base):
    __tablename__ = "workout_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    day_name: Mapped[str] = mapped_column(String(255), nullable=False)
    program_name: Mapped[str] = mapped_column(String(255), default="PPL-UL")
    workout_day_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("workout_days.id"), nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text(), nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(), default=datetime.now)

    workout_day: Mapped[Optional["WorkoutDayModel"]] = relationship("WorkoutDayModel", back_populates="sessions")
    exercises: Mapped[list["SessionExerciseModel"]] = relationship(
        "SessionExerciseModel", back_populates="session",
        cascade="all, delete-orphan",
        order_by="SessionExerciseModel.sort_order",
    )


class SessionExerciseModel(Base):
    __tablename__ = "session_exercises"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    session_id: Mapped[str] = mapped_column(String(36), ForeignKey("workout_sessions.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer(), default=0)
    notes: Mapped[str | None] = mapped_column(Text(), nullable=True)

    session: Mapped["WorkoutSessionModel"] = relationship("WorkoutSessionModel", back_populates="exercises")
    sets: Mapped[list["SessionSetModel"]] = relationship(
        "SessionSetModel", back_populates="exercise",
        cascade="all, delete-orphan",
        order_by="SessionSetModel.set_number",
    )


class SessionSetModel(Base):
    __tablename__ = "session_sets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    exercise_id: Mapped[str] = mapped_column(String(36), ForeignKey("session_exercises.id"), nullable=False)
    set_number: Mapped[int] = mapped_column(Integer(), nullable=False)
    weight_kg: Mapped[float | None] = mapped_column(Float(), nullable=True)
    reps: Mapped[int | None] = mapped_column(Integer(), nullable=True)
    rir: Mapped[int | None] = mapped_column(Integer(), nullable=True)
    completed: Mapped[bool] = mapped_column(Boolean(), default=True)

    exercise: Mapped["SessionExerciseModel"] = relationship("SessionExerciseModel", back_populates="sets")


class BodyWeightModel(Base):
    __tablename__ = "body_weight"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    date: Mapped[str] = mapped_column(String(10), nullable=False)  # YYYY-MM-DD
    weight_kg: Mapped[float] = mapped_column(Float(), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text(), nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(), default=datetime.now)


def init_db(db_path: str = "data/gymos.db") -> str:
    """Initialize the database and create all tables."""
    os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine)
    engine.dispose()
    return db_path
