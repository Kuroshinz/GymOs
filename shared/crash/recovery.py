"""Last session recovery dialog.

Shown on startup if the previous session crashed or no crash
recovery was performed.
"""

from __future__ import annotations

import json
import logging
import os
from datetime import UTC, datetime
from pathlib import Path

from shared.crash.handler import get_last_crash_report
from shared.version import APP_VERSION

logger = logging.getLogger(__name__)

_META_FILENAME = ".meta"
_ARCHIVE_DAYS = 30
_DELETE_DAYS = 90


def _get_crash_dir() -> Path:
    return Path(__file__).resolve().parent.parent.parent / "data" / "crashes"


def _cleanup_orphaned_metadata() -> None:
    """Remove .meta and .recovered files without a matching .log."""
    crash_dir = _get_crash_dir()
    if not crash_dir.exists():
        return
    for f in crash_dir.iterdir():
        if f.suffix not in (_META_FILENAME, ".recovered"):
            continue
        if not f.with_suffix(".log").exists():
            f.unlink()
            logger.info("Removed orphaned metadata: %s", f.name)


def _cleanup_old_reports() -> None:
    """Archive reports older than ARCHIVE_DAYS, delete older than DELETE_DAYS."""
    crash_dir = _get_crash_dir()
    if not crash_dir.exists():
        return

    now = datetime.now(UTC).timestamp()
    archive_dir = crash_dir / "archive"

    for f in crash_dir.iterdir():
        if f.suffix != ".log":
            continue
        try:
            age_days = (now - f.stat().st_mtime) / 86400
        except OSError:
            continue

        if age_days > _DELETE_DAYS:
            f.unlink()
            f.with_suffix(_META_FILENAME).unlink(missing_ok=True)
            f.with_suffix(".recovered").unlink(missing_ok=True)
            logger.info("Deleted old crash report: %s", f.name)
        elif age_days > _ARCHIVE_DAYS:
            archive_dir.mkdir(parents=True, exist_ok=True)
            dest = archive_dir / f.name
            f.rename(dest)
            meta_src = f.with_suffix(_META_FILENAME)
            if meta_src.exists():
                meta_src.rename(archive_dir / meta_src.name)
            logger.info("Archived crash report: %s", f.name)


def has_pending_recovery() -> bool:
    """Check if there is an unrecovered crash report."""
    report = get_last_crash_report()
    if report is None:
        return False
    return not _is_recovered(report)


def _is_recovered(report_path: str) -> bool:
    """Check if a specific crash report has been acknowledged.

    Checks the .meta file first (JSON with 'handled' field), then
    falls back to the legacy .recovered marker for backward compat.
    """
    meta_path = Path(report_path).with_suffix(_META_FILENAME)
    if meta_path.exists():
        try:
            data = json.loads(meta_path.read_text(encoding="utf-8"))
            return data.get("handled", False)
        except (json.JSONDecodeError, OSError):
            logger.warning("Corrupt crash metadata: %s", meta_path)
            return False
    # Backward compat: legacy .recovered marker
    return Path(report_path).with_suffix(".recovered").exists()


def mark_recovered(report_path: str) -> None:
    """Mark a crash report as recovered by writing a .meta file.

    Uses atomic write (tmp + rename) to prevent partial writes.
    """
    meta_path = Path(report_path).with_suffix(_META_FILENAME)
    meta = {
        "schema": 1,
        "handled": True,
        "timestamp": datetime.now(UTC).isoformat(),
        "version": APP_VERSION,
    }
    tmp_path = meta_path.with_suffix(f".tmp{_META_FILENAME}")
    tmp_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    os.replace(str(tmp_path), str(meta_path))
    # Clean up legacy .recovered marker if present
    legacy = Path(report_path).with_suffix(".recovered")
    if legacy.exists():
        legacy.unlink()


def show_recovery_dialog_if_needed() -> None:
    """Show recovery dialog if there are unrecovered crash reports.

    Safe to call on every startup; no-op if no pending recovery.
    Also cleans up orphaned metadata and old reports on each call.
    """
    _cleanup_orphaned_metadata()
    _cleanup_old_reports()

    report = get_last_crash_report()
    if report is None:
        return
    if _is_recovered(report):
        return

    try:
        _show_dialog(report)
    except ImportError:
        logger.warning("Cannot show recovery dialog (Qt not available)")
    except Exception:
        logger.exception("Failed to show recovery dialog")


def _show_dialog(report_path: str) -> None:
    """Show the recovery dialog."""
    from PySide6.QtWidgets import QApplication, QDialog, QLabel, QPushButton, QVBoxLayout

    app = QApplication.instance()
    if app is None:
        return

    dialog = QDialog()
    dialog.setWindowTitle("GymOS")
    dialog.setMinimumWidth(480)

    layout = QVBoxLayout(dialog)

    title = QLabel(
        "<h2>GymOS did not shut down properly</h2>"
        "<p>A crash report from a previous session was found.</p>"
    )
    title.setWordWrap(True)
    layout.addWidget(title)

    info = QLabel(
        "<p><b>Your data is safe.</b> "
        "Workouts, settings, and progress files are preserved.</p>"
        "<p>If you were in the middle of a workout, "
        "any unsaved progress may have been lost.</p>"
        "<p style='font-size: 11px; color: gray;'>"
        f"Crash report: {report_path}</p>"
        f"<p>Version: {APP_VERSION}</p>"
    )
    info.setWordWrap(True)
    layout.addWidget(info)

    btn = QPushButton("Continue")

    def _handle_recovered() -> None:
        mark_recovered(report_path)
        dialog.accept()

    btn.clicked.connect(_handle_recovered)
    layout.addWidget(btn)

    dialog.exec()
