from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass

from PySide6.QtCore import QObject, Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ui.command_center.theme import C, Font

logger = logging.getLogger("experience.empty_state")


@dataclass
class EmptyStateConfig:
    container_id: str
    icon: str = "📭"
    title: str = "No Data"
    description: str = "Nothing to display yet."
    action_label: str = ""
    action_callback: Callable[[], None] | None = None


class EmptyStateWidget(QFrame):
    action_clicked = Signal()

    def __init__(self, config: EmptyStateConfig, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._config = config
        self._build_ui()

    def _build_ui(self) -> None:
        self.setStyleSheet(f"""
            EmptyStateWidget {{
                background-color: {C.CARD_BG};
                border-radius: 12px;
                border: 1px dashed {C.BORDER};
            }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(12)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon_label = QLabel(self._config.icon)
        icon_label.setStyleSheet("font-size: 48px;")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)

        title = QLabel(self._config.title)
        title.setStyleSheet(Font.SUBHEADING)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        desc = QLabel(self._config.description)
        desc.setStyleSheet(Font.MUTED)
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setWordWrap(True)
        layout.addWidget(desc)

        if self._config.action_label and self._config.action_callback:
            btn = QPushButton(self._config.action_label)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {C.ACCENT};
                    color: #FFFFFF;
                    border: none;
                    border-radius: 8px;
                    padding: 10px 24px;
                    font-size: 14px;
                    font-weight: 600;
                }}
                QPushButton:hover {{
                    background-color: {C.ACCENT_HOVER};
                }}
            """)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(self._config.action_callback)
            btn.clicked.connect(self.action_clicked.emit)
            layout.addWidget(btn, 0, Qt.AlignmentFlag.AlignCenter)

    def update_config(self, config: EmptyStateConfig) -> None:
        self._config = config
        for i in range(self.layout().count()):
            item = self.layout().itemAt(i)
            if item and item.widget():
                item.widget().deleteLater()
        self._build_ui()


class EmptyStateManager(QObject):
    shown = Signal(str)
    hidden = Signal(str)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._states: dict[str, EmptyStateConfig] = {}
        self._shown: dict[str, EmptyStateWidget] = {}

    def register(self, config: EmptyStateConfig) -> None:
        self._states[config.container_id] = config

    def unregister(self, container_id: str) -> None:
        self._states.pop(container_id, None)
        self.hide(container_id)

    def show(self, container_id: str, parent: QWidget) -> EmptyStateWidget | None:
        self.hide(container_id)
        config = self._states.get(container_id)
        if not config:
            logger.warning("No empty state config for '%s'", container_id)
            return None
        widget = EmptyStateWidget(config, parent)
        if parent.layout():
            parent.layout().addWidget(widget)
        self._shown[container_id] = widget
        self.shown.emit(container_id)
        return widget

    def hide(self, container_id: str) -> None:
        widget = self._shown.pop(container_id, None)
        if widget:
            widget.setParent(None)
            widget.deleteLater()
            self.hidden.emit(container_id)

    def is_showing(self, container_id: str) -> bool:
        return container_id in self._shown

    def hide_all(self) -> None:
        for cid in list(self._shown.keys()):
            self.hide(cid)
