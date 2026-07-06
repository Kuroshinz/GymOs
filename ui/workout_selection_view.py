"""Workout selection screen — shows PPL-UL program days to choose from."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

DAY_ICONS = {
    "Push": "🏋️",
    "Pull": "🏋️",
    "Legs": "🦵",
    "Upper": "💪",
    "Lower": "🦵",
}

DAY_DESC = {
    "Push": "Chest, Shoulders, Triceps",
    "Pull": "Back, Biceps, Rear Delts",
    "Legs": "Quads, Hamstrings, Glutes",
    "Upper": "Full Upper Body",
    "Lower": "Lower Body Power",
}


class DayCard(QFrame):
    clicked = Signal(str)

    def __init__(self, name: str):
        super().__init__()
        self.day_name = name
        icon = "🏋️"
        desc = "Workout"
        for key, val in DAY_ICONS.items():
            if key in name:
                icon = val
                break
        for key, val in DAY_DESC.items():
            if key in name:
                desc = val
                break

        self.setMinimumSize(200, 140)
        self.setCursor(Qt.PointingHandCursor)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setStyleSheet("""
            DayCard {
                background-color: #1E293B;
                border: 2px solid transparent;
                border-radius: 16px;
                padding: 20px;
            }
            DayCard:hover {
                border: 2px solid #818CF8;
                background-color: #1E293B;
            }
            DayCard:focus {
                border: 2px solid #818CF8;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(6)

        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 28px;")
        layout.addWidget(icon_label)

        name_label = QLabel(name)
        name_label.setStyleSheet("color: #F1F5F9; font-size: 18px; font-weight: 700;")
        layout.addWidget(name_label)

        desc_label = QLabel(desc)
        desc_label.setStyleSheet("color: #64748B; font-size: 12px;")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)

    def mousePressEvent(self, event):
        self.clicked.emit(self.day_name)
        super().mousePressEvent(event)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Space):
            self.clicked.emit(self.day_name)
        super().keyPressEvent(event)


class WorkoutSelectionView(QWidget):
    workout_selected = Signal(str)

    def __init__(self, db, prog_mgr=None):
        super().__init__()
        self._db = db
        self._prog_mgr = prog_mgr
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)

        header = QLabel("Select Workout")
        header.setStyleSheet("font-size: 24px; font-weight: 700; color: #F1F5F9;")
        layout.addWidget(header)

        sub = QLabel("Choose your training session for today")
        sub.setStyleSheet("color: #94A3B8; font-size: 14px; margin-top: -16px;")
        layout.addWidget(sub)

        self._grid = QGridLayout()
        self._grid.setSpacing(16)
        layout.addLayout(self._grid)

        layout.addStretch()

    def refresh(self):
        """Reload the program days from the database."""
        self._clear_grid()

        days = []
        if self._prog_mgr:
            days = self._prog_mgr.get_active_program_days()
        if not days:
            days = self._db.get_program_days("PPL-UL")

        row, col = 0, 0
        for day in days:
            card = DayCard(day["name"])
            card.clicked.connect(self.workout_selected.emit)
            self._grid.addWidget(card, row, col)
            col += 1
            if col > 2:
                col = 0
                row += 1

    def _clear_grid(self):
        while self._grid.count():
            item = self._grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
