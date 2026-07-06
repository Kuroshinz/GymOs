from __future__ import annotations

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QFont, QPainter
from PySide6.QtWidgets import QFrame, QWidget

from ui.design_system.tokens.color import ColorScheme, color_from_scheme
from ui.design_system.tokens.radius import RadiusTokens, radius_to_px

R = RadiusTokens()


class RiskMeter(QFrame):
    def __init__(
        self,
        width: int = 160,
        height: int = 28,
        color_scheme: ColorScheme = ColorScheme.DARK,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._color_scheme = color_scheme
        self._value = 0.0
        self._label = ""
        self._meter_width = width
        self._meter_height = height
        self.setFixedSize(width, height + 24)

    def _colors(self):
        return color_from_scheme(self._color_scheme)

    def set_risk(self, value: float, label: str = "") -> None:
        self._value = max(0.0, min(1.0, value))
        self._label = label
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        colors = self._colors()
        w = self._meter_width
        h = self._meter_height
        r = radius_to_px(R.full)
        segment_count = 5
        seg_w = w / segment_count

        for i in range(segment_count):
            x = int(i * seg_w)
            sw = int(seg_w) - 2
            fraction = (i + 1) / segment_count
            color = colors.success
            if fraction >= 0.8:
                color = colors.error
            elif fraction >= 0.5:
                color = colors.warning

            is_active = i < int(self._value * segment_count)
            alpha = "FF" if is_active else "40"
            c = QColor(color + alpha) if len(color) == 7 else QColor(color)
            if not is_active:
                c = QColor(colors.scrollbar_handle)

            painter.setBrush(c)
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(x, 0, sw, h, r, r)

        font = QFont()
        font.setPixelSize(10)
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QColor(colors.text_primary))
        risk_pct = int(self._value * 100)
        painter.drawText(QRectF(0, 0, w, h), Qt.AlignCenter, f"{risk_pct}% Risk")

        if self._label:
            font2 = QFont()
            font2.setPixelSize(10)
            painter.setFont(font2)
            painter.setPen(QColor(colors.text_disabled))
            painter.drawText(QRectF(0, h, w, 20), Qt.AlignCenter, self._label)
