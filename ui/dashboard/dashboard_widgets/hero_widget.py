"""Dashboard Hero widget — greeting, rings, metrics, CTAs."""

from __future__ import annotations

from datetime import datetime
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
from ui.design_system.tokens.color import ColorScheme, color_from_scheme, resolve_alpha
from ui.design_system.tokens.elevation import apply_elevation, glow_effect
from ui.design_system.tokens.radius import RadiusTokens, px_from_token
from ui.design_system.tokens.spacing import SpacingTokens
from ui.design_system.tokens.typography import TypographyTokens, font_style
from ui.design_system.visualization import GoalRing, RecoveryRing

S = SpacingTokens()
R = RadiusTokens()
T = TypographyTokens()

_pxf = px_from_token
_px2 = _pxf(S.half)
_px4 = _pxf(S.s1)
_px6 = _pxf(S.s1_5)
_px8 = _pxf(S.s2)
_px12 = _pxf(S.s3)
_px16 = _pxf(S.s4)
_px20 = _pxf(S.s5)
_px24 = _pxf(S.s6)
_px28 = _pxf(S.s7)
_px32 = _pxf(S.s8)
_px36 = _pxf(S.s9) if hasattr(S, 's9') else 36
_px40 = _pxf(S.s10) if hasattr(S, 's10') else 40
_px48 = _pxf(S.s12) if hasattr(S, 's12') else 48

_ANI_DURATION = 200
_ANI_STAGGER = 80


