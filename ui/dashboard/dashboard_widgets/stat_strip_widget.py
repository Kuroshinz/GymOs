"""Overview metric strip — five premium stat cards.

Mirrors the top row of the dashboard mockup: Training Load, Calories
Burned, Active Time, Workout Score, Recovery.
"""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from ui.dashboard.dashboard_models import DashboardData
from ui.dashboard.dashboard_widgets.card_kit import make_chip, make_label
from ui.design_system.tokens.color import ColorScheme, color_from_scheme, resolve_alpha

C = color_from_scheme(ColorScheme.DARK)


class StatCard(QFrame):
    """A single overview metric card with icon badge, value and trend."""

    def __init__(
        self,
        *,
        label: str,
        icon: str,
        accent: str,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._accent = accent
        self.setObjectName("StatCard")
        self.setStyleSheet(
            f"""
            QFrame#StatCard {{
                background-color: {C.surface};
                border: 1px solid {C.border};
                border-radius: 18px;
            }}
            QFrame#StatCard:hover {{
                border-color: {resolve_alpha(accent, 0.45)};
            }}
            """
        )
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(28)
        shadow.setXOffset(0)
        shadow.setYOffset(8)
        from PySide6.QtGui import QColor
        shadow.setColor(QColor(0, 0, 0, 110))
        self.setGraphicsEffect(shadow)

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 16, 18, 16)
        root.setSpacing(12)

        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)
        top.addWidget(make_label(label, size=12, weight=600, color=C.text_secondary, uppercase=True, letter_spacing="0.04em"))
        top.addStretch()

        badge = QLabel(icon)
        badge.setFixedSize(44, 44)
        badge.setAlignment(Qt.AlignCenter)
        badge.setStyleSheet(
            f"background: {resolve_alpha(accent, 0.18)}; color: {accent}; "
            f"border-radius: 14px; font-size: 20px;"
        )
        top.addWidget(badge)
        root.addLayout(top)

        value_row = QHBoxLayout()
        value_row.setContentsMargins(0, 0, 0, 0)
        value_row.setSpacing(6)
        self._value = make_label("--", size=30, weight=800, color=C.text_primary, letter_spacing="-0.02em")
        value_row.addWidget(self._value)

        self._unit = make_label("", size=14, weight=600, color=C.text_secondary)
        self._unit.setAlignment(Qt.AlignBottom)
        value_row.addWidget(self._unit)
        value_row.addSpacing(4)

        self._qualifier = make_chip("", accent)
        self._qualifier.hide()
        value_row.addWidget(self._qualifier, 0, Qt.AlignVCenter)
        value_row.addStretch()
        root.addLayout(value_row)

        trend_row = QHBoxLayout()
        trend_row.setContentsMargins(0, 0, 0, 0)
        trend_row.setSpacing(6)
        self._trend = make_label("", size=12, weight=700, color=C.success)
        trend_row.addWidget(self._trend)
        self._trend_label = make_label("", size=12, weight=400, color=C.text_disabled)
        trend_row.addWidget(self._trend_label)
        trend_row.addStretch()
        root.addLayout(trend_row)

    def set_values(
        self,
        value: str,
        *,
        unit: str = "",
        qualifier: str = "",
        trend: str = "",
        trend_label: str = "from yesterday",
    ) -> None:
        self._value.setText(value)
        self._unit.setText(unit)
        if qualifier:
            self._qualifier.setText(qualifier)
            self._qualifier.show()
        else:
            self._qualifier.hide()
        if trend:
            color = C.success
            if trend.startswith("-"):
                color = C.error
            elif trend.startswith("~"):
                color = C.warning
            self._trend.setText(("\u2191 " if not trend.startswith("-") else "\u2193 ") + trend.lstrip("+"))
            self._trend.setStyleSheet(
                f"color: {color}; font-size: 12px; font-weight: 700; background: transparent;"
            )
            self._trend_label.setText(trend_label)
        else:
            self._trend.setText("")
            self._trend_label.setText("")


class StatStripWidget(QWidget):
    """Row of five overview metric cards."""

    def __init__(self, motion: Any = None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._motion = motion
        self.setStyleSheet("background: transparent;")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        self._load = StatCard(label="Training Load", icon="\U0001F4CA", accent=C.primary)
        self._calories = StatCard(label="Calories Burned", icon="\U0001F525", accent="#F97316")
        self._active = StatCard(label="Active Time", icon="\u23F1", accent="#22C55E")
        self._score = StatCard(label="Workout Score", icon="\u2B50", accent="#38BDF8")
        self._recovery = StatCard(label="Recovery", icon="\u2764", accent="#A855F7")

        for card in (self._load, self._calories, self._active, self._score, self._recovery):
            layout.addWidget(card, 1)

    def set_motion_service(self, motion: Any) -> None:
        self._motion = motion

    def update_data(self, data: DashboardData) -> None:
        self._load.set_values(
            f"{data.training_load:,}",
            qualifier=data.training_load_level,
            trend=data.training_load_trend,
        )
        self._calories.set_values(
            f"{data.calories_burned:,}",
            unit="kcal",
            trend=data.calories_trend,
        )
        h, m = divmod(int(data.active_minutes), 60)
        active_text = f"{h}h {m}m" if h else f"{m}m"
        self._active.set_values(active_text, trend=data.active_trend)
        self._score.set_values(
            f"{data.workout_score}",
            qualifier=data.workout_score_label,
            trend=data.workout_score_trend,
            trend_label="from last week",
        )
        self._recovery.set_values(
            f"{data.recovery_percent}%",
            qualifier=data.recovery_qualifier,
            trend=data.recovery_trend,
        )
