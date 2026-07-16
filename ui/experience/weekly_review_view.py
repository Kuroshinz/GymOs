"""Weekly Review View — renders a structured training summary with next-week priorities."""

from __future__ import annotations

from typing import Any
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
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
from ui.design_system.components.empty_state import EmptyState

R = RadiusTokens()


class MetricCard(QFrame):
    """A card displaying a single weekly review metric."""

    def __init__(self, label: str, value: str, subtitle: str = "", color: str | None = None) -> None:
        super().__init__()
        c = color_from_scheme(ColorScheme.DARK)
        border_color = color if color else c.border
        bg_color = c.surface_elevated
        if color:
            # Add a subtle translucent color tint to the background
            bg_color = f"rgba({QColor(color).red()}, {QColor(color).green()}, {QColor(color).blue()}, 0.08)"
            
        self.setStyleSheet(f"""
            MetricCard {{
                background-color: {bg_color};
                border: 1px solid {border_color};
                border-radius: {R.lg};
                padding: 16px;
            }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(4)

        lbl = QLabel(label)
        lbl.setStyleSheet(f"color: {c.text_secondary}; font-size: 11px; font-weight: 700; letter-spacing: 0.5px;")
        layout.addWidget(lbl)

        val_color = color or c.text_primary
        val = QLabel(value)
        val.setStyleSheet(f"color: {val_color}; font-size: 24px; font-weight: 700;")
        layout.addWidget(val)

        if subtitle:
            sub = QLabel(subtitle)
            sub.setStyleSheet(f"color: {c.text_disabled}; font-size: 11px;")
            layout.addWidget(sub)


class WeeklyReviewView(QWidget):
    """Displays weekly training review and optimization guidelines."""

    def __init__(self, db: Any = None, decision_engine: Any = None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._db = db
        self._engine = decision_engine
        self._build_ui()

    def _build_ui(self) -> None:
        self.setAccessibleName("Weekly Review Screen")
        c = color_from_scheme(ColorScheme.DARK)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(32, 32, 32, 32)
        main_layout.setSpacing(16)

        # Header section
        header_layout = QHBoxLayout()
        self._title_label = QLabel("WEEKLY REVIEW")
        self._title_label.setStyleSheet(f"color: {c.text_primary}; font-size: 24px; font-weight: 700;")
        header_layout.addWidget(self._title_label)

        self._date_label = QLabel("Analyzing recent training...")
        self._date_label.setStyleSheet(f"color: {c.text_secondary}; font-size: 13px; font-weight: 500;")
        header_layout.addStretch()
        header_layout.addWidget(self._date_label)
        main_layout.addLayout(header_layout)

        # Scroll Area for Content
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.scroll_content = QWidget()
        self.scroll_content.setStyleSheet("background: transparent;")
        self.content_layout = QVBoxLayout(self.scroll_content)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(24)

        # Grid for stats
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setSpacing(16)
        self.content_layout.addWidget(self.grid_widget)

        # Priority List Card
        self.priority_card = QFrame()
        self.priority_card.setStyleSheet(f"""
            QFrame {{
                background-color: {c.surface_elevated};
                border: 1px solid {c.border};
                border-radius: {R.lg};
                padding: 24px;
            }}
        """)
        priority_layout = QVBoxLayout(self.priority_card)
        priority_layout.setSpacing(12)

        priority_title = QLabel("OPTIMIZATION PRIORITIES")
        priority_title.setStyleSheet(f"color: {c.primary}; font-size: 12px; font-weight: 700; letter-spacing: 1px;")
        priority_layout.addWidget(priority_title)

        self.priority_list = QVBoxLayout()
        self.priority_list.setSpacing(8)
        priority_layout.addLayout(self.priority_list)

        self.content_layout.addWidget(self.priority_card)

        # Empty State
        self.empty_state = EmptyState(
            title="No sessions completed this week",
            description="Complete at least one workout session to generate a weekly intelligence review.",
            icon="📊",
        )
        self.content_layout.addWidget(self.empty_state)

        self.scroll.setWidget(self.scroll_content)
        main_layout.addWidget(self.scroll)

    def refresh(self) -> None:
        """Fetch and populate weekly review metrics."""
        if not self._engine:
            self._show_empty_state()
            return

        try:
            review = self._engine.get_weekly_review()
            if not review or review.total_workouts == 0:
                self._show_empty_state()
                return

            self._show_content(review)
        except Exception:
            self._show_empty_state()

    def _show_empty_state(self) -> None:
        self._date_label.setText("No training data")
        self.grid_widget.setVisible(False)
        self.priority_card.setVisible(False)
        self.empty_state.setVisible(True)

    def _show_content(self, review: Any) -> None:
        self.empty_state.setVisible(False)
        self.grid_widget.setVisible(True)
        self.priority_card.setVisible(True)

        self._date_label.setText(review.week_label)

        # Clear grid
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Populate grid
        c = color_from_scheme(ColorScheme.DARK)
        
        cards = [
            ("Workouts", f"{review.total_workouts}", f"Missed: {review.missed_sessions} sessions", None),
            ("Total Volume", f"{review.total_volume_kg:,.1f} kg", f"{review.total_sets} working sets", None),
            ("Top Milestone", f"{review.best_pr}", "Best progression", c.success),
            ("Recovery Status", f"{review.recovery_score}", f"Fatigue: {review.fatigue_level.upper()}", c.info),
            ("Bodyweight Shift", f"{review.bodyweight_change:+.1f} kg", "Lean bulk tracking", None),
            ("Most Improved", f"{review.most_improved_muscle or 'None'}", "Volume leader", c.warning),
        ]

        for i, (label, val, subtitle, col) in enumerate(cards):
            card = MetricCard(label, val, subtitle, col)
            self.grid_layout.addWidget(card, i // 3, i % 3)

        # Clear priority list
        while self.priority_list.count():
            item = self.priority_list.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Populate priorities
        if review.next_week_priorities:
            for p in review.next_week_priorities:
                lbl = QLabel(f"• {p}")
                lbl.setStyleSheet(f"color: {c.text_secondary}; font-size: 13px; line-height: 18px;")
                lbl.setWordWrap(True)
                self.priority_list.addWidget(lbl)
        else:
            lbl = QLabel("No priority modifications required. Continue standard training blocks.")
            lbl.setStyleSheet(f"color: {c.text_disabled}; font-size: 13px; font-style: italic;")
            self.priority_list.addWidget(lbl)
