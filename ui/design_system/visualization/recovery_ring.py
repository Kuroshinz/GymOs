from __future__ import annotations

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import QFrame, QWidget

from ui.design_system.tokens.color import ColorScheme, color_from_scheme
from ui.design_system.tokens.radius import RadiusTokens

R = RadiusTokens()


class RecoveryRing(QFrame):
    def __init__(
        self,
        size: int = 120,
        stroke_width: int = 8,
        color_scheme: ColorScheme = ColorScheme.DARK,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._value = 0.0
        self._max_value = 100.0
        self._ring_size = size
        self._stroke = stroke_width
        self._label = ""
        self._sub_label = ""
        self._color_scheme = color_scheme
        self.setFixedSize(size + 20, size)

    def _colors(self):
        return color_from_scheme(self._color_scheme)

    def set_value(self, value: float, max_value: float = 100.0, label: str = "", sub_label: str = "") -> None:
        self._value = min(value, max_value)
        self._max_value = max(max_value, 1.0)
        self._label = label
        self._sub_label = sub_label
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        colors = self._colors()
        center = self._ring_size / 2 + 10
        radius = self._ring_size / 2 - self._stroke
        fraction = self._value / self._max_value

        bg_pen = QPen(QColor(colors.scrollbar_handle), self._stroke)
        bg_pen.setCapStyle(Qt.RoundCap)
        painter.setPen(bg_pen)
        painter.drawArc(QRectF(center - radius, center - radius, radius * 2, radius * 2), 0, 360 * 16)

        arc_color = colors.success
        if fraction < 0.6:
            arc_color = colors.warning
        if fraction < 0.3:
            arc_color = colors.error

        fg_pen = QPen(QColor(arc_color), self._stroke)
        fg_pen.setCapStyle(Qt.RoundCap)
        painter.setPen(fg_pen)
        span = int(fraction * 360 * 16)
        painter.drawArc(QRectF(center - radius, center - radius, radius * 2, radius * 2), 90 * 16, -span)

        pct = int(fraction * 100)
        font = QFont()
        font.setPixelSize(22)
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QColor(colors.text_primary))
        painter.drawText(QRectF(0, center - 24, self._ring_size + 20, 28), Qt.AlignCenter, f"{pct}")

        font2 = QFont()
        font2.setPixelSize(10)
        painter.setFont(font2)
        painter.setPen(QColor(colors.text_disabled))
        painter.drawText(QRectF(0, center + 4, self._ring_size + 20, 16), Qt.AlignCenter, "%")

        painter.end()
