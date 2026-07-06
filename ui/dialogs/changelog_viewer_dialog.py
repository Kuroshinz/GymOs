"""Changelog viewer dialog — displays CHANGELOG.md."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from shared.version import APP_NAME
from ui.design_system.tokens.color import ColorScheme, color_from_scheme

_CHANGELOG_PATH = Path(__file__).parent.parent.parent / "docs" / "CHANGELOG.md"


class ChangelogViewerDialog(QDialog):
    """Displays the project changelog."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._color_scheme = ColorScheme.DARK
        self._changelog_content = self._load_changelog()
        self._build_ui()

    def _colors(self):
        return color_from_scheme(self._color_scheme)

    def _load_changelog(self) -> str:
        try:
            if _CHANGELOG_PATH.exists():
                return _CHANGELOG_PATH.read_text(encoding="utf-8")
        except Exception:
            pass
        return "No changelog available."

    def _build_ui(self) -> None:
        self.setWindowTitle(f"{APP_NAME} Changelog")
        self.setModal(True)
        self.setMinimumSize(560, 420)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        title = QLabel("Changelog")
        title.setStyleSheet(
            f"font-size: 18px; font-weight: 700; color: {self._colors().text_primary};"
        )
        layout.addWidget(title)

        text_edit = QPlainTextEdit()
        text_edit.setPlainText(self._changelog_content)
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
            ChangelogViewerDialog {{
                background-color: {self._colors().surface};
                border-radius: 16px;
            }}
        """)
