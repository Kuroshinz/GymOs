"""Add recovery intelligence tables

Revision ID: 003
Revises: 002
Create Date: 2026-07-03
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "003"
down_revision: str | None = "002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "recovery_profile",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("hrv_baseline", sa.Float(), default=65.0),
        sa.Column("resting_hr_baseline", sa.Float(), default=60.0),
        sa.Column("sleep_need_hours", sa.Float(), default=8.0),
        sa.Column("sleep_sensitivity", sa.Float(), default=1.0),
        sa.Column("stress_sensitivity", sa.Float(), default=1.0),
        sa.Column("fatigue_sensitivity", sa.Float(), default=1.0),
        sa.Column("deload_frequency_weeks", sa.Integer(), default=6),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.create_table(
        "recovery_scores",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("date", sa.String(10), nullable=False, index=True),
        sa.Column("overall_score", sa.Float(), default=0.0),
        sa.Column("readiness_score", sa.Float(), default=0.0),
        sa.Column("readiness_level", sa.String(20), default="good"),
        sa.Column("fatigue_score", sa.Float(), default=0.0),
        sa.Column("sleep_score", sa.Float(), default=0.0),
        sa.Column("sleep_hours", sa.Float(), default=0.0),
        sa.Column("sleep_quality", sa.String(20), nullable=True),
        sa.Column("stress_score", sa.Float(), default=0.0),
        sa.Column("stress_level", sa.String(20), nullable=True),
        sa.Column("soreness_level", sa.String(20), nullable=True),
        sa.Column("muscle_recovery_score", sa.Float(), default=0.0),
        sa.Column("training_fatigue_score", sa.Float(), default=0.0),
        sa.Column("nutrition_adherence_score", sa.Float(), default=0.0),
        sa.Column("bodyweight_trend_score", sa.Float(), default=0.0),
        sa.Column("consistency_score", sa.Float(), default=0.0),
        sa.Column("hrv_value", sa.Float(), nullable=True),
        sa.Column("resting_hr", sa.Float(), nullable=True),
        sa.Column("subjective_fatigue", sa.Integer(), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_table(
        "sleep_logs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("date", sa.String(10), nullable=False, index=True),
        sa.Column("hours", sa.Float(), default=0.0),
        sa.Column("quality", sa.String(20), nullable=True),
        sa.Column("bedtime", sa.String(5), nullable=True),
        sa.Column("wake_time", sa.String(5), nullable=True),
        sa.Column("interruptions", sa.Integer(), default=0),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_table(
        "stress_logs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("date", sa.String(10), nullable=False, index=True),
        sa.Column("level", sa.String(20), default="moderate"),
        sa.Column("source", sa.String(100), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_table(
        "readiness_history",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("date", sa.String(10), nullable=False, index=True),
        sa.Column("readiness_score", sa.Float(), default=0.0),
        sa.Column("readiness_level", sa.String(20), default="good"),
        sa.Column("recovery_score", sa.Float(), default=0.0),
        sa.Column("fatigue_score", sa.Float(), default=0.0),
        sa.Column("suggested_intensity_modifier", sa.Float(), default=1.0),
        sa.Column("suggested_volume_modifier", sa.Float(), default=1.0),
        sa.Column("recommended_action", sa.Text(), nullable=True),
        sa.Column("flags", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_table(
        "deload_history",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("start_date", sa.String(10), nullable=False),
        sa.Column("end_date", sa.String(10), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("volume_reduction_percent", sa.Float(), default=50.0),
        sa.Column("intensity_reduction_percent", sa.Float(), default=20.0),
        sa.Column("instructions", sa.Text(), nullable=True),
        sa.Column("status", sa.String(20), default="planned"),
        sa.Column("weeks_since_last_deload", sa.Integer(), default=0),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_table(
        "recovery_recommendations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("date", sa.String(10), nullable=False, index=True),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("priority", sa.Integer(), default=0),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("action", sa.Text(), nullable=True),
        sa.Column("dismissed", sa.Boolean(), default=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("recovery_recommendations")
    op.drop_table("deload_history")
    op.drop_table("readiness_history")
    op.drop_table("stress_logs")
    op.drop_table("sleep_logs")
    op.drop_table("recovery_scores")
    op.drop_table("recovery_profile")
