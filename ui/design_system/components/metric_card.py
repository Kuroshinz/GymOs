from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from ui.design_system.tokens.color import ColorScheme, color_from_scheme
from ui.design_system.tokens.radius import RadiusTokens
from ui.design_system.tokens.spacing import SpacingTokens
from ui.design_system.tokens.typography import font_style

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
        subtitle: str = "",
        color: str | None = None,
        accent_color: str | None = None,
    ) -> None:
        super().__init__(parent)
        self._color_scheme = color_scheme
        self._trend_label = None
        
        # Merge color and accent_color parameters
        resolved_accent = accent_color or color
        
        if label:
            self.setAccessibleName(f"Metric: {label}")
        self._build_ui(label, value, unit, icon, trend, trend_label, subtitle, resolved_accent)

    def _colors(self):
        return color_from_scheme(self._color_scheme)

    def _build_ui(self, label: str, value: str, unit: str, icon: str, trend: str, trend_label: str, subtitle: str = "", resolved_accent: str | None = None) -> None:
        colors = self._colors()
        
        # Determine background and border
        border_color = resolved_accent if resolved_accent else colors.border
        bg_color = colors.surface
        if resolved_accent:
            bg_color = f"rgba({QColor(resolved_accent).red()}, {QColor(resolved_accent).green()}, {QColor(resolved_accent).blue()}, 0.08)"

        self.setStyleSheet(f"""
            MetricCard {{
                background-color: {bg_color};
                border-radius: {RADIUS.lg};
                border: 1px solid {border_color};
            }}
            MetricCard:hover {{
                border-color: {colors.border_hover if not resolved_accent else border_color};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(6)

        if label:
            lbl = QLabel(label.upper())
            lbl.setStyleSheet(
                f"color: {colors.text_secondary}; {font_style('caption', 'bold')}; text-transform: uppercase; background: transparent; border: none; letter-spacing: 0.5px;"
            )
            layout.addWidget(lbl)

        value_row = QHBoxLayout()
        value_row.setSpacing(4)
        value_row.setAlignment(Qt.AlignBottom | Qt.AlignLeft)

        # Automatic unit splitting for backward compatibility
        parts = value.split(" ", 1)
        display_val = parts[0] if len(parts) == 2 else value
        display_unit = unit or (parts[1] if len(parts) == 2 else "")

        val_color = resolved_accent or colors.text_primary

        self._value_label = QLabel(display_val)
        self._value_label.setStyleSheet(f"color: {val_color}; {font_style('h1', 'bold')}; background: transparent; border: none;")
        value_row.addWidget(self._value_label)

        if display_unit:
            unit_label = QLabel(display_unit)
            unit_label.setStyleSheet(f"color: {colors.text_secondary}; {font_style('caption', 'medium')}; background: transparent; border: none; padding-bottom: 2px;")
            unit_label.setAlignment(Qt.AlignBottom)
            value_row.addWidget(unit_label)

        value_row.addStretch()
        layout.addLayout(value_row)

        if subtitle:
            sub = QLabel(subtitle)
            sub.setStyleSheet(f"color: {colors.text_disabled}; {font_style('caption')}; background: transparent; border: none;")
            layout.addWidget(sub)

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
                self._trend_label.setStyleSheet(f"color: {trend_color}; {font_style('body', weight='semibold')}; background: transparent;")
                trend_row.addWidget(self._trend_label)

            if trend_label:
                tl = QLabel(trend_label)
                tl.setStyleSheet(f"color: {colors.text_disabled}; {font_style('caption')}; background: transparent;")
                trend_row.addWidget(tl)

            trend_row.addStretch()
            layout.addLayout(trend_row)

    def set_value(self, value: str) -> None:
        if self._value_label:
            self._value_label.setText(value)

    def set_trend(self, trend: str, label: str = "") -> None:
        if trend and self._trend_label:
            colors = self._colors()
            trend_color = colors.success
            if trend.startswith("-"):
                trend_color = colors.error
            elif trend.startswith("~"):
                trend_color = colors.warning
            self._trend_label.setText(trend)
            self._trend_label.setStyleSheet(f"color: {trend_color}; {font_style('body', weight='semibold')}; background: transparent;")