class HeroWidget(QFrame):
    """Top hero section with greeting, recovery/goal rings, metrics, and CTAs."""

    start_workout_clicked = Signal()
    weekly_review_clicked = Signal()

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
        colors = self._colors()

        self.setObjectName("DashboardHero")
        self.setMinimumHeight(340)
        self.setStyleSheet(
            f"""
            QFrame#DashboardHero {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(15, 18, 55, 230),
                    stop:0.3 rgba(22, 18, 78, 200),
                    stop:0.6 rgba(28, 14, 70, 170),
                    stop:1 rgba(10, 14, 42, 130));
                border-radius: {R.xl};
                border: 1px solid {resolve_alpha(colors.primary, 0.10)};
            }}
        """
        )
        apply_elevation(self, 3, is_dark=True, bg_color=colors.surface)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(_px36, _px32, _px36, _px28)
        outer.setSpacing(0)

        # Top row: greeting + rings
        top_row = QHBoxLayout()
        top_row.setContentsMargins(0, 0, 0, 0)

        left_area = QVBoxLayout()
        left_area.setSpacing(_px8)

        self._greeting = QLabel("Good Morning")
        self._greeting.setStyleSheet(
            f"color: {colors.text_primary}; font-size: 34px; font-weight: 700; "
            f"letter-spacing: -0.04em; background: transparent;"
        )
        left_area.addWidget(self._greeting)

        self._subtitle = QLabel("")
        self._subtitle.setStyleSheet(
            f"color: {colors.text_secondary}; font-size: 15px; font-weight: 400; "
            f"background: transparent;"
        )
        self._subtitle.setWordWrap(True)
        left_area.addWidget(self._subtitle)

        left_area.addStretch()
        top_row.addLayout(left_area, 1)

        rings_area = QHBoxLayout()
        rings_area.setSpacing(_px20)
        rings_area.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self._recovery_ring = RecoveryRing(size=80)
        rings_area.addWidget(self._recovery_ring)

        self._goal_ring = GoalRing(size=80)
        rings_area.addWidget(self._goal_ring)

        top_row.addLayout(rings_area)
        outer.addLayout(top_row)

        outer.addSpacing(_px20)

        self._prediction = QLabel("")
        self._prediction.setStyleSheet(
            f"color: {colors.primary}; font-size: 15px; font-weight: 600; "
            f"font-style: italic; background: transparent; padding: {_px4} 0;"
        )
        self._prediction.setWordWrap(True)
        self._prediction.hide()
        outer.addWidget(self._prediction)

        outer.addSpacing(_px12)

        # Metrics row
        metrics_row = QHBoxLayout()
        metrics_row.setContentsMargins(0, 0, 0, 0)
        metrics_row.setSpacing(_px32)

        metric_defs = [
            ("_metric_ready", "Readiness", "success"),
            ("_metric_weight", "Current", "text_primary"),
            ("_metric_goal", "To Goal", "warning"),
            ("_metric_streak", "Streak", "text_primary"),
        ]

        for attr_prefix, label, color_key in metric_defs:
            block = QFrame()
            block.setStyleSheet("background: transparent; border: none;")
            bl = QVBoxLayout(block)
            bl.setContentsMargins(0, 0, 0, 0)
            bl.setSpacing(_px4)

            val = QLabel("--")
            val.setStyleSheet(
                f"color: {getattr(colors, color_key, colors.text_primary)}; "
                f"font-size: 28px; font-weight: 800; "
                f"letter-spacing: -0.03em; background: transparent;"
            )
            bl.addWidget(val)

            name = QLabel(label)
            name.setStyleSheet(
                f"color: {colors.text_disabled}; font-size: 12px; font-weight: 500; "
                f"letter-spacing: 0.03em; background: transparent;"
            )
            bl.addWidget(name)

            metrics_row.addWidget(block)
            setattr(self, f"{attr_prefix}_val", val)
            setattr(self, f"{attr_prefix}_lbl", name)

        metrics_row.addStretch()
        outer.addLayout(metrics_row)

        outer.addSpacing(_px20)

        # CTA buttons
        cta_row = QHBoxLayout()
        cta_row.setContentsMargins(0, 0, 0, 0)
        cta_row.setSpacing(_px16)

        self._start_btn = QPushButton("  \u25B6  Start Workout")
        self._start_btn.setCursor(Qt.PointingHandCursor)
        self._start_btn.setFixedHeight(54)
        self._start_btn.setMinimumWidth(220)
        self._start_btn.setStyleSheet(
            f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(99,102,241,0.95), stop:0.6 rgba(139,92,246,0.9), stop:1 rgba(167,139,250,0.85));
                color: #FFFFFF;
                border: 1px solid rgba(255,255,255,0.06);
                border-radius: {R.size_2xl};
                padding: 0 36px;
                font-size: 15px; font-weight: 700;
                letter-spacing: 0.01em;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(129,140,248,0.95), stop:0.6 rgba(167,139,250,0.9), stop:1 rgba(196,181,253,0.85));
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(79,70,229,0.95), stop:0.5 rgba(99,102,241,0.9), stop:1 rgba(129,140,248,0.85));
            }}
            QPushButton:focus {{
                border: 2px solid {colors.focus_ring};
            }}
        """
        )
        self._start_btn.clicked.connect(self.start_workout_clicked.emit)
        self._start_btn.setAccessibleName("Start Workout")
        glow_effect(self._start_btn, glow_rgba=resolve_alpha(colors.primary, 0.35), blur=20, offset_y=0)
        cta_row.addWidget(self._start_btn)

        self._review_btn = QPushButton("  \u270F  Review Week")
        self._review_btn.setCursor(Qt.PointingHandCursor)
        self._review_btn.setFixedHeight(54)
        self._review_btn.setMinimumWidth(180)
        self._review_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: transparent;
                color: {colors.text_primary};
                border: 1px solid {resolve_alpha(colors.text_primary, 0.10)};
                border-radius: {R.size_2xl};
                padding: 0 28px;
                font-size: 15px; font-weight: 600;
                letter-spacing: 0.01em;
            }}
            QPushButton:hover {{
                background-color: {resolve_alpha(colors.text_primary, 0.05)};
                border-color: {resolve_alpha(colors.text_primary, 0.20)};
            }}
            QPushButton:focus {{
                border: 2px solid {colors.focus_ring};
            }}
        """
        )
        self._review_btn.clicked.connect(self.weekly_review_clicked.emit)
        self._review_btn.setAccessibleName("Review Week")
        cta_row.addWidget(self._review_btn)

        cta_row.addStretch()
        outer.addLayout(cta_row)

        if self._motion:
            self._motion.bind_hover_elevation(self)
            self._motion.bind_press_scale(self._start_btn)
            self._motion.bind_press_scale(self._review_btn)

    # ── Public API ─────────────────────────────────────────────

    def update_data(self, data: DashboardData) -> None:
        """Update all hero content from dashboard data."""
        self._colors()

        greeting = self._greeting_text()
        user_name = getattr(data, "user_name", "") or ""
        title = f"{greeting}" + (f", {user_name}" if user_name else "")
        self._greeting.setText(title)

        prog = getattr(data, "current_program", "") or "No Active Program"
        week = getattr(data, "mesocycle_week", 0) or 0
        split_day = getattr(data, "current_split_day", "") or ""
        parts = [prog]
        if week:
            parts.append(f"Week {week}")
        if split_day:
            parts.append(split_day)
        self._subtitle.setText(" \u00b7 ".join(parts) if parts else "")

        rec_score = getattr(data, "recovery_score", 0.0) or 0.0
        self._recovery_ring.set_value(rec_score, 100.0, "Recovery")

        goal_target = getattr(data, "goal_progress_target", 100.0) or 100.0
        goal_current = getattr(data, "goal_progress_weight", 0.0) or 0.0
        if goal_current > 0:
            self._goal_ring.set_goal(goal_current, goal_target, "Goal", "kg")
        else:
            self._goal_ring.set_goal(0, 100, "Goal", "")

        # Prediction text from recommendations
        recs = getattr(data, "recommendations", [])
        prediction_text = ""
        if recs:
            first = recs[0]
            title_text = getattr(first, "title", "") or ""
            if title_text:
                prediction_text = f"\u201C{title_text}\u201D"
        if not prediction_text:
            level = getattr(data, "recovery_level", "") or ""
            if level:
                level_lower = level.lower()
                if level_lower in ("low", "moderate"):
                    prediction_text = "\u201CYou're ready to train. Make it count.\u201D"
                else:
                    prediction_text = "\u201CFocus on recovery today. Rest is training too.\u201D"

        if prediction_text:
            self._prediction.setText(prediction_text)
            self._prediction.show()
        else:
            self._prediction.hide()

        rec_pct = int(rec_score)
        self._metric_ready_val.setText(f"{rec_pct}")

        weight = getattr(data, "goal_progress_weight", 0.0) or 0.0
        self._metric_weight_val.setText(f"{weight:.1f}" if weight else "--")

        remaining = getattr(data, "goal_progress_remaining", 0.0) or 0.0
        if remaining:
            self._metric_goal_val.setText(f"{remaining:.1f}")
            self._metric_goal_lbl.setText("To Goal (kg)")
        else:
            self._metric_goal_val.setText("--")
            self._metric_goal_lbl.setText("To Goal")

        streak = getattr(data, "current_streak", 0) or 0
        if streak:
            self._metric_streak_val.setText(f"{streak}")
            self._metric_streak_lbl.setText("Streak (days)")
        else:
            self._metric_streak_val.setText("0")
            self._metric_streak_lbl.setText("Streak")

        self._fade_in(self, delay=_ANI_STAGGER)

    # ── Helpers ────────────────────────────────────────────────

    @staticmethod
    def _greeting_text() -> str:
        hour = datetime.now().hour
        if hour < 12:
            return "Good Morning"
        if hour < 18:
            return "Good Afternoon"
        return "Good Evening"

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
