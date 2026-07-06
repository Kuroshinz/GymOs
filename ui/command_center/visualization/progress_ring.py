from __future__ import annotations

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import QFrame, QWidget

from ui.command_center.theme import C


class ProgressRing(QFrame):
    def __init__(self, size: int = 100, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._value = 0.0
        self._target = 100.0
        self._ring_size = size
        self._label = ""
        self._sub_label = ""
        self.setFixedSize(size, size)

    def set_progress(self, value: float, target: float = 100.0,
                     label: str = "", sub_label: str = "") -> None:
        self._value = value
        self._target = target if target > 0 else 1.0
        self._label = label
        self._sub_label = sub_label
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        center = self._ring_size / 2
        radius = self._ring_size / 2 - 8
        fraction = min(self._value / self._target, 1.0)

        bg_pen = QPen(QColor(C.BORDER), 6)
        bg_pen.setCapStyle(Qt.RoundCap)
        painter.setPen(bg_pen)
        painter.drawArc(QRectF(center - radius, center - radius, radius * 2, radius * 2),
                        0, 360 * 16)

        arc_color = C.TEXT_SUCCESS if fraction >= 0.8 else C.TEXT_WARN if fraction >= 0.5 else C.TEXT_DANGER
        fg_pen = QPen(QColor(arc_color), 6)
        fg_pen.setCapStyle(Qt.RoundCap)
        painter.setPen(fg_pen)
        span = int(fraction * 360 * 16)
        painter.drawArc(QRectF(center - radius, center - radius, radius * 2, radius * 2),
                        90 * 16, -span if span > 0 else 0)

        pct = int(fraction * 100)
        font = QFont()
        font.setPixelSize(18)
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QColor(C.TEXT_PRIMARY))
        painter.drawText(QRectF(0, center - 20, self._ring_size, 24), Qt.AlignCenter, f"{pct}%")

        if self._label:
            font2 = QFont()
            font2.setPixelSize(9)
            painter.setFont(font2)
            painter.setPen(QColor(C.TEXT_MUTED))
            painter.drawText(QRectF(0, center + 6, self._ring_size, 16), Qt.AlignCenter, self._label)

        painter.end()
