"""AI Coach Recommendation card — recommendation banner + stat pills."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QWidget

from ui.dashboard.dashboard_models import DashboardData
from ui.dashboard.dashboard_widgets.card_kit import PanelCard, make_label
from ui.dashboard.dashboard_widgets.recovery_status_widget import ghost_button
from ui.design_system.tokens.color import ColorScheme, color_from_scheme, resolve_alpha

C = color_from_scheme(ColorScheme.DARK)


def _pill(caption: str):
    frame = QFrame()
    frame.setStyleSheet(
        f"QFrame {{ background: {resolve_alpha(C.primary, 0.08)}; "
        f"border: 1px solid {C.border}; border-radius: 12px; }}"
    )
    lay = QVBoxLayout(frame)
    lay.setContentsMargins(12, 10, 12, 10)
    lay.setSpacing(3)
    lay.addWidget(make_label(caption, size=11, weight=600, color=C.text_secondary, uppercase=True, letter_spacing="0.03em"))
    value = make_label("--", size=16, weight=800, color=C.text_primary)
    lay.addWidget(value)
    return frame, value


_LEVEL_COLORS = {
    "low": C.success,
    "good": C.success,
    "moderate": C.warning,
    "fair": C.warning,
    "high": C.error,
    "rest": C.error,
}


class AICoachWidget(PanelCard):
    chat_clicked = Signal()

    def __init__(self, motion: Any = None, parent: QWidget | None = None) -> None:
        super().__init__(title="AI Coach Recommendation", badge="PRO", parent=parent)
        self._motion = motion

        self.add_widget(make_label("Based on your data, I recommend:", size=12, weight=400, color=C.text_secondary))

        banner = QFrame()
        banner.setStyleSheet(
            f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {resolve_alpha(C.primary, 0.22)}, stop:1 {resolve_alpha('#38BDF8', 0.12)});
                border: 1px solid {resolve_alpha(C.primary, 0.30)};
                border-radius: 14px;
            }}
            """
        )
        bl = QVBoxLayout(banner)
        bl.setContentsMargins(16, 14, 16, 14)
        bl.setSpacing(6)
        self._title = make_label("", size=14, weight=700, color=C.text_primary)
        self._title.setWordWrap(True)
        self._body = make_label("", size=12, weight=400, color=C.text_secondary)
        self._body.setWordWrap(True)
        bl.addWidget(self._title)
        bl.addWidget(self._body)
        self.add_widget(banner)

        pills = QHBoxLayout()
        pills.setContentsMargins(0, 0, 0, 0)
        pills.setSpacing(10)
        self._recovery_pill, self._recovery_val = _pill("Recovery")
        self._fatigue_pill, self._fatigue_val = _pill("Fatigue")
        self._readiness_pill, self._readiness_val = _pill("Readiness")
        pills.addWidget(self._recovery_pill, 1)
        pills.addWidget(self._fatigue_pill, 1)
        pills.addWidget(self._readiness_pill, 1)
        self.add_layout(pills)

        self._button = ghost_button("\U0001F4AC  Chat with AI Coach")
        self._button.clicked.connect(self.chat_clicked.emit)
        self.add_widget(self._button)

    def set_motion_service(self, motion: Any) -> None:
        self._motion = motion

    def update_data(self, data: DashboardData) -> None:
        self._title.setText("\u2728  " + (data.ai_coach_title or ""))
        self._body.setText(data.ai_coach_body or "")

        self._recovery_val.setText(f"{data.recovery_percent}%")
        self._set_pill(self._fatigue_val, data.ai_coach_fatigue)
        self._set_pill(self._readiness_val, data.ai_coach_readiness)

    @staticmethod
    def _set_pill(label, value: str) -> None:
        color = _LEVEL_COLORS.get(value.lower(), C.text_primary)
        label.setText(value)
        label.setStyleSheet(
            f"color: {color}; font-size: 16px; font-weight: 800; background: transparent;"
        )
