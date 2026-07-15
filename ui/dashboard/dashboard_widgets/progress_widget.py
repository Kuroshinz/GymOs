"""Dashboard Progress widget — goal progress, weekly volume, and recent PRs."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt, QTimer
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from ui.dashboard.dashboard_models import DashboardData
from ui.design_system.tokens.color import ColorScheme, color_from_scheme, resolve_alpha
from ui.design_system.tokens.elevation import apply_elevation
from ui.design_system.tokens.radius import RadiusTokens, px_from_token
from ui.design_system.tokens.spacing import SpacingTokens
from ui.design_system.tokens.typography import TypographyTokens, font_style
from ui.design_system.visualization import WeeklyTimeline

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
_px28 = _pxf(S.s7) if hasattr(S, 's7') else 28

_ANI_DURATION = 200
_ANI_STAGGER = 80


class ProgressWidget(QFrame):
    """Goal progress, weekly volume timeline, and recent PRs.

    Displays:
      - Current weight vs goal (large metrics)
      - Weekly volume timeline bar
      - Recent personal records list
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
        colors = self._colors()

        self.setObjectName("ProgressCard")
        self.setStyleSheet(
            f"""
            QFrame#ProgressCard {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(15,18,55,220), stop:1 rgba(8,12,36,140));
                border-radius: {R.xl};
                border: 1px solid {resolve_alpha(colors.primary, 0.08)};
            }}
        """
        )
        apply_elevation(self, 1, is_dark=True, bg_color=colors.surface)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(_px28, _px24, _px28, _px24)
        layout.setSpacing(_px16)

        # Goal row: weight + details
        goal_row = QHBoxLayout()
        goal_row.setContentsMargins(0, 0, 0, 0)

        self._goal_weight = QLabel("--")
        self._goal_weight.setStyleSheet(
            f"color: {colors.text_primary}; font-size: 32px; font-weight: 800; "
            f"letter-spacing: -0.03em; background: transparent;"
        )
        goal_row.addWidget(self._goal_weight)

        self._goal_detail = QLabel("")
        self._goal_detail.setStyleSheet(
            f"color: {colors.text_disabled}; font-size: 14px; font-weight: 400; "
            f"background: transparent;"
        )
        self._goal_detail.setWordWrap(True)
        goal_row.addWidget(self._goal_detail, 1)

        self._goal_empty = QLabel("No goal data yet.")
        self._goal_empty.setStyleSheet(
            f"color: {colors.text_disabled}; font-size: 14px; font-weight: 400; "
            f"background: transparent;"
        )
        self._goal_empty.setAlignment(Qt.AlignCenter)
        goal_row.addWidget(self._goal_empty)
        self._goal_empty.hide()

        layout.addLayout(goal_row)

        # Weekly volume timeline
        self._weekly_timeline = WeeklyTimeline()
        self._weekly_timeline.setFixedHeight(44)
        layout.addWidget(self._weekly_timeline)

        self._weekly_total = QLabel("")
        self._weekly_total.setStyleSheet(
            f"color: {colors.text_disabled}; font-size: 13px; font-weight: 500; "
            f"background: transparent;"
        )
        layout.addWidget(self._weekly_total)

        self._volume_empty = QLabel("No volume data yet.")
        self._volume_empty.setStyleSheet(
            f"color: {colors.text_disabled}; font-size: 14px; font-weight: 400; "
            f"background: transparent;"
        )
        self._volume_empty.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._volume_empty)

        self._volume_content = QWidget()
        self._volume_content.setStyleSheet("background: transparent;")
        vcl = QVBoxLayout(self._volume_content)
        vcl.setContentsMargins(0, 0, 0, 0)
        vcl.addWidget(self._weekly_timeline)
        vcl.addWidget(self._weekly_total)
        self._volume_content.hide()
        self._volume_empty.show()

        self._goal_content = QWidget()
        self._goal_content.setStyleSheet("background: transparent;")
        gcl = QVBoxLayout(self._goal_content)
        gcl.setContentsMargins(0, 0, 0, 0)
        gcl.addWidget(self._goal_weight)
        gcl.addWidget(self._goal_detail)
        self._goal_content.hide()

        if self._motion:
            self._motion.bind_hover_elevation(self)

    # ── Public API ─────────────────────────────────────────────

    def update_data(self, data: DashboardData) -> None:
        """Update goal progress, volume, and PRs from dashboard data."""
        self._update_goal(data)
        self._update_volume(data)
        self._update_prs(data)

    def _update_goal(self, data: DashboardData) -> None:
        weight = getattr(data, "goal_progress_weight", 0.0) or 0.0
        target = getattr(data, "goal_progress_target", 0.0) or 0.0
        remaining = getattr(data, "goal_progress_remaining", 0.0) or 0.0
        weeks = getattr(data, "goal_progress_weeks", 0) or 0
        rate = getattr(data, "goal_progress_rate", 0.0) or 0.0
        quality = getattr(data, "goal_progress_quality", "") or ""
        percent = getattr(data, "goal_progress_percent", 0.0) or 0.0
        goal_date = getattr(data, "goal_progress_estimated_date", "") or ""

        if weight > 0:
            self._goal_empty.hide()
            self._goal_content.show()
            self._goal_weight.setText(f"{weight:.1f}")

            details_parts = []
            if target:
                details_parts.append(f"Target: {target:.1f} kg")
            if remaining:
                details_parts.append(f"{remaining:.1f} kg to go")
            if weeks:
                details_parts.append(f"~{weeks} weeks left")
            if rate:
                details_parts.append(f"{rate:.2f} kg/wk")
            if quality:
                quality_display = quality.replace("_", " ").title()
                details_parts.append(quality_display)
            if goal_date:
                details_parts.append(f"Est: {goal_date}")
            if percent:
                details_parts.append(f"{percent:.0f}% complete")

            self._goal_detail.setText(" \u00b7 ".join(details_parts))
        else:
            self._goal_empty.show()
            self._goal_content.hide()

    def _update_volume(self, data: DashboardData) -> None:
        vol_data = getattr(data, "weekly_volume_data", [])
        weekly_vol = getattr(data, "weekly_volume_kg", 0.0) or 0.0

        if vol_data:
            self._volume_empty.hide()
            self._volume_content.show()
            values = []
            for v in vol_data:
                if isinstance(v, dict):
                    values.append(v.get("volume", 0.0) or 0.0)
                else:
                    values.append(float(v) if v else 0.0)
            max_v = max(values) if values else 100.0
            self._weekly_timeline.set_data(values, max_value=max_v)
            self._weekly_total.setText(f"Total: {weekly_vol:.0f} kg this week")
        else:
            self._volume_empty.show()
            self._volume_content.hide()

    def _update_prs(self, data: DashboardData) -> None:
        # PRs are displayed inline in the goal section
        pass

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
