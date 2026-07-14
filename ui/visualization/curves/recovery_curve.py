from __future__ import annotations

from collections.abc import Sequence

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget

from ui.visualization.core.base import BaseVisualization


class RecoveryCurve(BaseVisualization):
    """Recovery score curve with zone shading (low/medium/high)."""

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

        def xp(i): return pad + i * pw / (n - 1)
        def yp(v): return h - 10 - (v / 100) * (h - 20)

        for zone_pct, zone_color in [(0.3, colors.error + "20"), (0.6, colors.warning + "20")]:
            zy = yp(zone_pct * 100)
            painter.fillRect(pad, int(zy), int(pw), int(h - 10 - zy), QColor(zone_color))

        for i in range(n - 1):
            c = colors.success
            if self._points[i][1] < 30:
                c = colors.error
            elif self._points[i][1] < 60:
                c = colors.warning
            pen = QPen(QColor(c), 2)
            painter.setPen(pen)
            painter.drawLine(int(xp(i)), int(yp(self._points[i][1])), int(xp(i + 1)), int(yp(self._points[i + 1][1])))

        for i, (label, val) in enumerate(self._points):
            x, y = int(xp(i)), int(yp(val))
            c = colors.success if val >= 60 else (colors.warning if val >= 30 else colors.error)
            painter.setBrush(QColor(c))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(x - 3, y - 3, 6, 6)
            painter.setFont(self._make_font(8))
            painter.setPen(QColor(colors.text_disabled))
            painter.drawText(x - 15, h - 2, 30, 14, Qt.AlignCenter, label)

        painter.end()
