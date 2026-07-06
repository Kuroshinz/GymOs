from __future__ import annotations

from collections.abc import Sequence

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget

from ui.visualization.core.base import BaseVisualization


class RecoveryTimeline(BaseVisualization):
    """Recovery score history as a filled area line chart."""

    def __init__(
        self,
        color_scheme=None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(color_scheme, parent)
        self._points: list[tuple[str, float]] = []
        self.setFixedHeight(100)

    def set_data(self, points: Sequence[tuple[str, float]] | None = None) -> None:
        self._points = list(points) if points else []
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        colors = self._colors()
        w = self.width()
        h = 85
        n = len(self._points)
        if n < 2:
            return

        pad = 35
        plot_w = w - pad * 2
        vals = [p[1] for p in self._points]
        min_v = min(vals) * 0.9 if vals else 0
        max_v = max(vals) * 1.1 if vals else 100

        def x_pos(i): return pad + i * plot_w / (n - 1)
        def y_pos(v):
            if max_v == min_v:
                return h / 2
            return h - 10 - (v - min_v) / (max_v - min_v) * (h - 20)

        path = []
        for i, (_, val) in enumerate(self._points):
            path.append((int(x_pos(i)), int(y_pos(val))))

        for i in range(n - 1):
            pen = QPen(QColor(colors.success), 2)
            painter.setPen(pen)
            painter.drawLine(path[i][0], path[i][1], path[i + 1][0], path[i + 1][1])

        for i, (date, val) in enumerate(self._points):
            x, y = path[i]
            painter.setBrush(QColor(colors.success))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(x - 3, y - 3, 6, 6)
            painter.setFont(self._make_font(8))
            painter.setPen(QColor(colors.text_disabled))
            painter.drawText(QRectF(x - 15, h - 2, 30, 14), Qt.AlignCenter, date)

        painter.end()
