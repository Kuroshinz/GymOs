from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from modules.workout.infrastructure.models import Base


class PredictionModel(Base):
    __tablename__ = "predictions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    prediction_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    window: Mapped[str] = mapped_column(String(5), nullable=False)
    value: Mapped[float] = mapped_column(Float(), default=0.0)
    probability: Mapped[float] = mapped_column(Float(), default=0.0)
    confidence_score: Mapped[float] = mapped_column(Float(), default=0.0)
    confidence_level: Mapped[str] = mapped_column(String(20), default="moderate")
    summary: Mapped[str | None] = mapped_column(Text(), nullable=True)
    reasoning: Mapped[str | None] = mapped_column(Text(), nullable=True)
    assumptions: Mapped[str | None] = mapped_column(Text(), nullable=True)
    risk_factors: Mapped[str | None] = mapped_column(Text(), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean(), default=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(), default=datetime.now)
    expires_at: Mapped[str | None] = mapped_column(String(10), nullable=True)


class PredictionScenarioModel(Base):
    __tablename__ = "prediction_scenarios"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    prediction_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)
    probability: Mapped[float] = mapped_column(Float(), default=0.5)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(), default=datetime.now)


class ForecastModel(Base):
    __tablename__ = "forecasts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    prediction_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    prediction_type: Mapped[str] = mapped_column(String(50), nullable=False)
    window: Mapped[str] = mapped_column(String(5), nullable=False)
    trend_model: Mapped[str] = mapped_column(String(30), default="linear")
    confidence_score: Mapped[float] = mapped_column(Float(), default=0.0)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(), default=datetime.now)


class ForecastPointModel(Base):
    __tablename__ = "forecast_points"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    forecast_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    date: Mapped[str] = mapped_column(String(10), nullable=False)
    predicted_value: Mapped[float] = mapped_column(Float(), default=0.0)
    lower_bound: Mapped[float] = mapped_column(Float(), default=0.0)
    upper_bound: Mapped[float] = mapped_column(Float(), default=0.0)
    confidence_at_point: Mapped[float] = mapped_column(Float(), default=0.0)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(), default=datetime.now)
