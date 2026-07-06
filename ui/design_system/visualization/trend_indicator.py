from __future__ import annotations

from PySide6.QtWidgets import QHBoxLayout, QLabel, QWidget

from ui.design_system.tokens.color import ColorScheme, color_from_scheme

TREND_ICONS = {
    "Improving": "\u2191",
    "Slightly improving": "\u2197",
    "Stable": "\u2192",
    "Slightly declining": "\u2198",
    "Declining": "\u2193",
    "Maintaining": "\u2192",
    "up": "\u2191",
    "down": "\u2193",
    "flat": "\u2192",
}




class TrendIndicator(QWidget):
    def __init__(
        self,
        trend: str = "",
        value: str = "",
        color_scheme: ColorScheme = ColorScheme.DARK,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._color_scheme = color_scheme
        self._build_ui(trend, value)

    def _colors(self):
        return color_from_scheme(self._color_scheme)

    def _trend_color(self, trend: str) -> str:
        colors = self._colors()
        trend = trend.lower()
        if trend in ("improving", "up"):
            return colors.success
        if trend in ("slightly improving",):
            return "#A3E635"
        if trend in ("stable", "maintaining", "flat"):
            return colors.text_secondary
        if trend in ("slightly declining",):
            return colors.warning
        if trend in ("declining", "down"):
            return colors.error
        return colors.text_disabled

    def _build_ui(self, trend: str, value: str) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        icon = TREND_ICONS.get(trend, "\u2192")
        color = self._trend_color(trend)

        self._icon = QLabel(icon)
        self._icon.setStyleSheet(f"color: {color}; font-size: 14px; font-weight: 700; background: transparent;")
        layout.addWidget(self._icon)

        self._value = QLabel(value)
        self._value.setStyleSheet(f"color: {color}; font-size: 13px; font-weight: 600; background: transparent;")
        layout.addWidget(self._value)

    def set_trend(self, trend: str, value: str) -> None:
        icon = TREND_ICONS.get(trend, "\u2192")
        color = self._trend_color(trend)
        self._icon.setText(icon)
        self._icon.setStyleSheet(f"color: {color}; font-size: 14px; font-weight: 700; background: transparent;")
        self._value.setText(value)
        self._value.setStyleSheet(f"color: {color}; font-size: 13px; font-weight: 600; background: transparent;")
