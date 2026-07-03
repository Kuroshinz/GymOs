"""Add is_active column to existing workout_programs table.

Run this once after updating to the new schema:
    python scripts/migration/add_is_active.py

This is safe to run multiple times (idempotent).
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from sqlalchemy import create_engine, inspect, text

DB_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "data", "gymos.db"
)


def add_is_active_column(db_path: str = DB_PATH) -> None:
    engine = create_engine(f"sqlite:///{db_path}")
    inspector = inspect(engine)
    columns = [c["name"] for c in inspector.get_columns("workout_programs")]

    if "is_active" not in columns:
        with engine.begin() as conn:
            conn.execute(text(
                "ALTER TABLE workout_programs ADD COLUMN is_active BOOLEAN DEFAULT 0"
            ))
        print("[OK] Added is_active column to workout_programs")
    else:
        print("[OK] is_active column already exists")

    engine.dispose()


if __name__ == "__main__":
    add_is_active_column()
