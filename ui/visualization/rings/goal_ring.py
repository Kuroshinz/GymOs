from __future__ import annotations

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget

from ui.visualization.core.base import BaseVisualization


class GoalRing(BaseVisualization):
    """Ring showing progress toward a numeric goal (current / target)."""

    def __init__(
        self,
        size: int = 140,
        stroke_width: int = 10,
        color_scheme=None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(color_scheme, parent)
        self._value = 0.0
        self._max_value = 100.0
        self._ring_size = size
        self._stroke = stroke_width
        self._label = ""
        self._unit = ""
        self.setFixedSize(size + 20, size + 20)

    def set_goal(self, current: float, target: float, label: str = "", unit: str = "") -> None:
        self._max_value = max(target, 1.0)
        target_val = min(current, self._max_value)
        if target_val != self._value:
            self.animate(target_val)
        self._label = label
        self._unit = unit

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        colors = self._colors()

        cx = self._ring_size / 2 + 10
        cy = self._ring_size / 2 + 10
        radius = self._ring_size / 2 - self._stroke
        fraction = min(self._value / self._max_value, 1.0)

        bg = QPen(QColor(colors.scrollbar_handle), self._stroke)
        bg.setCapStyle(Qt.RoundCap)
        painter.setPen(bg)
        painter.drawArc(QRectF(cx - radius, cy - radius, radius * 2, radius * 2), 0, 360 * 16)

        fg = QPen(QColor(colors.primary), self._stroke)
        fg.setCapStyle(Qt.RoundCap)
        painter.setPen(fg)
        span = int(fraction * 360 * 16)
        painter.drawArc(QRectF(cx - radius, cy - radius, radius * 2, radius * 2), 90 * 16, -span)

        txt = f"{self._value:.1f}" if self._value != int(self._value) else str(int(self._value))
        painter.setFont(self._make_font(20, True))
        painter.setPen(QColor(colors.text_primary))
        painter.drawText(QRectF(0, cy - 20, self._ring_size + 20, 26), Qt.AlignCenter, txt)

        if self._unit:
            painter.setFont(self._make_font(11))
            painter.setPen(QColor(colors.text_disabled))
            painter.drawText(QRectF(0, cy + 6, self._ring_size + 20, 16), Qt.AlignCenter, self._unit)

        painter.end()
