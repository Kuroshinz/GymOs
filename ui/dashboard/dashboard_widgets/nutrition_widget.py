"""Nutrition summary card — placeholder for future Nutrition Intelligence.

Architecture supports future integration via:
  - nutrition_configured flag (when Nutrition module is active)
  - nutrition_data dict (calories, protein, carbs, fat, hydration)
"""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QLabel, QPushButton, QVBoxLayout

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

    def update(self, data: Any) -> None:
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
        """Render nutrition data when configured.

        This is a stub for future Nutrition Intelligence integration.
        When the Nutrition module is live, this will display:
          - Calories (current/target)
          - Protein (current/target)
          - Carbs (current/target)
          - Fat (current/target)
          - Hydration (current/target)
        """
        nutrition = getattr(data, "nutrition_data", {}) or {}

        # Future: populate from Nutrition Intelligence module
        macros = [
            ("Calories", nutrition.get("calories", {}), "kcal"),
            ("Protein", nutrition.get("protein", {}), "g"),
            ("Carbs", nutrition.get("carbs", {}), "g"),
            ("Fat", nutrition.get("fat", {}), "g"),
            ("Hydration", nutrition.get("hydration", {}), "ml"),
        ]

        for label, values, unit in macros:
            current = values.get("current", 0) if isinstance(values, dict) else 0
            target = values.get("target", 0) if isinstance(values, dict) else 0
            row = DashboardCard.make_row(
                label,
                f"{current}/{target} {unit}",
                "#4ADE80" if current >= target else "#F1F5F9",
            )
            self._container.addWidget(row)

        self._container.addWidget(DashboardCard.make_separator())
        self._container.addWidget(self._button)
