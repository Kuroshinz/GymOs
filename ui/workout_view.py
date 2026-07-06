"""Active workout view — exercise list, set logging, finish summary."""

from datetime import datetime

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFrame,
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


class SetRow(QFrame):
    """A single set row with weight, reps, RIR inputs."""

    def __init__(self, set_number: int, prev_weight: float = 0, prev_reps: int = 0,
                 prev_rir: int = 0):
        super().__init__()
        self.set_number = set_number
        self.setStyleSheet("""
            SetRow {
                background-color: transparent;
                border-bottom: 1px solid #1E293B;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(8)

        # Set number
        num_label = QLabel(f"#{set_number}")
        num_label.setFixedWidth(28)
        num_label.setStyleSheet("color: #64748B; font-size: 13px; font-weight: 600;")
        layout.addWidget(num_label)

        # Weight input
        self._weight_input = QLineEdit()
        self._weight_input.setPlaceholderText("kg")
        self._weight_input.setFixedWidth(64)
        self._weight_input.setFixedHeight(36)
        self._weight_input.setValidator(QIntValidator(0, 999))
        self._weight_input.setStyleSheet("""
            QLineEdit {
                background-color: #0F172A;
                border: 1px solid #475569;
                border-radius: 6px;
                color: #F1F5F9;
                font-size: 16px;
                font-weight: 700;
                padding: 4px 8px;
            }
            QLineEdit:focus { border: 1px solid #818CF8; }
        """)
        if prev_weight > 0:
            self._weight_input.setText(str(int(prev_weight)))
        layout.addWidget(self._weight_input)

        # × label
        x_label = QLabel("×")
        x_label.setStyleSheet("color: #64748B; font-size: 16px; font-weight: 600;")
        layout.addWidget(x_label)

        # Reps input
        self._reps_input = QLineEdit()
        self._reps_input.setPlaceholderText("reps")
        self._reps_input.setFixedWidth(52)
        self._reps_input.setFixedHeight(36)
        self._reps_input.setValidator(QIntValidator(0, 100))
        self._reps_input.setStyleSheet(self._weight_input.styleSheet())
        if prev_reps > 0:
            self._reps_input.setText(str(prev_reps))
        layout.addWidget(self._reps_input)

        # RIR input
        rir_label = QLabel("RIR")
        rir_label.setStyleSheet("color: #64748B; font-size: 11px; font-weight: 500;")
        layout.addWidget(rir_label)

        self._rir_input = QLineEdit()
        self._rir_input.setPlaceholderText("-")
        self._rir_input.setFixedWidth(36)
        self._rir_input.setFixedHeight(36)
        self._rir_input.setValidator(QIntValidator(0, 5))
        self._rir_input.setStyleSheet("""
            QLineEdit {
                background-color: #0F172A;
                border: 1px solid #475569;
                border-radius: 6px;
                color: #FBBF24;
                font-size: 14px;
                font-weight: 700;
                padding: 4px 6px;
            }
            QLineEdit:focus { border: 1px solid #818CF8; }
        """)
        if prev_rir > 0:
            self._rir_input.setText(str(prev_rir))
        layout.addWidget(self._rir_input)

        # Previous session hint
        if prev_weight > 0 or prev_reps > 0:
            prev_text = f"prev: {int(prev_weight)}×{prev_reps}"
            if prev_rir:
                prev_text += f" RIR{prev_rir}"
            prev_label = QLabel(prev_text)
            prev_label.setStyleSheet("color: #64748B; font-size: 11px;")
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
        self.setStyleSheet("""
            ExerciseCard {
                background-color: #1E293B;
                border-radius: 12px;
                padding: 16px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)

        # Exercise name header
        name_label = QLabel(exercise_name)
        name_label.setStyleSheet("color: #F1F5F9; font-size: 18px; font-weight: 700;")
        layout.addWidget(name_label)

        # Show recommendation if available
        if recommendation:
            rec_color = "#4ADE80" if recommendation.should_increase else "#FBBF24"
            rec_text = recommendation.reason[:80]
            rec_label = QLabel(f"💡 {rec_text}")
            rec_label.setStyleSheet(f"color: {rec_color}; font-size: 11px; padding: 4px 0;")
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
    """Summary dialog shown after completing a workout.
    Displays PRs, recovery flags, and progression recommendations.
    """

    def __init__(self, session: WorkoutSession, prs: list = None,
                 recovery=None, recommendations=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Workout Complete")
        self.setMinimumSize(480, 450)
        self.setStyleSheet("""
            QDialog {
                background-color: #0F172A;
                color: #F1F5F9;
            }
            QLabel { color: #F1F5F9; }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        title = QLabel("✅ Workout Complete!")
        title.setStyleSheet("font-size: 22px; font-weight: 700; color: #4ADE80;")
        layout.addWidget(title)

        info_style = "color: #94A3B8; font-size: 13px;"

        dur = QLabel(f"Duration: {session.duration_minutes:.0f} min")
        dur.setStyleSheet(info_style)
        layout.addWidget(dur)

        vol = QLabel(f"Volume: {session.total_volume:.0f} kg")
        vol.setStyleSheet(info_style)
        layout.addWidget(vol)

        # ─── PRs ─────────────────────────────────
        if prs:
            sep = QLabel("───── PRs ─────")
            sep.setStyleSheet("color: #FBBF24; font-size: 13px; font-weight: 600;")
            layout.addWidget(sep)

            for pr in prs[:5]:  # Show top 5
                pr_text = f"{pr.label}: {pr.exercise_name} — {pr.display_value}"
                if pr.improvement_text:
                    pr_text += f" ({pr.improvement_text})"
                pr_label = QLabel(pr_text)
                pr_label.setStyleSheet("color: #FBBF24; font-size: 13px; font-weight: 600;")
                layout.addWidget(pr_label)

        # ─── Recommendations ─────────────────────
        if recommendations:
            sep2 = QLabel("───── Next Session ─────")
            sep2.setStyleSheet("color: #818CF8; font-size: 13px; font-weight: 600;")
            layout.addWidget(sep2)

            for rec in recommendations[:3]:
                if rec.should_increase:
                    rec_label = QLabel(
                        f"⬆ {rec.exercise_name}: {rec.suggested_weight:.0f} kg "
                        f"({rec.target_reps})"
                    )
                    rec_label.setStyleSheet("color: #4ADE80; font-size: 12px;")
                else:
                    rec_label = QLabel(
                        f"➡ {rec.exercise_name}: keep {rec.current_weight:.0f} kg"
                    )
                    rec_label.setStyleSheet("color: #FBBF24; font-size: 12px;")
                layout.addWidget(rec_label)

        # ─── Recovery Flags ──────────────────────
        if recovery and recovery.flags:
            sep3 = QLabel("───── Recovery ─────")
            sep3.setStyleSheet("color: #F87171; font-size: 13px; font-weight: 600;")
            layout.addWidget(sep3)

            for flag in recovery.flags[:2]:
                flag_color = {
                    "critical": "#F87171",
                    "warning": "#FBBF24",
                    "info": "#60A5FA",
                }.get(flag.severity, "#94A3B8")
                f_label = QLabel(f"⚠ {flag.message}")
                f_label.setStyleSheet(f"color: {flag_color}; font-size: 11px;")
                f_label.setWordWrap(True)
                layout.addWidget(f_label)

            if recovery.should_deload:
                deload_label = QLabel("⚠ Consider scheduling a deload week")
                deload_label.setStyleSheet("color: #F87171; font-size: 12px; font-weight: 700;")
                layout.addWidget(deload_label)

        layout.addStretch()

        btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        btn_box.setStyleSheet("""
            QPushButton {
                background-color: #818CF8;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                padding: 10px 24px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover { background-color: #6366F1; }
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
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header bar
        header_bar = QFrame()
        header_bar.setStyleSheet(
            "background-color: #0F172A; border-bottom: 1px solid #1E293B;"
        )
        header_layout = QHBoxLayout(header_bar)
        header_layout.setContentsMargins(32, 16, 32, 16)

        self._back_btn = QPushButton("← Back")
        self._back_btn.setCursor(Qt.PointingHandCursor)
        self._back_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #94A3B8;
                border: none;
                font-size: 14px;
                font-weight: 500;
            }
            QPushButton:hover { color: #F1F5F9; }
        """)
        self._back_btn.clicked.connect(self.back_clicked.emit)
        header_layout.addWidget(self._back_btn)

        self._title_label = QLabel("Workout")
        self._title_label.setStyleSheet(
            "color: #F1F5F9; font-size: 20px; font-weight: 700;"
        )
        header_layout.addWidget(self._title_label)
        header_layout.addStretch()

        finish_btn = QPushButton("Save & Finish")
        finish_btn.setFixedHeight(40)
        finish_btn.setCursor(Qt.PointingHandCursor)
        finish_btn.setStyleSheet("""
            QPushButton {
                background-color: #4ADE80;
                color: #0F172A;
                border: none;
                border-radius: 8px;
                padding: 8px 20px;
                font-size: 13px;
                font-weight: 700;
            }
            QPushButton:hover { background-color: #22C55E; }
        """)
        finish_btn.clicked.connect(self._finish_workout)
        header_layout.addWidget(finish_btn)
        layout.addWidget(header_bar)

        # Scrollable exercise list
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: #0F172A; }")

        scroll_widget = QWidget()
        scroll_widget.setStyleSheet("background-color: #0F172A;")
        self._scroll_layout = QVBoxLayout(scroll_widget)
        self._scroll_layout.setContentsMargins(32, 16, 32, 16)
        self._scroll_layout.setSpacing(12)
        self._scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

    def load_day(self, day_name: str):
        """Load a workout day's exercises into the view."""
        self._current_day_name = day_name
        self._title_label.setText(day_name)
        self._cards.clear()
        self._started_at = datetime.now()

        # Clear existing widgets
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

        # Get progression recommendations for each exercise
        prog_engine = ProgressionEngine(self._db)

        for ex in day_data["exercises"]:
            ex_name = ex["name"]
            target_sets = ex.get("target_sets", 3)
            target_reps = ex.get("target_reps", "8-12")

            # Get previous session data
            prev = self._db.get_last_session_for_exercise(ex_name)
            prev_sets = prev.sets if prev else None

            # Get progression recommendation
            rec = prog_engine.get_recommendation(ex_name, target_reps)

            card = ExerciseCard(ex_name, target_sets, prev_sets, rec)
            self._cards.append(card)
            self._scroll_layout.insertWidget(
                self._scroll_layout.count() - 1, card
            )

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

        # Detect PRs
        pr_engine = PREngine(self._db)
        prs = pr_engine.detect_prs(saved)

        # Analyse recovery
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

        # Get progression recommendations
        prog_engine = ProgressionEngine(self._db)
        recommendations = []
        for card in self._cards:
            data = card.get_exercise_data()
            ex_sets = data["sets"]
            ex_name = data["name"]
            reps_range = target_reps_map.get(ex_name, "8-12")
            rec = prog_engine.analyse_exercise(ex_name, ex_sets, reps_range)
            recommendations.append(rec)

        # Show summary dialog
        dialog = WorkoutSummaryDialog(saved, prs, recovery, recommendations, self)
        dialog.exec()

        self.workout_saved.emit()
