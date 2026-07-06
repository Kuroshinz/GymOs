"""Database backup and restore manager.

Provides:
  - Full database backup with WAL checkpoint
  - Backup validation (file exists, integrity check)
  - Backup metadata tracking
  - Automatic backup before migration
  - Restore from backup with compatibility checks
"""

from __future__ import annotations

import json
import logging
import os
import shutil
import sqlite3
from datetime import UTC, datetime
from pathlib import Path

from shared.version import APP_VERSION, BUILD_NUMBER

logger = logging.getLogger(__name__)

_BACKUP_DIR = Path(os.path.dirname(__file__)) / ".." / ".." / "data" / "backups"
_METADATA_FILE = "backup_meta.json"

# ── Backup ────────────────────────────────────────────────────────────────────


class BackupResult:
    """Result of a backup operation."""

    def __init__(
        self,
        success: bool,
        backup_path: str | None = None,
        error: str = "",
    ) -> None:
        self.success = success
        self.backup_path = backup_path
        self.error = error


def _ensure_backup_dir() -> Path:
    _BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    return _BACKUP_DIR


def _timestamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%d_%H%M%S")


def backup_database(db_path: str, label: str = "") -> BackupResult:
    """Create a full backup of the SQLite database.

    Performs a WAL checkpoint before copying to ensure consistency.

    Args:
        db_path: Path to the source database file.
        label: Optional label (e.g. "pre-migration", "manual").

    Returns:
        BackupResult with backup path on success.
    """
    src = Path(db_path)
    if not src.exists():
        return BackupResult(False, error=f"Database not found: {db_path}")

    try:
        # Checkpoint WAL first
        conn = sqlite3.connect(str(src))
        conn.execute("PRAGMA wal_checkpoint(FULL)")
        conn.close()

        backup_dir = _ensure_backup_dir()
        ts = _timestamp()
        stem = src.stem
        suffix = f"_{label}" if label else ""
        backup_name = f"{stem}_backup_{ts}{suffix}.db"
        backup_path = backup_dir / backup_name

        shutil.copy2(str(src), str(backup_path))

        # Write metadata
        schema_ver = _read_user_version(str(src))
        _write_metadata(backup_dir, backup_name, schema_ver, label)

        logger.info(
            "Database backed up: %s -> %s (schema v%d)",
            db_path, backup_path, schema_ver,
        )
        return BackupResult(True, backup_path=str(backup_path))

    except Exception as e:
        logger.exception("Backup failed for %s", db_path)
        return BackupResult(False, error=str(e))


def _read_user_version(db_path: str) -> int:
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.execute("PRAGMA user_version")
        version = cursor.fetchone()[0]
        conn.close()
        return version
    except Exception:
        return 0


def _write_metadata(
    backup_dir: Path,
    backup_name: str,
    schema_version: int,
    label: str,
) -> None:
    meta_path = backup_dir / _METADATA_FILE
    entries: list[dict] = []
    if meta_path.exists():
        try:
            entries = json.loads(meta_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, Exception):
            entries = []

    entries.append({
        "backup_name": backup_name,
        "timestamp": _timestamp(),
        "schema_version": schema_version,
        "app_version": APP_VERSION,
        "build_number": BUILD_NUMBER,
        "label": label,
    })

    # Keep last 50 entries
    entries = entries[-50:]
    meta_path.write_text(
        json.dumps(entries, indent=2),
        encoding="utf-8",
    )


# ── Restore ───────────────────────────────────────────────────────────────────


class RestoreResult:
    """Result of a restore operation."""

    def __init__(
        self,
        success: bool,
        error: str = "",
        schema_version: int = 0,
    ) -> None:
        self.success = success
        self.error = error
        self.schema_version = schema_version


def restore_database(backup_path: str, target_path: str) -> RestoreResult:
    """Restore a database from a backup file.

    Validates the backup before restoring.

    Args:
        backup_path: Path to the backup file.
        target_path: Path to restore to (the live database).

    Returns:
        RestoreResult indicating success/failure.
    """
    backup = Path(backup_path)
    target = Path(target_path)

    if not backup.exists():
        return RestoreResult(False, error=f"Backup not found: {backup_path}")

    try:
        # Validate backup integrity
        validation = validate_backup(backup_path)
        if not validation.success:
            return RestoreResult(False, error=validation.error)

        # Ensure target directory exists
        target.parent.mkdir(parents=True, exist_ok=True)

        # Create backup of current live database before overwriting
        if target.exists():
            pre_restore = backup_database(str(target), label="pre-restore")
            if not pre_restore.success:
                logger.warning("Pre-restore backup failed: %s", pre_restore.error)

        shutil.copy2(str(backup), str(target))

        schema_ver = _read_user_version(str(target))
        logger.info(
            "Database restored: %s -> %s (schema v%d)",
            backup_path, target_path, schema_ver,
        )
        return RestoreResult(True, schema_version=schema_ver)

    except Exception as e:
        logger.exception("Restore failed for %s", backup_path)
        return RestoreResult(False, error=str(e))


# ── Validation ────────────────────────────────────────────────────────────────


class ValidationResult:
    """Result of a backup validation."""

    def __init__(
        self,
        success: bool,
        error: str = "",
        schema_version: int = 0,
        file_size: int = 0,
    ) -> None:
        self.success = success
        self.error = error
        self.schema_version = schema_version
        self.file_size = file_size


def validate_backup(backup_path: str) -> ValidationResult:
    """Validate a backup file is a proper SQLite database.

    Checks:
      - File exists and is not empty
      - Is a valid SQLite database
      - PRAGMA integrity_check passes
      - Schema version is readable

    Args:
        backup_path: Path to the backup file.

    Returns:
        ValidationResult.
    """
    path = Path(backup_path)

    if not path.exists():
        return ValidationResult(False, error=f"File not found: {backup_path}")

    file_size = path.stat().st_size
    if file_size == 0:
        return ValidationResult(False, error="Backup file is empty")

    try:
        conn = sqlite3.connect(str(path))

        # SQLite format check
        cursor = conn.execute("PRAGMA schema_version")
        cursor.fetchone()

        # Check integrity
        cursor = conn.execute("PRAGMA integrity_check")
        result = cursor.fetchone()
        if result and result[0] != "ok":
            conn.close()
            return ValidationResult(False, error=f"Integrity check failed: {result[0]}")

        schema_ver = _read_user_version(str(path))
        conn.close()

        return ValidationResult(
            success=True,
            schema_version=schema_ver,
            file_size=file_size,
        )

    except sqlite3.DatabaseError as e:
        return ValidationResult(False, error=f"Invalid database file: {e}")
    except Exception as e:
        return ValidationResult(False, error=str(e))


# ── Automatic backup before migration ─────────────────────────────────────────


def backup_before_migration(db_path: str) -> BackupResult:
    """Create an automatic backup before running a migration."""
    return backup_database(db_path, label="pre-migration")


def list_backups() -> list[dict]:
    """List all backup entries from metadata."""
    meta_path = _BACKUP_DIR / _METADATA_FILE
    if not meta_path.exists():
        return []
    try:
        return json.loads(meta_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, Exception):
        return []


def get_latest_backup() -> str | None:
    """Get the path to the most recent backup."""
    entries = list_backups()
    if not entries:
        return None
    latest = entries[-1]
    backup_path = _BACKUP_DIR / latest["backup_name"]
    return str(backup_path) if backup_path.exists() else None
