"""Database migration runner.

Handles schema version tracking and migration execution.
Can be called programmatically or from the command line.

Usage:
    python scripts/migrate_db.py          # upgrade to latest
    python scripts/migrate_db.py --check   # check if migration needed
    python scripts/migrate_db.py --status  # show current schema version
"""

from __future__ import annotations

import argparse
import logging
import os
import sys

from sqlalchemy import Engine

from shared.database.engine import (
    create_safe_engine,
    get_schema_version,
    set_schema_version,
)
from shared.version import SCHEMA_VERSION

logger = logging.getLogger(__name__)

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "gymos.db")


def get_engine(db_path: str = DB_PATH) -> Engine:
    return create_safe_engine(db_path)


def needs_migration(db_path: str = DB_PATH) -> bool:
    """Check if the database needs a migration."""
    engine = get_engine(db_path)
    current = get_schema_version(engine)
    engine.dispose()
    return current < SCHEMA_VERSION


def show_status(db_path: str = DB_PATH) -> dict:
    """Show current migration status."""
    engine = get_engine(db_path)
    current = get_schema_version(engine)
    engine.dispose()
    return {
        "current_version": current,
        "expected_version": SCHEMA_VERSION,
        "needs_migration": current < SCHEMA_VERSION,
    }


def migrate_upgrade(
    db_path: str = DB_PATH,
    target: int | None = None,
) -> None:
    """Run Alembic migrations to upgrade the database.

    Args:
        db_path: Path to the database file.
        target: Target schema version (defaults to SCHEMA_VERSION).
    """
    target = target or SCHEMA_VERSION
    engine = get_engine(db_path)
    current = get_schema_version(engine)

    if current >= target:
        logger.info("Already at schema v%d (target v%d)", current, target)
        engine.dispose()
        return

    logger.info("Migrating schema v%d -> v%d...", current, target)

    # Run Alembic migrations
    from alembic import command
    from alembic.config import Config

    alembic_cfg = Config(os.path.join(os.path.dirname(__file__), "..", "alembic.ini"))
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(alembic_cfg, str(target))

    # Update PRAGMA user_version
    set_schema_version(engine, target)
    engine.dispose()
    logger.info("Migration complete. Schema v%d", target)


def migrate_downgrade(
    db_path: str = DB_PATH,
    target: int = 0,
) -> None:
    """Run Alembic migrations to downgrade the database.

    Args:
        db_path: Path to the database file.
        target: Target schema version to downgrade to.
    """
    engine = get_engine(db_path)
    current = get_schema_version(engine)

    if current <= target:
        logger.info("Already at or below schema v%d", target)
        engine.dispose()
        return

    logger.info("Downgrading schema v%d -> v%d...", current, target)

    from alembic import command
    from alembic.config import Config

    alembic_cfg = Config(os.path.join(os.path.dirname(__file__), "..", "alembic.ini"))
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.downgrade(alembic_cfg, str(target))

    set_schema_version(engine, target)
    engine.dispose()
    logger.info("Downgrade complete. Schema v%d", target)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    parser = argparse.ArgumentParser(description="GymOS database migration tool")
    parser.add_argument("--check", action="store_true", help="Check if migration is needed")
    parser.add_argument("--status", action="store_true", help="Show current schema version")
    parser.add_argument("--downgrade", type=int, default=None, help="Downgrade to version")
    parser.add_argument("--db", default=DB_PATH, help="Database path")
    parser.add_argument("--target", type=int, default=None, help="Target version")

    args = parser.parse_args()

    if args.status:
        info = show_status(args.db)
        print(f"Current schema:  v{info['current_version']}")
        print(f"Expected schema: v{info['expected_version']}")
        print(f"Needs migration: {info['needs_migration']}")
        return

    if args.check:
        if needs_migration(args.db):
            print("Migration needed")
            sys.exit(1)
        print("Up to date")
        return

    if args.downgrade is not None:
        migrate_downgrade(args.db, args.downgrade)
        return

    migrate_upgrade(args.db, args.target)


if __name__ == "__main__":
    main()
