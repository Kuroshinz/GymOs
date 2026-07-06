from __future__ import annotations

import logging

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ui.design_system.tokens.color import ColorScheme, color_from_scheme
from ui.design_system.tokens.radius import RadiusTokens

RADIUS = RadiusTokens()


class SystemLogViewerDialog(QDialog):
    def __init__(
        self,
        log_lines: list[str] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._log_lines = log_lines or []
        self._color_scheme = ColorScheme.DARK
        self._build_ui()
        self._apply_style()
        self._auto_refresh_timer = QTimer()
        self._auto_refresh_timer.setInterval(5000)
        self._auto_refresh_timer.timeout.connect(self._refresh_logs)

    def _colors(self):
        return color_from_scheme(self._color_scheme)

    def _apply_style(self) -> None:
        colors = self._colors()
        self.setStyleSheet(f"""
            SystemLogViewerDialog {{
                background-color: {colors.surface};
                border-radius: {RADIUS.xl};
                border: 1px solid {colors.border};
            }}
            QLabel {{ background: transparent; border: none; }}
            QPlainTextEdit {{
                background-color: {colors.background};
                color: {colors.text_primary};
                border: 1px solid {colors.border};
                border-radius: {RADIUS.md};
                padding: 8px;
                font-family: "Cascadia Code", "Fira Code", monospace;
                font-size: 12px;
            }}
            QComboBox {{
                background-color: {colors.background};
                color: {colors.text_primary};
                border: 1px solid {colors.border};
                border-radius: {RADIUS.md};
                padding: 4px 8px;
                font-size: 12px;
            }}
        """)

    def _build_ui(self) -> None:
        self.setWindowTitle("System Logs")
        self.setModal(True)
        self.setFixedSize(640, 480)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        header = QHBoxLayout()
        title = QLabel("System Log Viewer")
        title.setStyleSheet(f"font-size: 18px; font-weight: 700; color: {self._colors().text_primary};")
        header.addWidget(title)
        header.addStretch()

        self._level_filter = QComboBox()
        self._level_filter.addItems(["ALL", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        self._level_filter.setCurrentText("INFO")
        self._level_filter.currentTextChanged.connect(self._filter_logs)
        header.addWidget(self._level_filter)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {self._colors().text_secondary};
                border: 1px solid {self._colors().border};
                border-radius: {RADIUS.md};
                padding: 6px 14px; font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {self._colors().surface_hover};
                color: {self._colors().text_primary};
            }}
        """)
        refresh_btn.setCursor(Qt.PointingHandCursor)
        refresh_btn.clicked.connect(self._refresh_logs)
        header.addWidget(refresh_btn)

        layout.addLayout(header)

        self._log_display = QPlainTextEdit()
        self._log_display.setReadOnly(True)
        self._log_display.setMaximumBlockCount(10000)
        layout.addWidget(self._log_display, 1)

        btn_layout = QHBoxLayout()
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet(f"""
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
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self.accept)
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

        self._populate_logs()

    def _populate_logs(self) -> None:
        import io
        handler = logging.root.handlers
        log_text = ""
        for h in handler:
            if hasattr(h, "stream") and isinstance(h.stream, io.StringIO):
                log_text = h.stream.getvalue()
                break
        if not log_text:
            log_text = "\n".join(self._log_lines[-200:])
        self._log_display.setPlainText(log_text)
        self._log_display.moveCursor(
            self._log_display.textCursor().End
        )

    def _filter_logs(self, level: str) -> None:
        self._populate_logs()

    def _refresh_logs(self) -> None:
        self._populate_logs()

    def start_auto_refresh(self) -> None:
        self._auto_refresh_timer.start()

    def stop_auto_refresh(self) -> None:
        self._auto_refresh_timer.stop()
