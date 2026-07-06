"""Initial schema

Revision ID: 001
Revises:
Create Date: 2026-07-02
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "workouts",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    op.create_table(
        "workout_exercises",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("workout_id", sa.String(36), sa.ForeignKey("workouts.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("muscle_group", sa.String(50), nullable=True),
        sa.Column("exercise_type", sa.String(50), nullable=True),
        sa.Column("sort_order", sa.Integer(), default=0),
    )

    op.create_table(
        "exercise_sets",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("exercise_id", sa.String(36), sa.ForeignKey("workout_exercises.id"), nullable=False),
        sa.Column("reps", sa.Integer(), nullable=False),
        sa.Column("weight", sa.Float(), nullable=True),
        sa.Column("rpe", sa.Float(), nullable=True),
        sa.Column("completed", sa.Boolean(), default=False),
    )

    op.create_table(
        "meals",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("eaten_at", sa.DateTime(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
    )

    op.create_table(
        "meal_items",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("meal_id", sa.String(36), sa.ForeignKey("meals.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("calories", sa.Float(), default=0),
        sa.Column("protein_g", sa.Float(), default=0),
        sa.Column("carbs_g", sa.Float(), default=0),
        sa.Column("fat_g", sa.Float(), default=0),
        sa.Column("quantity", sa.Float(), default=1.0),
        sa.Column("unit", sa.String(50), default="serving"),
    )

    op.create_table(
        "plugin_config",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("plugin_name", sa.String(100), unique=True, nullable=False),
        sa.Column("enabled", sa.Boolean(), default=True),
        sa.Column("settings", sa.Text(), nullable=True),
        sa.Column("credentials", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("plugin_config")
    op.drop_table("meal_items")
    op.drop_table("meals")
    op.drop_table("exercise_sets")
    op.drop_table("workout_exercises")
    op.drop_table("workouts")
