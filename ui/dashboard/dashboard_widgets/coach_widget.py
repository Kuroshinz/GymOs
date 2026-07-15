"""Dashboard Coach + Predictions widget — personalized guidance and prediction cards."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, QTimer
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsOpacityEffect,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from ui.dashboard.dashboard_models import DashboardData
from ui.design_system.components.empty_state import EmptyState
from ui.design_system.layout import EditorialGrid, PanelSpan
from ui.design_system.tokens.color import ColorScheme, color_from_scheme, resolve_alpha
from ui.design_system.tokens.elevation import apply_elevation, glow_effect
from ui.design_system.tokens.radius import RadiusTokens, px_from_token
from ui.design_system.tokens.spacing import SpacingTokens
from ui.design_system.tokens.typography import TypographyTokens, font_style
from ui.narrative.cards import CoachCardStack
from ui.narrative.engine import Narrative

S = SpacingTokens()
R = RadiusTokens()
T = TypographyTokens()

_pxf = px_from_token
_px4 = _pxf(S.s1)
_px8 = _pxf(S.s2)
_px12 = _pxf(S.s3)
_px16 = _pxf(S.s4)
_px20 = _pxf(S.s5)
_px24 = _pxf(S.s6)
_px28 = _pxf(S.s7) if hasattr(S, 's7') else 28

_ANI_DURATION = 200
_ANI_STAGGER = 80


class CoachPredictionsWidget(QFrame):
    """Combined coach + predictions panels in an editorial grid.

    Shows personalized coaching recommendations and a prediction mini-view.
    """

    def __init__(self, motion: Any = None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._motion = motion
        self._animations: list[QPropertyAnimation] = []
        self._build_ui()

    def set_motion_service(self, motion: Any) -> None:
        self._motion = motion

    def _colors(self):
        return color_from_scheme(ColorScheme.DARK)

    def _build_ui(self) -> None:
        self.setStyleSheet("CoachPredictionsWidget { background: transparent; }")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        grid = EditorialGrid()
        grid.set_spacing(_px16)
        layout.addWidget(grid)

        self._build_coach_panel(grid)
        self._build_predictions_panel(grid)

    def _build_coach_panel(self, grid: EditorialGrid) -> None:
        colors = self._colors()

        self._coach_card = QFrame()
        self._coach_card.setObjectName("CoachCard")
        self._coach_card.setStyleSheet(
            f"""
            QFrame#CoachCard {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(17,15,63,230), stop:0.5 rgba(22,18,76,195),
                    stop:0.8 rgba(25,12,60,175), stop:1 rgba(12,16,51,135));
                border-radius: {R.xl};
                border: 1px solid {resolve_alpha(colors.primary, 0.10)};
            }}
        """
        )
        apply_elevation(self._coach_card, 2, is_dark=True, bg_color=colors.surface)
        glow_effect(self._coach_card, glow_rgba=resolve_alpha(colors.primary, 0.35), blur=20, offset_y=1)

        cl = QVBoxLayout(self._coach_card)
        cl.setContentsMargins(_px24, _px20, _px24, _px20)
        cl.setSpacing(_px12)

        self._coach_stack = CoachCardStack()
        cl.addWidget(self._coach_stack, 1)

        self._coach_empty = EmptyState(
            icon="\U0001F9D1\u200D\U0001F3EB",
            title="Coach Is Ready",
            message="Recommendations will appear after completing workouts.",
        )
        cl.addWidget(self._coach_empty)

        grid.add_panel(self._coach_card, span=PanelSpan.TWO_THIRDS)

        if self._motion:
            self._motion.bind_hover_elevation(self._coach_card)

    def _build_predictions_panel(self, grid: EditorialGrid) -> None:
        colors = self._colors()

        self._pred_card = QFrame()
        self._pred_card.setObjectName("PredictionsCard")
        self._pred_card.setStyleSheet(
            f"""
            QFrame#PredictionsCard {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(15,18,55,220), stop:1 rgba(8,12,36,140));
                border-radius: {R.xl};
                border: 1px solid {resolve_alpha(colors.primary, 0.08)};
            }}
        """
        )
        apply_elevation(self._pred_card, 1, is_dark=True, bg_color=colors.surface)

        pl = QVBoxLayout(self._pred_card)
        pl.setContentsMargins(_px24, _px20, _px24, _px20)
        pl.setSpacing(_px12)

        self._pred_headline = QLabel("")
        self._pred_headline.setStyleSheet(
            f"color: {colors.text_primary}; font-size: 18px; font-weight: 700; "
            f"letter-spacing: -0.02em; background: transparent;"
        )
        self._pred_headline.setWordWrap(True)
        pl.addWidget(self._pred_headline)

        self._pred_detail = QLabel("")
        self._pred_detail.setStyleSheet(
            f"color: {colors.text_secondary}; font-size: 14px; font-weight: 400; "
            f"background: transparent;"
        )
        self._pred_detail.setWordWrap(True)
        pl.addWidget(self._pred_detail)

        self._pred_confidence = QLabel("")
        self._pred_confidence.setStyleSheet(
            f"color: {colors.success}; font-size: 13px; font-weight: 700; "
            f"padding-top: {_px4}; background: transparent;"
        )
        pl.addWidget(self._pred_confidence)

        self._pred_empty = EmptyState(
            icon="\U0001F52E",
            title="No Predictions Yet",
            message="AI predictions will appear after a few workouts.",
        )
        pl.addWidget(self._pred_empty)

        self._pred_container = QWidget()
        self._pred_container.setLayout(pl)
        self._pred_container.setStyleSheet("background: transparent;")
        self._pred_container.hide()

        grid.add_panel(self._pred_card, span=PanelSpan.QUARTER)

        if self._motion:
            self._motion.bind_hover_elevation(self._pred_card)

    # ── Public API ─────────────────────────────────────────────

    def update_data(self, data: DashboardData) -> None:
        """Update coach and predictions panels from dashboard data."""
        self._update_coach(data)
        self._update_predictions(data)

    def _update_coach(self, data: DashboardData) -> None:
        self._coach_stack.clear()

        recs = getattr(data, "recommendations", [])

        if not recs:
            self._coach_empty.show()
            return

        self._coach_empty.hide()

        for rec in recs[:2]:
            title = (
                getattr(rec, "title", "")
                or getattr(rec, "description", "Coach Insight")
            )
            reason = getattr(rec, "reason", "") or ""
            priority = getattr(rec, "priority", 50) or 50

            sev = "info"
            if priority >= 70:
                sev = "warning"
            elif priority >= 50:
                sev = "info"
            else:
                sev = "success"

            n = Narrative(
                title=title,
                summary=reason or title,
                body=reason,
                metadata={"severity": sev},
            )
            self._coach_stack.add_card(n)

        self._fade_in(self._coach_card, delay=_ANI_STAGGER * 3)

    def _update_predictions(self, data: DashboardData) -> None:
        self._colors()

        recs = getattr(data, "recommendations", [])
        level_str = getattr(data, "recovery_level", "") or ""

        headline = ""
        detail = ""
        confidence = ""

        predictions_data = getattr(data, "predictions_data", None)
        if predictions_data:
            vm = getattr(predictions_data, "view_model", None)
            if vm:
                headlines = getattr(vm, "headlines", None) or getattr(vm, "summary", None)
                if headlines:
                    headline = str(headlines)
                    if hasattr(vm, "confidence"):
                        confidence = f"Confidence: {vm.confidence:.0f}%"

        if not headline and recs:
            for rec in recs[:2]:
                title = getattr(rec, "title", "") or ""
                reason = getattr(rec, "reason", "") or ""
                combined = title or reason
                if combined:
                    headline = f"You are on track for {combined}"
                    break

        if not headline:
            if level_str:
                level_lower = level_str.lower()
                if level_lower == "low":
                    headline = "Ready to push intensity today."
                    detail = "Low fatigue suggests optimal training conditions."
                elif level_lower == "moderate":
                    headline = "Maintain current volume."
                    detail = "Moderate fatigue \u2014 stay the course."
                elif level_lower in ("high", "very_high"):
                    headline = "Consider a deload or rest day."
                    detail = "High fatigue detected."
            else:
                headline = "Complete workouts to unlock predictions."
                detail = "AI will analyze your trends after a few sessions."

        self._pred_headline.setText(headline)
        self._pred_detail.setText(detail)
        if confidence:
            self._pred_confidence.setText(confidence)
            self._pred_confidence.show()
        else:
            self._pred_confidence.hide()

        has_content = bool(headline) and "Complete workouts" not in headline
        self._pred_container.setVisible(has_content)
        self._pred_empty.setVisible(not has_content)
        self._fade_in(self._pred_card, delay=_ANI_STAGGER * 5)

    # ── Helpers ────────────────────────────────────────────────

    def _fade_in(self, widget: QWidget, duration: int = _ANI_DURATION, delay: int = 0) -> None:
        if not widget.isVisible():
            return

        def _do_fade() -> None:
            if self._motion:
                self._motion.fade_slide_in(widget, duration=duration)
            else:
                opacity = QGraphicsOpacityEffect(widget)
                widget.setGraphicsEffect(opacity)
                anim = QPropertyAnimation(opacity, b"opacity")
                anim.setDuration(duration)
                anim.setStartValue(0.0)
                anim.setEndValue(1.0)
                anim.setEasingCurve(QEasingCurve.OutCubic)
                anim.start(QPropertyAnimation.DeleteWhenStopped)
                self._animations.append(anim)

        if delay:
            QTimer.singleShot(delay, _do_fade)
        else:
            _do_fade()
