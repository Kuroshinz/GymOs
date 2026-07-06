from __future__ import annotations

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QWidget

from ui.visualization.core.base import RADIUS, BaseVisualization, radius_to_px


class StabilityGauge(BaseVisualization):
    """Stability indicator — centered gauge showing variance/deviation."""

    def __init__(
        self,
        width: int = 180,
        height: int = 28,
        color_scheme=None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(color_scheme, parent)
        self._value = 0.0
        self._max_value = 1.0
        self._label = ""
        self._gauge_width = width
        self._gauge_height = height
        self.setFixedSize(width, height + 20)

    def set_stability(self, value: float, label: str = "") -> None:
        target = max(0.0, min(1.0, value))
        if target != self._value:
            self.animate(target)
        self._label = label

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        colors = self._colors()
        bar_h = self._gauge_height
        bar_w = self._gauge_width
        r = radius_to_px(RADIUS.full)

        painter.setBrush(QColor(colors.scrollbar_handle))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(QRectF(0, 0, bar_w, bar_h), r, r)

        cx = bar_w / 2
        fill_w = int(bar_w * self._value * 0.8)
        fill_x = int(cx - fill_w / 2)
        if fill_w > 0:
            color = self._value_color(colors, self._value)
            painter.setBrush(QColor(color))
            painter.drawRoundedRect(QRectF(fill_x, 0, fill_w, bar_h), r, r)

        painter.setFont(self._make_font(11, True))
        painter.setPen(QColor(colors.text_inverse))
        painter.drawText(QRectF(0, 0, bar_w, bar_h), Qt.AlignCenter, f"{int(self._value * 100)}%")

        if self._label:
            painter.setFont(self._make_font(10))
            painter.setPen(QColor(colors.text_disabled))
            painter.drawText(QRectF(0, bar_h + 4, bar_w, 16), Qt.AlignCenter, self._label)

        painter.end()
