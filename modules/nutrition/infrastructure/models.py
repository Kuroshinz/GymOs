"""SQLAlchemy ORM models for GymOS nutrition data.

All nutrition data is persisted in the same SQLite database as workout data.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from modules.workout.infrastructure.models import Base


class NutritionDayModel(Base):
    __tablename__ = "nutrition_days"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    date: Mapped[str] = mapped_column(String(10), nullable=False, unique=True, index=True)
    water_ml: Mapped[float] = mapped_column(Float(), default=0.0)
    notes: Mapped[str | None] = mapped_column(Text(), nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(), default=datetime.now)

    meals: Mapped[list[MealModel]] = relationship(
        "MealModel", back_populates="nutrition_day",
        cascade="all, delete-orphan",
        order_by="MealModel.eaten_at",
    )


class MealModel(Base):
    __tablename__ = "nutrition_meals"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    nutrition_day_id: Mapped[str] = mapped_column(String(36), ForeignKey("nutrition_days.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    meal_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    eaten_at: Mapped[datetime | None] = mapped_column(DateTime(), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text(), nullable=True)

    nutrition_day: Mapped[NutritionDayModel] = relationship("NutritionDayModel", back_populates="meals")
    items: Mapped[list[MealItemModel]] = relationship(
        "MealItemModel", back_populates="meal",
        cascade="all, delete-orphan",
    )


class MealItemModel(Base):
    __tablename__ = "nutrition_meal_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    meal_id: Mapped[str] = mapped_column(String(36), ForeignKey("nutrition_meals.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    calories: Mapped[float] = mapped_column(Float(), default=0.0)
    protein_g: Mapped[float] = mapped_column(Float(), default=0.0)
    carbs_g: Mapped[float] = mapped_column(Float(), default=0.0)
    fat_g: Mapped[float] = mapped_column(Float(), default=0.0)
    fiber_g: Mapped[float] = mapped_column(Float(), default=0.0)
    quantity: Mapped[float] = mapped_column(Float(), default=1.0)
    unit: Mapped[str] = mapped_column(String(50), default="serving")

    meal: Mapped[MealModel] = relationship("MealModel", back_populates="items")


class MacroTargetModel(Base):
    __tablename__ = "macro_targets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    date: Mapped[str] = mapped_column(String(10), nullable=False, unique=True, index=True)
    calories: Mapped[float] = mapped_column(Float(), default=2800.0)
    protein_g: Mapped[float] = mapped_column(Float(), default=160.0)
    carbs_g: Mapped[float] = mapped_column(Float(), default=350.0)
    fat_g: Mapped[float] = mapped_column(Float(), default=70.0)
    fiber_g: Mapped[float] = mapped_column(Float(), default=30.0)
    water_ml: Mapped[float] = mapped_column(Float(), default=3000.0)
    goal_type: Mapped[str] = mapped_column(String(50), default="lean_bulk")
    created_at: Mapped[datetime | None] = mapped_column(DateTime(), default=datetime.now)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(), default=datetime.now, onupdate=datetime.now)
