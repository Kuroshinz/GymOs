"""Credits dialog — contributors and acknowledgments."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ui.design_system.tokens.color import ColorScheme, color_from_scheme

CONTRIBUTORS = [
    ("GymOS Contributors", "Core Architecture & Development"),
    ("Open Source Community", "Libraries & Support"),
]


class CreditsDialog(QDialog):
    """Displays application credits and contributors."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._color_scheme = ColorScheme.DARK
        self._build_ui()

    def _colors(self):
        return color_from_scheme(self._color_scheme)

    def _build_ui(self) -> None:
        self.setWindowTitle("Credits")
        self.setModal(True)
        self.setFixedSize(400, 340)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 24)
        layout.setSpacing(16)

        title = QLabel("Credits")
        title.setStyleSheet(
            f"font-size: 20px; font-weight: 700; color: {self._colors().text_primary};"
        )
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        desc = QLabel(
            "GymOS is built with passion by the following contributors, "
            "and powered by open-source software."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet(f"font-size: 12px; color: {self._colors().text_secondary}; line-height: 1.5;")
        desc.setAlignment(Qt.AlignCenter)
        layout.addWidget(desc)

        layout.addSpacing(8)

        for name, role in CONTRIBUTORS:
            name_lbl = QLabel(name)
            name_lbl.setStyleSheet(
                f"font-size: 14px; font-weight: 600; color: {self._colors().text_primary};"
            )
            layout.addWidget(name_lbl)

            role_lbl = QLabel(role)
            role_lbl.setStyleSheet(
                f"font-size: 11px; color: {self._colors().text_disabled};"
            )
            layout.addWidget(role_lbl)

            layout.addSpacing(4)

        layout.addStretch()

        close_btn = QPushButton("Close")
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self._colors().primary};
                color: white; border: none; border-radius: 8px;
                padding: 8px 24px; font-size: 13px; font-weight: 600;
            }}
            QPushButton:hover {{ background-color: {self._colors().primary_hover}; }}
        """)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignCenter)

        self.setStyleSheet(f"""
            CreditsDialog {{
                background-color: {self._colors().surface};
                border-radius: 16px;
            }}
        """)
