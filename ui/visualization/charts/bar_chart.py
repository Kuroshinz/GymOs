from __future__ import annotations

from collections.abc import Sequence

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QWidget

from ui.visualization.core.base import RADIUS, BaseVisualization, radius_to_px


class BarChart(BaseVisualization):
    """Generic horizontal or vertical bar chart."""

    def __init__(
        self,
        orientation: str = "vertical",
        color_scheme=None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(color_scheme, parent)
        self._orientation = orientation
        self._bars: list[tuple[str, float]] = []
        self._max_val = 100.0
        self._bar_color: str = ""
        self.setFixedHeight(120 if orientation == "vertical" else 80)

    def set_data(self, bars: Sequence[tuple[str, float]] | None = None, max_val: float = 100.0, bar_color: str = "") -> None:
        self._bars = list(bars) if bars else []
        self._max_val = max(max_val, 1.0)
        self._bar_color = bar_color
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        colors = self._colors()
        w = self.width()
        h = self.height() - 20
        n = len(self._bars)
        if n == 0:
            return

        bc = self._bar_color or colors.primary
        r = radius_to_px(RADIUS.sm)

        if self._orientation == "vertical":
            bar_w = min(30, (w - 20) // n - 4)
            spacing = max((w - 20 - bar_w * n) // max(n - 1, 1), 3)
            for i, (label, val) in enumerate(self._bars):
                x = 10 + i * (bar_w + spacing)
                fraction = min(val / self._max_val, 1.0)
                bar_h = max(int(fraction * (h - 10)), 0)
                painter.setBrush(QColor(bc))
                painter.setPen(Qt.NoPen)
                painter.drawRoundedRect(x, h - 10 - bar_h, bar_w, bar_h, r, r)
                painter.setFont(self._make_font(8))
                painter.setPen(QColor(colors.text_disabled))
                painter.drawText(QRectF(x, h + 2, bar_w, 14), Qt.AlignCenter, label)
        else:
            bar_h = max(12, (h - 10) // n - 2)
            for i, (label, val) in enumerate(self._bars):
                y = 5 + i * (bar_h + 2)
                fraction = min(val / self._max_val, 1.0)
                bar_w = max(int(fraction * (w - 60)), 2)
                painter.setBrush(QColor(bc))
                painter.setPen(Qt.NoPen)
                painter.drawRoundedRect(50, y, bar_w, bar_h, r, r)
                painter.setFont(self._make_font(8))
                painter.setPen(QColor(colors.text_disabled))
                painter.drawText(QRectF(0, y, 46, bar_h), Qt.AlignRight | Qt.AlignVCenter, label)

        painter.end()
