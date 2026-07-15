"""First-launch wizard / welcome screen.

Uses the existing WorkflowEngine to present a step-by-step
onboarding experience for new users.
"""

from __future__ import annotations

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QGraphicsOpacityEffect,
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
from ui.design_system.tokens.radius import RadiusTokens

R = RadiusTokens()

# Pixel equivalents of SpacingTokens values (0.25rem multiplier, 16px base)
_s2 = 8
_s3 = 12
_s4 = 16
_s6 = 24
_s8 = 32
_s10 = 40

STEP_NAMES = ["Welcome", "Profile", "Goals", "Demo"]


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
        self._current_step = 0
        self._user_name = ""
        self._goal = "Build Muscle"
        self._experience = "Intermediate"
        self._load_demo = True
        self._active_anims: list[QPropertyAnimation] = []

        self._build_ui()
        self._show_step(0)

    def _colors(self):
        return color_from_scheme(ColorScheme.DARK)

    def _build_ui(self) -> None:
        c = self._colors()
        self.setWindowTitle("Welcome to GymOS")
        self.setModal(True)
        self.setMinimumSize(640, 580)
        self.setStyleSheet(f"""
            WelcomeWizard {{
                background-color: {c.background};
            }}
        """)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Scrollable content wrapper ───
        scroll_widget = QWidget()
        scroll_widget.setObjectName("wizard_scroll")
        scroll_widget.setStyleSheet(f"""
            #wizard_scroll {{
                background-color: {c.background};
            }}
        """)
        self._scroll_layout = QVBoxLayout(scroll_widget)
        self._scroll_layout.setContentsMargins(_s10, _s8, _s10, 0)
        self._scroll_layout.setSpacing(_s6)

        # ── Hero ───
        hero = QVBoxLayout()
        hero.setSpacing(_s2)

        self._hero_sub = QLabel("Hi, nice to meet you")
        self._hero_sub.setAlignment(Qt.AlignCenter)
        self._hero_sub.setStyleSheet(
            f"color: {c.text_disabled}; font-size: 13px; font-weight: 500; "
            f"letter-spacing: 0.05em; text-transform: uppercase; background: transparent;"
        )
        hero.addWidget(self._hero_sub)

        self._title = QLabel("Welcome to GymOS")
        self._title.setAlignment(Qt.AlignCenter)
        self._title.setStyleSheet(
            f"color: {c.text_primary}; font-size: 32px; font-weight: 700; "
            f"letter-spacing: -0.025em; background: transparent;"
        )
        hero.addWidget(self._title)

        self._subtitle = QLabel("Let's get you set up in a few steps.")
        self._subtitle.setAlignment(Qt.AlignCenter)
        self._subtitle.setStyleSheet(
            f"color: {c.text_secondary}; font-size: 15px; background: transparent;"
        )
        hero.addWidget(self._subtitle)

        self._scroll_layout.addLayout(hero)

        # ── Step indicator ───
        steps_row = QHBoxLayout()
        steps_row.setSpacing(_s3)
        steps_row.setContentsMargins(_s8, _s2, _s8, _s2)

        self._step_dots: list[QWidget] = []
        for i in range(4):
            dot = QWidget()
            dot.setFixedSize(48, 4)
            dot.setObjectName(f"step_dot_{i}")
            dot.setStyleSheet(f"""
                #step_dot_{i} {{
                    background-color: {c.border};
                    border-radius: 2px;
                }}
            """)
            dot.setAccessibleName(f"Step {i + 1} of 4: {STEP_NAMES[i]}")
            steps_row.addWidget(dot)
            self._step_dots.append(dot)

        self._scroll_layout.addLayout(steps_row)

        # ── Primary content ───
        content_card = QWidget()
        content_card.setObjectName("wizard_content")
        content_card.setStyleSheet(f"""
            #wizard_content {{
                background-color: {c.surface};
                border: 1px solid {c.border};
                border-radius: {R.lg};
            }}
        """)
        self._content_layout = QVBoxLayout(content_card)
        self._content_layout.setContentsMargins(_s6, _s6, _s6, _s6)
        self._content_layout.setSpacing(_s4)

        self._content = QWidget()
        self._content.setStyleSheet("background: transparent;")
        self._step_layout = QVBoxLayout(self._content)
        self._step_layout.setContentsMargins(0, 0, 0, 0)
        self._step_layout.setSpacing(_s4)
        self._content_layout.addWidget(self._content)

        self._scroll_layout.addWidget(content_card)
        self._scroll_layout.addStretch()

        root.addWidget(scroll_widget)

        # ── Footer ───
        footer = QWidget()
        footer.setObjectName("wizard_footer")
        footer.setStyleSheet(f"""
            #wizard_footer {{
                background-color: {c.surface};
                border-top: 1px solid {c.border};
            }}
        """)
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(_s6, _s4, _s6, _s4)
        footer_layout.setSpacing(_s3)

        self._skip_btn = QPushButton("Skip")
        self._skip_btn.setCursor(Qt.PointingHandCursor)
        self._skip_btn.clicked.connect(lambda: self.done(QDialog.Accepted))
        self._skip_btn.setStyleSheet(
            f"QPushButton {{ background: transparent; color: {c.text_disabled}; "
            f"border: none; padding: {_s2}px {_s4}px; font-size: 13px; }}"
            f"QPushButton:hover {{ color: {c.text_secondary}; }}"
        )
        footer_layout.addWidget(self._skip_btn)

        footer_layout.addStretch()

        self._back_btn = QPushButton("Back")
        self._back_btn.setCursor(Qt.PointingHandCursor)
        self._back_btn.clicked.connect(self._on_back)
        self._back_btn.setVisible(False)
        self._back_btn.setMinimumWidth(90)
        footer_layout.addWidget(self._back_btn)

        self._next_btn = QPushButton("Next")
        self._next_btn.setCursor(Qt.PointingHandCursor)
        self._next_btn.setDefault(True)
        self._next_btn.clicked.connect(self._on_next)
        self._next_btn.setMinimumWidth(120)
        self._next_btn.setStyleSheet(
            f"QPushButton {{ background-color: {c.primary}; color: white; "
            f"border: none; border-radius: {R.md}; padding: {_s3}px {_s6}px; "
            f"font-size: 14px; font-weight: 600; }}"
            f"QPushButton:hover {{ background-color: {c.primary_hover}; }}"
            f"QPushButton:pressed {{ background-color: {c.primary_hover}; }}"
        )

        footer_layout.addWidget(self._back_btn)
        footer_layout.addWidget(self._next_btn)

        root.addWidget(footer)

        # ── Reduced motion support ───
        self._reduced_motion = False
        try:
            from ui.experience.accessibility import AccessibilityManager
            parent_widget = self.parent()
            while parent_widget is not None:
                if hasattr(parent_widget, "_experience") and hasattr(parent_widget._experience, "accessibility"):
                    a11y = parent_widget._experience.accessibility
                    if isinstance(a11y, AccessibilityManager):
                        a11y.register_reduced_motion_widget(self)
                    break
                parent_widget = parent_widget.parent() if hasattr(parent_widget, "parent") else None
        except ImportError:
            pass

    def set_reduced_motion(self, enabled: bool) -> None:
        self._reduced_motion = enabled

    # ── Step indicator update ─────────────────────────────────

    def _update_step_indicator(self, step: int) -> None:
        c = self._colors()
        for i, dot in enumerate(self._step_dots):
            if i < step:
                bg = c.success
            elif i == step:
                bg = c.primary
            else:
                bg = c.border
            dot.setStyleSheet(f"#{dot.objectName()} {{ background-color: {bg}; border-radius: 2px; }}")

    # ── Content management ────────────────────────────────────

    def _clear_content(self) -> None:
        while self._step_layout.count():
            item = self._step_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _fade_in(self, widget: QWidget) -> None:
        if self._reduced_motion:
            return
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)
        anim = QPropertyAnimation(effect, b"opacity")
        anim.setDuration(200)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        self._active_anims.append(anim)
        anim.finished.connect(lambda: self._active_anims.remove(anim) if anim in self._active_anims else None)
        anim.start()

    # ── Step navigation ───────────────────────────────────────

    def _show_step(self, step: int) -> None:
        self._clear_content()
        self._current_step = step

        c = self._colors()
        is_last = step == 3

        self._title.setText(STEP_NAMES[step])

        subtitle_texts = [
            "Let's get you set up in a few steps.",
            "Tell us what to call you.",
            "Set your training preferences.",
            "One last thing \u2014 demo data or fresh start?",
        ]
        self._subtitle.setText(subtitle_texts[step])

        self._hero_sub.setText(f"Step {step + 1} of 4")

        self._back_btn.setVisible(step > 0)
        self._next_btn.setText("Create Profile" if is_last else "Continue")
        self._next_btn.setStyleSheet(
            f"QPushButton {{ background-color: {c.primary}; color: white; "
            f"border: none; border-radius: {R.md}; padding: {_s3}px {_s6}px; "
            f"font-size: 14px; font-weight: 600; }}"
            f"QPushButton:hover {{ background-color: {c.primary_hover}; }}"
            f"QPushButton:pressed {{ background-color: {c.primary_hover}; }}"
        )
        self._skip_btn.setVisible(not is_last)

        self._update_step_indicator(step)

        steps = [
            self._step_welcome,
            self._step_profile,
            self._step_goal,
            self._step_demo,
        ]
        steps[step]()

        self._fade_in(self._content)

        # Focus management
        if step == 0:
            self._next_btn.setFocus()
        elif step == 1:
            self._name_input.setFocus()
        elif step == 2:
            self._goal_group[0].setFocus()
        elif step == 3:
            self._demo_check.setFocus()

    # ── Step builders ─────────────────────────────────────────

    def _step_welcome(self) -> None:
        c = self._colors()
        icon = QLabel("\U0001F3CB")
        icon.setAlignment(Qt.AlignCenter)
        icon.setStyleSheet("font-size: 48px; background: transparent;")
        icon.setAccessibleName("GymOS mascot")
        self._step_layout.addWidget(icon)

        desc = QLabel(
            "GymOS is your intelligent training companion. It helps you "
            "plan workouts, track recovery, predict progress, and make "
            "data-driven decisions about your training."
        )
        desc.setWordWrap(True)
        desc.setAlignment(Qt.AlignCenter)
        desc.setStyleSheet(
            f"color: {c.text_secondary}; font-size: 15px; "
            f"line-height: 1.6; background: transparent;"
        )
        self._step_layout.addWidget(desc)

        feat_grid = QHBoxLayout()
        feat_grid.setSpacing(_s4)
        features = [
            ("\U0001F4C8", "Track Progress"),
            ("\U0001F50B", "Plan Workouts"),
            ("\U0001F4CA", "Analyze Data"),
        ]
        for emoji, label in features:
            cell = QVBoxLayout()
            cell.setSpacing(_s2)
            e = QLabel(emoji)
            e.setAlignment(Qt.AlignCenter)
            e.setStyleSheet("font-size: 28px; background: transparent;")
            cell.addWidget(e)
            l = QLabel(label)
            l.setAlignment(Qt.AlignCenter)
            l.setStyleSheet(
                f"color: {c.text_primary}; font-size: 13px; font-weight: 600; "
                f"background: transparent;"
            )
            cell.addWidget(l)
            feat_grid.addLayout(cell)

        self._step_layout.addLayout(feat_grid)

        ver = QLabel(f"Version {APP_VERSION}")
        ver.setAlignment(Qt.AlignCenter)
        ver.setStyleSheet(
            f"color: {c.text_disabled}; font-size: 11px; background: transparent;"
        )
        self._step_layout.addWidget(ver)

    def _step_profile(self) -> None:
        c = self._colors()
        label = QLabel("Your Name")
        label.setStyleSheet(
            f"color: {c.text_primary}; font-size: 14px; font-weight: 600; "
            f"background: transparent;"
        )
        self._step_layout.addWidget(label)

        self._name_input = QLineEdit()
        self._name_input.setPlaceholderText("Enter your name")
        self._name_input.setMinimumHeight(44)
        self._name_input.setStyleSheet(
            f"QLineEdit {{ background-color: {c.background}; color: {c.text_primary}; "
            f"border: 1px solid {c.border}; border-radius: {R.md}; "
            f"padding: 10px {_s4}px; font-size: 15px; }}"
            f"QLineEdit:focus {{ border-color: {c.primary}; }}"
        )
        self._name_input.setAccessibleName("Your Name")
        self._name_input.setAccessibleDescription("Enter your display name for GymOS")
        self._step_layout.addWidget(self._name_input)

        hint = QLabel("This will be shown on your profile and workout logs.")
        hint.setStyleSheet(
            f"color: {c.text_disabled}; font-size: 12px; background: transparent;"
        )
        self._step_layout.addWidget(hint)

    def _step_goal(self) -> None:
        c = self._colors()
        section_title = QLabel("Primary Goal")
        section_title.setStyleSheet(
            f"color: {c.text_primary}; font-size: 14px; font-weight: 600; "
            f"background: transparent;"
        )
        self._step_layout.addWidget(section_title)

        goals = ["Build Muscle", "Increase Strength", "Improve Endurance", "General Fitness"]
        radio_style = (
            f"color: {c.text_primary}; font-size: 14px; spacing: {_s2}px;"
        )
        self._goal_group: list[QRadioButton] = []
        for g in goals:
            rb = QRadioButton(g)
            rb.setStyleSheet(radio_style + "background: transparent;")
            rb.setCursor(Qt.PointingHandCursor)
            if g == self._goal:
                rb.setChecked(True)
            self._goal_group.append(rb)
            self._step_layout.addWidget(rb)

        self._step_layout.addSpacing(12)

        exp_title = QLabel("Experience Level")
        exp_title.setStyleSheet(
            f"color: {c.text_primary}; font-size: 14px; font-weight: 600; "
            f"background: transparent;"
        )
        self._step_layout.addWidget(exp_title)

        levels = ["Beginner", "Intermediate", "Advanced"]
        self._exp_group: list[QRadioButton] = []
        for lvl in levels:
            rb = QRadioButton(lvl)
            rb.setStyleSheet(radio_style + "background: transparent;")
            rb.setCursor(Qt.PointingHandCursor)
            if lvl == self._experience:
                rb.setChecked(True)
            self._exp_group.append(rb)
            self._step_layout.addWidget(rb)

    def _step_demo(self) -> None:
        c = self._colors()
        icon = QLabel("\U0001F4C2")
        icon.setAlignment(Qt.AlignCenter)
        icon.setStyleSheet("font-size: 40px; background: transparent;")
        icon.setAccessibleName("Demo data icon")
        self._step_layout.addWidget(icon)

        desc = QLabel(
            "Would you like to start with sample workout data and a "
            "pre-configured program? You can always delete it later."
        )
        desc.setWordWrap(True)
        desc.setAlignment(Qt.AlignCenter)
        desc.setStyleSheet(
            f"color: {c.text_secondary}; font-size: 14px; "
            f"line-height: 1.5; background: transparent;"
        )
        self._step_layout.addWidget(desc)

        self._demo_check = QCheckBox("Load demo data with sample workouts")
        self._demo_check.setChecked(True)
        self._demo_check.setStyleSheet(
            f"color: {c.text_primary}; font-size: 14px; spacing: {_s2}px; background: transparent;"
        )
        self._demo_check.setCursor(Qt.PointingHandCursor)
        self._demo_check.setAccessibleName("Load demo data")
        self._demo_check.setAccessibleDescription(
            "Start with sample workout data and a pre-configured program"
        )
        self._step_layout.addWidget(self._demo_check)

    # ── Navigation callbacks ──────────────────────────────────

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
