from __future__ import annotations

import math
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QPainter, QPen, QPainterPath, QColor
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ui.design_system.tokens.color import ColorScheme, color_from_scheme, resolve_alpha
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
        ("weekly_review", "Weekly Review", "\u22EE"),
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


class VectorIconWidget(QWidget):
    def __init__(self, page_id: str, color: QColor, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._page_id = page_id
        self._color = color
        self.setFixedSize(18, 18)

    def set_color(self, color: QColor) -> None:
        self._color = color
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        pen = QPen(self._color, 2)
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)

        x, y = 0, 0
        
        if self._page_id == "dashboard":
            path = QPainterPath()
            path.moveTo(x + 2, y + 8)
            path.lineTo(x + 9, y + 2)
            path.lineTo(x + 16, y + 8)
            path.moveTo(x + 4, y + 7)
            path.lineTo(x + 4, y + 16)
            path.lineTo(x + 14, y + 16)
            path.lineTo(x + 14, y + 7)
            painter.drawPath(path)
        elif self._page_id == "workout":
            path = QPainterPath()
            path.moveTo(x + 5, y + 3)
            path.lineTo(x + 14, y + 9)
            path.lineTo(x + 5, y + 15)
            path.closeSubpath()
            painter.drawPath(path)
        elif self._page_id == "progress":
            painter.drawRect(x + 2, y + 10, 3, 6)
            painter.drawRect(x + 7, y + 6, 3, 10)
            painter.drawRect(x + 12, y + 2, 3, 14)
        elif self._page_id == "recovery":
            path = QPainterPath()
            path.moveTo(x + 9, y + 15)
            path.cubicTo(x + 9, y + 15, x + 2, y + 9, x + 2, y + 5.5)
            path.cubicTo(x + 2, y + 3, x + 4, y + 1, x + 6.5, y + 1)
            path.cubicTo(x + 8, y + 1, x + 9, y + 2, x + 9, y + 2)
            path.cubicTo(x + 9, y + 2, x + 10, y + 1, x + 11.5, y + 1)
            path.cubicTo(x + 14, y + 1, x + 16, y + 3, x + 16, y + 5.5)
            path.cubicTo(x + 16, y + 9, x + 9, y + 15, x + 9, y + 15)
            painter.drawPath(path)
        elif self._page_id == "predictions":
            path = QPainterPath()
            path.moveTo(x + 9, y + 2)
            path.quadTo(x + 9, y + 9, x + 16, y + 9)
            path.quadTo(x + 9, y + 9, x + 9, y + 16)
            path.quadTo(x + 9, y + 9, x + 2, y + 9)
            path.quadTo(x + 9, y + 9, x + 9, y + 2)
            painter.drawPath(path)
        elif self._page_id == "prs":
            path = QPainterPath()
            path.moveTo(x + 4, y + 2)
            path.lineTo(x + 14, y + 2)
            path.lineTo(x + 14, y + 9)
            path.cubicTo(x + 14, y + 13, x + 4, y + 13, x + 4, y + 9)
            path.closeSubpath()
            painter.drawPath(path)
            painter.drawLine(x + 9, y + 13, x + 9, y + 16)
            painter.drawLine(x + 5, y + 16, x + 13, y + 16)
        elif self._page_id == "weekly_review":
            path = QPainterPath()
            path.moveTo(x + 4, y + 2)
            path.lineTo(x + 14, y + 2)
            path.lineTo(x + 14, y + 16)
            path.lineTo(x + 4, y + 16)
            path.closeSubpath()
            painter.drawPath(path)
            painter.drawLine(x + 6, y + 6, x + 12, y + 6)
            painter.drawLine(x + 6, y + 10, x + 12, y + 10)
        elif self._page_id == "settings":
            painter.drawEllipse(x + 5, y + 5, 8, 8)
            for i in range(8):
                angle = i * math.pi / 4
                x1 = x + 9 + int(4 * math.cos(angle))
                y1 = y + 9 + int(4 * math.sin(angle))
                x2 = x + 9 + int(7 * math.cos(angle))
                y2 = y + 9 + int(7 * math.sin(angle))
                painter.drawLine(x1, y1, x2, y2)


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
        self._expanded = expanded
        self._active = False
        self.setFixedHeight(44)
        self.setCursor(Qt.PointingHandCursor)
        self.setFocusPolicy(Qt.StrongFocus)

        self._btn_layout = QHBoxLayout(self)
        self._btn_layout.setContentsMargins(12, 0, 12, 0)
        self._btn_layout.setSpacing(12)

        c = self._get_colors()
        self._icon_widget = VectorIconWidget(self._page_id, QColor(c.text_secondary))
        self._btn_layout.addWidget(self._icon_widget)

        self._text_label = QLabel(self._label)
        self._text_label.setStyleSheet("background: transparent; color: inherit; font-size: 14px; font-weight: inherit;")
        self._btn_layout.addWidget(self._text_label)

        self._update_content()
        self._update_style()

    def set_expanded(self, expanded: bool) -> None:
        self._expanded = expanded
        self._update_content()
        self._update_style()

    def set_active(self, active: bool) -> None:
        self._active = active
        c = self._get_colors()
        active_color = QColor(c.primary if self._active else c.text_secondary)
        self._icon_widget.set_color(active_color)
        self._update_style()

    def _update_content(self) -> None:
        if self._expanded:
            self._text_label.show()
            self._btn_layout.setContentsMargins(12, 0, 12, 0)
            self._btn_layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.setToolTip("")
        else:
            self._text_label.hide()
            self._btn_layout.setContentsMargins(0, 0, 0, 0)
            self._btn_layout.setAlignment(Qt.AlignCenter)
            self.setToolTip(self._label)

    def _get_colors(self):
        return color_from_scheme(ColorScheme.DARK)

    def _update_style(self) -> None:
        c = self._get_colors()
        if self._active:
            bg = "rgba(99, 102, 241, 0.12)"
            border_style = "1px solid rgba(99, 102, 241, 0.25)"
            color = c.primary
            weight = "600"
        else:
            bg = "transparent"
            border_style = "none"
            color = c.text_secondary
            weight = "500"

        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg};
                color: {color};
                border: {border_style};
                border-radius: {RADIUS.md};
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
        self._layout.setContentsMargins(12, 20, 12, 20)
        self._layout.setSpacing(6)

        logo = QLabel("N")
        logo.setAccessibleName("GymOS logo")
        logo.setAlignment(Qt.AlignCenter)
        self._logo_label = QLabel("GymOS")
        self._logo_label.setAccessibleName("GymOS logo")
        self._logo_label.setAlignment(Qt.AlignLeft)
        self._logo_label.setStyleSheet(
            f"color: {c.primary}; font-size: 20px; font-weight: 800; background: transparent; border: none; padding: 4px 14px;"
        )
        self._layout.addWidget(self._logo_label)
        self._layout.addSpacing(16)

        prev_btn: QPushButton | None = None

        for section_name, items in NAV_SECTIONS:
            self._layout.addSpacing(12)
            sec = QLabel(section_name.upper())
            sec.setStyleSheet(
                f"color: #565f73; font-size: 11px; font-weight: 700; "
                f"letter-spacing: 1px; background: transparent; border: none; padding: 0px 14px;"
            )
            self._section_labels.append(sec)
            self._layout.addWidget(sec)
            self._layout.addSpacing(4)

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

        from PySide6.QtWidgets import QProgressBar

        # User Profile Card
        self._profile_card = QFrame()
        self._profile_card.setObjectName("ProfileCard")
        self._profile_card.setStyleSheet(f"""
            QFrame#ProfileCard {{
                background-color: {resolve_alpha(c.primary, 0.04)};
                border: 1px solid {c.border};
                border-radius: {RADIUS.md};
                padding: 10px;
            }}
        """)
        
        profile_layout = QVBoxLayout(self._profile_card)
        profile_layout.setContentsMargins(8, 8, 8, 8)
        profile_layout.setSpacing(8)

        # Upper row: Avatar + Details
        upper_row = QHBoxLayout()
        upper_row.setContentsMargins(0, 0, 0, 0)
        upper_row.setSpacing(10)

        # Avatar placeholder with a nice gradient
        avatar = QFrame()
        avatar.setFixedSize(36, 36)
        avatar.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {c.primary}, stop:1 {c.secondary});
                border-radius: 18px;
                border: 2px solid {c.border};
            }}
        """)
        upper_row.addWidget(avatar)

        # Name and Level
        details = QVBoxLayout()
        details.setContentsMargins(0, 0, 0, 0)
        details.setSpacing(2)
        
        name_lbl = QLabel("Nguyễn Thiện Nhân")
        name_lbl.setStyleSheet(f"color: {c.text_primary}; font-weight: 700; font-size: 13px; background: transparent;")
        
        level_lbl = QLabel("Level 28 • Elite")
        level_lbl.setStyleSheet(f"color: {c.text_disabled}; font-size: 10px; background: transparent;")
        
        details.addWidget(name_lbl)
        details.addWidget(level_lbl)
        upper_row.addLayout(details)
        upper_row.addStretch()
        profile_layout.addLayout(upper_row)

        # XP Progress Bar and Label
        xp_row = QHBoxLayout()
        xp_row.setContentsMargins(0, 0, 0, 0)
        
        xp_lbl = QLabel("8,450 / 10,000 XP")
        xp_lbl.setStyleSheet(f"color: {c.text_secondary}; font-size: 9px; font-weight: 600; background: transparent;")
        xp_row.addWidget(xp_lbl)
        xp_row.addStretch()
        profile_layout.addLayout(xp_row)

        xp_bar = QProgressBar()
        xp_bar.setFixedHeight(6)
        xp_bar.setRange(0, 10000)
        xp_bar.setValue(8450)
        xp_bar.setTextVisible(False)
        xp_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {c.background};
                border: none;
                border-radius: 3px;
            }}
            QProgressBar::chunk {{
                background-color: {c.primary};
                border-radius: 3px;
            }}
        """)
        profile_layout.addWidget(xp_bar)

        self._layout.addWidget(self._profile_card)
        self._layout.addSpacing(4)

        # Settings and Version footer row
        bottom_container = QFrame()
        bottom_container.setStyleSheet("background: transparent; border: none;")
        bottom_container.setFixedHeight(36)
        bottom_layout = QHBoxLayout(bottom_container)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(8)

        settings_btn = QPushButton("\u2699")
        settings_btn.setFixedSize(32, 32)
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
            f"color: {c.text_disabled}; font-size: 11px; background: transparent; border: none;"
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
        self._profile_card.setVisible(self._expanded)

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