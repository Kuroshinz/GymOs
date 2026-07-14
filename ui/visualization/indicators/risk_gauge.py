from __future__ import annotations

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QWidget

from ui.design_system.tokens.radius import radius_to_px
from ui.visualization.core.base import RADIUS, BaseVisualization


class RiskGauge(BaseVisualization):
    """Segmented risk meter — segments fill to indicate risk level."""

    def __init__(
        self,
        width: int = 160,
        height: int = 28,
        segments: int = 5,
        color_scheme=None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(color_scheme, parent)
        self._value = 0.0
        self._max_value = 1.0
        self._label = ""
        self._meter_width = width
        self._meter_height = height
        self._segments = segments
        self.setFixedSize(width, height + 24)

    def set_risk(self, value: float, label: str = "") -> None:
        target = max(0.0, min(1.0, value))
        if target != self._value:
            self.animate(target)
        self._label = label

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        colors = self._colors()
        w = self._meter_width
        h = self._meter_height
        r = radius_to_px(RADIUS.full)
        seg_w = w / self._segments

        for i in range(self._segments):
            x = int(i * seg_w)
            sw = int(seg_w) - 2
            fraction = (i + 1) / self._segments
            color = colors.success
            if fraction >= 0.8:
                color = colors.error
            elif fraction >= 0.5:
                color = colors.warning

            is_active = i < int(self._value * self._segments)
            painter.setBrush(QColor(colors.scrollbar_handle if not is_active else color))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(x, 0, sw, h, r, r)

        painter.setFont(self._make_font(10, True))
        painter.setPen(QColor(colors.text_primary))
        painter.drawText(QRectF(0, 0, w, h), Qt.AlignCenter, f"{int(self._value * 100)}% Risk")

        if self._label:
            painter.setFont(self._make_font(10))
            painter.setPen(QColor(colors.text_disabled))
            painter.drawText(QRectF(0, h, w, 20), Qt.AlignCenter, self._label)

        painter.end()
