from __future__ import annotations

from collections.abc import Sequence

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QWidget

from ui.design_system.tokens.radius import radius_to_px
from ui.visualization.core.base import RADIUS, BaseVisualization


class WeeklyTimeline(BaseVisualization):
    """Bar chart showing daily values across a week."""

    def __init__(
        self,
        days: Sequence[str] | None = None,
        color_scheme=None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(color_scheme, parent)
        self._days: list[str] = list(days) if days else ["M", "T", "W", "T", "F", "S", "S"]
        self._values: list[float] = [0.0] * len(self._days)
        self._labels: list[str] = [""] * len(self._days)
        self._value = 0.0
        self._max_value = 100.0
        self.setFixedHeight(80)

    def set_data(self, values: Sequence[float], labels: Sequence[str] | None = None, max_value: float = 100.0) -> None:
        self._values = list(values)
        self._max_value = max(max_value, 1.0)
        if labels:
            self._labels = list(labels)
        if len(self._values) < len(self._days):
            self._values.extend([0.0] * (len(self._days) - len(self._values)))
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        colors = self._colors()
        w = self.width()
        h = 60
        n = len(self._days)
        if n == 0:
            return

        bar_w = min(32, (w - 20) // n - 6)
        spacing = max((w - 20 - bar_w * n) // max(n - 1, 1), 4)
        start_x = 10

        for i, day in enumerate(self._days):
            x = start_x + i * (bar_w + spacing)
            fraction = min(self._values[i] / self._max_value, 1.0) if self._max_value > 0 else 0.0
            bar_h = max(int(fraction * (h - 20)), 0)
            bar_y = h - 10 - bar_h

            bar_color = self._value_color(colors, fraction)
            r = radius_to_px(RADIUS.sm)
            painter.setBrush(QColor(bar_color))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(x, bar_y, bar_w, bar_h, r, r)

            painter.setFont(self._make_font(10))
            painter.setPen(QColor(colors.text_disabled))
            painter.drawText(QRectF(x, h - 8, bar_w, 14), Qt.AlignCenter, day)

        painter.end()
