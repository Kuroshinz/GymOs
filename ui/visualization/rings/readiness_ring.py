from __future__ import annotations

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget

from ui.visualization.core.base import BaseVisualization


class ReadinessRing(BaseVisualization):
    """Training readiness ring — combines recovery, fatigue, and stress."""

    def __init__(
        self,
        size: int = 130,
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
        self._sub_value = 0.0  # secondary metric (e.g. sleep)
        self.setFixedSize(size + 20, size + 20)

    def set_readiness(self, score: float, sleep_score: float = 0.0, label: str = "") -> None:
        self._max_value = 100.0
        target = max(0.0, min(100.0, score))
        if target != self._value:
            self.animate(target)
        self._sub_value = min(sleep_score, 100.0)
        self._label = label

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        colors = self._colors()

        cx = self._ring_size / 2 + 10
        cy = self._ring_size / 2 + 10
        radius = self._ring_size / 2 - self._stroke
        fraction = self._value / self._max_value

        bg = QPen(QColor(colors.scrollbar_handle), self._stroke)
        bg.setCapStyle(Qt.RoundCap)
        painter.setPen(bg)
        painter.drawArc(QRectF(cx - radius, cy - radius, radius * 2, radius * 2), 0, 360 * 16)

        fg_color = self._value_color(colors, fraction)
        fg = QPen(QColor(fg_color), self._stroke)
        fg.setCapStyle(Qt.RoundCap)
        painter.setPen(fg)
        span = int(min(fraction, 1.0) * 360 * 16)
        painter.drawArc(QRectF(cx - radius, cy - radius, radius * 2, radius * 2), 90 * 16, -span)

        painter.setFont(self._make_font(20, True))
        painter.setPen(QColor(colors.text_primary))
        painter.drawText(QRectF(0, cy - 20, self._ring_size + 20, 26), Qt.AlignCenter, f"{int(fraction * 100)}")

        painter.setFont(self._make_font(10))
        painter.setPen(QColor(colors.text_disabled))
        painter.drawText(QRectF(0, cy + 6, self._ring_size + 20, 16), Qt.AlignCenter, "READY")

        painter.end()
