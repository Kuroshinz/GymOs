from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from ui.design_system.tokens.color import ColorScheme, color_from_scheme
from ui.design_system.tokens.radius import RadiusTokens

RADIUS = RadiusTokens()


class GoalAdjustmentDialog(QDialog):
    goal_adjusted = Signal(str, float)

    def __init__(
        self,
        current_goal: str = "",
        progress_percent: float = 0.0,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._current_goal = current_goal
        self._progress = progress_percent
        self._color_scheme = ColorScheme.DARK
        self._build_ui()
        self._apply_style()

    def _colors(self):
        return color_from_scheme(self._color_scheme)

    def _apply_style(self) -> None:
        colors = self._colors()
        self.setStyleSheet(f"""
            GoalAdjustmentDialog {{
                background-color: {colors.surface};
                border-radius: {RADIUS.xl};
                border: 1px solid {colors.border};
            }}
            QLabel {{ background: transparent; border: none; }}
            QSlider::groove:horizontal {{
                height: 6px; background: {colors.border};
                border-radius: 3px;
            }}
            QSlider::handle:horizontal {{
                background: {colors.primary};
                width: 18px; height: 18px;
                margin: -6px 0; border-radius: 9px;
            }}
            QSlider::sub-page:horizontal {{
                background: {colors.primary};
                border-radius: 3px;
            }}
        """)

    def _build_ui(self) -> None:
        self.setWindowTitle("Adjust Goal")
        self.setModal(True)
        self.setFixedSize(400, 280)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        title = QLabel("Adjust Training Goal")
        title.setStyleSheet(f"font-size: 18px; font-weight: 700; color: {self._colors().text_primary};")
        layout.addWidget(title)

        if self._current_goal:
            goal_lbl = QLabel(f"Current Goal: {self._current_goal}")
            goal_lbl.setStyleSheet(f"font-size: 14px; color: {self._colors().text_secondary};")
            layout.addWidget(goal_lbl)

        progress_lbl = QLabel(f"Progress: {self._progress:.0f}%")
        progress_lbl.setStyleSheet(f"font-size: 14px; color: {self._colors().text_secondary};")
        layout.addWidget(progress_lbl)

        self._slider = QSlider(Qt.Horizontal)
        self._slider.setRange(0, 100)
        self._slider.setValue(int(self._progress))
        self._slider.setTickPosition(QSlider.TicksBelow)
        self._slider.setTickInterval(10)
        layout.addWidget(self._slider)

        self._value_label = QLabel(f"Target: {int(self._progress)}%")
        self._value_label.setStyleSheet(
            f"font-size: 24px; font-weight: 800; color: {self._colors().primary};"
        )
        self._value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._value_label)

        self._slider.valueChanged.connect(
            lambda v: self._value_label.setText(f"Target: {v}%")
        )

        layout.addStretch()

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {self._colors().text_secondary};
                border: 1px solid {self._colors().border};
                border-radius: {RADIUS.md};
                padding: 8px 20px; font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {self._colors().surface_hover};
                color: {self._colors().text_primary};
            }}
        """)
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)

        apply_btn = QPushButton("Apply")
        apply_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self._colors().primary};
                color: white;
                border: none;
                border-radius: {RADIUS.md};
                padding: 8px 20px; font-size: 13px; font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {self._colors().primary_hover};
            }}
        """)
        apply_btn.setCursor(Qt.PointingHandCursor)
        apply_btn.clicked.connect(self._on_apply)

        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(apply_btn)
        layout.addLayout(btn_layout)

    def _on_apply(self) -> None:
        self.goal_adjusted.emit(self._current_goal, float(self._slider.value()))
        self.accept()
