from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QWidget,
)

from ui.design_system.tokens.color import ColorScheme, color_from_scheme
from ui.design_system.tokens.radius import RadiusTokens
from ui.design_system.tokens.spacing import SpacingTokens
from ui.design_system.tokens.typography import font_style

RADIUS = RadiusTokens()
SPACE = SpacingTokens()


class ShellHeader(QFrame):
    palette_triggered = Signal()
    notifications_triggered = Signal()
    menu_triggered = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._build_ui()
        self.set_page_title("Dashboard")

    def _get_colors(self):
        return color_from_scheme(ColorScheme.DARK)

    def _build_ui(self) -> None:
        c = self._get_colors()

        self.setStyleSheet(f"""
            ShellHeader {{
                background-color: transparent;
                border: none;
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(32, 20, 32, 8)
        layout.setSpacing(12)

        title_layout = QHBoxLayout()
        title_layout.setSpacing(8)

        self._breadcrumb = QLabel()
        self._breadcrumb.setStyleSheet(
            f"color: {c.text_disabled}; {font_style('caption')}; background: transparent; border: none;"
        )
        self._breadcrumb.setVisible(False)
        title_layout.addWidget(self._breadcrumb)

        self._title = QLabel("Dashboard")
        self._title.setStyleSheet(
            f"color: {c.text_primary}; {font_style('hero')}; background: transparent; border: none;"
        )
        title_layout.addWidget(self._title)

        layout.addLayout(title_layout, 1)

        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(6)

        cmd_k_btn = QPushButton("\u2318K")
        cmd_k_btn.setFixedSize(40, 32)
        cmd_k_btn.setAccessibleName("Open command palette")
        cmd_k_btn.setCursor(Qt.PointingHandCursor)
        cmd_k_btn.setToolTip("Command palette (Ctrl+K)")
        cmd_k_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {c.surface_hover}; color: {c.text_secondary};
                border: 1px solid {c.border}; border-radius: {RADIUS.sm};
                {font_style('caption', weight='semibold')}
            }}
            QPushButton:hover {{
                background-color: {c.surface}; color: {c.text_primary};
                border-color: {c.border_hover};
            }}
            QPushButton:focus {{
                border: 2px solid {c.focus_ring};
            }}
        """)
        cmd_k_btn.clicked.connect(self.palette_triggered.emit)
        actions_layout.addWidget(cmd_k_btn)

        notify_btn = QPushButton("\U0001F514")
        notify_btn.setFixedSize(36, 32)
        notify_btn.setAccessibleName("Open notifications")
        notify_btn.setCursor(Qt.PointingHandCursor)
        notify_btn.setToolTip("Notifications")
        notify_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent; color: {c.text_secondary};
                border: 1px solid transparent; border-radius: {RADIUS.sm};
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {c.surface_hover}; color: {c.text_primary};
                border-color: {c.border};
            }}
            QPushButton:focus {{
                border: 2px solid {c.focus_ring};
            }}
        """)
        notify_btn.clicked.connect(self.notifications_triggered.emit)
        actions_layout.addWidget(notify_btn)

        layout.addLayout(actions_layout)

    def set_page_title(self, title: str) -> None:
        self._title.setText(title)

    def set_breadcrumb(self, path: str) -> None:
        if path:
            self._breadcrumb.setText(path)
            self._breadcrumb.setVisible(True)
        else:
            self._breadcrumb.setVisible(False)
