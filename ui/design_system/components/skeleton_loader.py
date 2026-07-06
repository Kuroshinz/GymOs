from __future__ import annotations

from PySide6.QtCore import Property, Qt
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QFrame, QWidget

from ui.design_system.tokens.color import ColorScheme, color_from_scheme
from ui.design_system.tokens.radius import RadiusTokens, radius_to_px

RADIUS = RadiusTokens()


class SkeletonLoader(QFrame):
    def __init__(
        self,
        lines: int = 3,
        line_height: int = 14,
        last_line_width: int = 60,
        color_scheme: ColorScheme = ColorScheme.DARK,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._lines = lines
        self._line_height = line_height
        self._last_line_width = last_line_width
        self._color_scheme = color_scheme
        self._progress: float = 0.0
        self.setFixedHeight(lines * (line_height + 10) + 10)

    def _colors(self):
        return color_from_scheme(self._color_scheme)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        colors = self._colors()
        base = QColor(colors.scrollbar_handle)
        highlight = QColor(colors.surface_hover)
        w = self.width()

        for i in range(self._lines):
            y = 10 + i * (self._line_height + 10)
            lw = w - 20
            if i == self._lines - 1:
                lw = int(lw * self._last_line_width / 100)

            painter.setBrush(base)
            painter.setPen(Qt.NoPen)
            r = radius_to_px(RADIUS.sm)
            painter.drawRoundedRect(10, y, lw, self._line_height, r, r)

    @Property(float)
    def progress(self) -> float:
        return self._progress

    @progress.setter
    def progress(self, value: float) -> None:
        self._progress = value
        self.update()


class SkeletonBlock(QFrame):
    def __init__(
        self,
        height: int = 100,
        color_scheme: ColorScheme = ColorScheme.DARK,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._color_scheme = color_scheme
        self._height = height
        self.setFixedHeight(height)

    def _colors(self):
        return color_from_scheme(self._color_scheme)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        colors = self._colors()
        painter.setBrush(QColor(colors.scrollbar_handle))
        painter.setPen(Qt.NoPen)
        r = radius_to_px(RADIUS.lg) if RADIUS.lg else 8
        painter.drawRoundedRect(0, 0, self.width(), self._height, r, r)
