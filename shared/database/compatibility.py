"""Database and version compatibility checking.

Used at startup to determine whether the existing database can
be used, needs migration, or is incompatible.
"""

from __future__ import annotations

from sqlalchemy import Engine

from shared.database.engine import get_schema_version, verify_schema_version
from shared.version import (
    APP_VERSION,
    DATABASE_VERSION,
    SCHEMA_VERSION,
)


class CompatibilityResult:
    """Result of a compatibility check."""

    def __init__(
        self,
        compatible: bool,
        db_version: int,
        expected_version: int,
        reason: str = "",
    ) -> None:
        self.compatible = compatible
        self.db_version = db_version
        self.expected_version = expected_version
        self.reason = reason

    def __bool__(self) -> bool:
        return self.compatible

    def __repr__(self) -> str:
        return (
            f"CompatibilityResult(compatible={self.compatible}, "
            f"db={self.db_version}, expected={self.expected_version}, "
            f"reason={self.reason!r})"
        )


def check_schema_compatibility(engine: Engine) -> CompatibilityResult:
    """Check schema compatibility between existing DB and expected version.

    Compatibility rules:
      - Same SCHEMA_VERSION -> compatible
      - Older SCHEMA_VERSION -> incompatible (needs migration)
      - Newer SCHEMA_VERSION -> incompatible (application too old)
      - user_version == 0 (no schema) -> compatible (fresh DB, will be initialized)
    """
    db_version = get_schema_version(engine)

    if db_version == 0:
        return CompatibilityResult(True, db_version, SCHEMA_VERSION, "fresh database")

    schema_check = verify_schema_version(engine)
    if schema_check == 0:
        return CompatibilityResult(True, db_version, SCHEMA_VERSION, "schema match")
    if schema_check < 0:
        return CompatibilityResult(
            False, db_version, SCHEMA_VERSION,
            f"Database schema v{db_version} is older than expected v{SCHEMA_VERSION}. "
            f"Run migration to upgrade.",
        )

    return CompatibilityResult(
        False, db_version, SCHEMA_VERSION,
        f"Database schema v{db_version} is newer than expected v{SCHEMA_VERSION}. "
        f"This application version ({APP_VERSION}) is too old.",
    )


def check_database_compatibility(engine: Engine) -> CompatibilityResult:
    """Check overall database format compatibility.

    DATABASE_VERSION is bumped on breaking format changes (e.g. file format).
    """
    db_version = get_schema_version(engine)

    if db_version > DATABASE_VERSION:
        return CompatibilityResult(
            False, db_version, DATABASE_VERSION,
            f"Database format v{db_version} is newer than supported v{DATABASE_VERSION}. "
            f"Upgrade this application.",
        )

    return CompatibilityResult(True, db_version, DATABASE_VERSION, "")


def check_all(engine: Engine) -> list[CompatibilityResult]:
    """Run all compatibility checks and return results."""
    return [
        check_schema_compatibility(engine),
        check_database_compatibility(engine),
    ]


def all_compatible(engine: Engine) -> bool:
    """Quick check if all compatibility checks pass."""
    return all(check_all(engine))
