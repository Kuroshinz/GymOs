"""Last session recovery dialog.

Shown on startup if the previous session crashed or no crash
recovery was performed.
"""

from __future__ import annotations

import logging
from pathlib import Path

from shared.crash.handler import get_last_crash_report
from shared.version import APP_VERSION

logger = logging.getLogger(__name__)


def has_pending_recovery() -> bool:
    """Check if there is an unrecovered crash report."""
    report = get_last_crash_report()
    if report is None:
        return False
    return not _is_recovered(report)


def _is_recovered(report_path: str) -> bool:
    """Check if a specific crash report has been acknowledged."""
    marker = Path(report_path).with_suffix(".recovered")
    return marker.exists()


def mark_recovered(report_path: str) -> None:
    """Mark a crash report as recovered."""
    marker = Path(report_path).with_suffix(".recovered")
    marker.write_text("recovered", encoding="utf-8")


def show_recovery_dialog_if_needed() -> None:
    """Show recovery dialog if there are unrecovered crash reports.

    Safe to call on every startup; no-op if no pending recovery.
    """
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
        "<p style='font-size: 11px; color: gray;'>"
    )
    title.setWordWrap(True)
    layout.addWidget(title)

    info = QLabel(
        "<p><b>Your data is safe.</b> "
        "Workouts, settings, and progress files are preserved.</p>"
        "<p>If you were in the middle of a workout, "
        "any unsaved progress may have been lost.</p>"
        "<p>Version: {}</p>".format(APP_VERSION)
    )
    info.setWordWrap(True)
    layout.addWidget(info)

    btn = QPushButton("Continue")
    btn.clicked.connect(lambda: (mark_recovered(report_path), dialog.accept()))
    layout.addWidget(btn)

    dialog.exec()
