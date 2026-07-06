from __future__ import annotations

from collections.abc import Sequence

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget

from ui.visualization.core.base import BaseVisualization


class TrendChart(BaseVisualization):
    """Line chart tracking a metric over time with trend emphasis."""

    def __init__(
        self,
        color_scheme=None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(color_scheme, parent)
        self._series: list[tuple[str, float]] = []
        self._line_color: str = ""
        self.setFixedHeight(100)

    def set_data(self, series: Sequence[tuple[str, float]] | None = None, line_color: str = "") -> None:
        self._series = list(series) if series else []
        self._line_color = line_color
        self.update()

    def paintEvent(self, event) -> None:
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

        lc = self._line_color or colors.primary
        for i in range(n - 1):
            pen = QPen(QColor(lc), 2)
            painter.setPen(pen)
            painter.drawLine(int(xp(i)), int(yp(self._series[i][1])), int(xp(i + 1)), int(yp(self._series[i + 1][1])))

        for i, (label, val) in enumerate(self._series):
            x, y = int(xp(i)), int(yp(val))
            painter.setBrush(QColor(lc))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(x - 3, y - 3, 6, 6)
            painter.setFont(self._make_font(8))
            painter.setPen(QColor(colors.text_disabled))
            painter.drawText(QRectF(x - 15, h - 2, 30, 14), Qt.AlignCenter, label)

        painter.end()
