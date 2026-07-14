from __future__ import annotations

from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QRect, QEasingCurve
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from ui.design_system.tokens.color import ColorScheme, color_from_scheme
from ui.design_system.tokens.layout import LayoutTokens
from ui.design_system.tokens.radius import RadiusTokens, px_from_token
from ui.design_system.tokens.spacing import SpacingTokens

RADIUS = RadiusTokens()
SPACE = SpacingTokens()
LAYOUT = LayoutTokens()

NAV_SECTIONS: list[tuple[str, list[tuple[str, str, str]]]] = [
    ("Training", [
        ("dashboard", "Dashboard", "\u2302"),
        ("workout", "Workout", "\u25B6"),
        ("progress", "Progress", "\u2191"),
    ]),
    ("Data", [
        ("recovery", "Recovery", "\u2665"),
        ("predictions", "Predictions", "\u2606"),
        ("prs", "Records", "\u2605"),
    ]),
    ("System", [
        ("settings", "Settings", "\u2699"),
    ]),
]

COLLAPSED_WIDTH = 56
EXPANDED_WIDTH = px_from_token(LAYOUT.sidebar_width)


class ShellSidebarButton(QPushButton):
    def __init__(
        self,
        page_id: str,
        label: str,
        icon: str,
        expanded: bool = True,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._page_id = page_id
        self._label = label
        self._icon = icon
        self._expanded = expanded
        self._active = False
        self.setFixedHeight(44)
        self.setCursor(Qt.PointingHandCursor)
        self.setFocusPolicy(Qt.StrongFocus)
        self._update_content()
        self._update_style()

    def set_expanded(self, expanded: bool) -> None:
        self._expanded = expanded
        self._update_content()
        self._update_style()

    def set_active(self, active: bool) -> None:
        self._active = active
        self._update_style()

    def _update_content(self) -> None:
        if self._expanded:
            self.setText(f"{self._icon}  {self._label}")
            self.setToolTip("")
        else:
            self.setText(self._icon)
            self.setToolTip(self._label)

    def _get_colors(self):
        return color_from_scheme(ColorScheme.DARK)

    def _update_style(self) -> None:
        c = self._get_colors()
        bg = "transparent"
        color = c.primary if self._active else c.text_secondary
        weight = "600" if self._active else "500"

        if self._expanded:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {bg};
                    color: {color};
                    border: none;
                    border-radius: {RADIUS.md};
                    padding: 8px 14px;
                    text-align: left;
                    font-size: 14px;
                    font-weight: {weight};
                }}
                QPushButton:hover {{
                    background-color: {c.surface_hover};
                    color: {c.text_primary};
                }}
                QPushButton:focus {{
                    border: 2px solid {c.focus_ring};
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {bg};
                    color: {color};
                    border: none;
                    border-radius: {RADIUS.md};
                    padding: 0px;
                    text-align: center;
                    font-size: 18px;
                    font-weight: {weight};
                }}
                QPushButton:hover {{
                    background-color: {c.surface_hover};
                    color: {c.text_primary};
                }}
                QPushButton:focus {{
                    border: 2px solid {c.focus_ring};
                }}
            """)


class ShellSidebar(QFrame):
    page_selected = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._expanded = True
        self._buttons: dict[str, ShellSidebarButton] = {}
        self._section_labels: list[QLabel] = []
        self._build_ui()
        self._update_dimensions()

    def _get_colors(self):
        return color_from_scheme(ColorScheme.DARK)

    def _build_ui(self) -> None:
        c = self._get_colors()

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(10, 16, 10, 16)
        self._layout.setSpacing(2)

        logo = QLabel("N")
        logo.setAccessibleName("GymOS logo")
        logo.setAlignment(Qt.AlignCenter)
        self._logo_label = QLabel("GymOS")
        self._logo_label.setAccessibleName("GymOS logo")
        self._logo_label.setAlignment(Qt.AlignLeft)
        self._logo_label.setStyleSheet(
            f"color: {c.primary}; font-size: 18px; font-weight: 800; background: transparent; border: none; padding: 4px 14px;"
        )
        self._layout.addWidget(self._logo_label)
        self._layout.addSpacing(12)

        for section_name, items in NAV_SECTIONS:
            sec = QLabel(section_name.upper())
            sec.setStyleSheet(
                f"color: {c.text_disabled}; font-size: 10px; font-weight: 600; "
                f"letter-spacing: 1px; background: transparent; border: none; padding: 8px 14px 4px 14px;"
            )
            self._section_labels.append(sec)
            self._layout.addWidget(sec)

            prev_btn: QPushButton | None = None
            for page_id, label, icon in items:
                btn = ShellSidebarButton(page_id, label, icon, expanded=self._expanded)
                btn.setAccessibleName(f"Navigate to {label}")
                btn.clicked.connect(lambda checked=False, pid=page_id: self._on_page_clicked(pid))
                self._buttons[page_id] = btn
                self._layout.addWidget(btn)
                if prev_btn:
                    self.setTabOrder(prev_btn, btn)
                prev_btn = btn

        self._layout.addStretch()

        bottom_container = QFrame()
        bottom_container.setStyleSheet("background: transparent; border: none;")
        bottom_layout = QHBoxLayout(bottom_container)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(4)

        settings_btn = QPushButton("\u2699")
        settings_btn.setFixedSize(36, 36)
        settings_btn.setCursor(Qt.PointingHandCursor)
        settings_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent; color: {c.text_disabled};
                border: none; border-radius: {RADIUS.md}; font-size: 16px;
            }}
            QPushButton:hover {{ color: {c.text_primary}; background-color: {c.surface_hover}; }}
        """)
        settings_btn.setToolTip("Settings")
        settings_btn.clicked.connect(lambda: self._on_page_clicked("settings"))
        bottom_layout.addWidget(settings_btn)

        self._version_label = QLabel("v0.5.0")
        self._version_label.setStyleSheet(
            f"color: {c.text_disabled}; font-size: 10px; background: transparent; border: none;"
        )
        bottom_layout.addWidget(self._version_label, 1)

        self._layout.addWidget(bottom_container)

    def _on_page_clicked(self, page_id: str) -> None:
        self.set_active(page_id)
        self.page_selected.emit(page_id)

    def toggle_expanded(self) -> None:
        self._expanded = not self._expanded
        self._update_dimensions()
        for btn in self._buttons.values():
            btn.set_expanded(self._expanded)
        for label in self._section_labels:
            label.setVisible(self._expanded)
        self._logo_label.setText("GymOS" if self._expanded else "N")
        self._version_label.setVisible(self._expanded)

    def set_expanded(self, expanded: bool) -> None:
        if expanded != self._expanded:
            self.toggle_expanded()

    @property
    def is_expanded(self) -> bool:
        return self._expanded

    def _update_dimensions(self) -> None:
        w = EXPANDED_WIDTH if self._expanded else COLLAPSED_WIDTH
        self.setFixedWidth(w)
        self.setStyleSheet(f"""
            ShellSidebar {{
                background-color: {self._get_colors().background_alt};
                border-right: 1px solid {self._get_colors().border};
            }}
        """)

    def set_active(self, page_id: str) -> None:
        for pid, btn in self._buttons.items():
            btn.set_active(pid == page_id)
