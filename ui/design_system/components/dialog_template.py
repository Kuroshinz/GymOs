from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ui.design_system.tokens.color import ColorScheme, color_from_scheme
from ui.design_system.tokens.elevation import ElevationTokens
from ui.design_system.tokens.radius import RadiusTokens
from ui.design_system.tokens.spacing import SpacingTokens

RADIUS = RadiusTokens()
SPACE = SpacingTokens()
ELEVATION = ElevationTokens()


class DialogTemplate(QDialog):
    accepted = Signal()
    rejected = Signal()

    def __init__(
        self,
        title: str = "",
        message: str = "",
        confirm_text: str = "Confirm",
        cancel_text: str = "Cancel",
        show_cancel: bool = True,
        destructive: bool = False,
        color_scheme: ColorScheme = ColorScheme.DARK,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._color_scheme = color_scheme
        self._destructive = destructive
        self._result: bool = False
        if title:
            self.setAccessibleName(f"Dialog: {title}")
        if message:
            self.setAccessibleDescription(message)
        self._build_ui(title, message, confirm_text, cancel_text, show_cancel)

    def _colors(self):
        return color_from_scheme(self._color_scheme)

    def _build_ui(self, title: str, message: str, confirm_text: str, cancel_text: str, show_cancel: bool) -> None:
        colors = self._colors()
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setModal(True)
        self.setStyleSheet(f"""
            DialogTemplate {{
                background-color: {colors.surface};
                border-radius: {RADIUS.xl};
                border: 1px solid {colors.border};
            }}
        """)
        self.setFixedWidth(420)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        if title:
            title_label = QLabel(title)
            title_label.setStyleSheet(
                f"color: {colors.text_primary}; font-size: 16px; font-weight: 700; "
                f"background: transparent; border: none;"
            )
            layout.addWidget(title_label)

        if message:
            msg_label = QLabel(message)
            msg_label.setStyleSheet(
                f"color: {colors.text_secondary}; font-size: 13px; line-height: 1.5; "
                f"background: transparent; border: none;"
            )
            msg_label.setWordWrap(True)
            layout.addWidget(msg_label)

        self._content_area = QVBoxLayout()
        self._content_area.setSpacing(8)
        layout.addLayout(self._content_area)

        layout.addStretch()

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)

        if show_cancel:
            cancel_btn = QPushButton(cancel_text)
            cancel_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {colors.text_secondary};
                    border: 1px solid {colors.border};
                    border-radius: {RADIUS.md};
                    padding: 8px 20px;
                    font-size: 13px;
                    font-weight: 500;
                }}
                QPushButton:hover {{
                    background-color: {colors.surface_hover};
                    color: {colors.text_primary};
                }}
            """)
            cancel_btn.setCursor(Qt.PointingHandCursor)
            cancel_btn.clicked.connect(self._reject)
            btn_layout.addWidget(cancel_btn)

        confirm_color = colors.error if self._destructive else colors.primary
        confirm_hover = colors.error_hover if self._destructive else colors.primary_hover
        confirm_btn = QPushButton(confirm_text)
        confirm_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {confirm_color};
                color: {colors.text_inverse};
                border: none;
                border-radius: {RADIUS.md};
                padding: 8px 20px;
                font-size: 13px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {confirm_hover};
            }}
        """)
        confirm_btn.setCursor(Qt.PointingHandCursor)
        confirm_btn.clicked.connect(self._accept)
        btn_layout.addWidget(confirm_btn)

        layout.addLayout(btn_layout)

    def _accept(self) -> None:
        self._result = True
        self.accepted.emit()
        self.accept()

    def _reject(self) -> None:
        self._result = False
        self.rejected.emit()
        self.reject()

    def add_content(self, widget: QWidget) -> None:
        self._content_area.addWidget(widget)

    def result(self) -> bool:
        return self._result

    @staticmethod
    def confirm(
        parent: QWidget,
        title: str,
        message: str,
        confirm_text: str = "Confirm",
        destructive: bool = False,
    ) -> bool:
        dlg = DialogTemplate(
            title=title,
            message=message,
            confirm_text=confirm_text,
            destructive=destructive,
            parent=parent,
        )
        dlg.exec()
        return dlg._result
