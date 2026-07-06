"""Recovery status card — color-coded fatigue and recovery insights from GymBrain."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from .base_card import DashboardCard

LEVEL_COLORS = {
    "low": "#4ADE80",
    "moderate": "#FBBF24",
    "high": "#F87171",
    "very_high": "#EF4444",
}

LEVEL_ICONS = {
    "low": "🟢",
    "moderate": "🟡",
    "high": "🔴",
    "very_high": "⛔",
}

SEVERITY_ICONS = {
    "info": "ℹ",
    "warning": "⚠",
    "critical": "✦",
}


class RecoveryWidget(DashboardCard):
    """Shows recovery status from GymBrain FatigueAnalyzer.

    Color-coded (green/yellow/red/red-dark):
      - Recovery level
      - Fatigue score
      - Recovery flags with severity
      - Suggested action
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(title="RECOVERY STATUS", parent=parent)

        self._empty_label = QLabel(
            "No recovery data yet. Complete a workout to get recovery insights."
        )
        self._empty_label.setStyleSheet(
            "color: #64748B; font-size: 13px; padding: 16px 0px;"
        )
        self._empty_label.setWordWrap(True)
        self._empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_label.hide()

        self._content_widget = QWidget()
        self._content_layout = QVBoxLayout(self._content_widget)
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(10)

        # Indicator + score row
        indicator_row = QHBoxLayout()
        indicator_row.setContentsMargins(0, 0, 0, 0)
        indicator_row.setSpacing(12)

        self._indicator = QLabel("●")
        self._indicator.setStyleSheet("font-size: 36px; color: #4ADE80;")
        indicator_row.addWidget(self._indicator)

        score_col = QVBoxLayout()
        score_col.setContentsMargins(0, 0, 0, 0)
        score_col.setSpacing(2)

        self._level_label = QLabel()
        self._level_label.setStyleSheet(
            "color: #F1F5F9; font-size: 16px; font-weight: 700;"
        )
        score_col.addWidget(self._level_label)

        self._score_label = QLabel()
        self._score_label.setStyleSheet("color: #94A3B8; font-size: 13px;")
        score_col.addWidget(self._score_label)

        indicator_row.addLayout(score_col, 1)
        self._content_layout.addLayout(indicator_row)

        # Explanation
        self._explanation_label = QLabel()
        self._explanation_label.setStyleSheet("color: #94A3B8; font-size: 12px;")
        self._explanation_label.setWordWrap(True)
        self._content_layout.addWidget(self._explanation_label)

        # Flags section
        self._flags_section = QWidget()
        self._flags_layout = QVBoxLayout(self._flags_section)
        self._flags_layout.setContentsMargins(0, 0, 0, 0)
        self._flags_layout.setSpacing(4)
        self._content_layout.addWidget(self._flags_section)

        # Suggested action
        self._action_label = QLabel()
        self._action_label.setStyleSheet(
            "color: #818CF8; font-size: 12px; font-weight: 600; padding-top: 4px;"
        )
        self._action_label.setWordWrap(True)
        self._content_layout.addWidget(self._action_label)

        self.add_content(self._empty_label)
        self.add_content(self._content_widget)
        self._content_widget.hide()

    def update(self, data: Any) -> None:
        """Update with dashboard data."""
        status = getattr(data, "recovery_status", None)
        level_str = getattr(data, "recovery_level", "") or ""
        score_val = getattr(data, "recovery_score", 0.0) or 0.0
        flags = getattr(data, "recovery_flags", []) or []
        suggested_action = getattr(data, "recovery_suggested_action", "") or ""

        if status is None and not level_str:
            self._content_widget.hide()
            self._empty_label.show()
            return

        self._empty_label.hide()
        self._content_widget.show()

        # Determine level from status object or fallback
        if status and not level_str:
            level_obj = getattr(status, "level", "low")
            if hasattr(level_obj, "value"):
                level_str = level_obj.value
            else:
                level_str = str(level_obj).lower()

        level_key = level_str.lower() if level_str else "low"
        color = LEVEL_COLORS.get(level_key, "#4ADE80")
        icon = LEVEL_ICONS.get(level_key, "🟢")

        self._indicator.setStyleSheet(f"font-size: 36px; color: {color};")

        level_display = level_key.upper().replace("_", " ")
        self._level_label.setText(f"{icon} {level_display}")
        self._score_label.setText(f"Score: {score_val:.0f}/100")

        # Explanation
        explanation = ""
        if status:
            explanation = getattr(status, "explanation", "") or ""
        self._explanation_label.setText(explanation or f"Fatigue level is {level_display}.")

        # Flags
        for i in reversed(range(self._flags_layout.count())):
            w = self._flags_layout.itemAt(i).widget()
            if w is not None:
                w.deleteLater()

        if flags:
            for flag in flags[:5]:
                flag_text = getattr(flag, "message", str(flag))
                severity = getattr(flag, "severity", "info")
                if hasattr(severity, "value"):
                    severity = severity.value
                sev_icon = SEVERITY_ICONS.get(severity, "ℹ")
                fg_color = LEVEL_COLORS.get(severity, "#FBBF24")

                flag_row = QHBoxLayout()
                flag_row.setContentsMargins(4, 2, 4, 2)
                flag_row.setSpacing(6)

                icon_label = QLabel(sev_icon)
                icon_label.setStyleSheet(f"color: {fg_color}; font-size: 12px;")
                icon_label.setFixedWidth(16)
                flag_row.addWidget(icon_label)

                text_label = QLabel(flag_text)
                text_label.setStyleSheet("color: #F1F5F9; font-size: 12px;")
                text_label.setWordWrap(True)
                flag_row.addWidget(text_label, 1)

                flag_widget = QWidget()
                flag_widget.setLayout(flag_row)
                self._flags_layout.addWidget(flag_widget)

        # Suggested action
        if suggested_action:
            self._action_label.setText(f"→ {suggested_action}")
        elif level_key in ("high", "very_high"):
            self._action_label.setText(
                "→ Prioritize sleep, nutrition, and reduce training volume."
            )
        else:
            self._action_label.setText(
                "→ Continue your current training plan."
            )
