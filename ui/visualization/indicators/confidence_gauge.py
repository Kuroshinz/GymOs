from __future__ import annotations

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QWidget

from ui.design_system.tokens.radius import radius_to_px
from ui.visualization.core.base import RADIUS, BaseVisualization


class ConfidenceGauge(BaseVisualization):
    """Horizontal confidence bar with percentage label."""

    def __init__(
        self,
        width: int = 200,
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

    def set_confidence(self, value: float, label: str = "") -> None:
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

        bg = QRectF(0, 0, bar_w, bar_h)
        painter.setBrush(QColor(colors.scrollbar_handle))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(bg, r, r)

        fill_w = int(bar_w * self._value)
        if fill_w > 0:
            fill_color = self._value_color(colors, self._value)
            painter.setBrush(QColor(fill_color))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(QRectF(0, 0, fill_w, bar_h), r, r)

        painter.setFont(self._make_font(12, True))
        painter.setPen(QColor(colors.text_inverse))
        painter.drawText(QRectF(0, 0, bar_w, bar_h), Qt.AlignCenter, f"{int(self._value * 100)}%")

        if self._label:
            painter.setFont(self._make_font(10))
            painter.setPen(QColor(colors.text_disabled))
            painter.drawText(QRectF(0, bar_h + 4, bar_w, 16), Qt.AlignCenter, self._label)

        painter.end()
