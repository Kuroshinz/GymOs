"""Nutrition summary card — placeholder for future Nutrition Intelligence.

Architecture supports future integration via:
  - nutrition_configured flag (when Nutrition module is active)
  - nutrition_data dict (calories, protein, carbs, fat, hydration)
"""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QLabel, QPushButton, QVBoxLayout, QProgressBar

from .base_card import DashboardCard


class NutritionWidget(DashboardCard):
    """Shows daily nutrition summary.

    When nutrition is not configured, displays a helpful placeholder
    with clear messaging. When configured, shows macronutrient breakdown.

    Future: When Nutrition Intelligence is implemented, set
    data.nutrition_configured = True and populate nutrition_data.
    """

    configure_nutrition_clicked = Signal()

    def __init__(self, parent: QFrame | None = None) -> None:
        super().__init__(title="NUTRITION", parent=parent)
        self._container = QVBoxLayout()
        self._container.setContentsMargins(0, 0, 0, 0)
        self._container.setSpacing(8)
        self.add_layout(self._container)

        self._button = QPushButton("Configure Nutrition")
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
        self._button.clicked.connect(self.configure_nutrition_clicked.emit)

    def update_data(self, data: Any) -> None:
        """Update with dashboard data."""
        while self._container.count():
            item = self._container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        configured = getattr(data, "nutrition_configured", False)

        if not configured:
            self._show_placeholder()
            return

        self._render_nutrition(data)

    def _show_placeholder(self) -> None:
        """Show placeholder when nutrition is not configured."""
        title = QLabel("Nutrition tracking not configured.")
        title.setStyleSheet("color: #F1F5F9; font-size: 14px; font-weight: 600;")
        title.setAlignment(Qt.AlignCenter)
        self._container.addWidget(title)

        sub = QLabel(
            "Set your daily targets to track calories, "
            "protein, carbs, fat, and hydration."
        )
        sub.setStyleSheet("color: #64748B; font-size: 12px;")
        sub.setWordWrap(True)
        sub.setAlignment(Qt.AlignCenter)
        self._container.addWidget(sub)

        self._container.addSpacing(8)
        self._container.addWidget(self._button)

    def _render_nutrition(self, data: Any) -> None:
        """Render nutrition data when configured."""
        nutrition = getattr(data, "nutrition_data", {}) or {}

        macros = [
            ("Calories", nutrition.get("calories", {}), "kcal", "#6366F1"),
            ("Protein", nutrition.get("protein", {}), "g", "#10B981"),
            ("Carbs", nutrition.get("carbs", {}), "g", "#3B82F6"),
            ("Fat", nutrition.get("fat", {}), "g", "#F59E0B"),
            ("Hydration", nutrition.get("hydration", {}), "ml", "#06B6D4"),
        ]

        for label, values, unit, color in macros:
            current = values.get("current", 0) if isinstance(values, dict) else 0
            target = values.get("target", 0) if isinstance(values, dict) else 0
            
            # Row label/value
            row = DashboardCard.make_row(
                label,
                f"{current}/{target} {unit}",
                "#10B981" if current >= target and target > 0 else "#F1F5F9",
            )
            self._container.addWidget(row)
            
            # Progress bar
            bar = QProgressBar()
            bar.setFixedHeight(5)
            bar.setTextVisible(False)
            bar.setRange(0, int(target) if target > 0 else 100)
            bar.setValue(int(current))
            bar.setStyleSheet(f"""
                QProgressBar {{
                    background-color: rgba(255, 255, 255, 0.05);
                    border: none;
                    border-radius: 2px;
                }}
                QProgressBar::chunk {{
                    background-color: {color};
                    border-radius: 2px;
                }}
            """)
            self._container.addWidget(bar)
            self._container.addSpacing(4)

        self._container.addWidget(DashboardCard.make_separator())
        self._container.addWidget(self._button)
