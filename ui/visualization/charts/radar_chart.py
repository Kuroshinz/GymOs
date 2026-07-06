from __future__ import annotations

import math
from collections.abc import Sequence

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QWidget

from ui.visualization.core.base import BaseVisualization


class RadarChart(BaseVisualization):
    """Radar/spider chart for multi-dimensional comparison."""

    def __init__(
        self,
        color_scheme=None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(color_scheme, parent)
        self._axes: list[tuple[str, float]] = []
        self._max_val = 100.0
        self.setFixedSize(200, 200)

    def set_data(self, axes: Sequence[tuple[str, float]] | None = None, max_val: float = 100.0) -> None:
        self._axes = list(axes) if axes else []
        self._max_val = max(max_val, 1.0)
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        colors = self._colors()
        cx = self.width() / 2
        cy = self.height() / 2 - 10
        r = min(cx, cy) - 20
        n = len(self._axes)
        if n < 3:
            return

        angle_step = 2 * math.pi / n

        for ring in [0.25, 0.5, 0.75, 1.0]:
            path = QPainterPath()
            for i in range(n + 1):
                a = -math.pi / 2 + i * angle_step
                px = cx + r * ring * math.cos(a)
                py = cy + r * ring * math.sin(a)
                if i == 0:
                    path.moveTo(px, py)
                else:
                    path.lineTo(px, py)
            painter.setPen(QPen(QColor(colors.border), 1))
            painter.setBrush(Qt.NoBrush)
            painter.drawPath(path)

        data_path = QPainterPath()
        for i, (label, val) in enumerate(self._axes):
            a = -math.pi / 2 + i * angle_step
            frac = min(val / self._max_val, 1.0)
            px = cx + r * frac * math.cos(a)
            py = cy + r * frac * math.sin(a)
            if i == 0:
                data_path.moveTo(px, py)
            else:
                data_path.lineTo(px, py)

        data_path.closeSubpath()
        painter.setBrush(QColor(colors.primary + "40"))
        painter.setPen(QPen(QColor(colors.primary), 2))
        painter.drawPath(data_path)

        for i, (label, val) in enumerate(self._axes):
            a = -math.pi / 2 + i * angle_step
            frac = min(val / self._max_val, 1.0)
            px = cx + r * frac * math.cos(a)
            py = cy + r * frac * math.sin(a)
            painter.setBrush(QColor(colors.primary))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(QPointF(px, py), 3, 3)

            lx = cx + (r + 15) * math.cos(a)
            ly = cy + (r + 15) * math.sin(a)
            painter.setFont(self._make_font(8))
            painter.setPen(QColor(colors.text_secondary))
            painter.drawText(int(lx) - 15, int(ly) - 4, 30, 12, Qt.AlignCenter, label)

        painter.end()
