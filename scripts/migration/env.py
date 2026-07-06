"""Alembic environment configuration.

Fixed to use sync engine (matching application's engine type)
and to point at the correct database (gymos.db, not nexus.db).
"""

from __future__ import annotations

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Point target_metadata at the ORM models so autogenerate works
try:
    from modules.nutrition.infrastructure.models import Base as NutritionBase
    from modules.prediction.infrastructure.models import Base as PredictionBase
    from modules.recovery.infrastructure.models import Base as RecoveryBase
    from modules.workout.infrastructure.models import Base as WorkoutBase

    # Combine all ORM metadata
    combined_metadata = WorkoutBase.metadata
    combined_metadata.update(RecoveryBase.metadata)
    combined_metadata.update(NutritionBase.metadata)
    combined_metadata.update(PredictionBase.metadata)
    target_metadata = combined_metadata
except ImportError:
    target_metadata = None


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()
    connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
