from __future__ import annotations

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QFont, QPainter
from PySide6.QtWidgets import QFrame, QWidget

from ui.design_system.tokens.color import ColorScheme, color_from_scheme
from ui.design_system.tokens.radius import RadiusTokens, radius_to_px

R = RadiusTokens()


class ConfidenceGauge(QFrame):
    def __init__(
        self,
        width: int = 200,
        height: int = 40,
        color_scheme: ColorScheme = ColorScheme.DARK,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._color_scheme = color_scheme
        self._value = 0.0
        self._label = ""
        self._gauge_width = width
        self._gauge_height = height
        self.setFixedSize(width, height + 20)

    def _colors(self):
        return color_from_scheme(self._color_scheme)

    def set_confidence(self, value: float, label: str = "") -> None:
        self._value = max(0.0, min(1.0, value))
        self._label = label
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        colors = self._colors()
        bar_h = self._gauge_height
        bar_w = self._gauge_width
        y = 0
        r = radius_to_px(R.full)

        bg_rect = QRectF(0, y, bar_w, bar_h)
        painter.setBrush(QColor(colors.scrollbar_handle))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(bg_rect, r, r)

        fill_w = max(int(bar_w * self._value), 0)
        if fill_w > 0:
            fill_color = colors.success
            if self._value < 0.6:
                fill_color = colors.warning
            if self._value < 0.3:
                fill_color = colors.error
            fill_rect = QRectF(0, y, fill_w, bar_h)
            painter.setBrush(QColor(fill_color))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(fill_rect, r, r)

        pct_text = f"{int(self._value * 100)}%"
        font = QFont()
        font.setPixelSize(12)
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QColor(colors.text_inverse))
        painter.drawText(QRectF(0, y, bar_w, bar_h), Qt.AlignCenter, pct_text)

        if self._label:
            font2 = QFont()
            font2.setPixelSize(10)
            painter.setFont(font2)
            painter.setPen(QColor(colors.text_disabled))
            painter.drawText(QRectF(0, bar_h + 4, bar_w, 16), Qt.AlignCenter, self._label)
