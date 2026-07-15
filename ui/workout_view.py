"""Active workout view — exercise list, set logging, finish summary."""

from __future__ import annotations

from datetime import datetime

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt, QTimer, Signal
from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFrame,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
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
from ui.design_system.tokens.color import ColorScheme, color_from_scheme
from ui.design_system.tokens.radius import RadiusTokens, px_from_token
from ui.design_system.tokens.spacing import SpacingTokens
from ui.design_system.tokens.typography import TypographyTokens, font_style

S = SpacingTokens()
R = RadiusTokens()
T = TypographyTokens()

_c = color_from_scheme(ColorScheme.DARK)

_px4 = px_from_token(S.s1)
_px6 = px_from_token(S.s1_5)
_px8 = px_from_token(S.s2)
_px12 = px_from_token(S.s3)
_px16 = px_from_token(S.s4)
_px20 = px_from_token(S.s5)
_px24 = px_from_token(S.s6)
_px28 = px_from_token(S.s7)
_px32 = px_from_token(S.s8)
_px36 = px_from_token(S.s9)
_px40 = px_from_token(S.s10)
_px48 = px_from_token(S.s12)
_px52 = px_from_token(S.step(13))
_px64 = px_from_token(S.s16)

_ANI_DURATION = 250


class SetRow(QFrame):
    """A single set row with weight, reps, RIR inputs."""

    def __init__(self, set_number: int, prev_weight: float = 0,
                 prev_reps: int = 0, prev_rir: int = 0):
        super().__init__()
        self.set_number = set_number
        self.setStyleSheet(f"""
            SetRow {{
                background-color: transparent;
                border-bottom: 1px solid {_c.border};
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(_px8)

        num_label = QLabel(f"#{set_number}")
        num_label.setFixedWidth(_px28)
        num_label.setStyleSheet(
            f"color: {_c.text_disabled}; {font_style('caption', 'bold')}"
        )
        layout.addWidget(num_label)

        self._weight_input = QLineEdit()
        self._weight_input.setAccessibleName(f"Set {set_number} weight in kg")
        self._weight_input.setToolTip("Enter weight in kilograms")
        self._weight_input.setPlaceholderText("kg")
        self._weight_input.setFixedWidth(_px64)
        self._weight_input.setFixedHeight(_px36)
        self._weight_input.setValidator(QIntValidator(0, 999))
        self._weight_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {_c.background};
                border: 1px solid {_c.border};
                border-radius: {R.md};
                color: {_c.text_primary};
                {font_style('body', 'bold')}
                padding: {S.s1} {S.s2};
            }}
            QLineEdit:focus {{ border-color: {_c.primary}; }}
        """)
        if prev_weight > 0:
            self._weight_input.setText(str(int(prev_weight)))
        layout.addWidget(self._weight_input)

        x_label = QLabel("×")
        x_label.setAccessibleName("times")
        x_label.setStyleSheet(
            f"color: {_c.text_disabled}; {font_style('body', 'bold')}"
        )
        layout.addWidget(x_label)

        self._reps_input = QLineEdit()
        self._reps_input.setAccessibleName(f"Set {set_number} repetitions")
        self._reps_input.setToolTip("Enter number of repetitions")
        self._reps_input.setPlaceholderText("reps")
        self._reps_input.setFixedWidth(_px52)
        self._reps_input.setFixedHeight(_px36)
        self._reps_input.setValidator(QIntValidator(0, 100))
        self._reps_input.setStyleSheet(self._weight_input.styleSheet())
        if prev_reps > 0:
            self._reps_input.setText(str(prev_reps))
        layout.addWidget(self._reps_input)

        rir_label = QLabel("RIR")
        rir_label.setAccessibleName(f"Set {set_number} RIR label")
        rir_label.setStyleSheet(
            f"color: {_c.text_disabled}; {font_style('caption', 'medium')}"
        )
        layout.addWidget(rir_label)

        self._rir_input = QLineEdit()
        self._rir_input.setAccessibleName(f"Set {set_number} RIR value")
        self._rir_input.setToolTip("Enter reps in reserve (0-5)")
        self._rir_input.setPlaceholderText("-")
        self._rir_input.setFixedWidth(_px36)
        self._rir_input.setFixedHeight(_px36)
        self._rir_input.setValidator(QIntValidator(0, 5))
        self._rir_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {_c.background};
                border: 1px solid {_c.border};
                border-radius: {R.md};
                color: {_c.warning};
                {font_style('body', 'bold')}
                padding: {S.s1} {S.s1_5};
            }}
            QLineEdit:focus {{ border-color: {_c.primary}; }}
        """)
        if prev_rir > 0:
            self._rir_input.setText(str(prev_rir))
        layout.addWidget(self._rir_input)

        if prev_weight > 0 or prev_reps > 0:
            prev_text = f"prev: {int(prev_weight)}\u00d7{prev_reps}"
            if prev_rir:
                prev_text += f" RIR {prev_rir}"
            prev_label = QLabel(prev_text)
            prev_label.setStyleSheet(
                f"color: {_c.text_disabled}; {font_style('caption')}"
            )
            layout.addWidget(prev_label)

        layout.addStretch()

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


class ExerciseCard(QFrame):
    """A card for one exercise with its set rows."""

    def __init__(self, exercise_name: str, target_sets: int,
                 prev_data: list[dict] | None = None,
                 recommendation=None):
        super().__init__()
        self._exercise_name = exercise_name
        self.setStyleSheet(f"""
            ExerciseCard {{
                background-color: {_c.surface};
                border-radius: {R.lg};
                border: 1px solid {_c.border};
            }}
            ExerciseCard:focus-within {{
                border-color: {_c.primary};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(_px16, _px12, _px16, _px12)
        layout.setSpacing(_px8)

        # Exercise name + sets badge
        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(_px8)

        name_label = QLabel(exercise_name)
        name_label.setStyleSheet(
            f"color: {_c.text_primary}; {font_style('h4')}"
        )
        header.addWidget(name_label)

        badge = StatusBadge(
            f"{target_sets} sets",
            level=StatusLevel.INFO,
            outlined=True,
        )
        header.addWidget(badge)
        header.addStretch()
        layout.addLayout(header)

        # Recommendation
        if recommendation:
            rec_label = QLabel(recommendation.reason[:80])
            rec_label.setStyleSheet(f"""
                color: {_c.success if recommendation.should_increase else _c.warning};
                {font_style('caption', 'medium')}
            """)
            rec_label.setWordWrap(True)
            layout.addWidget(rec_label)

        # Set rows
        self._set_rows: list[SetRow] = []
        for i in range(target_sets):
            prev_w = 0.0
            prev_r = 0
            prev_rir = 0
            if prev_data and i < len(prev_data):
                ps = prev_data[i]
                prev_w = ps.get("weight", 0) or 0
                prev_r = ps.get("reps", 0) or 0
                prev_rir = ps.get("rir", 0) or 0
            row = SetRow(i + 1, prev_w, prev_r, prev_rir)
            self._set_rows.append(row)
            layout.addWidget(row)

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
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {_c.surface};
                color: {_c.text_primary};
            }}
            QLabel {{ color: {_c.text_primary}; }}
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(_px16)
        layout.setContentsMargins(_px24, _px20, _px24, _px20)

        title = QLabel("Workout Complete")
        title.setStyleSheet(
            f"color: {_c.success}; {font_style('h3')}"
        )
        layout.addWidget(title)

        dur = QLabel(f"Duration: {session.duration_minutes:.0f} min")
        dur.setStyleSheet(f"color: {_c.text_secondary}; {font_style('body_small')}")
        layout.addWidget(dur)

        vol = QLabel(f"Volume: {session.total_volume:.0f} kg")
        vol.setStyleSheet(f"color: {_c.text_secondary}; {font_style('body_small')}")
        layout.addWidget(vol)

        # ─── PRs ─────────────────────────────────
        if prs:
            sep = QLabel("Personal Records")
            sep.setStyleSheet(
                f"color: {_c.warning}; {font_style('body_small', 'bold')}; margin-top: {S.s2}"
            )
            layout.addWidget(sep)

            for pr in prs[:5]:
                pr_text = f"{pr.label}: {pr.exercise_name} \u2014 {pr.display_value}"
                if pr.improvement_text:
                    pr_text += f" ({pr.improvement_text})"
                pr_label = QLabel(pr_text)
                pr_label.setStyleSheet(
                    f"color: {_c.warning}; {font_style('caption', 'bold')}"
                )
                layout.addWidget(pr_label)

        # ─── Recommendations ─────────────────────
        if recommendations:
            sep2 = QLabel("Next Session")
            sep2.setStyleSheet(
                f"color: {_c.primary}; {font_style('body_small', 'bold')}; margin-top: {S.s2}"
            )
            layout.addWidget(sep2)

            for rec in recommendations[:3]:
                if rec.should_increase:
                    text = f"\u2b06 {rec.exercise_name}: {rec.suggested_weight:.0f} kg ({rec.target_reps})"
                    color = _c.success
                else:
                    text = f"\u27a1 {rec.exercise_name}: keep {rec.current_weight:.0f} kg"
                    color = _c.warning
                rec_label = QLabel(text)
                rec_label.setStyleSheet(f"color: {color}; {font_style('caption')}")
                layout.addWidget(rec_label)

        # ─── Recovery Flags ──────────────────────
        if recovery and recovery.flags:
            sep3 = QLabel("Recovery")
            sep3.setStyleSheet(
                f"color: {_c.error}; {font_style('body_small', 'bold')}; margin-top: {S.s2}"
            )
            layout.addWidget(sep3)

            sev_colors = {
                "critical": _c.error,
                "warning": _c.warning,
                "info": _c.info,
            }
            for flag in recovery.flags[:2]:
                fc = sev_colors.get(flag.severity, _c.text_secondary)
                f_label = QLabel(flag.message)
                f_label.setStyleSheet(
                    f"color: {fc}; {font_style('caption')}"
                )
                f_label.setWordWrap(True)
                layout.addWidget(f_label)

            if recovery.should_deload:
                dl = QLabel("Consider scheduling a deload week")
                dl.setStyleSheet(
                    f"color: {_c.error}; {font_style('caption', 'bold')}"
                )
                layout.addWidget(dl)

        layout.addStretch()

        btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        btn_box.setStyleSheet(f"""
            QPushButton {{
                background-color: {_c.primary};
                color: {_c.text_inverse};
                border: none;
                border-radius: {R.md};
                padding: {S.s2_5} {S.s6};
                {font_style('body_small', 'bold')}
            }}
            QPushButton:hover {{ background-color: {_c.primary_hover}; }}
        """)
        btn_box.accepted.connect(self.accept)
        layout.addWidget(btn_box)


