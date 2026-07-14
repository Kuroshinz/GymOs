"""ProgressRing — basic Doughnut-shaped ring widget.

DEPRECATED: Superseded by ui/visualization/rings/ProgressRingV2
and other specialized ring components (GoalRing, RecoveryRing).
New code should prefer ui/visualization/rings for richer animation
and reduced-motion support.
"""

from __future__ import annotations

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import QFrame, QWidget

from ui.design_system.tokens.color import ColorScheme, color_from_scheme


class ProgressRing(QFrame):
    def __init__(
        self,
        size: int = 100,
        stroke_width: int = 6,
        color_scheme: ColorScheme = ColorScheme.DARK,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._value = 0.0
        self._target = 100.0
        self._ring_size = size
        self._stroke = stroke_width
        self._label = ""
        self._sub_label = ""
        self._color_scheme = color_scheme
        self.setFixedSize(size, size)

    def _colors(self):
        return color_from_scheme(self._color_scheme)

    def set_progress(
        self,
        value: float,
        target: float = 100.0,
        label: str = "",
        sub_label: str = "",
    ) -> None:
        self._value = value
        self._target = target if target > 0 else 1.0
        self._label = label
        self._sub_label = sub_label
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        colors = self._colors()
        center = self._ring_size / 2
        radius = self._ring_size / 2 - self._stroke
        fraction = min(self._value / self._target, 1.0)

        bg_pen = QPen(QColor(colors.scrollbar_handle), self._stroke)
        bg_pen.setCapStyle(Qt.RoundCap)
        painter.setPen(bg_pen)
        painter.drawArc(
            QRectF(center - radius, center - radius, radius * 2, radius * 2),
            0, 360 * 16,
        )

        arc_color = colors.success if fraction >= 0.8 else colors.warning if fraction >= 0.5 else colors.error
        fg_pen = QPen(QColor(arc_color), self._stroke)
        fg_pen.setCapStyle(Qt.RoundCap)
        painter.setPen(fg_pen)
        span = int(fraction * 360 * 16)
        painter.drawArc(
            QRectF(center - radius, center - radius, radius * 2, radius * 2),
            90 * 16, -span if span > 0 else 0,
        )

        pct = int(fraction * 100)
        font = QFont()
        font.setPixelSize(18)
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QColor(colors.text_primary))
        painter.drawText(QRectF(0, center - 20, self._ring_size, 24), Qt.AlignCenter, f"{pct}%")

        if self._label:
            font2 = QFont()
            font2.setPixelSize(9)
            painter.setFont(font2)
            painter.setPen(QColor(colors.text_disabled))
            painter.drawText(QRectF(0, center + 6, self._ring_size, 16), Qt.AlignCenter, self._label)

        painter.end()
