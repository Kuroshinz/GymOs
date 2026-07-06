"""License viewer dialog — displays the MIT license."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from shared.version import APP_NAME, COPYRIGHT
from ui.design_system.tokens.color import ColorScheme, color_from_scheme

LICENSE_TEXT = f"""MIT License

{COPYRIGHT}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE."""


class LicenseViewerDialog(QDialog):
    """Displays the software license."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._color_scheme = ColorScheme.DARK
        self._build_ui()

    def _colors(self):
        return color_from_scheme(self._color_scheme)

    def _build_ui(self) -> None:
        self.setWindowTitle(f"{APP_NAME} License")
        self.setModal(True)
        self.setMinimumSize(480, 360)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        title = QLabel("License")
        title.setStyleSheet(
            f"font-size: 18px; font-weight: 700; color: {self._colors().text_primary};"
        )
        layout.addWidget(title)

        text_edit = QPlainTextEdit()
        text_edit.setPlainText(LICENSE_TEXT)
        text_edit.setReadOnly(True)
        text_edit.setStyleSheet(f"""
            QPlainTextEdit {{
                background-color: {self._colors().background};
                color: {self._colors().text_secondary};
                border: 1px solid {self._colors().border};
                border-radius: 8px;
                padding: 16px;
                font-family: "JetBrains Mono", monospace;
                font-size: 11px;
            }}
        """)
        layout.addWidget(text_edit, stretch=1)

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
            LicenseViewerDialog {{
                background-color: {self._colors().surface};
                border-radius: 16px;
            }}
        """)
