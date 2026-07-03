"""Recent personal records card — shows last 5 PRs with navigation to full history."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from .base_card import DashboardCard


class PRWidget(DashboardCard):
    """Shows the last 5 personal records achieved.

    Each PR shows:
      - Exercise name
      - New value
      - Date
      - PR type
    """

    view_all_prs_clicked = Signal()

    def __init__(self, parent: QFrame | None = None) -> None:
        super().__init__(title="RECENT PERSONAL RECORDS", parent=parent)
        self._container = QVBoxLayout()
        self._container.setContentsMargins(0, 0, 0, 0)
        self._container.setSpacing(6)
        self.add_layout(self._container)

        self._button = QPushButton("View All PRs")
        self._button.setStyleSheet("""
            QPushButton {
                background-color: #334155;
                color: #F1F5F9;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #475569;
            }
        """)
        self._button.clicked.connect(self.view_all_prs_clicked.emit)

    def set_data(self, data: Any) -> None:
        """Update with dashboard data."""
        while self._container.count():
            item = self._container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        prs = getattr(data, "recent_prs", []) or []

        if not prs:
            msg = QLabel(
                "No personal records yet. Push yourself in your next workout!"
            )
            msg.setStyleSheet(
                "color: #64748B; font-size: 13px; padding: 20px 0px;"
            )
            msg.setWordWrap(True)
            msg.setAlignment(Qt.AlignCenter)
            self._container.addWidget(msg)
            self._container.addWidget(self._button)
            return

        for pr in prs[:5]:
            exercise_name = getattr(pr, "exercise_name", "Unknown")
            pr_type = getattr(pr, "pr_type", "") or ""
            value = getattr(pr, "value", "") or ""
            display_value = getattr(pr, "display_value", str(value)) or str(value)
            improvement = getattr(pr, "improvement_text", "") or ""
            achieved_at = getattr(pr, "achieved_at", None)

            emoji = self._pr_emoji(pr_type)
            date_str = ""
            if achieved_at:
                if isinstance(achieved_at, datetime):
                    date_str = achieved_at.strftime("%b %d")
                else:
                    try:
                        dt = datetime.fromisoformat(str(achieved_at))
                        date_str = dt.strftime("%b %d")
                    except (ValueError, TypeError):
                        date_str = str(achieved_at)[:10]

            row = QFrame()
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(0, 4, 0, 4)
            row_layout.setSpacing(8)

            # PR type badge
            type_label = QLabel(f"{emoji} {pr_type.upper()}" if pr_type else emoji)
            type_label.setStyleSheet("color: #FBBF24; font-size: 12px; font-weight: 600;")
            type_label.setFixedWidth(60)
            row_layout.addWidget(type_label)

            # Exercise name
            name_label = QLabel(exercise_name)
            name_label.setStyleSheet("color: #F1F5F9; font-size: 13px; font-weight: 600;")
            name_label.setFixedWidth(120)
            row_layout.addWidget(name_label)

            # Value
            val_label = QLabel(display_value)
            val_label.setStyleSheet("color: #4ADE80; font-size: 13px; font-weight: 700;")
            val_label.setFixedWidth(70)
            row_layout.addWidget(val_label)

            # Improvement
            imp_label = QLabel(improvement)
            imp_label.setStyleSheet("color: #94A3B8; font-size: 11px;")
            imp_label.setFixedWidth(60)
            row_layout.addWidget(imp_label)

            # Date
            date_label = QLabel(date_str)
            date_label.setStyleSheet("color: #64748B; font-size: 11px;")
            row_layout.addWidget(date_label)

            row_layout.addStretch()
            self._container.addWidget(row)

        self._container.addStretch()
        self._container.addWidget(self._button)

    @staticmethod
    def _pr_emoji(pr_type: str) -> str:
        mapping = {
            "weight": "🏋️",
            "volume": "📈",
            "reps": "🔁",
            "1rm": "💪",
            "estimated_1rm": "💪",
            "e1rm": "💪",
        }
        return mapping.get(pr_type.lower(), "⭐")
