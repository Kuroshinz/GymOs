from __future__ import annotations

from datetime import date

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDateEdit,
    QDialog,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ui.design_system.tokens.color import ColorScheme, color_from_scheme
from ui.design_system.tokens.radius import RadiusTokens
from ui.design_system.tokens.spacing import SpacingTokens

RADIUS = RadiusTokens()
SPACE = SpacingTokens()


class LogWeightDialog(QDialog):
    weight_logged = Signal(float, str, str)

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
            LogWeightDialog {{
                background-color: {colors.surface};
                border-radius: {RADIUS.xl};
                border: 1px solid {colors.border};
            }}
            QLabel {{
                background: transparent; border: none;
            }}
            QDateEdit, QDoubleSpinBox, QTextEdit {{
                background-color: {colors.background};
                color: {colors.text_primary};
                border: 1px solid {colors.border};
                border-radius: {RADIUS.md};
                padding: 6px 10px;
                font-size: 13px;
            }}
            QDateEdit:focus, QDoubleSpinBox:focus, QTextEdit:focus {{
                border-color: {colors.primary};
            }}
        """)

    def _build_ui(self) -> None:
        self.setWindowTitle("Log Body Weight")
        self.setModal(True)
        self.setFixedSize(380, 320)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        title = QLabel("Log Body Weight")
        title.setStyleSheet(f"font-size: 18px; font-weight: 700; color: {self._colors().text_primary};")
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(12)

        self._date_input = QDateEdit()
        self._date_input.setCalendarPopup(True)
        self._date_input.setDate(date.today())
        form.addRow("Date:", self._date_input)

        self._weight_input = QDoubleSpinBox()
        self._weight_input.setRange(30.0, 300.0)
        self._weight_input.setDecimals(1)
        self._weight_input.setSuffix(" kg")
        self._weight_input.setValue(self._current_weight)
        form.addRow("Weight:", self._weight_input)

        self._notes_input = QTextEdit()
        self._notes_input.setPlaceholderText("Optional notes...")
        self._notes_input.setMaximumHeight(80)
        form.addRow("Notes:", self._notes_input)

        layout.addLayout(form)
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

        save_btn = QPushButton("Save Weight")
        save_btn.setStyleSheet(f"""
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
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.clicked.connect(self._on_save)

        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

    def _on_save(self) -> None:
        w = self._weight_input.value()
        d = self._date_input.date().toString("yyyy-MM-dd")
        n = self._notes_input.toPlainText().strip()
        self.weight_logged.emit(w, d, n)
        self.accept()
