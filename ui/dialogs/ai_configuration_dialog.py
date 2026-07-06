from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFormLayout,
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


class AIConfigurationDialog(QDialog):
    config_applied = Signal(dict)

    def __init__(
        self,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._color_scheme = ColorScheme.DARK
        self._build_ui()
        self._apply_style()

    def _colors(self):
        return color_from_scheme(self._color_scheme)

    def _apply_style(self) -> None:
        colors = self._colors()
        self.setStyleSheet(f"""
            AIConfigurationDialog {{
                background-color: {colors.surface};
                border-radius: {RADIUS.xl};
                border: 1px solid {colors.border};
            }}
            QLabel {{ background: transparent; border: none; }}
            QComboBox, QCheckBox {{
                background-color: {colors.background};
                color: {colors.text_primary};
                border: 1px solid {colors.border};
                border-radius: {RADIUS.md};
                padding: 4px 8px;
                font-size: 13px;
            }}
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
        self.setWindowTitle("AI Configuration")
        self.setModal(True)
        self.setFixedSize(420, 360)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        title = QLabel("AI Assistant Configuration")
        title.setStyleSheet(f"font-size: 18px; font-weight: 700; color: {self._colors().text_primary};")
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(12)

        self._model_combo = QComboBox()
        self._model_combo.addItems(["Default", "Conservative", "Balanced", "Aggressive"])
        form.addRow("Reasoning Mode:", self._model_combo)

        self._detail_slider = QSlider(Qt.Horizontal)
        self._detail_slider.setRange(1, 10)
        self._detail_slider.setValue(5)
        form.addRow("Detail Level:", self._detail_slider)

        self._auto_analyze = QCheckBox("Auto-analyze new data")
        self._auto_analyze.setChecked(True)
        form.addRow("", self._auto_analyze)

        self._show_confidence = QCheckBox("Show confidence scores")
        self._show_confidence.setChecked(True)
        form.addRow("", self._show_confidence)

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
        config = {
            "model": self._model_combo.currentText(),
            "detail_level": self._detail_slider.value(),
            "auto_analyze": self._auto_analyze.isChecked(),
            "show_confidence": self._show_confidence.isChecked(),
        }
        self.config_applied.emit(config)
        self.accept()
