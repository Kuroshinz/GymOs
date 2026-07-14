from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from ui.design_system.tokens.color import ColorScheme, color_from_scheme
from ui.design_system.tokens.radius import RadiusTokens
from ui.design_system.tokens.spacing import SpacingTokens

SPACE = SpacingTokens()
RADIUS = RadiusTokens()


class MetricCard(QFrame):
    def __init__(
        self,
        label: str = "",
        value: str = "",
        unit: str = "",
        icon: str = "",
        trend: str = "",
        trend_label: str = "",
        color_scheme: ColorScheme = ColorScheme.DARK,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._color_scheme = color_scheme
        self._build_ui(label, value, unit, icon, trend, trend_label)

    def _colors(self):
        return color_from_scheme(self._color_scheme)

    def _build_ui(self, label: str, value: str, unit: str, icon: str, trend: str, trend_label: str) -> None:
        colors = self._colors()
        self.setStyleSheet(f"""
            MetricCard {{
                background-color: {colors.surface};
                border-radius: {RADIUS.lg};
                border: 1px solid {colors.border};
            }}
            MetricCard:hover {{
                border-color: {colors.border_hover};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(6)

        if label:
            lbl = QLabel(label.upper())
            lbl.setStyleSheet(
                f"color: {colors.text_secondary}; font-size: 11px; font-weight: 600; "
                f"letter-spacing: 0.5px; text-transform: uppercase;"
            )
            layout.addWidget(lbl)

        value_row = QHBoxLayout()
        value_row.setSpacing(4)

        self._value_label = QLabel(value)
        self._value_label.setStyleSheet(f"color: {colors.text_primary}; font-size: 24px; font-weight: 700; background: transparent;")
        value_row.addWidget(self._value_label)

        if unit:
            unit_label = QLabel(unit)
            unit_label.setStyleSheet(f"color: {colors.text_secondary}; font-size: 14px; font-weight: 500;")
            unit_label.setAlignment(Qt.AlignBottom)
            value_row.addWidget(unit_label)

        value_row.addStretch()
        layout.addLayout(value_row)

        if trend or trend_label:
            trend_row = QHBoxLayout()
            trend_row.setSpacing(4)

            trend_color = colors.success
            if trend.startswith("-"):
                trend_color = colors.error
            elif trend.startswith("~"):
                trend_color = colors.warning

            if trend:
                self._trend_label = QLabel(trend)
                self._trend_label.setStyleSheet(f"color: {trend_color}; font-size: 13px; font-weight: 600; background: transparent;")
                trend_row.addWidget(self._trend_label)

            if trend_label:
                tl = QLabel(trend_label)
                tl.setStyleSheet(f"color: {colors.text_disabled}; font-size: 12px; background: transparent;")
                trend_row.addWidget(tl)

            trend_row.addStretch()
            layout.addLayout(trend_row)

    def set_value(self, value: str) -> None:
        self._value_label.setText(value)

    def set_trend(self, trend: str, label: str = "") -> None:
        if trend:
            self._trend_label.setText(trend)
