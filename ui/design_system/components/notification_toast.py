from __future__ import annotations

from enum import Enum

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from ui.design_system.tokens.color import ColorScheme, color_from_scheme
from ui.design_system.tokens.elevation import ElevationTokens
from ui.design_system.tokens.radius import RadiusTokens

RADIUS = RadiusTokens()
ELEVATION = ElevationTokens()


class ToastType(Enum):
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class NotificationToast(QFrame):
    dismissed = Signal()

    def __init__(
        self,
        message: str = "",
        toast_type: ToastType = ToastType.INFO,
        title: str = "",
        duration_ms: int = 4000,
        dismissable: bool = True,
        color_scheme: ColorScheme = ColorScheme.DARK,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._toast_type = toast_type
        self._color_scheme = color_scheme
        self._build_ui(title, message, dismissable)

        if duration_ms > 0:
            QTimer.singleShot(duration_ms, self._auto_dismiss)

    def _colors(self):
        return color_from_scheme(self._color_scheme)

    def _toast_colors(self):
        colors = self._colors()
        mapping = {
            ToastType.SUCCESS: (colors.success, colors.success_surface, colors.success_border),
            ToastType.ERROR: (colors.error, colors.error_surface, colors.error_border),
            ToastType.WARNING: (colors.warning, colors.warning_surface, colors.warning_border),
            ToastType.INFO: (colors.info, colors.info_surface, colors.info_border),
        }
        return mapping.get(self._toast_type, (colors.info, colors.info_surface, colors.info_border))

    def _build_ui(self, title: str, message: str, dismissable: bool) -> None:
        fg, bg, border = self._toast_colors()
        self.setStyleSheet(f"""
            NotificationToast {{
                background-color: {bg};
                border: 1px solid {border};
                border-radius: {RADIUS.lg};
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(10)

        indicator = QFrame()
        indicator.setFixedSize(4, 32)
        indicator.setStyleSheet(
            f"background-color: {fg}; border-radius: 2px; border: none;"
        )
        layout.addWidget(indicator)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)

        if title:
            t = QLabel(title)
            t.setStyleSheet(
                f"color: {fg}; font-size: 13px; font-weight: 600; "
                f"background: transparent; border: none;"
            )
            text_layout.addWidget(t)

        m = QLabel(message)
        m.setStyleSheet(
            f"color: {self._colors().text_secondary}; font-size: 12px; "
            f"background: transparent; border: none;"
        )
        m.setWordWrap(True)
        text_layout.addWidget(m)

        layout.addLayout(text_layout, 1)

        if dismissable:
            close = QPushButton("\u00D7")
            close.setFixedSize(20, 20)
            close.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {self._colors().text_disabled};
                    border: none;
                    font-size: 16px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    color: {self._colors().text_primary};
                }}
            """)
            close.setCursor(Qt.PointingHandCursor)
            close.clicked.connect(self._dismiss)
            layout.addWidget(close)

    def _auto_dismiss(self) -> None:
        self._dismiss()

    def _dismiss(self) -> None:
        self.dismissed.emit()
        self.deleteLater()
