"""Dashboard Mission + Recovery widget — today's workout and recovery status."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt, QTimer, Signal
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ui.dashboard.dashboard_models import DashboardData
from ui.design_system.components.empty_state import EmptyState
from ui.design_system.components.status_badge import StatusBadge, StatusLevel
from ui.design_system.layout import EditorialGrid, PanelSpan
from ui.design_system.tokens.color import ColorScheme, color_from_scheme, resolve_alpha
from ui.design_system.tokens.elevation import apply_elevation, glow_effect
from ui.design_system.tokens.motion import MotionTokens
from ui.design_system.tokens.radius import RadiusTokens, px_from_token
from ui.design_system.tokens.spacing import SpacingTokens
from ui.design_system.tokens.typography import TypographyTokens, font_style

S = SpacingTokens()
R = RadiusTokens()
T = TypographyTokens()

_pxf = px_from_token
_px4 = _pxf(S.s1)
_px6 = _pxf(S.s1_5)
_px8 = _pxf(S.s2)
_px12 = _pxf(S.s3)
_px16 = _pxf(S.s4)
_px20 = _pxf(S.s5)
_px24 = _pxf(S.s6)
_px32 = _pxf(S.s8)

_ANI_DURATION = 200
_ANI_STAGGER = 80


class MissionRecoveryWidget(QFrame):
    """Combined mission panel + recovery panel in an editorial grid.

    Shows today's workout (or empty state) and recovery status side by side.
    """

    start_workout_clicked = Signal()
    import_program_clicked = Signal()

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
        self.setStyleSheet("MissionRecoveryWidget { background: transparent; }")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        grid = EditorialGrid()
        grid.set_spacing(_px16)
        layout.addWidget(grid)

        self._build_mission_panel(grid)
        self._build_recovery_panel(grid)

    def _build_mission_panel(self, grid: EditorialGrid) -> None:
        colors = self._colors()

        self._card = QFrame()
        self._card.setObjectName("MissionCard")
        self._card.setStyleSheet(
            f"""
            QFrame#MissionCard {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(12,16,51,220), stop:0.4 rgba(17,13,61,180),
                    stop:0.75 rgba(22,10,56,160), stop:1 rgba(10,14,40,120));
                border-radius: {R.xl};
                border: 1px solid {resolve_alpha(colors.primary, 0.10)};
            }}
        """
        )
        apply_elevation(self._card, 2, is_dark=True, bg_color=colors.surface)

        ml = QVBoxLayout(self._card)
        ml.setContentsMargins(_px24, _px20, _px24, _px20)
        ml.setSpacing(_px12)

        self._workout_name = QLabel("")
        self._workout_name.setStyleSheet(
            f"color: {colors.text_primary}; {font_style('h2')}; "
            f"letter-spacing: -0.02em; background: transparent;"
        )
        self._workout_name.setWordWrap(True)
        ml.addWidget(self._workout_name)

        self._workout_meta = QLabel("")
        self._workout_meta.setStyleSheet(
            f"color: {colors.text_secondary}; {font_style('body')}; background: transparent;"
        )
        self._workout_meta.setWordWrap(True)
        ml.addWidget(self._workout_meta)

        muscle_row = QHBoxLayout()
        muscle_row.setContentsMargins(0, 0, 0, 0)
        muscle_row.setSpacing(_px6)
        self._muscle_container = QWidget()
        self._muscle_container.setLayout(muscle_row)
        self._muscle_container.setStyleSheet("background: transparent;")
        ml.addWidget(self._muscle_container)

        self._start_btn = QPushButton("  \u25B6  Start Workout")
        self._start_btn.setCursor(Qt.PointingHandCursor)
        self._start_btn.setFixedHeight(52)
        self._start_btn.setMinimumWidth(200)
        self._start_btn.setStyleSheet(
            f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(139,92,246,0.9), stop:0.5 rgba(168,85,247,0.85), stop:1 rgba(217,70,239,0.8));
                color: #FFFFFF;
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: {R.size_2xl};
                padding: 0 {S.s7};
                {font_style('body', 'bold')}
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(167,139,250,0.9), stop:0.5 rgba(192,132,252,0.85), stop:1 rgba(232,121,249,0.8));
            }}
            QPushButton:focus {{
                border: 2px solid {colors.focus_ring};
            }}
        """
        )
        self._start_btn.clicked.connect(self.start_workout_clicked.emit)
        self._start_btn.setAccessibleName("Start Workout")
        glow_effect(self._start_btn, glow_rgba=resolve_alpha(colors.primary, 0.35), blur=16, offset_y=0)
        ml.addWidget(self._start_btn)

        self._empty = EmptyState(
            icon="\U0001F3CB",
            title="No Workout Today",
            message="Import a program or start a free workout to get going.",
            action_text="Import Program",
            on_action=self.import_program_clicked.emit,
        )
        ml.addWidget(self._empty)

        self._workout_name.hide()
        self._workout_meta.hide()
        self._muscle_container.hide()
        self._start_btn.hide()

        grid.add_panel(self._card, span=PanelSpan.TWO_THIRDS)

        if self._motion:
            self._motion.bind_hover_elevation(self._card)
            self._motion.bind_press_scale(self._start_btn)

    def _build_recovery_panel(self, grid: EditorialGrid) -> None:
        colors = self._colors()

        self._rec_card = QFrame()
        self._rec_card.setObjectName("RecoveryCard")
        self._rec_card.setStyleSheet(
            f"""
            QFrame#RecoveryCard {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(12,16,51,200), stop:1 rgba(8,12,36,120));
                border-radius: {R.lg};
                border: 1px solid {resolve_alpha(colors.primary, 0.08)};
            }}
        """
        )
        apply_elevation(self._rec_card, 1, is_dark=True, bg_color=colors.surface)

        rl = QVBoxLayout(self._rec_card)
        rl.setContentsMargins(_px20, _px16, _px20, _px16)
        rl.setSpacing(_px8)

        self._rec_narrative = QLabel("--")
        self._rec_narrative.setStyleSheet(
            f"color: {colors.text_primary}; {font_style('h3')}; "
            f"letter-spacing: -0.02em; background: transparent;"
        )
        rl.addWidget(self._rec_narrative)

        self._rec_score_text = QLabel("")
        self._rec_score_text.setStyleSheet(
            f"color: {colors.text_secondary}; {font_style('body')}; background: transparent;"
        )
        rl.addWidget(self._rec_score_text)

        self._rec_suggested = QLabel("")
        self._rec_suggested.setWordWrap(True)
        self._rec_suggested.setStyleSheet(
            f"color: {colors.primary}; {font_style('body')}; "
            f"padding-top: {S.s1}; background: transparent;"
        )
        rl.addWidget(self._rec_suggested)

        self._rec_empty = EmptyState(
            icon="\U0001FA9D",
            title="No Recovery Data",
            message="Complete a workout to unlock recovery insights.",
        )
        rl.addWidget(self._rec_empty)
        self._rec_empty.hide()

        self._rec_content = QWidget()
        self._rec_content.setStyleSheet("background: transparent;")
        rcl = QVBoxLayout(self._rec_content)
        rcl.setContentsMargins(0, 0, 0, 0)
        rcl.addWidget(self._rec_narrative)
        rcl.addWidget(self._rec_score_text)
        rcl.addWidget(self._rec_suggested)

        grid.add_panel(self._rec_card, span=PanelSpan.QUARTER)

        if self._motion:
            self._motion.bind_hover_elevation(self._rec_card)

    # ── Public API ─────────────────────────────────────────────

    def update_data(self, data: DashboardData) -> None:
        """Update mission and recovery panels from dashboard data."""
        self._update_mission(data)
        self._update_recovery(data)

    def _update_mission(self, data: DashboardData) -> None:
        workout_name = getattr(data, "today_workout_name", "") or ""
        if workout_name:
            self._empty.hide()
            self._workout_name.show()
            self._workout_meta.show()
            self._muscle_container.show()
            self._start_btn.show()

            self._workout_name.setText(workout_name)

            ex_count = getattr(data, "today_workout_exercise_count", 0) or 0
            duration = getattr(data, "today_workout_estimated_duration", 0) or 0

            rec_level = getattr(data, "recovery_level", "") or ""
            recovery_hint = ""
            if rec_level:
                rec_display = rec_level.capitalize().replace("_", " ")
                recovery_hint = f" \u00b7 {rec_display}"

            meta = f"{ex_count} exercises"
            if duration:
                meta += f" \u00b7 ~{duration} min"
            meta += recovery_hint
            self._workout_meta.setText(meta)

            for i in reversed(range(self._muscle_container.layout().count())):
                item = self._muscle_container.layout().takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

            muscles = getattr(data, "today_workout_primary_muscles", []) or []
            for m in muscles:
                badge = StatusBadge(
                    text=str(m).capitalize() if isinstance(m, str) else str(m),
                    level=StatusLevel.INFO,
                    outlined=True,
                )
                self._muscle_container.layout().addWidget(badge)

            self._fade_in(self._card, delay=_ANI_STAGGER * 1)
        else:
            self._workout_name.hide()
            self._workout_meta.hide()
            self._muscle_container.hide()
            self._start_btn.hide()
            self._empty.show()

    def _update_recovery(self, data: DashboardData) -> None:
        colors = self._colors()
        rec_score = getattr(data, "recovery_score", 0.0) or 0.0
        level_str = getattr(data, "recovery_level", "") or ""
        suggested = getattr(data, "recovery_suggested_action", "") or ""
        flags = getattr(data, "recovery_flags", []) or []
        status = getattr(data, "recovery_status", None)

        if status is None and not level_str:
            self._rec_empty.show()
            self._rec_content.hide()
            return

        self._rec_empty.hide()
        self._rec_content.show()

        if status and not level_str:
            level_obj = getattr(status, "level", "low")
            level_str = (
                level_obj.value if hasattr(level_obj, "value") else str(level_obj).lower()
            )

        level_key = level_str.lower() if level_str else "low"

        narrative_label = {
            "low": "Ready for PR \U0001F525",
            "moderate": "Nearly recovered",
            "high": "Take it easy today",
            "very_high": "Rest day recommended",
            "critical": "Prioritize recovery",
        }.get(level_key, level_key.upper().replace("_", " "))

        score_color = colors.success
        if level_key in ("high", "very_high", "critical"):
            score_color = colors.error
        elif level_key in ("moderate", "warning"):
            score_color = colors.warning

        self._rec_narrative.setStyleSheet(
            f"color: {score_color}; {font_style('h3')}; "
            f"letter-spacing: -0.02em; background: transparent;"
        )
        self._rec_narrative.setText(narrative_label)

        score_text = f"Score: {rec_score:.0f}/100"
        if status:
            expl = getattr(status, "explanation", "") or ""
            if expl:
                score_text += f" \u00b7 {expl}"
        self._rec_score_text.setText(score_text)

        if suggested:
            self._rec_suggested.setText(f"\u2192 {suggested}")
        elif level_key in ("high", "very_high"):
            self._rec_suggested.setText("\u2192 Prioritize sleep and nutrition")
        else:
            self._rec_suggested.setText("\u2192 Continue your current training plan")

        self._fade_in(self._rec_card, delay=_ANI_STAGGER * 2)

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
