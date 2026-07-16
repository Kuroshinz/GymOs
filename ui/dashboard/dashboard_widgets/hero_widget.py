"""Dashboard Hero widget — greeting, rings, metrics, CTAs."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QFrame,
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
from ui.design_system.tokens.typography import TypographyTokens

S = SpacingTokens()
R = RadiusTokens()
T = TypographyTokens()

_pxf = px_from_token
_px8 = _pxf(S.s2)
_px12 = _pxf(S.s3)
_px16 = _pxf(S.s4)
_px24 = _pxf(S.s6)
_px32 = _pxf(S.s8)


class HeroWidget(QFrame):
    """Top hero section with greeting, recovery/goal rings, metrics, and CTAs."""

    start_workout_clicked = Signal()
    weekly_review_clicked = Signal()

    def __init__(self, motion: Any = None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._motion = motion
        self._build_ui()

    def set_motion_service(self, motion: Any) -> None:
        self._motion = motion
        if self._motion:
            self._motion.bind_hover_elevation(self)
            self._motion.bind_press_scale(self._start_btn)

    def _colors(self):
        return color_from_scheme(ColorScheme.DARK)

    def _build_ui(self) -> None:
        colors = self._colors()

        self.setObjectName("DashboardHero")
        self.setFixedHeight(230)
        self.setStyleSheet(
            f"""
            QFrame#DashboardHero {{
                background-color: rgba(20, 21, 38, 0.65);
                border-radius: {R.xl};
                border: 1px solid rgba(255, 255, 255, 0.05);
            }}
        """
        )
        apply_elevation(self, 3, is_dark=True, bg_color=colors.surface)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(_px32, _px24, _px32, _px24)
        main_layout.setSpacing(_px24)

        # 1. Left Section (Greeting, Workout, Active Program Meta)
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(_px12)
        left_layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self._greeting = QLabel("GOOD MORNING, NHAN")
        self._greeting.setStyleSheet(
            f"color: {colors.text_disabled}; font-size: 11px; font-weight: 700; "
            f"letter-spacing: 1.5px; background: transparent; text-transform: uppercase;"
        )
        left_layout.addWidget(self._greeting)

        self._workout_name = QLabel("TODAY'S PULL DAY")
        self._workout_name.setStyleSheet(
            f"color: {colors.text_primary}; font-size: 32px; font-weight: 800; "
            f"letter-spacing: -0.04em; background: transparent;"
        )
        left_layout.addWidget(self._workout_name)

        self._muscle_groups = QLabel("Back · Biceps · Rear Delts")
        self._muscle_groups.setStyleSheet(
            f"color: {colors.text_secondary}; font-size: 14px; font-weight: 500; "
            f"background: transparent;"
        )
        left_layout.addWidget(self._muscle_groups)
        main_layout.addLayout(left_layout, 2)

        # 2. Center Section (Primary Start Workout Button)
        center_layout = QHBoxLayout()
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setAlignment(Qt.AlignCenter)

        self._start_btn = QPushButton("Start Workout \u2192")
        self._start_btn.setCursor(Qt.PointingHandCursor)
        self._start_btn.setFixedHeight(50)
        self._start_btn.setMinimumWidth(180)
        self._start_btn.setStyleSheet(
            f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(99,102,241,0.95), stop:0.6 rgba(139,92,246,0.9), stop:1 rgba(167,139,250,0.85));
                color: #FFFFFF;
                border: 1px solid rgba(255,255,255,0.06);
                border-radius: {R.lg};
                padding: 0 28px;
                font-size: 14px; font-weight: 700;
                letter-spacing: 0.01em;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(129,140,248,0.95), stop:0.6 rgba(167,139,250,0.9), stop:1 rgba(196,181,253,0.85));
            }}
            QPushButton:focus {{
                border: 2px solid {colors.focus_ring};
            }}
        """
        )
        self._start_btn.clicked.connect(self.start_workout_clicked.emit)
        self._start_btn.setAccessibleName("Start Workout")
        glow_effect(self._start_btn, glow_rgba=resolve_alpha(colors.primary, 0.35), blur=20, offset_y=0)
        center_layout.addWidget(self._start_btn)
        main_layout.addLayout(center_layout, 1)

        # 3. Right Section (Compact status indicators)
        right_layout = QHBoxLayout()
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(_px32)
        right_layout.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        # Recovery Badge
        self._recovery_badge = QFrame()
        self._recovery_badge.setStyleSheet("background: transparent; border: none;")
        rec_layout = QVBoxLayout(self._recovery_badge)
        rec_layout.setContentsMargins(0, 0, 0, 0)
        rec_layout.setSpacing(4)
        
        self._recovery_val = QLabel("0%")
        self._recovery_val.setAlignment(Qt.AlignCenter)
        self._recovery_val.setStyleSheet(f"color: {colors.text_primary}; font-size: 26px; font-weight: 800; background: transparent;")
        self._recovery_lbl = QLabel("RECOVERY")
        self._recovery_lbl.setAlignment(Qt.AlignCenter)
        self._recovery_lbl.setStyleSheet(f"color: {colors.text_disabled}; font-size: 9px; font-weight: 700; letter-spacing: 0.5px; background: transparent;")
        self._recovery_status = QLabel("Optimal")
        self._recovery_status.setAlignment(Qt.AlignCenter)
        self._recovery_status.setStyleSheet(f"color: {colors.success}; font-size: 11px; font-weight: 600; background: transparent;")
        
        rec_layout.addWidget(self._recovery_val)
        rec_layout.addWidget(self._recovery_lbl)
        rec_layout.addWidget(self._recovery_status)
        right_layout.addWidget(self._recovery_badge)

        # Goal Badge
        self._goal_badge = QFrame()
        self._goal_badge.setStyleSheet("background: transparent; border: none;")
        goal_layout = QVBoxLayout(self._goal_badge)
        goal_layout.setContentsMargins(0, 0, 0, 0)
        goal_layout.setSpacing(4)
        
        self._goal_val = QLabel("--")
        self._goal_val.setAlignment(Qt.AlignCenter)
        self._goal_val.setStyleSheet(f"color: {colors.text_primary}; font-size: 26px; font-weight: 800; background: transparent;")
        self._goal_lbl = QLabel("GOAL PROGRESS")
        self._goal_lbl.setAlignment(Qt.AlignCenter)
        self._goal_lbl.setStyleSheet(f"color: {colors.text_disabled}; font-size: 9px; font-weight: 700; letter-spacing: 0.5px; background: transparent;")
        self._goal_status = QLabel("On Track")
        self._goal_status.setAlignment(Qt.AlignCenter)
        self._goal_status.setStyleSheet(f"color: {colors.primary}; font-size: 11px; font-weight: 600; background: transparent;")
        
        goal_layout.addWidget(self._goal_val)
        goal_layout.addWidget(self._goal_lbl)
        goal_layout.addWidget(self._goal_status)
        right_layout.addWidget(self._goal_badge)

        main_layout.addLayout(right_layout, 1)

    def update_data(self, data: DashboardData) -> None:
        """Update all hero content from dashboard data."""
        colors = self._colors()

        # Update Greeting
        greeting = self._greeting_text()
        user_name = getattr(data, "user_name", "") or "Nhan"
        self._greeting.setText(f"{greeting}, {user_name}")

        # Update Workout Name
        workout_name = getattr(data, "today_workout_name", "") or "Rest Day"
        self._workout_name.setText(workout_name.upper())

        # Update Muscles
        muscles = getattr(data, "today_workout_primary_muscles", [])
        if muscles:
            self._muscle_groups.setText(" · ".join(muscles))
        else:
            self._muscle_groups.setText("Active recovery & stretch suggestions")

        # Update Recovery Badge
        rec_score = getattr(data, "recovery_score", 0.0) or 0.0
        self._recovery_val.setText(f"{int(rec_score)}%")
        rec_level = getattr(data, "recovery_level", "Optimal") or "Optimal"
        self._recovery_status.setText(rec_level)
        if rec_level.lower() in ("low", "poor"):
            self._recovery_status.setStyleSheet(f"color: {colors.error}; font-size: 11px; font-weight: 600; background: transparent;")
        elif rec_level.lower() in ("moderate", "fair"):
            self._recovery_status.setStyleSheet(f"color: {colors.warning}; font-size: 11px; font-weight: 600; background: transparent;")
        else:
            self._recovery_status.setStyleSheet(f"color: {colors.success}; font-size: 11px; font-weight: 600; background: transparent;")

        # Update Goal Badge
        goal_target = getattr(data, "goal_progress_target", 0.0) or 0.0
        goal_current = getattr(data, "goal_progress_weight", 0.0) or 0.0
        if goal_current > 0 and goal_target > 0:
            self._goal_val.setText(f"{goal_current:.0f} / {goal_target:.0f} kg")
        else:
            self._goal_val.setText("--")

        goal_quality = getattr(data, "goal_progress_quality", "On Track") or "On Track"
        self._goal_status.setText(goal_quality)

    @staticmethod
    def _greeting_text() -> str:
        hour = datetime.now().hour
        if hour < 12:
            return "Good Morning"
        if hour < 18:
            return "Good Afternoon"
        return "Good Evening"
