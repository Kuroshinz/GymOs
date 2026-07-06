from __future__ import annotations

from collections.abc import Sequence

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QWidget

from ui.visualization.core.base import BaseVisualization
from ui.visualization.core.utils import interpolate_color


class FatigueHeatmap(BaseVisualization):
    """Fatigue levels by body area as a color-coded heatmap."""

    def __init__(
        self,
        color_scheme=None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(color_scheme, parent)
        self._areas: list[tuple[str, float]] = []
        self._max_fatigue = 100.0
        self.setFixedHeight(50)

    def set_data(self, areas: Sequence[tuple[str, float]] | None = None, max_fatigue: float = 100.0) -> None:
        self._areas = list(areas) if areas else []
        self._max_fatigue = max(max_fatigue, 1.0)
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        colors = self._colors()
        w = self.width()
        h = 40
        n = len(self._areas)
        if n == 0:
            return

        cell_w = max(24, (w - 10) // max(n, 1))
        for i, (name, val) in enumerate(self._areas):
            x = i * cell_w
            fraction = min(val / self._max_fatigue, 1.0)
            c = interpolate_color(colors.success, colors.error, fraction)
            painter.setBrush(QColor(c))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(x + 1, 2, cell_w - 2, h - 4, 3, 3)

            painter.setFont(self._make_font(7))
            painter.setPen(QColor(colors.text_inverse))
            painter.drawText(QRectF(x, 0, cell_w, h), Qt.AlignCenter, name)

        painter.end()
