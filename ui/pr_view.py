"""Personal Records screen — displays all PRs with best weight, reps, volume, e1RM."""

from datetime import date, datetime

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ui.design_system.tokens.color import ColorScheme, color_from_scheme
from ui.design_system.tokens.radius import RadiusTokens
from ui.design_system.tokens.typography import font_style


R = RadiusTokens()


class PRCard(QFrame):
    """A card showing a personal record for an exercise."""

    def __init__(self, pr):
        super().__init__()
        c = color_from_scheme(ColorScheme.DARK)
        type_labels = {
            "weight": "Weight PR",
            "reps": "Rep PR",
            "volume": "Volume PR",
            "e1rm": "Est. 1RM",
        }
        pr_type_label = type_labels.get(pr.pr_type, pr.pr_type)
        self.setAccessibleName(f"Personal Record: {pr.exercise_name} - {pr_type_label}")
        if pr.display_value:
            self.setAccessibleDescription(f"{pr.exercise_name}: {pr.display_value}")
        self.setStyleSheet(f"""
            PRCard {{
                background-color: {c.surface_elevated};
                border: 1px solid {c.border};
                border-radius: {R.lg};
                padding: 16px;
            }}
            PRCard:focus {{
                border-color: {c.primary};
            }}
        """)
        self.setFocusPolicy(Qt.StrongFocus)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(4)

        # Exercise name and type
        type_colors = {
            "weight": c.success,
            "reps": c.info,
            "volume": c.warning,
            "e1rm": c.primary,
        }
        color = type_colors.get(pr.pr_type, c.text_secondary)

        row1 = QHBoxLayout()
        row1.setSpacing(8)

        name_label = QLabel(pr.exercise_name)
        name_label.setAccessibleName(f"{pr.exercise_name} exercise name")
        name_label.setStyleSheet(f"color: {c.text_primary}; font-size: 15px; font-weight: 700;")
        row1.addWidget(name_label)

        type_label = QLabel(pr_type_label)
        type_label.setAccessibleName(f"PR type: {pr_type_label}")
        type_label.setStyleSheet(f"color: {color}; font-size: 11px; font-weight: 600; "
                                 f"background-color: {c.surface}; border-radius: {R.sm}; "
                                 f"padding: 2px 8px;")
        row1.addWidget(type_label)
        row1.addStretch()
        layout.addLayout(row1)

        # Value
        value_text = pr.display_value
        if pr.improvement_text:
            value_text += f"  {pr.improvement_text}"
        value_label = QLabel(value_text)
        value_label.setAccessibleName(f"{pr.exercise_name} PR value")
        value_label.setStyleSheet(f"color: {color}; font-size: 22px; font-weight: 700;")
        layout.addWidget(value_label)

        # Date and days since
        if pr.achieved_at:
            try:
                pr_date = datetime.fromisoformat(pr.achieved_at).date()
                days_since = (date.today() - pr_date).days
                date_text = f"{pr_date.strftime('%b %d, %Y')} · {days_since}d ago"
            except (ValueError, TypeError):
                date_text = pr.achieved_at
        else:
            date_text = ""

        if date_text:
            date_label = QLabel(date_text)
            date_label.setStyleSheet(f"color: {c.text_disabled}; font-size: 11px;")
            layout.addWidget(date_label)


class PRView(QWidget):
    """Personal Records screen — displays all PRs."""

    def __init__(self, db):
        super().__init__()
        self._db = db
        self._build_ui()

    def _colors(self):
        return color_from_scheme(ColorScheme.DARK)

    def _build_ui(self):
        c = self._colors()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(16)

        header = QLabel("Personal Records")
        header.setAccessibleName("Personal Records heading")
        header.setStyleSheet(f"color: {c.text_primary}; {font_style('h2')}; background: transparent;")
        layout.addWidget(header)

        sub = QLabel("Your best performances across all exercises")
        sub.setAccessibleName("Personal Records description")
        sub.setStyleSheet(f"color: {c.text_secondary}; font-size: 14px; margin-top: -8px; background: transparent;")
        layout.addWidget(sub)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")

        scroll_widget = QWidget()
        scroll_widget.setStyleSheet("background-color: transparent;")
        self._grid = QGridLayout(scroll_widget)
        self._grid.setSpacing(12)
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

    def refresh(self):
        """Reload PR data from the database."""
        c = self._colors()
        self._clear_grid()
        from modules.workout.application.pr_engine import PREngine

        engine = PREngine(self._db)
        prs = engine.get_best_prs()

        if not prs:
            placeholder = QLabel("No PRs yet. Complete a workout to start tracking!")
            placeholder.setStyleSheet(f"color: {c.text_disabled}; font-size: 14px; padding: 40px; background: transparent;")
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._grid.addWidget(placeholder, 0, 0)
            return

        row, col = 0, 0
        for pr in prs:
            card = PRCard(pr)
            self._grid.addWidget(card, row, col)
            col += 1
            if col >= 2:
                col = 0
                row += 1

    def _clear_grid(self):
        while self._grid.count():
            item = self._grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
