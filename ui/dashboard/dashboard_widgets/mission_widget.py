"""Dashboard Mission widget — today's workout target exercises list."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from ui.dashboard.dashboard_models import DashboardData
from ui.design_system.components.empty_state import EmptyState
from ui.design_system.components.status_badge import StatusBadge, StatusLevel
from ui.design_system.tokens.color import ColorScheme, color_from_scheme, resolve_alpha
from ui.design_system.tokens.elevation import apply_elevation
from ui.design_system.tokens.radius import RadiusTokens, px_from_token
from ui.design_system.tokens.spacing import SpacingTokens
from ui.design_system.tokens.typography import TypographyTokens

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


class MissionRecoveryWidget(QFrame):
    """Today's target workout and exercise list card."""

    start_workout_clicked = Signal()
    import_program_clicked = Signal()

    def __init__(
        self,
        prog_mgr: Any = None,
        db: Any = None,
        motion: Any = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._prog_mgr = prog_mgr
        self._db = db
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

        self.setObjectName("MissionCard")
        self.setStyleSheet(
            f"""
            QFrame#MissionCard {{
                background-color: rgba(20, 21, 38, 0.65);
                border-radius: {R.xl};
                border: 1px solid rgba(255, 255, 255, 0.05);
            }}
        """
        )
        apply_elevation(self, 1, is_dark=True, bg_color=colors.surface)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(_px24, _px20, _px24, _px20)
        main_layout.setSpacing(_px12)

        # Header Title
        self._section_title = QLabel("TODAY'S MISSION")
        self._section_title.setStyleSheet(
            f"color: {colors.text_disabled}; font-size: 10px; font-weight: 700; "
            f"letter-spacing: 1px; background: transparent;"
        )
        main_layout.addWidget(self._section_title)

        # Workout Detail Row
        self._workout_name = QLabel("")
        self._workout_name.setStyleSheet(
            f"color: {colors.text_primary}; font-size: 20px; font-weight: 700; "
            f"letter-spacing: -0.02em; background: transparent;"
        )
        main_layout.addWidget(self._workout_name)

        # Muscles Badge Container
        self._muscle_layout = QHBoxLayout()
        self._muscle_layout.setContentsMargins(0, 0, 0, 0)
        self._muscle_layout.setSpacing(_px8)
        self._muscle_widget = QWidget()
        self._muscle_widget.setLayout(self._muscle_layout)
        self._muscle_widget.setStyleSheet("background: transparent;")
        main_layout.addWidget(self._muscle_widget)

        # Separator Line
        self._separator = QFrame()
        self._separator.setFixedHeight(1)
        self._separator.setStyleSheet("background-color: rgba(255, 255, 255, 0.08); border: none;")
        main_layout.addWidget(self._separator)

        # Exercises List Container
        self._exercises_layout = QVBoxLayout()
        self._exercises_layout.setContentsMargins(0, 0, 0, 0)
        self._exercises_layout.setSpacing(_px8)
        self._exercises_widget = QWidget()
        self._exercises_widget.setLayout(self._exercises_layout)
        self._exercises_widget.setStyleSheet("background: transparent;")
        main_layout.addWidget(self._exercises_widget)

        # View Full Plan Text Link
        self._view_plan_btn = QLabel("View Full Plan \u2192")
        self._view_plan_btn.setCursor(Qt.PointingHandCursor)
        self._view_plan_btn.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self._view_plan_btn.setStyleSheet(
            f"color: {colors.primary}; font-size: 12px; font-weight: 600; background: transparent; padding-top: 4px;"
        )
        self._view_plan_btn.mousePressEvent = lambda e: self.start_workout_clicked.emit()
        main_layout.addWidget(self._view_plan_btn)

        # Empty State
        self._empty = EmptyState(
            icon="\U0001F3CB",
            title="No Workout Program",
            message="Please activate a workout program to view targets.",
            action_text="Import Program",
            on_action=self.import_program_clicked.emit,
        )
        main_layout.addWidget(self._empty)

        # Initial hidden state
        self._workout_name.hide()
        self._muscle_widget.hide()
        self._separator.hide()
        self._exercises_widget.hide()
        self._view_plan_btn.hide()
        self._empty.show()

    def update_data(self, data: DashboardData) -> None:
        """Update target exercise list from active program database."""
        colors = self._colors()
        workout_name = getattr(data, "today_workout_name", "") or ""

        if workout_name:
            self._empty.hide()
            self._workout_name.show()
            self._muscle_widget.show()
            self._separator.show()
            self._exercises_widget.show()
            self._view_plan_btn.show()

            self._workout_name.setText(workout_name)

            # Clear muscle badges
            for i in reversed(range(self._muscle_layout.count())):
                item = self._muscle_layout.takeAt(i)
                if item.widget():
                    item.widget().deleteLater()

            # Add primary muscles status badges
            muscles = getattr(data, "today_workout_primary_muscles", []) or []
            for m in muscles:
                badge = StatusBadge(
                    text=str(m).capitalize() if isinstance(m, str) else str(m),
                    level=StatusLevel.INFO,
                    outlined=True,
                )
                self._muscle_layout.addWidget(badge)
            self._muscle_layout.addStretch()

            # Clear exercises list
            for i in reversed(range(self._exercises_layout.count())):
                item = self._exercises_layout.takeAt(i)
                if item.widget():
                    item.widget().deleteLater()

            # Query exercises list dynamically
            exercises = []
            if self._prog_mgr and self._db:
                try:
                    days = self._prog_mgr.get_active_program_days()
                    total = self._db.get_total_workouts()
                    if days:
                        idx = total % len(days) if total > 0 else 0
                        day = days[idx] if idx < len(days) else days[0]
                        exercises = day.get("exercises", [])
                except Exception:
                    pass

            # Render dynamic exercise rows
            if exercises:
                for idx, e in enumerate(exercises[:3]):  # Show up to top 3 exercises
                    row = QFrame()
                    row.setStyleSheet("background: transparent;")
                    row_layout = QHBoxLayout(row)
                    row_layout.setContentsMargins(0, 4, 0, 4)
                    row_layout.setSpacing(_px12)

                    num_lbl = QLabel(f"{idx + 1}")
                    num_lbl.setFixedWidth(20)
                    num_lbl.setStyleSheet(f"color: {colors.text_disabled}; font-size: 12px; font-weight: 600;")
                    
                    ex_name = QLabel(e.get("name", ""))
                    ex_name.setStyleSheet(f"color: {colors.text_primary}; font-size: 13px; font-weight: 500;")
                    
                    sets_reps = QLabel(f"{e.get('target_sets', 3)} sets x {e.get('target_reps', 10)} reps @ RIR {e.get('target_rir', 2)}")
                    sets_reps.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    sets_reps.setStyleSheet(f"color: {colors.text_secondary}; font-size: 12px;")

                    row_layout.addWidget(num_lbl)
                    row_layout.addWidget(ex_name, 1)
                    row_layout.addWidget(sets_reps)
                    self._exercises_layout.addWidget(row)
            else:
                ex_count = getattr(data, "today_workout_exercise_count", 0) or 0
                placeholder = QLabel(f"Contains {ex_count} planned exercises in sequence.")
                placeholder.setStyleSheet(f"color: {colors.text_secondary}; font-size: 13px; font-style: italic;")
                self._exercises_layout.addWidget(placeholder)

        else:
            self._workout_name.hide()
            self._muscle_widget.hide()
            self._separator.hide()
            self._exercises_widget.hide()
            self._view_plan_btn.hide()
            self._empty.show()
