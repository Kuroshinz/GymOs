"""Seed the database with demo data for first-run experience.

Creates a sample user profile, workouts, nutrition entries,
and recovery data so new users see a populated application.
"""

from __future__ import annotations

import logging
import os
from datetime import UTC, datetime, timedelta

logger = logging.getLogger(__name__)

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "gymos.db")


def seed_demo_data(db_path: str = DB_PATH) -> None:
    """Populate the database with sample data if empty."""
    from modules.workout.infrastructure.models import init_db
    from modules.workout.infrastructure.repository import GymDatabase

    init_db(db_path)

    db = GymDatabase(db_path)
    if db._count_workouts() > 0:
        logger.info("Demo data skipped: workouts exist")
        return

    _seed_workouts(db)
    _seed_program(db_path)
    _seed_nutrition(db_path)
    _seed_recovery(db_path)

    logger.info("Demo data seeded successfully")


def _seed_workouts(db) -> None:
    """Create 6 sample workouts over the past 2 weeks."""

    from modules.workout.domain.models import Workout as WorkoutDomain

    workouts_data = [
        ("Upper Body Push", "2026-06-22", 60, 8),
        ("Lower Body", "2026-06-24", 55, 7),
        ("Upper Body Pull", "2026-06-26", 65, 9),
        ("Full Body", "2026-06-28", 70, 10),
        ("Upper Body Push", "2026-07-01", 62, 8),
        ("Lower Body", "2026-07-03", 58, 7),
    ]

    for name, date_str, duration, rpe in workouts_data:
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=UTC)
            domain = WorkoutDomain(
                name=name,
                started_at=date,
                completed_at=date + timedelta(minutes=duration),
                notes="Demo workout",
            )
            db.save(domain)
        except Exception as e:
            logger.warning("Failed to seed workout %s: %s", name, e)


def _seed_program(db_path: str) -> None:
    """Create a sample program if none exist."""
    from uuid import uuid4

    from modules.workout_program.domain import WorkoutProgram
    from modules.workout_program.repository import WorkoutProgramRepository

    repo = WorkoutProgramRepository(db_path)
    if repo.count() > 0:
        return

    program = WorkoutProgram(
        id=str(uuid4()),
        name="Intermediate PPL",
        description="A push/pull/legs split for intermediate lifters. "
                     "6 days per week with progressive overload.",
        weeks=12,
        sessions_per_week=6,
        is_active=True,
        created_at=datetime.now(UTC),
    )
    try:
        repo.save(program)
    except Exception as e:
        logger.warning("Failed to seed program: %s", e)


def _seed_nutrition(db_path: str) -> None:
    """Create sample nutrition entries."""
    from uuid import uuid4

    from modules.nutrition.infrastructure.repository import NutritionRepository

    repo = NutritionRepository(db_path)

    meals = [
        ("Breakfast - Oatmeal & Eggs", "2026-07-03", 450, 32, 45, 15),
        ("Lunch - Chicken & Rice", "2026-07-03", 650, 48, 60, 12),
        ("Dinner - Salmon & Veggies", "2026-07-03", 550, 40, 30, 22),
        ("Breakfast - Smoothie & Toast", "2026-07-04", 380, 25, 50, 10),
        ("Lunch - Turkey Sandwich", "2026-07-04", 520, 35, 55, 14),
    ]

    for name, date_str, cal, protein, carbs, fat in meals:
        try:
            from datetime import datetime as dt

            from modules.nutrition.domain.models import Meal

            meal = Meal(
                id=str(uuid4()),
                name=name,
                eaten_at=dt.strptime(date_str, "%Y-%m-%d").replace(tzinfo=UTC),
                calories=cal,
                protein_g=protein,
                carbs_g=carbs,
                fat_g=fat,
            )
            repo.save(meal)
        except Exception as e:
            logger.warning("Failed to seed meal: %s", e)


def _seed_recovery(db_path: str) -> None:
    """Create sample recovery scores and sleep logs."""
    from modules.recovery.infrastructure.repository import RecoveryRepository

    repo = RecoveryRepository(db_path)

    scores_data = [
        ("2026-07-01", 78, 82, 25, 7.5),
        ("2026-07-02", 72, 75, 35, 6.8),
        ("2026-07-03", 85, 88, 20, 8.0),
        ("2026-07-04", 80, 84, 28, 7.2),
        ("2026-07-05", 76, 79, 30, 7.0),
    ]

    for date_str, overall, readiness, fatigue, sleep_hrs in scores_data:
        try:
            from modules.recovery.domain.models import RecoveryScore as RecoveryScoreDomain

            score = RecoveryScoreDomain(
                date=date_str,
                overall_score=overall,
                readiness_score=readiness,
                fatigue_score=fatigue,
                sleep_hours=sleep_hrs,
            )
            repo.save_score(score)
        except Exception as e:
            logger.warning("Failed to seed recovery: %s", e)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seed_demo_data()
