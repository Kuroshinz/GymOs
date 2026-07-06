from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ui.command_center.theme import NAV_ITEMS, C, Font


class SidebarButton(QPushButton):
    def __init__(self, text: str, icon: str = "", active: bool = False,
                 parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._active = active
        icon_text = f"{icon} " if icon else ""
        self.setText(f"{icon_text}{text}")
        self.setFixedHeight(44)
        self.setCursor(Qt.PointingHandCursor)
        self._update_style()

    def set_active(self, active: bool) -> None:
        self._active = active
        self._update_style()

    def _update_style(self) -> None:
        bg = C.SIDEBAR_ACTIVE if self._active else "transparent"
        color = C.ACCENT if self._active else C.TEXT_SECONDARY
        weight = "600" if self._active else "500"
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg};
                color: {color};
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                text-align: left;
                font-size: 13px;
                font-weight: {weight};
            }}
            QPushButton:hover {{
                background-color: {C.SIDEBAR_HOVER};
                color: {C.TEXT_PRIMARY};
            }}
        """)


class Sidebar(QFrame):
    page_changed = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(220)
        self._buttons: dict[str, SidebarButton] = {}
        self._build_ui()

    def _build_ui(self) -> None:
        self.setStyleSheet(f"""
            QFrame#sidebar {{
                background-color: {C.SIDEBAR_BG};
                border-right: 1px solid {C.BORDER};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 20, 12, 20)
        layout.setSpacing(4)

        logo = QLabel("GYMOS")
        logo.setStyleSheet(f"color: {C.ACCENT}; font-size: 20px; font-weight: 800; letter-spacing: 2px;")
        logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo)
        layout.addSpacing(20)

        for page_id, section, icon, desc in NAV_ITEMS:
            sec_label = QLabel(section)
            sec_label.setStyleSheet(Font.LABEL)
            sec_label.setContentsMargins(12, 8, 0, 2)
            layout.addWidget(sec_label)

            btn = SidebarButton(page_id.replace("_", " ").title(), icon=icon)
            btn.clicked.connect(lambda checked=False, pid=page_id: self._on_page_clicked(pid))
            self._buttons[page_id] = btn
            layout.addWidget(btn)

        layout.addStretch()

        version = QLabel("v1.0.0")
        version.setStyleSheet(Font.CAPTION)
        version.setAlignment(Qt.AlignCenter)
        layout.addWidget(version)

    def _on_page_clicked(self, page_id: str) -> None:
        for pid, btn in self._buttons.items():
            btn.set_active(pid == page_id)
        self.page_changed.emit(page_id)

    def set_active(self, page_id: str) -> None:
        for pid, btn in self._buttons.items():
            btn.set_active(pid == page_id)
