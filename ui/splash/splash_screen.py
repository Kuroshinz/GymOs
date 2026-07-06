"""Splash screen with startup progress indication."""

from __future__ import annotations

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QColor, QFont, QPainter, QPixmap
from PySide6.QtWidgets import QSplashScreen, QWidget

from shared.version import APP_VERSION, COPYRIGHT

_SPLASH_WIDTH = 520
_SPLASH_HEIGHT = 340
_BG_COLOR = QColor("#0F172A")
_ACCENT_COLOR = QColor("#818CF8")
_TEXT_PRIMARY = QColor("#F1F5F9")
_TEXT_SECONDARY = QColor("#94A3B8")
_TEXT_MUTED = QColor("#64748B")
_PROGRESS_BG = QColor("#1E293B")


class SplashScreen(QSplashScreen):
    """Custom splash screen with animated progress indicator.

    Usage:
        splash = SplashScreen()
        splash.show()
        splash.advance("Loading modules...")

    The splash auto-closes when the application window is ready.
    """

    progress_updated = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        pixmap = QPixmap(_SPLASH_WIDTH, _SPLASH_HEIGHT)
        pixmap.fill(_BG_COLOR)
        super().__init__(pixmap)
        self._progress = 0
        self._message = "Initializing..."
        self._angle = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._rotate_spinner)
        self._timer.start(50)

    def _rotate_spinner(self) -> None:
        self._angle = (self._angle + 15) % 360
        self._draw()

    def advance(self, message: str, progress: int | None = None) -> None:
        """Update splash message and optional progress (0-100)."""
        self._message = message
        if progress is not None:
            self._progress = max(0, min(100, progress))
        self._draw()
        self.progress_updated.emit(message)

    def _draw(self) -> None:
        pixmap = QPixmap(_SPLASH_WIDTH, _SPLASH_HEIGHT)
        pixmap.fill(_BG_COLOR)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        # App icon area — stylized diamond logo
        cx, cy = _SPLASH_WIDTH // 2, 90
        self._draw_logo(painter, cx, cy)

        # Title
        title_font = QFont("Inter", 28, 700)
        painter.setFont(title_font)
        painter.setPen(_TEXT_PRIMARY)
        painter.drawText(0, cy + 40, _SPLASH_WIDTH, 40, Qt.AlignCenter, "GymOS")

        # Tagline
        tagline_font = QFont("Inter", 12, 400)
        painter.setFont(tagline_font)
        painter.setPen(_TEXT_SECONDARY)
        painter.drawText(
            0, cy + 72, _SPLASH_WIDTH, 24, Qt.AlignCenter,
            "Personal Hypertrophy Operating System",
        )

        # Progress bar background
        bar_x, bar_y = 80, cy + 120
        bar_w, bar_h = _SPLASH_WIDTH - 160, 4
        painter.fillRect(bar_x, bar_y, bar_w, bar_h, _PROGRESS_BG)

        # Progress bar fill
        fill_w = int(bar_w * (self._progress / 100))
        if fill_w > 0:
            painter.fillRect(bar_x, bar_y, fill_w, bar_h, _ACCENT_COLOR)

        # Spinner
        self._draw_spinner(painter, cx, bar_y + 24)

        # Message text
        msg_font = QFont("Inter", 11, 400)
        painter.setFont(msg_font)
        painter.setPen(_TEXT_MUTED)
        painter.drawText(
            0, bar_y + 20, _SPLASH_WIDTH, 24, Qt.AlignCenter,
            self._message,
        )

        # Version footer
        footer_font = QFont("Inter", 9, 400)
        painter.setFont(footer_font)
        painter.setPen(_TEXT_MUTED)
        painter.drawText(
            16, _SPLASH_HEIGHT - 28, _SPLASH_WIDTH - 32, 20,
            Qt.AlignLeft, f"v{APP_VERSION}",
        )
        painter.drawText(
            16, _SPLASH_HEIGHT - 28, _SPLASH_WIDTH - 32, 20,
            Qt.AlignRight, COPYRIGHT,
        )

        painter.end()
        self.setPixmap(pixmap)

    def _draw_logo(self, painter: QPainter, cx: int, cy: int) -> None:
        """Draw a diamond/hexagon logo shape."""
        size = 36
        painter.setPen(Qt.NoPen)
        painter.setBrush(_ACCENT_COLOR)
        points = [
            (cx, cy - size),
            (cx + size, cy),
            (cx, cy + size),
            (cx - size, cy),
        ]
        polygon = [__import__("PySide6.QtCore", fromlist=["QPoint"]).QPoint(x, y) for x, y in points]
        painter.drawPolygon(polygon)

    def _draw_spinner(self, painter: QPainter, cx: int, cy: int) -> None:
        """Draw a small spinning arc indicator."""
        r = 8
        painter.save()
        painter.translate(cx, cy)
        painter.rotate(self._angle)
        painter.setPen(Qt.NoPen)
        painter.setBrush(_ACCENT_COLOR)
        painter.drawPie(-r, -r, r * 2, r * 2, 0, 120 * 16)
        painter.restore()


def install_splash() -> SplashScreen:
    """Create and show the splash screen."""
    splash = SplashScreen()
    splash.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
    splash.setAttribute(Qt.WA_TranslucentBackground, False)
    splash.show()
    return splash
