"""About GymOS dialog with tabs for About, Credits, License, Build Info."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from shared.version import (
    APP_DESCRIPTION,
    APP_NAME,
    APP_VERSION,
    BUILD_DATE,
    BUILD_NUMBER,
    COPYRIGHT,
    DATABASE_VERSION,
    PROTOCOL_VERSION,
    RELEASE_CHANNEL,
    SCHEMA_VERSION,
)
from ui.design_system.tokens.color import ColorScheme, color_from_scheme
from ui.design_system.tokens.radius import RadiusTokens

RADIUS = RadiusTokens()

TAB_STYLE = """
    QTabWidget::pane {
        background: {surface};
        border: none;
        border-top: 1px solid {border};
    }
    QTabBar::tab {
        background: transparent;
        color: {text_secondary};
        border: none;
        padding: 8px 16px;
        font-size: 12px;
        font-weight: 500;
    }
    QTabBar::tab:selected {
        color: {primary};
        border-bottom: 2px solid {primary};
    }
    QTabBar::tab:hover {
        color: {text_primary};
    }
"""


class AboutGymOSDialog(QDialog):
    VERSION = APP_VERSION
    BUILD = BUILD_DATE
    COPYRIGHT = COPYRIGHT

    def __init__(
        self,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._color_scheme = ColorScheme.DARK
        self._build_ui()

    def _colors(self):
        return color_from_scheme(self._color_scheme)

    def _build_ui(self) -> None:
        self.setWindowTitle(f"About {APP_NAME}")
        self.setModal(True)
        self.setMinimumSize(480, 420)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 20)
        layout.setSpacing(16)

        title = QLabel(APP_NAME)
        title_font = QFont("Inter", 24, 700)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {self._colors().text_primary};")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        tagline = QLabel(APP_DESCRIPTION)
        tagline.setStyleSheet(f"font-size: 12px; color: {self._colors().text_secondary};")
        tagline.setAlignment(Qt.AlignCenter)
        layout.addWidget(tagline)

        tabs = QTabWidget()
        tabs.setStyleSheet(
            TAB_STYLE.format(
                surface=self._colors().surface,
                border=self._colors().border,
                text_secondary=self._colors().text_secondary,
                text_primary=self._colors().text_primary,
                primary=self._colors().primary,
            )
        )

        tabs.addTab(self._tab_about(), "About")
        tabs.addTab(self._tab_credits(), "Credits")
        tabs.addTab(self._tab_license(), "License")
        tabs.addTab(self._tab_build(), "Build Info")

        layout.addWidget(tabs, stretch=1)

        close_btn = QPushButton("Close")
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self._colors().primary};
                color: white; border: none;
                border-radius: {RADIUS.md};
                padding: 8px 24px; font-size: 13px; font-weight: 600;
            }}
            QPushButton:hover {{ background-color: {self._colors().primary_hover}; }}
        """)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignCenter)

        self.setStyleSheet(f"""
            AboutGymOSDialog {{
                background-color: {self._colors().surface};
                border-radius: {RADIUS.xl};
                border: 1px solid {self._colors().border};
            }}
            QLabel {{ background: transparent; border: none; }}
        """)

    def _tab_about(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(10)

        desc = QLabel(
            "GymOS is a modular, domain-driven fitness intelligence platform "
            "that integrates workout programming, recovery tracking, "
            "predictive analytics, and adaptive decision-making."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet(
            f"font-size: 12px; color: {self._colors().text_secondary}; line-height: 1.5;"
        )
        layout.addWidget(desc)

        info = QLabel(
            f"Version: {APP_VERSION}\n"
            f"Build: {BUILD_DATE}\n"
            f"{COPYRIGHT}"
        )
        info.setStyleSheet(
            f"font-size: 12px; color: {self._colors().text_disabled}; line-height: 1.6;"
        )
        layout.addWidget(info)

        layout.addStretch()
        return w

    def _tab_credits(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(8)

        contributors = [
            ("GymOS Contributors", "Core Architecture & Development"),
            ("Open Source Community", "Libraries & Support"),
        ]
        for name, role in contributors:
            name_lbl = QLabel(name)
            name_lbl.setStyleSheet(
                f"font-size: 13px; font-weight: 600; color: {self._colors().text_primary};"
            )
            layout.addWidget(name_lbl)

            role_lbl = QLabel(role)
            role_lbl.setStyleSheet(
                f"font-size: 11px; color: {self._colors().text_disabled};"
            )
            layout.addWidget(role_lbl)
            layout.addSpacing(4)

        layout.addStretch()
        return w

    def _tab_license(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(20, 16, 20, 16)

        license_text = (
            f"MIT License\n\n{COPYRIGHT}\n\n"
            "Permission is hereby granted, free of charge, to any person "
            "obtaining a copy of this software and associated documentation "
            "files (the \"Software\"), to deal in the Software without "
            "restriction, including without limitation the rights to use, "
            "copy, modify, merge, publish, distribute, sublicense, and/or "
            "sell copies of the Software, and to permit persons to whom "
            "the Software is furnished to do so, subject to the following "
            "conditions:\n\n"
            "The above copyright notice and this permission notice shall "
            "be included in all copies or substantial portions of the "
            "Software.\n\n"
            "THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY "
            "KIND, EXPRESS OR IMPLIED, including but not limited to the "
            "warranties of MERCHANTABILITY, FITNESS FOR A PARTICULAR "
            "PURPOSE AND NONINFRINGEMENT."
        )

        text = QPlainTextEdit()
        text.setPlainText(license_text)
        text.setReadOnly(True)
        text.setStyleSheet(f"""
            QPlainTextEdit {{
                background-color: {self._colors().background};
                color: {self._colors().text_secondary};
                border: 1px solid {self._colors().border};
                border-radius: 8px;
                padding: 12px;
                font-family: "JetBrains Mono", monospace;
                font-size: 10px;
            }}
        """)
        layout.addWidget(text)
        return w

    def _tab_build(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(8)

        fields = [
            ("Application Version", APP_VERSION),
            ("Build Number", str(BUILD_NUMBER)),
            ("Build Date", BUILD_DATE),
            ("Release Channel", RELEASE_CHANNEL),
            ("Schema Version", str(SCHEMA_VERSION)),
            ("Database Version", str(DATABASE_VERSION)),
            ("Protocol Version", PROTOCOL_VERSION),
            ("Python", __import__("sys").version.split()[0]),
        ]

        for label, value in fields:
            row = QWidget()
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(8)

            lbl = QLabel(label)
            lbl.setStyleSheet(
                f"font-size: 12px; font-weight: 500; color: {self._colors().text_primary};"
            )
            val = QLabel(value)
            val.setStyleSheet(
                f"font-size: 12px; color: {self._colors().text_secondary};"
            )
            val.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

            row_layout.addWidget(lbl, stretch=1)
            row_layout.addWidget(val)

            layout.addWidget(row)

        layout.addStretch()
        return w
