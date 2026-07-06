from __future__ import annotations

from collections.abc import Sequence

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget

from ui.visualization.core.base import BaseVisualization


class PRCurve(BaseVisualization):
    """Personal record progression curve — highlights PR events."""

    def __init__(
        self,
        color_scheme=None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(color_scheme, parent)
        self._points: list[tuple[str, float, bool]] = []
        self.setFixedHeight(100)

    def set_data(self, points: Sequence[tuple[str, float, bool]] | None = None) -> None:
        self._points = list(points) if points else []
        self.update()

    def paintEvent(self, event) -> None:
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
        mn = min(vals) * 0.9 if vals else 0
        mx = max(vals) * 1.1 if vals else 100

        def xp(i): return pad + i * pw / (n - 1)
        def yp(v): return h - 10 - (v - mn) / (mx - mn) * (h - 20) if mx != mn else h / 2

        for i in range(n - 1):
            painter.setPen(QPen(QColor(colors.primary), 2))
            painter.drawLine(int(xp(i)), int(yp(self._points[i][1])), int(xp(i + 1)), int(yp(self._points[i + 1][1])))

        for i, (label, val, is_pr) in enumerate(self._points):
            x, y = int(xp(i)), int(yp(val))
            if is_pr:
                painter.setBrush(QColor(colors.accent))
                painter.setPen(QPen(QColor(colors.accent), 2))
                painter.drawEllipse(x - 5, y - 5, 10, 10)
                painter.setPen(QPen(QColor(colors.accent), 1))
                painter.drawLine(x, y - 6, x, y - 14)
                painter.setFont(self._make_font(7, True))
                painter.setPen(QColor(colors.accent))
                painter.drawText(x - 10, y - 22, 20, 10, Qt.AlignCenter, "PR")
            else:
                painter.setBrush(QColor(colors.text_disabled))
                painter.setPen(Qt.NoPen)
                painter.drawEllipse(x - 3, y - 3, 6, 6)

            painter.setFont(self._make_font(8))
            painter.setPen(QColor(colors.text_disabled))
            painter.drawText(x - 15, h - 2, 30, 14, Qt.AlignCenter, label)

        painter.end()