class WorkoutView(QWidget):
    workout_saved = Signal()
    back_clicked = Signal()

    def __init__(self, db, prog_mgr=None):
        super().__init__()
        self._db = db
        self._prog_mgr = prog_mgr
        self._current_day_name = ""
        self._current_session: WorkoutSession | None = None
        self._cards: list[ExerciseCard] = []
        self._started_at: datetime | None = None
        self._card_animations: list[QPropertyAnimation] = []
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Header Bar ────────────────────────────────────────────
        header_bar = QFrame()
        header_bar.setStyleSheet(f"""
            QFrame {{
                background-color: {_c.background};
                border-bottom: 1px solid {_c.border_light};
            }}
        """)
        header = QHBoxLayout(header_bar)
        header.setContentsMargins(_px32, _px16, _px32, _px16)
        header.setSpacing(_px12)

        self._back_btn = QPushButton("\u2190 Back")
        self._back_btn.setCursor(Qt.PointingHandCursor)
        self._back_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {_c.text_secondary};
                border: none;
                {font_style('body_small', 'semibold')}
            }}
            QPushButton:hover {{ color: {_c.text_primary}; }}
        """)
        self._back_btn.clicked.connect(self.back_clicked.emit)
        header.addWidget(self._back_btn)

        self._title_label = QLabel("Workout")
        self._title_label.setStyleSheet(
            f"color: {_c.text_primary}; {font_style('h4')}"
        )
        header.addWidget(self._title_label)

        header.addStretch()

        self._elapsed_label = QLabel("00:00")
        self._elapsed_label.setStyleSheet(
            f"color: {_c.text_disabled}; {font_style('body_small')}"
        )
        header.addWidget(self._elapsed_label)

        self._progress_ring = ProgressRing(size=_px36, stroke_width=3)
        header.addWidget(self._progress_ring)

        finish_btn = QPushButton("Save & Finish")
        finish_btn.setFixedHeight(_px36)
        finish_btn.setCursor(Qt.PointingHandCursor)
        finish_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {_c.success};
                color: {_c.text_inverse};
                border: none;
                border-radius: {R.md};
                padding: {S.s2} {S.s5};
                {font_style('body_small', 'bold')}
            }}
            QPushButton:hover {{ background-color: {_c.success_hover}; }}
        """)
        finish_btn.clicked.connect(self._finish_workout)
        header.addWidget(finish_btn)

        layout.addWidget(header_bar)

        # ── Scroll Area ──────────────────────────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(
            f"QScrollArea {{ border: none; background-color: {_c.background}; }}"
        )

        scroll_widget = QWidget()
        scroll_widget.setStyleSheet(f"background-color: {_c.background};")
        self._scroll_layout = QVBoxLayout(scroll_widget)
        self._scroll_layout.setContentsMargins(_px32, _px24, _px32, _px24)
        self._scroll_layout.setSpacing(_px12)

        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

        # ── Timer ────────────────────────────────────────────────
        self._timer = QTimer()
        self._timer.timeout.connect(self._update_elapsed)

    def _update_elapsed(self):
        if not self._started_at:
            return
        elapsed = datetime.now() - self._started_at
        mins = int(elapsed.total_seconds() // 60)
        secs = int(elapsed.total_seconds() % 60)
        self._elapsed_label.setText(f"{mins:02d}:{secs:02d}")

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

    def _fade_in_widget(self, widget: QWidget, delay: int = 0):
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)
        effect.setOpacity(0.0)
        anim = QPropertyAnimation(effect, b"opacity")
        anim.setDuration(_ANI_DURATION)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        if delay > 0:
            QTimer.singleShot(delay, anim.start)
        else:
            anim.start()
        self._card_animations.append(anim)

    def load_day(self, day_name: str):
        """Load a workout day's exercises into the view."""
        self._current_day_name = day_name
        self._title_label.setText(day_name)
        self._cards.clear()
        self._card_animations.clear()
        self._started_at = datetime.now()
        self._elapsed_label.setText("00:00")
        self._timer.start(10000)

        while self._scroll_layout.count():
            item = self._scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        program_days = []
        if self._prog_mgr:
            program_days = self._prog_mgr.get_active_program_days()
        if not program_days:
            program_days = self._db.get_program_days("PPL-UL")
        day_data = None
        for d in program_days:
            if d["name"] == day_name:
                day_data = d
                break

        if not day_data or not day_data.get("exercises"):
            return

        total_sets = sum(
            ex.get("target_sets", 3) for ex in day_data["exercises"]
        )
        n_ex = len(day_data["exercises"])
        timeline_header = SectionHeader(
            "Exercise Timeline",
            subtitle=f"{n_ex} exercises \u00b7 {total_sets} total sets"
        )
        self._scroll_layout.addWidget(timeline_header)

        prog_engine = ProgressionEngine(self._db)

        for i, ex in enumerate(day_data["exercises"]):
            ex_name = ex["name"]
            target_sets = ex.get("target_sets", 3)
            target_reps = ex.get("target_reps", "8-12")

            prev = self._db.get_last_session_for_exercise(ex_name)
            prev_sets = prev.sets if prev else None

            rec = prog_engine.get_recommendation(ex_name, target_reps)

            card = ExerciseCard(ex_name, target_sets, prev_sets, rec)
            self._cards.append(card)
            self._scroll_layout.addWidget(card)

            self._fade_in_widget(card, delay=i * 60)

        self._scroll_layout.addStretch()
        self._update_progress()

        # Connect input signals for live progress tracking
        for card in self._cards:
            for row in card._set_rows:
                row._weight_input.textChanged.connect(self._update_progress)
                row._reps_input.textChanged.connect(self._update_progress)

    def _finish_workout(self):
        """Save the workout, detect PRs, analyse recovery, show summary."""
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

        saved = self._db.save_session(session)

        pr_engine = PREngine(self._db)
        prs = pr_engine.detect_prs(saved)

        recovery_engine = RecoveryEngine(self._db)
        recovery = recovery_engine.analyse_session(saved)

        program_days = []
        if self._prog_mgr:
            program_days = self._prog_mgr.get_active_program_days()
        if not program_days:
            program_days = self._db.get_program_days("PPL-UL")
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
