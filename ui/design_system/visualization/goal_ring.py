from __future__ import annotations

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import QFrame, QWidget

from ui.design_system.tokens.color import ColorScheme, color_from_scheme


class GoalRing(QFrame):
    def __init__(
        self,
        size: int = 140,
        stroke_width: int = 10,
        color_scheme: ColorScheme = ColorScheme.DARK,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._current = 0.0
        self._target = 100.0
        self._ring_size = size
        self._stroke = stroke_width
        self._label = ""
        self._unit = ""
        self._color_scheme = color_scheme
        self.setFixedSize(size + 20, size)

    def _colors(self):
        return color_from_scheme(self._color_scheme)

    def set_goal(self, current: float, target: float, label: str = "", unit: str = "") -> None:
        self._current = current
        self._target = max(target, 1.0)
        self._label = label
        self._unit = unit
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        colors = self._colors()
        center = self._ring_size / 2 + 10
        radius = self._ring_size / 2 - self._stroke
        fraction = min(self._current / self._target, 1.0)

        bg_pen = QPen(QColor(colors.scrollbar_handle), self._stroke)
        bg_pen.setCapStyle(Qt.RoundCap)
        painter.setPen(bg_pen)
        painter.drawArc(QRectF(center - radius, center - radius, radius * 2, radius * 2), 0, 360 * 16)

        fg_pen = QPen(QColor(colors.primary), self._stroke)
        fg_pen.setCapStyle(Qt.RoundCap)
        painter.setPen(fg_pen)
        span = int(fraction * 360 * 16)
        painter.drawArc(QRectF(center - radius, center - radius, radius * 2, radius * 2), 90 * 16, -span)

        current_str = f"{self._current:.1f}" if self._current != int(self._current) else str(int(self._current))
        font = QFont()
        font.setPixelSize(20)
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QColor(colors.text_primary))
        painter.drawText(QRectF(0, center - 20, self._ring_size + 20, 26), Qt.AlignCenter, current_str)

        if self._unit:
            font2 = QFont()
            font2.setPixelSize(11)
            painter.setFont(font2)
            painter.setPen(QColor(colors.text_disabled))
            painter.drawText(QRectF(0, center + 6, self._ring_size + 20, 16), Qt.AlignCenter, self._unit)

        painter.end()
