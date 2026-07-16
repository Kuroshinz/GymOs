"""Active workout view — premium editor-like layout matching V3 Design language."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt, QTimer, Signal
from PySide6.QtGui import QIntValidator, QKeyEvent
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFrame,
    QGraphicsOpacityEffect,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from modules.workout.application.pr_engine import PREngine
from modules.workout.application.progression_engine import ProgressionEngine
from modules.workout.application.recovery_engine import RecoveryEngine
from modules.workout.domain import SessionExercise, SessionSet, WorkoutSession
from ui.design_system.components.progress_ring import ProgressRing
from ui.design_system.components.section_header import SectionHeader
from ui.design_system.components.status_badge import StatusBadge, StatusLevel
from ui.design_system.tokens.color import ColorScheme, color_from_scheme, resolve_alpha
from ui.design_system.tokens.elevation import apply_elevation, glow_effect
from ui.design_system.tokens.radius import RadiusTokens, px_from_token
from ui.design_system.tokens.spacing import SpacingTokens
from ui.design_system.tokens.typography import TypographyTokens, font_style
from ui.design_system.layout import ScrollContainer

S = SpacingTokens()
R = RadiusTokens()
T = TypographyTokens()

_c = color_from_scheme(ColorScheme.DARK)

_px8 = px_from_token(S.s2)
_px12 = px_from_token(S.s3)
_px16 = px_from_token(S.s4)
_px20 = px_from_token(S.s5)
_px24 = px_from_token(S.s6)
_px32 = px_from_token(S.s8)
_px36 = px_from_token(S.s9)
_px48 = px_from_token(S.s12)
_px64 = px_from_token(S.s16)


class SetRow(QFrame):
    """A single set row with weight, reps, RIR inputs."""

    def __init__(self, set_number: int, prev_weight: float = 0,
                 prev_reps: int = 0, prev_rir: int = 0):
        super().__init__()
        self.set_number = set_number
        self.setStyleSheet("background: transparent; border: none;")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(_px16)

        num_label = QLabel(f"Set {set_number}")
        num_label.setFixedWidth(60)
        self._num_label = num_label
        layout.addWidget(num_label)

        self._weight_input = QLineEdit()
        self._weight_input.setPlaceholderText("kg")
        self._weight_input.setFixedWidth(80)
        self._weight_input.setFixedHeight(_px36)
        self._weight_input.setValidator(QIntValidator(0, 999))
        if prev_weight > 0:
            self._weight_input.setText(str(int(prev_weight)))
        layout.addWidget(self._weight_input)

        self._reps_input = QLineEdit()
        self._reps_input.setPlaceholderText("reps")
        self._reps_input.setFixedWidth(80)
        self._reps_input.setFixedHeight(_px36)
        self._reps_input.setValidator(QIntValidator(0, 100))
        if prev_reps > 0:
            self._reps_input.setText(str(prev_reps))
        layout.addWidget(self._reps_input)

        self._rir_input = QLineEdit()
        self._rir_input.setPlaceholderText("RIR")
        self._rir_input.setFixedWidth(60)
        self._rir_input.setFixedHeight(_px36)
        self._rir_input.setValidator(QIntValidator(0, 5))
        if prev_rir > 0:
            self._rir_input.setText(str(prev_rir))
        layout.addWidget(self._rir_input)

        self._prev_label = None
        if prev_weight > 0 or prev_reps > 0:
            prev_text = f"prev: {int(prev_weight)}\u00d7{prev_reps}"
            if prev_rir:
                prev_text += f" RIR {prev_rir}"
            prev_label = QLabel(prev_text)
            self._prev_label = prev_label
            layout.addWidget(prev_label)

        layout.addStretch()
        self.update_theme_styles(color_from_scheme(ColorScheme.DARK))

    def update_theme_styles(self, colors: Any) -> None:
        self.setStyleSheet(f"""
            SetRow {{
                background-color: rgba(99, 102, 241, 0.04);
                border: 1px solid rgba(99, 102, 241, 0.2);
                border-radius: {R.md};
            }}
        """)
        self._num_label.setStyleSheet(
            f"color: {colors.text_disabled}; {font_style('body_small', 'bold')}; background: transparent; border: none;"
        )
        input_qss = f"""
            QLineEdit {{
                background-color: {colors.background};
                border: 1px solid {colors.border};
                border-radius: {R.md};
                color: {colors.text_primary};
                {font_style('body', 'bold')}
                padding: 4px 12px;
            }}
            QLineEdit:hover {{
                border-color: {colors.border_hover};
            }}
            QLineEdit:focus {{
                border: 2px solid {colors.focus_ring};
                background-color: {colors.surface};
            }}
            QLineEdit:disabled {{
                color: {colors.text_disabled};
                background-color: {colors.background};
                border-color: {colors.border};
            }}
        """
        self._weight_input.setStyleSheet(input_qss)
        self._reps_input.setStyleSheet(input_qss)

        rir_qss = f"""
            QLineEdit {{
                background-color: {colors.background};
                border: 1px solid {colors.border};
                border-radius: {R.md};
                color: {colors.warning};
                {font_style('body', 'bold')}
                padding: 4px 12px;
            }}
            QLineEdit:hover {{
                border-color: {colors.border_hover};
            }}
            QLineEdit:focus {{
                border: 2px solid {colors.focus_ring};
                background-color: {colors.surface};
            }}
            QLineEdit:disabled {{
                color: {colors.text_disabled};
                background-color: {colors.background};
                border-color: {colors.border};
            }}
        """
        self._rir_input.setStyleSheet(rir_qss)

        if self._prev_label:
            self._prev_label.setStyleSheet(
                f"color: {colors.text_disabled}; {font_style('caption')}; background: transparent;"
            )

    def get_data(self) -> SessionSet:
        weight_text = self._weight_input.text().strip()
        reps_text = self._reps_input.text().strip()
        rir_text = self._rir_input.text().strip()
        return SessionSet(
            set_number=self.set_number,
            weight_kg=float(weight_text) if weight_text else 0.0,
            reps=int(reps_text) if reps_text else 0,
            rir=int(rir_text) if rir_text else None,
            completed=True,
        )


class ExerciseCard(QWidget):
    """Exercise data container for workout selection compatibility."""
    def __init__(self, exercise_name: str, target_sets: int,
                 prev_data: list[dict] | None = None, recommendation=None) -> None:
        super().__init__()
        self._exercise_name = exercise_name
        self._target_sets = target_sets
        self._recommendation = recommendation
        self._set_rows: list[SetRow] = []
        for i in range(target_sets):
            prev_w = 0.0
            prev_r = 0
            prev_rir = 0
            if prev_data and i < len(prev_data):
                ps = prev_data[i]
                if isinstance(ps, dict):
                    prev_w = ps.get("weight", 0.0) or ps.get("weight_kg", 0.0) or 0.0
                    prev_r = ps.get("reps", 0) or 0
                    prev_rir = ps.get("rir", 0) or 0
                else:
                    prev_w = getattr(ps, "weight_kg", 0.0) or getattr(ps, "weight", 0.0) or 0.0
                    prev_r = getattr(ps, "reps", 0) or 0
                    prev_rir = getattr(ps, "rir", 0) or 0
            self._set_rows.append(SetRow(i + 1, prev_w, prev_r, prev_rir))

    def get_exercise_data(self) -> dict:
        return {
            "name": self._exercise_name,
            "sets": [row.get_data() for row in self._set_rows],
        }


class WorkoutSummaryDialog(QDialog):
    """Summary dialog shown after completing a workout."""

    def __init__(self, session: WorkoutSession, prs: list = None,
                 recovery=None, recommendations=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Workout Complete")
        self.setMinimumSize(480, 450)
        
        colors = parent._colors() if parent and hasattr(parent, "_colors") else color_from_scheme(ColorScheme.DARK)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {colors.surface};
                color: {colors.text_primary};
                border-radius: {R.xl};
                border: 1px solid {colors.border};
            }}
            QLabel {{ color: {colors.text_primary}; background: transparent; }}
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(_px16)
        layout.setContentsMargins(_px32, _px24, _px32, _px24)

        title = QLabel("Workout Complete")
        title.setStyleSheet(
            f"color: {colors.success}; {font_style('h3')}"
        )
        layout.addWidget(title)

        dur = QLabel(f"Duration: {session.duration_minutes:.0f} min")
        dur.setStyleSheet(f"color: {colors.text_secondary}; {font_style('body_small')}")
        layout.addWidget(dur)

        vol = QLabel(f"Volume: {session.total_volume:.0f} kg")
        vol.setStyleSheet(f"color: {colors.text_secondary}; {font_style('body_small')}")
        layout.addWidget(vol)

        # ─── PRs ─────────────────────────────────
        if prs:
            sep = QLabel("Personal Records")
            sep.setStyleSheet(
                f"color: {colors.warning}; {font_style('body_small', 'bold')}; margin-top: {S.s2}"
            )
            layout.addWidget(sep)

            for pr in prs[:5]:
                pr_label = QLabel(
                    f"\u2728 {pr.exercise_name}: {int(pr.weight_kg)}kg \u00d7 {pr.reps} reps"
                )
                pr_label.setStyleSheet(
                    f"color: {colors.text_primary}; {font_style('caption')}"
                )
                layout.addWidget(pr_label)

        layout.addStretch()

        btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        btn_box.setStyleSheet(f"""
            QPushButton {{
                background-color: {colors.primary};
                color: {colors.text_inverse};
                border: 1px solid transparent;
                border-radius: {R.md};
                padding: 8px 24px;
                {font_style('body_small', 'bold')}
            }}
            QPushButton:hover {{
                background-color: {colors.primary_hover};
            }}
            QPushButton:focus {{
                border: 2px solid {colors.focus_ring};
            }}
        """)
        btn_box.accepted.connect(self.accept)
        layout.addWidget(btn_box)


class WorkoutView(QWidget):
    workout_saved = Signal()
    back_clicked = Signal()

    def __init__(self, db_or_repo: Any, prog_mgr=None, recovery_service=None):
        super().__init__()
        from shared.interfaces import IWorkoutRepository
        from shared.database.repositories import SQLiteWorkoutRepository
        
        if isinstance(db_or_repo, IWorkoutRepository):
            self._repo = db_or_repo
            self._db = getattr(db_or_repo, "_db", db_or_repo)
        else:
            self._repo = SQLiteWorkoutRepository(db_or_repo)
            self._db = db_or_repo
        self._prog_mgr = prog_mgr
        self._recovery_service = recovery_service
        self._current_day_name = ""
        self._current_session: WorkoutSession | None = None
        self._cards: list[ExerciseCard] = []
        self._current_ex_idx = 0
        self._current_set_idx = 0
        self._started_at: datetime | None = None
        
        # Rest timer variables
        self._rest_seconds_left = 90
        self._rest_active = False
        self._rest_overdue = False

        self._build_ui()
        self._connect_timer()

    def _colors(self):
        window = self.window()
        if window and hasattr(window, "_active_scheme"):
            return color_from_scheme(window._active_scheme)
        if window:
            experience = getattr(window, "_experience", None)
            if experience and hasattr(experience, "accessibility"):
                if experience.accessibility.high_contrast:
                    return color_from_scheme(ColorScheme.HIGH_CONTRAST)
        return color_from_scheme(ColorScheme.DARK)

    def _update_theme_styles(self) -> None:
        colors = self._colors()
        window = self.window()
        is_hc = colors.text_primary == "#000000"
        
        # Determine theme scheme
        scheme = ColorScheme.DARK
        if window and hasattr(window, "_active_scheme"):
            scheme = window._active_scheme
        elif is_hc:
            scheme = ColorScheme.HIGH_CONTRAST
        elif colors.background == "#F7F8FA":
            scheme = ColorScheme.LIGHT

        # 1. Header Bar styling
        self._header_bar.setStyleSheet(f"""
            QFrame {{
                background-color: {colors.surface};
                border-bottom: 1px solid {colors.border};
            }}
        """)
        
        self._back_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {colors.text_secondary};
                border: none;
                {font_style('body_small', 'semibold')}
            }}
            QPushButton:hover {{ color: {colors.text_primary}; }}
            QPushButton:focus {{ border: 1px solid {colors.focus_ring}; }}
        """)
        
        self._title_label.setStyleSheet(
            f"color: {colors.text_primary}; {font_style('h3', 'bold')}; background: transparent;"
        )
        
        self._elapsed_label.setStyleSheet(
            f"color: {colors.text_disabled}; {font_style('body_small')}; background: transparent;"
        )
        
        self._progress_ring._color_scheme = scheme
        self._progress_ring.update()

        # Save & Finish button (Standard primary CTA on screen)
        self._finish_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {colors.success};
                color: {colors.text_inverse};
                border: 1px solid transparent;
                border-radius: {R.md};
                padding: 6px 16px;
                {font_style('body_small', 'bold')}
            }}
            QPushButton:hover {{ background-color: {colors.success_hover}; }}
            QPushButton:focus {{ border: 2px solid {colors.focus_ring}; }}
        """)

        # 2. Main split layouts & Cards
        card_bg = colors.surface if is_hc else resolve_alpha(colors.surface, 0.65)
        card_border = colors.border if is_hc else "rgba(255, 255, 255, 0.05)"
        card_style = f"""
            QFrame {{
                background-color: {card_bg};
                border-radius: {R.xl};
                border: 1px solid {card_border};
            }}
        """
        
        self._hero_card.setStyleSheet(card_style)
        self._set_card.setStyleSheet(card_style)
        self._coach_card.setStyleSheet(card_style)
        self._next_card.setStyleSheet(card_style)

        # Hero labels styling
        self._curr_ex_name.setStyleSheet(
            f"color: {colors.text_primary}; {font_style('hero', 'extrabold')}; background: transparent; border: none;"
        )
        self._curr_set_label.setStyleSheet(
            f"color: {colors.text_secondary}; {font_style('h2', 'medium')}; background: transparent; border: none;"
        )

        # Rest timer labels styling
        timer_color = colors.success
        if self._rest_active:
            if self._rest_seconds_left <= 0:
                timer_color = colors.error
            else:
                timer_color = colors.warning
                
        self._rest_timer_val.setStyleSheet(
            f"color: {timer_color}; {font_style('metric', 'bold')}; background: transparent; border: none;"
        )
        self._rest_status_lbl.setStyleSheet(
            f"color: {colors.text_disabled}; {font_style('caption', 'bold')}; background: transparent; border: none;"
        )

        # Complete Set button (Secondary Action, styled nicely)
        self._complete_set_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {colors.primary};
                color: {colors.text_inverse};
                border: 1px solid transparent;
                border-radius: {R.lg};
                {font_style('body', 'bold')}
            }}
            QPushButton:hover {{ background-color: {colors.primary_hover}; }}
            QPushButton:focus {{ border: 2px solid {colors.focus_ring}; }}
        """)

        # Right column card text stylings
        self._coach_title_lbl.setStyleSheet(
            f"color: {colors.text_disabled}; {font_style('overline')}; letter-spacing: 1px; background: transparent; border: none;"
        )
        self._coach_rec.setStyleSheet(
            f"color: {colors.text_primary}; {font_style('body_small', 'medium')}; background: transparent; border: none;"
        )
        self._next_title_lbl.setStyleSheet(
            f"color: {colors.text_disabled}; {font_style('overline')}; letter-spacing: 1px; background: transparent; border: none;"
        )
        self._next_ex_lbl.setStyleSheet(
            f"color: {colors.text_primary}; {font_style('body', 'bold')}; background: transparent; border: none;"
        )

        # 3. Bottom Timeline
        self._timeline_strip.setStyleSheet(f"""
            QFrame {{
                background-color: {colors.background};
                border-top: 1px solid {colors.border};
            }}
        """)

        # Highlight timeline items
        for i in range(len(self._cards)):
            item = self._timeline_layout.itemAt(i)
            if item and item.widget():
                lbl = item.widget()
                if i == self._current_ex_idx:
                    lbl.setStyleSheet(f"color: {colors.primary}; {font_style('caption', 'bold')}; background: transparent;")
                else:
                    lbl.setStyleSheet(f"color: {colors.text_disabled}; {font_style('caption', 'medium')}; background: transparent;")

        # Update set rows theme styles
        for card in self._cards:
            for row in card._set_rows:
                row.update_theme_styles(colors)

    def showEvent(self, event) -> None:  # noqa: N802
        super().showEvent(event)
        self._update_theme_styles()

    def _build_ui(self):
        colors = self._colors()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 1. Header Bar
        self._header_bar = QFrame()
        header_layout = QHBoxLayout(self._header_bar)
        header_layout.setContentsMargins(_px32, _px16, _px32, _px16)
        header_layout.setSpacing(_px12)

        self._back_btn = QPushButton("\u2190 Exit Workout")
        self._back_btn.setCursor(Qt.PointingHandCursor)
        self._back_btn.clicked.connect(self.back_clicked.emit)
        header_layout.addWidget(self._back_btn)

        self._title_label = QLabel("Workout")
        header_layout.addWidget(self._title_label)
        header_layout.addStretch()

        self._elapsed_label = QLabel("00:00")
        header_layout.addWidget(self._elapsed_label)

        self._progress_ring = ProgressRing(size=_px36, stroke_width=3)
        header_layout.addWidget(self._progress_ring)

        self._finish_btn = QPushButton("Save & Finish")
        self._finish_btn.setFixedHeight(_px36)
        self._finish_btn.setCursor(Qt.PointingHandCursor)
        self._finish_btn.clicked.connect(self._finish_workout)
        header_layout.addWidget(self._finish_btn)
        layout.addWidget(self._header_bar)

        # 2. Main Split Area
        split_widget = QWidget()
        split_widget.setStyleSheet("background: transparent;")
        split_layout = QHBoxLayout(split_widget)
        split_layout.setContentsMargins(_px32, _px24, _px32, _px24)
        split_layout.setSpacing(_px24)

        # Left Column (2/3 width)
        left_column = QVBoxLayout()
        left_column.setSpacing(_px24)

        # Top Hero: Current Exercise Details & Timer
        self._hero_card = QFrame()
        hero_inner = QHBoxLayout(self._hero_card)
        hero_inner.setContentsMargins(_px24, _px24, _px24, _px24)
        
        ex_details = QVBoxLayout()
        ex_details.setSpacing(4)
        
        self._curr_ex_name = QLabel("Bench Press")
        self._curr_set_label = QLabel("Set 1 of 3 \u00b7 RIR 2")
        
        ex_details.addWidget(self._curr_ex_name)
        ex_details.addWidget(self._curr_set_label)
        ex_details.addStretch()
        hero_inner.addLayout(ex_details, 2)

        # Centered Rest Timer Widget
        rest_container = QVBoxLayout()
        rest_container.setAlignment(Qt.AlignCenter)
        self._rest_timer_val = QLabel("01:30")
        self._rest_status_lbl = QLabel("Ready")
        self._rest_status_lbl.setAlignment(Qt.AlignCenter)
        
        rest_container.addWidget(self._rest_timer_val)
        rest_container.addWidget(self._rest_status_lbl)
        hero_inner.addLayout(rest_container, 1)
        left_column.addWidget(self._hero_frame_wrapper())

        # Middle: Current Set Card (Large inputs)
        self._set_card = QFrame()
        set_layout = QVBoxLayout(self._set_card)
        set_layout.setContentsMargins(_px24, _px24, _px24, _px24)
        set_layout.setSpacing(_px16)
        
        self._inputs_container = QVBoxLayout()
        set_layout.addLayout(self._inputs_container)

        self._complete_set_btn = QPushButton("Complete Set (Enter)")
        self._complete_set_btn.setFixedHeight(48)
        self._complete_set_btn.setCursor(Qt.PointingHandCursor)
        self._complete_set_btn.clicked.connect(self._complete_current_set)
        set_layout.addWidget(self._complete_set_btn)
        left_column.addWidget(self._set_card)
        split_layout.addLayout(left_column, 2)

        # Right Column (1/3 width)
        right_column = QVBoxLayout()
        right_column.setSpacing(_px24)

        # AI Coach Card
        self._coach_card = QFrame()
        coach_layout = QVBoxLayout(self._coach_card)
        coach_layout.setContentsMargins(_px24, _px20, _px24, _px20)
        coach_layout.setSpacing(_px12)

        self._coach_title_lbl = QLabel("AI COACH")
        self._coach_rec = QLabel("Maintain same load to stabilize technique adaptation.")
        self._coach_rec.setWordWrap(True)
        
        coach_layout.addWidget(self._coach_title_lbl)
        coach_layout.addWidget(self._coach_rec)
        coach_layout.addStretch()
        right_column.addWidget(self._coach_card)

        # Next Exercise Card
        self._next_card = QFrame()
        next_layout = QVBoxLayout(self._next_card)
        next_layout.setContentsMargins(_px24, _px20, _px24, _px20)
        next_layout.setSpacing(_px12)

        self._next_title_lbl = QLabel("UPCOMING EXERCISE")
        self._next_ex_lbl = QLabel("Incline Dumbbell Press")
        
        next_layout.addWidget(self._next_title_lbl)
        next_layout.addWidget(self._next_ex_lbl)
        next_layout.addStretch()
        right_column.addWidget(self._next_card)
        
        split_layout.addLayout(right_column, 1)
        layout.addWidget(split_widget)

        # 3. Bottom Timeline
        self._timeline_strip = QFrame()
        self._timeline_layout = QHBoxLayout(self._timeline_strip)
        self._timeline_layout.setContentsMargins(_px32, _px12, _px32, _px12)
        self._timeline_layout.setSpacing(_px16)
        layout.addWidget(self._timeline_strip)

        # Global key press event filter registration
        self.setFocusPolicy(Qt.StrongFocus)

    def _hero_frame_wrapper(self) -> QFrame:
        return self._hero_card

    def _connect_timer(self):
        self._timer = QTimer()
        self._timer.timeout.connect(self._update_time_and_rest)
        self._timer.start(1000)

    def showEvent(self, event) -> None:
        super().showEvent(event)
        if hasattr(self, "_timer") and not self._timer.isActive():
            self._timer.start(1000)

    def hideEvent(self, event) -> None:
        super().hideEvent(event)
        if hasattr(self, "_timer") and self._timer.isActive():
            self._timer.stop()

    def _update_time_and_rest(self):
        colors = self._colors()
        # Update elapsed workout duration
        if self._started_at:
            elapsed = datetime.now() - self._started_at
            mins = int(elapsed.total_seconds() // 60)
            secs = int(elapsed.total_seconds() % 60)
            self._elapsed_label.setText(f"{mins:02d}:{secs:02d}")

        # Update rest timer
        if self._rest_active:
            if self._rest_seconds_left > 0:
                self._rest_seconds_left -= 1
                rmins = self._rest_seconds_left // 60
                rsecs = self._rest_seconds_left % 60
                self._rest_timer_val.setText(f"{rmins:02d}:{rsecs:02d}")
                self._rest_status_lbl.setText("RESTING")
                self._rest_timer_val.setStyleSheet(f"color: {colors.warning}; {font_style('metric', 'bold')}; background: transparent; border: none;")
            else:
                self._rest_overdue = True
                self._rest_status_lbl.setText("REST OVERDUE!")
                self._rest_timer_val.setStyleSheet(f"color: {colors.error}; {font_style('metric', 'bold')}; background: transparent; border: none;")
        else:
            self._rest_timer_val.setText("01:30")
            self._rest_status_lbl.setText("Ready")
            self._rest_timer_val.setStyleSheet(f"color: {colors.success}; {font_style('metric', 'bold')}; background: transparent; border: none;")

    def _update_progress(self):
        total = 0
        filled = 0
        for card in self._cards:
            for row in card._set_rows:
                total += 1
                if row._weight_input.text().strip() or row._reps_input.text().strip():
                    filled += 1
        if total > 0:
            self._progress_ring.set_progress(filled, total, label=f"{filled}/{total}")

    def load_day(self, day_name: str):
        """Load exercises and construct core widgets."""
        self._current_day_name = day_name
        self._title_label.setText(day_name)
        self._cards.clear()
        self._started_at = datetime.now()
        self._current_ex_idx = 0
        self._current_set_idx = 0
        self._rest_active = False

        program_days = []
        if self._prog_mgr:
            program_days = self._prog_mgr.get_active_program_days()
        if not program_days:
            program_days = self._repo.get_program_days("PPL-UL")
        day_data = None
        for d in program_days:
            if d["name"] == day_name:
                day_data = d
                break

        if not day_data or not day_data.get("exercises"):
            return

        prog_engine = ProgressionEngine(self._db)

        # Clear timeline layouts
        try:
            import shiboken
        except ImportError:
            shiboken = None

        while self._timeline_layout.count():
            item = self._timeline_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                if shiboken is None or shiboken.isValid(w):
                    w.deleteLater()

        for i, ex in enumerate(day_data["exercises"]):
            ex_name = ex["name"]
            target_sets = ex.get("target_sets", 3)
            if self._recovery_service and self._recovery_service.get_active_deload():
                target_sets = max(1, target_sets // 2)
            target_reps = ex.get("target_reps", "8-12")

            prev = self._repo.get_last_session_for_exercise(ex_name)
            prev_sets = prev.sets if prev else None
            rec = prog_engine.get_recommendation(ex_name, target_reps)

            card = ExerciseCard(ex_name, target_sets, prev_sets, rec)
            self._cards.append(card)

            # Render bottom timeline labels
            lbl = QLabel(ex_name)
            self._timeline_layout.addWidget(lbl)

        self._timeline_layout.addStretch()
        self._render_current_exercise()
        self._update_theme_styles()

    def _render_current_exercise(self):
        if not self._cards or self._current_ex_idx >= len(self._cards):
            return

        # Update timeline highlighting
        colors = self._colors()
        for i in range(len(self._cards)):
            item = self._timeline_layout.itemAt(i)
            if item and item.widget():
                lbl = item.widget()
                if i == self._current_ex_idx:
                    lbl.setStyleSheet(f"color: {colors.primary}; {font_style('caption', 'bold')}; background: transparent;")
                else:
                    lbl.setStyleSheet(f"color: {colors.text_disabled}; {font_style('caption', 'medium')}; background: transparent;")

        card = self._cards[self._current_ex_idx]
        self._curr_ex_name.setText(card._exercise_name.upper())
        self._curr_set_label.setText(f"Set {self._current_set_idx + 1} of {card._target_sets} \u00b7 Target RIR 2")

        # Load input row
        while self._inputs_container.count():
            item = self._inputs_container.takeAt(0)
            if item.widget():
                item.widget().setParent(None)

        if self._current_set_idx < len(card._set_rows):
            row = card._set_rows[self._current_set_idx]
            self._inputs_container.addWidget(row)
            row.show()
            # Set focus to first input
            row._weight_input.setFocus()
            row._weight_input.textChanged.connect(self._update_progress)
            row._reps_input.textChanged.connect(self._update_progress)

        # AI Coach recommendation text
        if card._recommendation:
            self._coach_rec.setText(card._recommendation.reason)
        else:
            self._coach_rec.setText("Maintain current resistance load to stabilize technique adaptation.")

        # Next exercise label
        if self._current_ex_idx + 1 < len(self._cards):
            self._next_ex_lbl.setText(self._cards[self._current_ex_idx + 1]._exercise_name)
        else:
            self._next_ex_lbl.setText("None (Final Exercise)")

        self._update_progress()

    def _complete_current_set(self):
        if not self._cards or self._current_ex_idx >= len(self._cards):
            return

        card = self._cards[self._current_ex_idx]
        if self._current_set_idx < len(card._set_rows):
            row = card._set_rows[self._current_set_idx]
            # Verify input values
            if row._weight_input.text().strip() or row._reps_input.text().strip():
                self._current_set_idx += 1
                # Start Rest Timer automatically
                self._rest_seconds_left = 90
                self._rest_active = True
                
                if self._current_set_idx >= len(card._set_rows):
                    # Transition to next exercise
                    self._current_ex_idx += 1
                    self._current_set_idx = 0

                self._render_current_exercise()

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self._complete_current_set()
        elif event.key() == Qt.Key_Space:
            # Toggle Rest Timer
            self._rest_active = not self._rest_active
            self._rest_overdue = False
        elif event.key() == Qt.Key_Escape:
            self.back_clicked.emit()
        elif event.key() == Qt.Key_Left:
            if self._current_set_idx > 0:
                self._current_set_idx -= 1
                self._render_current_exercise()
        elif event.key() == Qt.Key_Right:
            card = self._cards[self._current_ex_idx]
            if self._current_set_idx + 1 < len(card._set_rows):
                self._current_set_idx += 1
                self._render_current_exercise()
        else:
            super().keyPressEvent(event)

    def _finish_workout(self):
        completed_at = datetime.now()
        started_at = self._started_at or completed_at

        exercises = []
        for card in self._cards:
            data = card.get_exercise_data()
            ex = SessionExercise(
                name=data["name"],
                sets=data["sets"],
            )
            exercises.append(ex)

        session = WorkoutSession(
            day_name=self._current_day_name,
            exercises=exercises,
            started_at=started_at,
            completed_at=completed_at,
        )

        saved = self._repo.save_session(session)

        pr_engine = PREngine(self._db)
        prs = pr_engine.detect_prs(saved)

        recovery_engine = RecoveryEngine(self._db)
        recovery = recovery_engine.analyse_session(saved)

        program_days = []
        if self._prog_mgr:
            program_days = self._prog_mgr.get_active_program_days()
        if not program_days:
            program_days = self._repo.get_program_days("PPL-UL")
        target_reps_map: dict[str, str] = {}
        for d in program_days:
            if d["name"] == self._current_day_name:
                for ex in d.get("exercises", []):
                    target_reps_map[ex["name"]] = ex.get("target_reps", "8-12")
                break

        prog_engine = ProgressionEngine(self._db)
        recommendations = []
        for card in self._cards:
            data = card.get_exercise_data()
            ex_sets = data["sets"]
            ex_name = data["name"]
            reps_range = target_reps_map.get(ex_name, "8-12")
            rec = prog_engine.analyse_exercise(ex_name, ex_sets, reps_range)
            recommendations.append(rec)

        self._timer.stop()

        dialog = WorkoutSummaryDialog(saved, prs, recovery, recommendations, self)
        dialog.exec()

        self.workout_saved.emit()
