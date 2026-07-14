from __future__ import annotations

from collections.abc import Sequence

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QFont, QPainter
from PySide6.QtWidgets import QFrame, QWidget

from ui.design_system.tokens.color import ColorScheme, color_from_scheme
from ui.design_system.tokens.radius import RadiusTokens, radius_to_px

R = RadiusTokens()


class WeeklyTimeline(QFrame):
    def __init__(
        self,
        days: Sequence[str] | None = None,
        color_scheme: ColorScheme = ColorScheme.DARK,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._color_scheme = color_scheme
        self._days: list[str] = list(days) if days else ["M", "T", "W", "T", "F", "S", "S"]
        self._values: list[float] = [0.0] * len(self._days)
        self._labels: list[str] = [""] * len(self._days)
        self._max_value = 100.0
        self.setFixedHeight(80)

    def _colors(self):
        return color_from_scheme(self._color_scheme)

    def set_data(self, values: Sequence[float], labels: Sequence[str] | None = None, max_value: float = 100.0) -> None:
        self._values = list(values)
        self._max_value = max(max_value, 1.0)
        if labels:
            self._labels = list(labels)
        if len(self._values) < len(self._days):
            self._values.extend([0.0] * (len(self._days) - len(self._values)))
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        colors = self._colors()
        w = self.width()
        h = 60
        n = len(self._days)
        if n == 0:
            return

        bar_w = min(32, (w - 20) // n - 6)
        spacing = (w - 20 - bar_w * n) // max(n - 1, 1)
        if spacing < 4:
            spacing = 4
        start_x = 10

        for i, day in enumerate(self._days):
            x = start_x + i * (bar_w + spacing)
            fraction = min(self._values[i] / self._max_value, 1.0) if self._max_value > 0 else 0.0
            bar_h = max(int(fraction * (h - 20)), 0)
            bar_y = h - 10 - bar_h

            bar_color = colors.primary
            if fraction < 0.3:
                bar_color = colors.error
            elif fraction < 0.6:
                bar_color = colors.warning

            painter.setBrush(QColor(bar_color))
            painter.setPen(Qt.NoPen)
            r = radius_to_px(R.sm)
            painter.drawRoundedRect(x, bar_y, bar_w, bar_h, r, r)

            font = QFont()
            font.setPixelSize(10)
            painter.setFont(font)
            painter.setPen(QColor(colors.text_disabled))
            painter.drawText(QRectF(x, h - 8, bar_w, 14), Qt.AlignCenter, day)

        painter.end()
