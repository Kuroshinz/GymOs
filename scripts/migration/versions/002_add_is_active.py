"""Add is_active column to workout_programs

Revision ID: 002
Revises: 001
Create Date: 2026-07-02
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "002"
down_revision: str | None = "001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("workout_programs", sa.Column("is_active", sa.Boolean(), default=False))


def downgrade() -> None:
    op.drop_column("workout_programs", "is_active")
