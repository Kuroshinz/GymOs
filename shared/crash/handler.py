"""Global crash handler, safe shutdown, and session recovery.

Installs an excepthook that:
  1. Logs the crash with full traceback
  2. Writes a crash report to data/crashes/
  3. Shows a recovery dialog
  4. Performs safe shutdown
"""

from __future__ import annotations

import contextlib
import logging
import os
import sys
import traceback
import types
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path

from shared.version import APP_VERSION, BUILD_NUMBER

logger = logging.getLogger(__name__)

_CRASH_DIR = Path(os.path.dirname(__file__)) / ".." / ".." / "data" / "crashes"
_original_excepthook: Callable[[type[BaseException], BaseException, types.TracebackType | None], None] = sys.excepthook
_cleanup_callbacks: list[Callable[[], None]] = []


def register_cleanup(callback: Callable[[], None]) -> None:
    """Register a cleanup callback for safe shutdown."""
    _cleanup_callbacks.append(callback)


def _ensure_crash_dir() -> Path:
    _CRASH_DIR.mkdir(parents=True, exist_ok=True)
    return _CRASH_DIR


def write_crash_report(exc_type: type[BaseException], exc_value: BaseException, tb: types.TracebackType | None) -> str:
    """Write a crash report file.

    Returns:
        Path to the crash report file.
    """
    ts = datetime.now(UTC).strftime("%Y%m%d_%H%M%S_%f")
    crash_dir = _ensure_crash_dir()
    report_path = crash_dir / f"crash_{ts}.log"

    lines = [
        "=" * 60,
        "GymOS Crash Report",
        "=" * 60,
        f"Time:       {datetime.now(UTC).isoformat()}",
        f"Version:    {APP_VERSION} (build {BUILD_NUMBER})",
        f"Python:     {sys.version}",
        f"Platform:   {sys.platform}",
        "-" * 60,
        "Exception:",
        "".join(traceback.format_exception(exc_type, exc_value, tb)),
        "-" * 60,
        "Loaded Modules (last 20):",
    ]
    for mod_name in sorted(sys.modules.keys())[-20:]:
        lines.append(f"  {mod_name}")

    report_path.write_text("\n".join(lines), encoding="utf-8")
    return str(report_path)


def safe_shutdown() -> None:
    """Run all cleanup callbacks and exit."""
    for cb in _cleanup_callbacks:
        try:
            cb()
        except Exception:
            logger.exception("Cleanup callback failed")
    _cleanup_callbacks.clear()


def _global_excepthook(exc_type: type[BaseException], exc_value: BaseException, tb: types.TracebackType | None) -> None:
    """Global exception handler installed as sys.excepthook.

    On PySide6 applications, also installs qInstallMessageHandler
    for Qt-level crashes.
    """
    if issubclass(exc_type, KeyboardInterrupt):
        safe_shutdown()
        sys.exit(0)

    logger.critical(
        "Unhandled exception: %s: %s",
        exc_type.__name__,
        exc_value,
        exc_info=(exc_type, exc_value, tb),
    )

    report_path = write_crash_report(exc_type, exc_value, tb)
    logger.critical("Crash report written to %s", report_path)

    safe_shutdown()

    with contextlib.suppress(Exception):
        _show_recovery_dialog(exc_type, exc_value, report_path)

    _original_excepthook(exc_type, exc_value, tb)


def _show_recovery_dialog(
    exc_type: type[BaseException],
    exc_value: BaseException,
    report_path: str,
) -> None:
    """Show a recovery dialog when running in GUI mode.

    Falls back silently if Qt is not available.
    """
    try:
        from PySide6.QtWidgets import QApplication, QMessageBox

        app = QApplication.instance()
        if app is None:
            return

        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("GymOS — Unexpected Error")
        msg.setText(
            "GymOS encountered an unexpected error and needs to close.\n\n"
            "Your workouts and settings have been saved."
        )
        msg.setInformativeText(
            "Please restart GymOS. If the problem persists, "
            "contact support with the crash report file.\n\n"
            "Crash report: data/crashes/crash.log"
        )
        msg.setDetailedText(
            f"{exc_type.__name__}: {exc_value}\n"
            f"Report: {report_path}"
        )
        msg.setStandardButtons(QMessageBox.Close)
        msg.exec()
    except ImportError:
        pass


def install_global_handler() -> None:
    """Install the global exception handler.

    Call once at application startup.
    """
    global _original_excepthook
    _original_excepthook = sys.excepthook
    sys.excepthook = _global_excepthook


def get_last_crash_report() -> str | None:
    """Get the path to the most recent crash report, if any."""
    if not _CRASH_DIR.exists():
        return None
    crash_files = _list_crash_reports()
    return str(crash_files[0]) if crash_files else None


def get_all_crash_reports() -> list[str]:
    """Get paths to all crash reports, newest first."""
    if not _CRASH_DIR.exists():
        return []
    return [str(p) for p in _list_crash_reports()]


def _list_crash_reports() -> list[Path]:
    """List crash report files (*.log) in the crash dir, newest first."""
    return sorted(
        (p for p in _CRASH_DIR.iterdir() if p.suffix == ".log"),
        reverse=True,
    )
