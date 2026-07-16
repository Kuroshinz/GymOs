"""Dashboard Coach widget — personalized AI guidance recommendation card."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from ui.dashboard.dashboard_models import DashboardData
from ui.design_system.components.empty_state import EmptyState
from ui.design_system.tokens.color import ColorScheme, color_from_scheme, resolve_alpha
from ui.design_system.tokens.radius import RadiusTokens, px_from_token
from ui.design_system.tokens.spacing import SpacingTokens
from ui.design_system.tokens.typography import TypographyTokens

S = SpacingTokens()
R = RadiusTokens()
T = TypographyTokens()

_pxf = px_from_token
_px8 = _pxf(S.s2)
_px12 = _pxf(S.s3)
_px16 = _pxf(S.s4)
_px20 = _pxf(S.s5)
_px24 = _pxf(S.s6)


class CoachPredictionsWidget(QFrame):
    """Personalized AI Coach recommendations card."""

    why_clicked = Signal()

    def __init__(self, motion: Any = None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._motion = motion
        self._build_ui()

    def set_motion_service(self, motion: Any) -> None:
        self._motion = motion
        if self._motion:
            self._motion.bind_hover_elevation(self)

    def _colors(self):
        return color_from_scheme(ColorScheme.DARK)

    def _build_ui(self) -> None:
        colors = self._colors()

        self.setObjectName("CoachCard")
        self.setStyleSheet(
            f"""
            QFrame#CoachCard {{
                background-color: rgba(20, 21, 38, 0.65);
                border-radius: {R.xl};
                border: 1px solid rgba(255, 255, 255, 0.05);
            }}
        """
        )

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(_px24, _px20, _px24, _px20)
        main_layout.setSpacing(_px12)

        # Header Title
        self._title = QLabel("AI COACH")
        self._title.setStyleSheet(
            f"color: {colors.text_disabled}; font-size: 10px; font-weight: 700; "
            f"letter-spacing: 1px; background: transparent;"
        )
        main_layout.addWidget(self._title)

        # Highlight status
        self._status_label = QLabel("Recovery is optimal.")
        self._status_label.setStyleSheet(
            f"color: {colors.success}; font-size: 16px; font-weight: 700; background: transparent;"
        )
        main_layout.addWidget(self._status_label)

        # Detail Recommendation
        self._recommendation_lbl = QLabel(
            "Increase target set volume or weight to stimulate hypertrophy progression."
        )
        self._recommendation_lbl.setWordWrap(True)
        self._recommendation_lbl.setStyleSheet(
            f"color: {colors.text_primary}; font-size: 14px; font-weight: 500; "
            f"line-height: 1.4; background: transparent;"
        )
        main_layout.addWidget(self._recommendation_lbl)

        # Why Text Link
        self._why_btn = QLabel("Why? \u2192")
        self._why_btn.setCursor(Qt.PointingHandCursor)
        self._why_btn.setStyleSheet(
            f"color: {colors.primary}; font-size: 12px; font-weight: 600; background: transparent; padding-top: 4px;"
        )
        self._why_btn.mousePressEvent = lambda e: self._on_why_clicked()
        main_layout.addWidget(self._why_btn)

        # Empty State
        self._empty = EmptyState(
            icon="\U0001F9D1\u200D\U0001F3EB",
            title="Coach Offline",
            message="Insights will generate once recovery parameters sync.",
        )
        main_layout.addWidget(self._empty)

        # Initial view states
        self._status_label.hide()
        self._recommendation_lbl.hide()
        self._why_btn.hide()
        self._empty.show()

        self._why_reason = ""

    def update_data(self, data: DashboardData) -> None:
        """Update coach recommendations from dashboard data."""
        colors = self._colors()
        recs = getattr(data, "recommendations", [])

        if recs:
            self._empty.hide()
            self._status_label.show()
            self._recommendation_lbl.show()
            self._why_btn.show()

            first_rec = recs[0]
            title = getattr(first_rec, "title", "") or "Coach Insight"
            reason = getattr(first_rec, "reason", "") or "Based on your progressive volume trends."
            priority = getattr(first_rec, "priority", 50) or 50

            self._recommendation_lbl.setText(title)
            self._why_reason = reason

            # Dynamic header based on priority/recovery
            rec_level = getattr(data, "recovery_level", "Optimal") or "Optimal"
            self._status_label.setText(f"Recovery is {rec_level.lower()}.")
            
            if rec_level.lower() in ("low", "poor"):
                self._status_label.setStyleSheet(f"color: {colors.error}; font-size: 16px; font-weight: 700; background: transparent;")
            elif rec_level.lower() in ("moderate", "fair"):
                self._status_label.setStyleSheet(f"color: {colors.warning}; font-size: 16px; font-weight: 700; background: transparent;")
            else:
                self._status_label.setStyleSheet(f"color: {colors.success}; font-size: 16px; font-weight: 700; background: transparent;")
        else:
            self._status_label.hide()
            self._recommendation_lbl.hide()
            self._why_btn.hide()
            self._empty.show()

    def _on_why_clicked(self) -> None:
        """Display dialog with detailed scientific/athletic reasoning."""
        if not self._why_reason:
            return
        msg = QMessageBox(self)
        msg.setWindowTitle("AI Coach Guidance")
        msg.setText(self._why_reason)
        msg.setIcon(QMessageBox.Information)
        msg.setStyleSheet("""
            QMessageBox { background-color: #121324; }
            QLabel { color: #F8FAFC; }
            QPushButton { background-color: #312E81; color: #FFFFFF; border-radius: 6px; padding: 6px 16px; }
        """)
        msg.exec()
        self.why_clicked.emit()
