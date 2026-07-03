"""Personal Records screen — displays all PRs with best weight, reps, volume, e1RM."""

from datetime import datetime, date

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QScrollArea,
    QGridLayout, QSizePolicy,
)


class PRCard(QFrame):
    """A card showing a personal record for an exercise."""

    def __init__(self, pr):
        super().__init__()
        self.setStyleSheet("""
            PRCard {
                background-color: #1E293B;
                border-radius: 12px;
                padding: 16px;
            }
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(4)

        # Exercise name and type
        type_colors = {
            "weight": "#4ADE80",
            "reps": "#60A5FA",
            "volume": "#FBBF24",
            "e1rm": "#818CF8",
        }
        type_labels = {
            "weight": "Weight PR",
            "reps": "Rep PR",
            "volume": "Volume PR",
            "e1rm": "Est. 1RM",
        }
        color = type_colors.get(pr.pr_type, "#94A3B8")

        row1 = QHBoxLayout()
        row1.setSpacing(8)

        name_label = QLabel(pr.exercise_name)
        name_label.setStyleSheet("color: #F1F5F9; font-size: 15px; font-weight: 700;")
        row1.addWidget(name_label)

        type_label = QLabel(type_labels.get(pr.pr_type, pr.pr_type))
        type_label.setStyleSheet(f"color: {color}; font-size: 11px; font-weight: 600; "
                                 f"background-color: #0F172A; border-radius: 4px; "
                                 f"padding: 2px 8px;")
        row1.addWidget(type_label)
        row1.addStretch()
        layout.addLayout(row1)

        # Value
        value_text = pr.display_value
        if pr.improvement_text:
            value_text += f"  {pr.improvement_text}"
        value_label = QLabel(value_text)
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
            date_label.setStyleSheet("color: #64748B; font-size: 11px;")
            layout.addWidget(date_label)


class PRView(QWidget):
    """Personal Records screen — displays all PRs."""

    def __init__(self, db):
        super().__init__()
        self._db = db
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(16)

        header = QLabel("Personal Records")
        header.setStyleSheet("font-size: 24px; font-weight: 700; color: #F1F5F9;")
        layout.addWidget(header)

        sub = QLabel("Your best performances across all exercises")
        sub.setStyleSheet("color: #94A3B8; font-size: 14px; margin-top: -12px;")
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
        self._clear_grid()
        from modules.workout.application.pr_engine import PREngine

        engine = PREngine(self._db)
        prs = engine.get_best_prs()

        if not prs:
            placeholder = QLabel("No PRs yet. Complete a workout to start tracking!")
            placeholder.setStyleSheet("color: #64748B; font-size: 14px; padding: 40px;")
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
