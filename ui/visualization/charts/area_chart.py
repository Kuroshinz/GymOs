from __future__ import annotations

from collections.abc import Sequence

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QWidget

from ui.visualization.core.base import BaseVisualization


class AreaChart(BaseVisualization):
    """Filled area chart with optional gradient for cumulative metrics."""

    def __init__(
        self,
        color_scheme=None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(color_scheme, parent)
        self._series: list[tuple[str, float]] = []
        self._fill_color: str = ""
        self.setFixedHeight(100)

    def set_data(self, series: Sequence[tuple[str, float]] | None = None, fill_color: str = "") -> None:
        self._series = list(series) if series else []
        self._fill_color = fill_color
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        colors = self._colors()
        w = self.width()
        h = 85
        n = len(self._series)
        if n < 2:
            return

        pad = 35
        plot_w = w - pad * 2
        vals = [p[1] for p in self._series]
        min_v = min(vals) * 0.9 if vals else 0
        max_v = max(vals) * 1.1 if vals else 100

        def xp(i): return pad + i * plot_w / (n - 1)
        def yp(v):
            if max_v == min_v:
                return h / 2
            return h - 10 - (v - min_v) / (max_v - min_v) * (h - 20)

        path = QPainterPath()
        path.moveTo(xp(0), h)
        for i in range(n):
            path.lineTo(xp(i), yp(self._series[i][1]))
        path.lineTo(xp(n - 1), h)
        path.closeSubpath()

        fc = self._fill_color or colors.primary
        painter.setBrush(QColor(fc + "40"))
        painter.setPen(Qt.NoPen)
        painter.drawPath(path)

        pen = QPen(QColor(fc), 2)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        for i in range(n - 1):
            painter.drawLine(int(xp(i)), int(yp(self._series[i][1])), int(xp(i + 1)), int(yp(self._series[i + 1][1])))

        painter.end()
