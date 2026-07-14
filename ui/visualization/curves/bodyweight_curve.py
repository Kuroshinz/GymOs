from __future__ import annotations

from collections.abc import Sequence

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget

from ui.visualization.core.base import BaseVisualization


class BodyweightCurve(BaseVisualization):
    """Bodyweight trend with goal range band."""

    def __init__(
        self,
        color_scheme=None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(color_scheme, parent)
        self._points: list[tuple[str, float]] = []
        self._goal_low: float = 0.0
        self._goal_high: float = 0.0
        self.setFixedHeight(100)

    def set_data(self, points: Sequence[tuple[str, float]] | None = None, goal_low: float = 0.0, goal_high: float = 0.0) -> None:
        self._points = list(points) if points else []
        self._goal_low = goal_low
        self._goal_high = goal_high
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
        mn = min(vals + ([self._goal_low] if self._goal_low > 0 else [])) * 0.95
        mx = max(vals + ([self._goal_high] if self._goal_high > 0 else [])) * 1.05

        def xp(i): return pad + i * pw / (n - 1)
        def yp(v): return h - 10 - (v - mn) / (mx - mn) * (h - 20) if mx != mn else h / 2

        if self._goal_low > 0 and self._goal_high > 0:
            gy1, gy2 = yp(self._goal_low), yp(self._goal_high)
            painter.fillRect(pad, int(gy2), int(pw), int(gy1 - gy2), QColor(colors.success + "18"))
            painter.setPen(QPen(QColor(colors.success), 1, Qt.DashLine))
            painter.drawLine(pad, int(gy1), pad + pw, int(gy1))
            painter.drawLine(pad, int(gy2), pad + pw, int(gy2))

        for i in range(n - 1):
            painter.setPen(QPen(QColor(colors.primary), 2))
            painter.drawLine(int(xp(i)), int(yp(self._points[i][1])), int(xp(i + 1)), int(yp(self._points[i + 1][1])))

        for i, (label, val) in enumerate(self._points):
            x, y = int(xp(i)), int(yp(val))
            painter.setBrush(QColor(colors.primary))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(x - 3, y - 3, 6, 6)
            painter.setFont(self._make_font(8))
            painter.setPen(QColor(colors.text_disabled))
            painter.drawText(x - 15, h - 2, 30, 14, Qt.AlignCenter, label)

        painter.end()
