from __future__ import annotations

from collections.abc import Sequence

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget

from ui.visualization.core.base import BaseVisualization


class TrainingLoadCurve(BaseVisualization):
    """Training load (volume × intensity) smoothed curve over time."""

    def __init__(
        self,
        color_scheme=None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(color_scheme, parent)
        self._points: list[tuple[str, float]] = []
        self._overload_threshold: float = 0.0
        self.setFixedHeight(100)

    def set_data(self, points: Sequence[tuple[str, float]] | None = None, overload_threshold: float = 0.0) -> None:
        self._points = list(points) if points else []
        self._overload_threshold = overload_threshold
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        colors = self._colors()
        w, h = self.width(), 85
        n = len(self._points)
        if n < 2:
            return

        pad = 35
        pw = w - pad * 2
        vals = [p[1] for p in self._points]
        mx = max(vals) * 1.1 if vals else 100

        def xp(i): return pad + i * pw / (n - 1)
        def yp(v): return h - 10 - (v / mx) * (h - 20) if mx > 0 else h / 2

        if self._overload_threshold > 0:
            oy = yp(self._overload_threshold)
            painter.setPen(QPen(QColor(colors.warning), 1, Qt.DashLine))
            painter.drawLine(int(pad), int(oy), int(pad + pw), int(oy))

        for i in range(n - 1):
            pen = QPen(QColor(colors.primary), 2)
            painter.setPen(pen)
            painter.drawLine(int(xp(i)), int(yp(self._points[i][1])), int(xp(i + 1)), int(yp(self._points[i + 1][1])))

        for i, (label, val) in enumerate(self._points):
            x, y = int(xp(i)), int(yp(val))
            c = colors.error if val > self._overload_threshold > 0 else colors.primary
            painter.setBrush(QColor(c))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(x - 3, y - 3, 6, 6)
            painter.setFont(self._make_font(8))
            painter.setPen(QColor(colors.text_disabled))
            painter.drawText(x - 15, h - 2, 30, 14, Qt.AlignCenter, label)

        painter.end()
