from __future__ import annotations

from collections.abc import Sequence

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QWidget

from ui.visualization.core.base import BaseVisualization
from ui.visualization.core.utils import interpolate_color


class VolumeHeatmap(BaseVisualization):
    """Training volume distribution across muscle groups as a heatmap."""

    def __init__(
        self,
        color_scheme=None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(color_scheme, parent)
        self._data: list[tuple[str, float]] = []
        self._max_val = 100.0
        self.setFixedHeight(50)

    def set_data(self, data: Sequence[tuple[str, float]] | None = None, max_val: float = 100.0) -> None:
        self._data = list(data) if data else []
        self._max_val = max(max_val, 1.0)
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        colors = self._colors()
        w = self.width()
        h = 40
        n = len(self._data)
        if n == 0:
            return

        cell_w = max(20, (w - 10) // max(n, 1))
        for i, (label, val) in enumerate(self._data):
            x = i * cell_w
            fraction = min(val / self._max_val, 1.0)
            c = interpolate_color("#1E293B", colors.primary, fraction)
            painter.setBrush(QColor(c))
            painter.setPen(Qt.NoPen)
            painter.drawRect(x, 0, cell_w, h)

            painter.setFont(self._make_font(7))
            painter.setPen(QColor(colors.text_inverse))
            painter.drawText(QRectF(x, 0, cell_w, h), Qt.AlignCenter, label)

        painter.end()
