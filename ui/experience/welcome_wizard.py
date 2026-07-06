"""First-launch wizard / welcome screen.

Uses the existing WorkflowEngine to present a step-by-step
onboarding experience for new users.
"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)

from shared.version import APP_VERSION
from ui.design_system.tokens.color import ColorScheme, color_from_scheme


def needs_onboarding() -> bool:
    """Check if the application needs to show the onboarding wizard.

    Returns True if no profile has been created yet.
    """
    from pathlib import Path
    profile_marker = Path(__file__).parent.parent.parent / "data" / ".profile_created"
    return not profile_marker.exists()


def mark_onboarding_done() -> None:
    """Mark onboarding as completed by creating a marker file."""
    from pathlib import Path
    marker = Path(__file__).parent.parent.parent / "data" / ".profile_created"
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text("onboarded", encoding="utf-8")


class WelcomeWizard(QDialog):
    """First-launch onboarding wizard with multiple steps."""

    onboarding_complete = Signal(str, str, str)  # name, goal, experience_level

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._colors = color_from_scheme(ColorScheme.DARK)
        self._current_step = 0
        self._user_name = ""
        self._goal = "Build Muscle"
        self._experience = "Intermediate"
        self._load_demo = True

        self._build_ui()
        self._show_step(0)

    def _colors(self):
        return color_from_scheme(ColorScheme.DARK)

    def _build_ui(self) -> None:
        self.setWindowTitle("Welcome to GymOS")
        self.setModal(True)
        self.setFixedSize(520, 480)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 36, 40, 28)
        main_layout.setSpacing(20)

        # Title
        title = QLabel("Welcome to GymOS")
        title_font = QFont("Inter", 24, 700)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {self._colors().text_primary};")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        # Subtitle
        subtitle = QLabel("Let's get you set up in a few steps.")
        subtitle_font = QFont("Inter", 13, 400)
        subtitle.setFont(subtitle_font)
        subtitle.setStyleSheet(f"color: {self._colors().text_secondary};")
        subtitle.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(subtitle)

        # Step indicator
        self._step_label = QLabel("Step 1 of 4")
        self._step_label.setStyleSheet(f"color: {self._colors().text_disabled}; font-size: 11px;")
        self._step_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self._step_label)

        # Content area
        self._content = QWidget()
        self._content_layout = QVBoxLayout(self._content)
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(12)
        main_layout.addWidget(self._content, stretch=1)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        self._skip_btn = QPushButton("Skip")
        self._skip_btn.setCursor(Qt.PointingHandCursor)
        self._skip_btn.clicked.connect(lambda: self.done(QDialog.Accepted))

        self._back_btn = QPushButton("Back")
        self._back_btn.setCursor(Qt.PointingHandCursor)
        self._back_btn.clicked.connect(self._on_back)
        self._back_btn.setVisible(False)

        self._next_btn = QPushButton("Next")
        self._next_btn.setCursor(Qt.PointingHandCursor)
        self._next_btn.setDefault(True)
        self._next_btn.clicked.connect(self._on_next)

        btn_layout.addWidget(self._skip_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self._back_btn)
        btn_layout.addWidget(self._next_btn)

        # Button styling
        btn_style = f"""
            QPushButton {{
                background-color: {self._colors().primary};
                color: white; border: none; border-radius: 8px;
                padding: 8px 20px; font-size: 13px; font-weight: 600;
            }}
            QPushButton:hover {{ background-color: {self._colors().primary_hover}; }}
            QPushButton:pressed {{ background-color: {self._colors().primary_active}; }}
        """
        skip_style = f"""
            QPushButton {{
                background-color: transparent; color: {self._colors().text_secondary};
                border: none; padding: 8px 16px; font-size: 12px;
            }}
            QPushButton:hover {{ color: {self._colors().text_primary}; }}
        """

        for b in (self._back_btn, self._next_btn):
            b.setStyleSheet(btn_style)
        self._skip_btn.setStyleSheet(skip_style)

        main_layout.addLayout(btn_layout)

        self.setStyleSheet(f"""
            WelcomeWizard {{
                background-color: {self._colors().surface};
                border-radius: 16px;
            }}
        """)

    def _clear_content(self) -> None:
        while self._content_layout.count():
            item = self._content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _show_step(self, step: int) -> None:
        self._clear_content()
        self._current_step = step
        self._step_label.setText(f"Step {step + 1} of 4")

        self._back_btn.setVisible(step > 0)
        is_last = step == 3
        self._next_btn.setText("Finish" if is_last else "Next")

        steps = [
            self._step_welcome,
            self._step_profile,
            self._step_goal,
            self._step_demo,
        ]
        steps[step]()

    def _step_welcome(self) -> None:
        lbl = QLabel(
            "<p style='font-size: 14px; line-height: 1.6;'>"
            "GymOS is your intelligent training companion. It helps you "
            "plan workouts, track recovery, predict progress, and make "
            "data-driven decisions about your training.</p>"
            f"<p style='font-size: 13px; color: {self._colors().text_secondary};'>"
            f"Version {APP_VERSION}</p>"
        )
        lbl.setWordWrap(True)
        lbl.setStyleSheet(f"color: {self._colors().text_primary};")
        self._content_layout.addWidget(lbl)

    def _step_profile(self) -> None:
        form = QFormLayout()
        form.setSpacing(12)

        lbl_style = f"color: {self._colors().text_primary}; font-size: 13px; font-weight: 500;"
        input_style = (
            f"background-color: {self._colors().background}; color: {self._colors().text_primary};"
            f"border: 1px solid {self._colors().border}; border-radius: 6px;"
            f"padding: 8px 12px; font-size: 13px;"
        )

        name_label = QLabel("Your Name")
        name_label.setStyleSheet(lbl_style)
        self._name_input = QLineEdit()
        self._name_input.setPlaceholderText("Enter your name")
        self._name_input.setStyleSheet(input_style)
        form.addRow(name_label, self._name_input)

        self._content_layout.addLayout(form)

    def _step_goal(self) -> None:
        lbl = QLabel("What is your primary training goal?")
        lbl.setStyleSheet(f"color: {self._colors().text_primary}; font-size: 14px; font-weight: 600;")
        self._content_layout.addWidget(lbl)

        goals = ["Build Muscle", "Increase Strength", "Improve Endurance", "General Fitness"]
        radio_style = (
            f"color: {self._colors().text_primary}; font-size: 13px; spacing: 8px;"
        )
        self._goal_group: list[QRadioButton] = []
        for g in goals:
            rb = QRadioButton(g)
            rb.setStyleSheet(radio_style)
            rb.setCursor(Qt.PointingHandCursor)
            if g == self._goal:
                rb.setChecked(True)
            self._goal_group.append(rb)
            self._content_layout.addWidget(rb)

        self._content_layout.addSpacing(12)

        exp_lbl = QLabel("Experience Level")
        exp_lbl.setStyleSheet(f"color: {self._colors().text_primary}; font-size: 14px; font-weight: 600;")
        self._content_layout.addWidget(exp_lbl)

        levels = ["Beginner", "Intermediate", "Advanced"]
        self._exp_group: list[QRadioButton] = []
        for lvl in levels:
            rb = QRadioButton(lvl)
            rb.setStyleSheet(radio_style)
            rb.setCursor(Qt.PointingHandCursor)
            if lvl == self._experience:
                rb.setChecked(True)
            self._exp_group.append(rb)
            self._content_layout.addWidget(rb)

    def _step_demo(self) -> None:
        lbl = QLabel("Load Demo Data?")
        lbl.setStyleSheet(f"color: {self._colors().text_primary}; font-size: 16px; font-weight: 600;")
        self._content_layout.addWidget(lbl)

        desc = QLabel(
            "Would you like to start with sample workout data and a "
            "pre-configured program? You can always delete it later."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet(f"color: {self._colors().text_secondary}; font-size: 13px;")
        self._content_layout.addWidget(desc)

        self._demo_check = QCheckBox("Load demo data with sample workouts")
        self._demo_check.setChecked(True)
        self._demo_check.setStyleSheet(
            f"color: {self._colors().text_primary}; font-size: 13px; spacing: 8px;"
        )
        self._content_layout.addWidget(self._demo_check)

    def _on_back(self) -> None:
        if self._current_step > 0:
            self._show_step(self._current_step - 1)

    def _on_next(self) -> None:
        if self._current_step == 1:
            self._user_name = getattr(self, "_name_input", None) and self._name_input.text().strip()

        if self._current_step == 2:
            for rb in self._goal_group:
                if rb.isChecked():
                    self._goal = rb.text()
                    break
            for rb in self._exp_group:
                if rb.isChecked():
                    self._experience = rb.text()
                    break

        if self._current_step == 3:
            self._load_demo = getattr(self, "_demo_check", None) and self._demo_check.isChecked()
            mark_onboarding_done()
            self.onboarding_complete.emit(self._user_name, self._goal, self._experience)
            self.accept()
        else:
            self._show_step(self._current_step + 1)
