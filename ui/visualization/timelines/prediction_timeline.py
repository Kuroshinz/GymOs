from __future__ import annotations

from collections.abc import Sequence

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget

from ui.visualization.core.base import BaseVisualization


class PredictionTimeline(BaseVisualization):
    """Line chart with dots showing predicted values over time with optional goal line."""

    def __init__(
        self,
        color_scheme=None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(color_scheme, parent)
        self._points: list[tuple[str, float, float]] = []
        self._goal_line: float = 0.0
        self.setFixedHeight(120)

    def set_data(self, points: Sequence[tuple[str, float, float]] | None = None, goal_line: float = 0.0) -> None:
        self._points = list(points) if points else []
        self._goal_line = goal_line
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        colors = self._colors()
        w = self.width()
        h = 100
        n = len(self._points)
        if n < 2:
            return

        pad = 40
        plot_w = w - pad * 2
        values = [p[2] for p in self._points]
        min_v = min(values) * 0.9 if values else 0
        max_v = max(values) * 1.1 if values else 100

        def x_pos(i): return pad + i * plot_w / (n - 1)
        def y_pos(v):
            if max_v == min_v:
                return h / 2
            return h - 15 - (v - min_v) / (max_v - min_v) * (h - 30)

        if self._goal_line > 0:
            gy = y_pos(self._goal_line)
            pen = QPen(QColor(colors.warning), 1, Qt.DashLine)
            painter.setPen(pen)
            painter.drawLine(int(pad), int(gy), int(pad + plot_w), int(gy))

        for i in range(n - 1):
            x1, y1 = int(x_pos(i)), int(y_pos(self._points[i][2]))
            x2, y2 = int(x_pos(i + 1)), int(y_pos(self._points[i + 1][2]))
            pen = QPen(QColor(colors.primary), 2)
            painter.setPen(pen)
            painter.drawLine(x1, y1, x2, y2)

        for i, (date, label, val) in enumerate(self._points):
            x, y = int(x_pos(i)), int(y_pos(val))
            painter.setBrush(QColor(colors.primary))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(x - 4, y - 4, 8, 8)
            painter.setFont(self._make_font(9))
            painter.setPen(QColor(colors.text_disabled))
            painter.drawText(QRectF(x - 20, h, 40, 16), Qt.AlignCenter, date)

        painter.end()
