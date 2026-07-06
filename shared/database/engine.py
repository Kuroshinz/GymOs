"""Database engine factory with safety configuration.

Every create_engine call should use this factory to ensure:
  - WAL mode (crash safety)
  - Foreign keys enforced (referential integrity)
  - Busy timeout (concurrency)
  - Schema version tracking (PRAGMA user_version)
"""

from __future__ import annotations

import os

from sqlalchemy import Engine, create_engine, event, text

from shared.version import SCHEMA_VERSION

_DEFAULT_TIMEOUT_MS = 5000


def _set_sqlite_pragma(dbapi_connection, connection_record) -> None:
    """Configure SQLite safety pragmas on every new connection."""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute(f"PRAGMA busy_timeout={_DEFAULT_TIMEOUT_MS}")
    cursor.close()


def create_safe_engine(db_path: str, **kwargs) -> Engine:
    """Create a SQLAlchemy engine with safety pragmas.

    Args:
        db_path: Path to the SQLite database file.
        **kwargs: Additional kwargs forwarded to create_engine.

    Returns:
        Configured Engine instance.
    """
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    connect_args = kwargs.pop("connect_args", {})
    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args=connect_args,
        **kwargs,
    )

    event.listen(engine, "connect", _set_sqlite_pragma)
    return engine


def set_schema_version(engine: Engine, version: int = SCHEMA_VERSION) -> None:
    """Write the schema version to PRAGMA user_version."""
    with engine.begin() as conn:
        conn.execute(text(f"PRAGMA user_version={version}"))


def get_schema_version(engine: Engine) -> int:
    """Read the schema version from PRAGMA user_version."""
    with engine.connect() as conn:
        row = conn.execute(text("PRAGMA user_version")).fetchone()
        return row[0] if row else 0


def verify_schema_version(engine: Engine) -> int:
    """Verify DB schema matches expected version.

    Returns:
        0 if match, -1 if DB is older (needs upgrade), 1 if DB is newer (unknown version).
    """
    current = get_schema_version(engine)
    if current == SCHEMA_VERSION:
        return 0
    if current < SCHEMA_VERSION:
        return -1
    return 1
