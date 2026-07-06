from __future__ import annotations

from collections.abc import Sequence

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QWidget

from ui.visualization.core.base import RADIUS, BaseVisualization, radius_to_px
from ui.visualization.core.utils import interpolate_color


class MuscleHeatmap(BaseVisualization):
    """Colored bars showing relative volume per muscle group."""

    def __init__(
        self,
        muscles: Sequence[tuple[str, float]] | None = None,
        color_scheme=None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(color_scheme, parent)
        self._muscles: list[tuple[str, float]] = list(muscles) if muscles else []
        self._max_volume = 100.0
        self.setFixedHeight(60)

    def set_data(self, muscles: Sequence[tuple[str, float]] | None = None, max_volume: float = 100.0) -> None:
        self._muscles = list(muscles) if muscles else []
        self._max_volume = max(max_volume, 1.0)
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        colors = self._colors()
        w = self.width()
        h = 50
        n = len(self._muscles)
        if n == 0:
            return

        cell_w = min(80, (w - 20) // n - 4)
        start_x = 10

        for i, (name, volume) in enumerate(self._muscles):
            x = start_x + i * (cell_w + 4)
            fraction = min(volume / self._max_volume, 1.0) if self._max_volume > 0 else 0.0

            lo, hi = colors.surface, colors.primary
            c = interpolate_color(lo, hi, fraction)
            r = radius_to_px(RADIUS.md)

            painter.setBrush(QColor(c))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(x, 0, cell_w, h, r, r)

            painter.setFont(self._make_font(9, True))
            painter.setPen(QColor(colors.text_inverse))
            painter.drawText(QRectF(x, 0, cell_w, h), Qt.AlignCenter, name)

        painter.end()
