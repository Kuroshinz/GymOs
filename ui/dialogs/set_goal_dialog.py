"""Set Goal Dialog — allows the user to set their target body weight and calorie surplus.

Emits ``goal_set(target_weight_kg, target_calorie_surplus)`` on save.
Follows the same design pattern as LogWeightDialog.
"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from ui.design_system.tokens.color import ColorScheme, color_from_scheme
from ui.design_system.tokens.radius import RadiusTokens
from ui.design_system.tokens.spacing import SpacingTokens

RADIUS = RadiusTokens()
SPACE = SpacingTokens()


class SetGoalDialog(QDialog):
    """Modal dialog to set target body weight and daily calorie surplus.

    Signals:
        goal_set(target_weight_kg, target_calorie_surplus): Emitted
            when the user confirms the new goal values.
    """

    goal_set = Signal(float, int)

    def __init__(
        self,
        current_weight: float = 70.0,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._current_weight = current_weight
        self._color_scheme = ColorScheme.DARK
        self._build_ui()
        self._apply_style()

    def _colors(self):
        return color_from_scheme(self._color_scheme)

    def _apply_style(self) -> None:
        colors = self._colors()
        self.setStyleSheet(f"""
            SetGoalDialog {{
                background-color: {colors.surface};
                border-radius: {RADIUS.xl};
                border: 1px solid {colors.border};
            }}
            QLabel {{
                background: transparent; border: none;
            }}
            QDoubleSpinBox, QSpinBox {{
                background-color: {colors.background};
                color: {colors.text_primary};
                border: 1px solid {colors.border};
                border-radius: {RADIUS.md};
                padding: 6px 10px;
                font-size: 13px;
            }}
            QDoubleSpinBox:focus, QSpinBox:focus {{
                border-color: {colors.primary};
            }}
        """)

    def _build_ui(self) -> None:
        colors = self._colors()
        self.setWindowTitle("Set Your Goal")
        self.setModal(True)
        self.setFixedSize(380, 300)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        # Title
        title = QLabel("Set Your Goal")
        title.setStyleSheet(
            f"font-size: 18px; font-weight: 700; color: {colors.text_primary};"
        )
        layout.addWidget(title)

        subtitle = QLabel(
            "Set a target body weight and daily calorie surplus "
            "to track your lean bulk progress."
        )
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet(
            f"font-size: 13px; color: {colors.text_secondary}; "
            f"padding-bottom: {SPACE.s1};"
        )
        layout.addWidget(subtitle)

        # Form
        form = QFormLayout()
        form.setSpacing(12)

        self._weight_input = QDoubleSpinBox()
        self._weight_input.setRange(30.0, 300.0)
        self._weight_input.setDecimals(1)
        self._weight_input.setSuffix(" kg")
        self._weight_input.setValue(self._current_weight)
        self._weight_input.setToolTip("Your target body weight for this bulk.")
        form.addRow("Target Weight:", self._weight_input)

        self._surplus_input = QSpinBox()
        self._surplus_input.setRange(0, 1000)
        self._surplus_input.setSuffix(" kcal")
        self._surplus_input.setValue(300)
        self._surplus_input.setSingleStep(50)
        self._surplus_input.setToolTip(
            "Daily calorie surplus (300-500 is optimal for lean bulk)."
        )
        form.addRow("Daily Surplus:", self._surplus_input)

        layout.addLayout(form)

        # Optional hint
        hint = QLabel(
            "Tip: A surplus of 300-500 kcal with adequate protein "
            "(~1.6-2.2 g/kg) is ideal for lean bulk."
        )
        hint.setWordWrap(True)
        hint.setStyleSheet(
            f"font-size: 11px; color: {colors.text_disabled}; "
            f"padding-top: {SPACE.s1};"
        )
        layout.addWidget(hint)

        layout.addStretch()

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {colors.text_secondary};
                border: 1px solid {colors.border};
                border-radius: {RADIUS.md};
                padding: 8px 20px; font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {colors.surface_hover};
                color: {colors.text_primary};
            }}
        """)
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)

        save_btn = QPushButton("Set Goal")
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {colors.primary};
                color: white;
                border: none;
                border-radius: {RADIUS.md};
                padding: 8px 20px; font-size: 13px; font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {colors.primary_hover};
            }}
        """)
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.clicked.connect(self._on_save)

        btn_layout.addWidget(cancel_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

    def _on_save(self) -> None:
        """Emit goal_set signal and close dialog."""
        target_weight = self._weight_input.value()
        target_surplus = self._surplus_input.value()
        self.goal_set.emit(target_weight, target_surplus)
        self.accept()
