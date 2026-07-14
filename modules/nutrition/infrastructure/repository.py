"""NutritionRepository — CRUD operations for nutrition data in the database."""

from __future__ import annotations

import contextlib
import uuid
from datetime import datetime, timedelta

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from modules.nutrition.domain import (
    DailyNutrition,
    MacroTarget,
    Meal,
    MealItem,
    MealType,
    NutritionGoalType,
)
from modules.nutrition.infrastructure.models import (
    MacroTargetModel,
    MealItemModel,
    MealModel,
    NutritionDayModel,
)
from modules.workout.infrastructure.models import init_db as ensure_tables


class NutritionRepository:
    """Persistent repository for nutrition data backed by SQLite."""

    def __init__(self, db_path: str = "data/gymos.db"):
        self._db_path = db_path
        self._engine = create_engine(f"sqlite:///{db_path}")
        ensure_tables(db_path)

    def _get_session(self) -> Session:
        return Session(self._engine)

    # ─── Daily Nutrition ─────────────────────────────────────

    def save_day(self, day: DailyNutrition) -> DailyNutrition:
        """Save a full day of nutrition data (upsert)."""
        with self._get_session() as session:
            existing = session.execute(
                select(NutritionDayModel).where(NutritionDayModel.date == day.date)
            ).scalars().first()

            if existing:
                existing.water_ml = day.water_ml
                existing.notes = day.notes
                for meal_model in existing.meals:
                    session.delete(meal_model)
                existing.meals.clear()
                day_id = existing.id
            else:
                day_id = uuid.uuid4().hex[:36]
                existing = NutritionDayModel(
                    id=day_id,
                    date=day.date,
                    water_ml=day.water_ml,
                    notes=day.notes,
                )
                session.add(existing)

            for meal in day.meals:
                meal_id = uuid.uuid4().hex[:36]
                meal_model = MealModel(
                    id=meal_id,
                    nutrition_day_id=day_id,
                    name=meal.name,
                    meal_type=meal.meal_type.value if meal.meal_type else None,
                    eaten_at=meal.eaten_at or datetime.now(),
                    notes=meal.notes,
                )
                for item in meal.items:
                    item_model = MealItemModel(
                        id=uuid.uuid4().hex[:36],
                        meal_id=meal_id,
                        name=item.name,
                        calories=item.calories,
                        protein_g=item.protein_g,
                        carbs_g=item.carbs_g,
                        fat_g=item.fat_g,
                        fiber_g=item.fiber_g,
                        quantity=item.quantity,
                        unit=item.unit,
                    )
                    meal_model.items.append(item_model)
                existing.meals.append(meal_model)

            session.commit()
            return day

    def get_day(self, date: str) -> DailyNutrition | None:
        """Get nutrition data for a specific date."""
        with self._get_session() as session:
            model = session.execute(
                select(NutritionDayModel).where(NutritionDayModel.date == date)
            ).scalars().first()
            if model is None:
                return None
            return self._model_to_domain(model)

    def get_recent_days(self, days: int = 7) -> list[DailyNutrition]:
        """Get nutrition data for the last N days."""
        with self._get_session() as session:
            cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            models = session.execute(
                select(NutritionDayModel)
                .where(NutritionDayModel.date >= cutoff)
                .order_by(NutritionDayModel.date.desc())
            ).scalars().all()
            return [self._model_to_domain(m) for m in models]

    def get_day_range(self, start_date: str, end_date: str) -> list[DailyNutrition]:
        """Get nutrition data for a date range."""
        with self._get_session() as session:
            models = session.execute(
                select(NutritionDayModel)
                .where(NutritionDayModel.date >= start_date)
                .where(NutritionDayModel.date <= end_date)
                .order_by(NutritionDayModel.date)
            ).scalars().all()
            return [self._model_to_domain(m) for m in models]

    def delete_day(self, date: str) -> bool:
        """Delete nutrition data for a specific date."""
        with self._get_session() as session:
            model = session.execute(
                select(NutritionDayModel).where(NutritionDayModel.date == date)
            ).scalars().first()
            if model is None:
                return False
            session.delete(model)
            session.commit()
            return True

    def count_days(self) -> int:
        """Count how many days have nutrition data."""
        with self._get_session() as session:
            return session.execute(
                select(func.count(NutritionDayModel.id))
            ).scalar() or 0

    def get_all_dates(self) -> list[str]:
        """Get all dates that have nutrition data, sorted."""
        with self._get_session() as session:
            results = session.execute(
                select(NutritionDayModel.date).order_by(NutritionDayModel.date)
            ).scalars().all()
            return list(results)

    # ─── Macro Targets ───────────────────────────────────────

    def save_target(self, target: MacroTarget, date: str | None = None) -> MacroTarget:
        """Save macro targets for a date (or as default if date is None)."""
        target_date = date or "default"
        with self._get_session() as session:
            existing = session.execute(
                select(MacroTargetModel).where(MacroTargetModel.date == target_date)
            ).scalars().first()

            if existing:
                existing.calories = target.calories
                existing.protein_g = target.protein_g
                existing.carbs_g = target.carbs_g
                existing.fat_g = target.fat_g
                existing.fiber_g = target.fiber_g
                existing.water_ml = target.water_ml
                existing.goal_type = target.goal_type.value
                existing.updated_at = datetime.now()
            else:
                new_model = MacroTargetModel(
                    id=uuid.uuid4().hex[:36],
                    date=target_date,
                    calories=target.calories,
                    protein_g=target.protein_g,
                    carbs_g=target.carbs_g,
                    fat_g=target.fat_g,
                    fiber_g=target.fiber_g,
                    water_ml=target.water_ml,
                    goal_type=target.goal_type.value,
                )
                session.add(new_model)
            session.commit()
            return target

    def get_target(self, date: str | None = None) -> MacroTarget | None:
        """Get macro targets for a date (falls back to 'default')."""
        target_date = date or "default"
        with self._get_session() as session:
            # Try specific date first
            model = session.execute(
                select(MacroTargetModel).where(MacroTargetModel.date == target_date)
            ).scalars().first()
            if model:
                return self._model_to_target(model)

            # Fall back to default
            if target_date != "default":
                model = session.execute(
                    select(MacroTargetModel).where(MacroTargetModel.date == "default")
                ).scalars().first()
                if model:
                    return self._model_to_target(model)
            return None

    def get_default_target(self) -> MacroTarget:
        """Get the default macro target, or return sensible defaults."""
        target = self.get_target("default")
        if target:
            return target
        return MacroTarget()  # Returns defaults

    # ─── Stats ───────────────────────────────────────────────

    def get_average_calories(self, days: int = 7) -> float:
        """Get average daily calories for the last N days."""
        days_list = self.get_recent_days(days)
        if not days_list:
            return 0.0
        return sum(d.total_calories for d in days_list) / len(days_list)

    def get_average_protein(self, days: int = 7) -> float:
        """Get average daily protein for the last N days."""
        days_list = self.get_recent_days(days)
        if not days_list:
            return 0.0
        return sum(d.total_protein for d in days_list) / len(days_list)

    def has_data(self) -> bool:
        """Check if any nutrition data exists."""
        return self.count_days() > 0

    # ─── Mapping ─────────────────────────────────────────────

    def _model_to_domain(self, model: NutritionDayModel) -> DailyNutrition:
        meals = []
        for m in model.meals:
            items = [
                MealItem(
                    name=i.name,
                    calories=i.calories,
                    protein_g=i.protein_g,
                    carbs_g=i.carbs_g,
                    fat_g=i.fat_g,
                    fiber_g=i.fiber_g or 0.0,
                    quantity=i.quantity,
                    unit=i.unit,
                )
                for i in m.items
            ]
            meal_type = None
            if m.meal_type:
                with contextlib.suppress(ValueError):
                    meal_type = MealType(m.meal_type)
            meals.append(Meal(
                id=m.id,
                name=m.name,
                meal_type=meal_type,
                items=items,
                eaten_at=m.eaten_at,
                notes=m.notes or "",
            ))
        return DailyNutrition(
            date=model.date,
            meals=meals,
            water_ml=model.water_ml,
            notes=model.notes or "",
        )

    def _model_to_target(self, model: MacroTargetModel) -> MacroTarget:
        goal_type = NutritionGoalType.LEAN_BULK
        with contextlib.suppress(ValueError):
            goal_type = NutritionGoalType(model.goal_type)
        return MacroTarget(
            calories=model.calories,
            protein_g=model.protein_g,
            carbs_g=model.carbs_g,
            fat_g=model.fat_g,
            fiber_g=model.fiber_g,
            water_ml=model.water_ml,
            goal_type=goal_type,
        )

    def dispose(self) -> None:
        self._engine.dispose()
