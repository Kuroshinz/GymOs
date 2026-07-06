"""SQLAlchemy ORM models for GymOS recovery data.

All recovery data is persisted in the same SQLite database as workout and nutrition data.
Extends Base from the workout infrastructure module.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from modules.workout.infrastructure.models import Base


class RecoveryProfileModel(Base):
    __tablename__ = "recovery_profile"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    hrv_baseline: Mapped[float] = mapped_column(Float(), default=65.0)
    resting_hr_baseline: Mapped[float] = mapped_column(Float(), default=60.0)
    sleep_need_hours: Mapped[float] = mapped_column(Float(), default=8.0)
    sleep_sensitivity: Mapped[float] = mapped_column(Float(), default=1.0)
    stress_sensitivity: Mapped[float] = mapped_column(Float(), default=1.0)
    fatigue_sensitivity: Mapped[float] = mapped_column(Float(), default=1.0)
    deload_frequency_weeks: Mapped[int] = mapped_column(Integer(), default=6)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(), default=datetime.now)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(), default=datetime.now, onupdate=datetime.now)


class RecoveryScoreModel(Base):
    __tablename__ = "recovery_scores"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    date: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    overall_score: Mapped[float] = mapped_column(Float(), default=0.0)
    readiness_score: Mapped[float] = mapped_column(Float(), default=0.0)
    readiness_level: Mapped[str] = mapped_column(String(20), default="good")
    fatigue_score: Mapped[float] = mapped_column(Float(), default=0.0)
    sleep_score: Mapped[float] = mapped_column(Float(), default=0.0)
    sleep_hours: Mapped[float] = mapped_column(Float(), default=0.0)
    sleep_quality: Mapped[str | None] = mapped_column(String(20), nullable=True)
    stress_score: Mapped[float] = mapped_column(Float(), default=0.0)
    stress_level: Mapped[str | None] = mapped_column(String(20), nullable=True)
    soreness_level: Mapped[str | None] = mapped_column(String(20), nullable=True)
    muscle_recovery_score: Mapped[float] = mapped_column(Float(), default=0.0)
    training_fatigue_score: Mapped[float] = mapped_column(Float(), default=0.0)
    nutrition_adherence_score: Mapped[float] = mapped_column(Float(), default=0.0)
    bodyweight_trend_score: Mapped[float] = mapped_column(Float(), default=0.0)
    consistency_score: Mapped[float] = mapped_column(Float(), default=0.0)
    hrv_value: Mapped[float | None] = mapped_column(Float(), nullable=True)
    resting_hr: Mapped[float | None] = mapped_column(Float(), nullable=True)
    subjective_fatigue: Mapped[int | None] = mapped_column(Integer(), nullable=True)
    note: Mapped[str | None] = mapped_column(Text(), nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(), default=datetime.now)


class SleepLogModel(Base):
    __tablename__ = "sleep_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    date: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    hours: Mapped[float] = mapped_column(Float(), default=0.0)
    quality: Mapped[str | None] = mapped_column(String(20), nullable=True)
    bedtime: Mapped[str | None] = mapped_column(String(5), nullable=True)       # HH:MM
    wake_time: Mapped[str | None] = mapped_column(String(5), nullable=True)     # HH:MM
    interruptions: Mapped[int] = mapped_column(Integer(), default=0)
    note: Mapped[str | None] = mapped_column(Text(), nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(), default=datetime.now)


class StressLogModel(Base):
    __tablename__ = "stress_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    date: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    level: Mapped[str] = mapped_column(String(20), default="moderate")
    source: Mapped[str | None] = mapped_column(String(100), nullable=True)
    note: Mapped[str | None] = mapped_column(Text(), nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(), default=datetime.now)


class ReadinessAssessmentModel(Base):
    __tablename__ = "readiness_history"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    date: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    readiness_score: Mapped[float] = mapped_column(Float(), default=0.0)
    readiness_level: Mapped[str] = mapped_column(String(20), default="good")
    recovery_score: Mapped[float] = mapped_column(Float(), default=0.0)
    fatigue_score: Mapped[float] = mapped_column(Float(), default=0.0)
    suggested_intensity_modifier: Mapped[float] = mapped_column(Float(), default=1.0)
    suggested_volume_modifier: Mapped[float] = mapped_column(Float(), default=1.0)
    recommended_action: Mapped[str | None] = mapped_column(Text(), nullable=True)
    flags: Mapped[str | None] = mapped_column(Text(), nullable=True)  # JSON list
    created_at: Mapped[datetime | None] = mapped_column(DateTime(), default=datetime.now)


class DeloadPlanModel(Base):
    __tablename__ = "deload_history"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    start_date: Mapped[str] = mapped_column(String(10), nullable=False)
    end_date: Mapped[str] = mapped_column(String(10), nullable=False)
    reason: Mapped[str | None] = mapped_column(Text(), nullable=True)
    volume_reduction_percent: Mapped[float] = mapped_column(Float(), default=50.0)
    intensity_reduction_percent: Mapped[float] = mapped_column(Float(), default=20.0)
    instructions: Mapped[str | None] = mapped_column(Text(), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="planned")
    weeks_since_last_deload: Mapped[int] = mapped_column(Integer(), default=0)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(), default=datetime.now)


class RecoveryRecommendationModel(Base):
    __tablename__ = "recovery_recommendations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    date: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    priority: Mapped[int] = mapped_column(Integer(), default=0)
    message: Mapped[str] = mapped_column(Text(), nullable=False)
    reason: Mapped[str | None] = mapped_column(Text(), nullable=True)
    action: Mapped[str | None] = mapped_column(Text(), nullable=True)
    dismissed: Mapped[bool] = mapped_column(Boolean(), default=False)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(), default=datetime.now)
