from __future__ import annotations

from enum import Enum

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from ui.design_system.tokens.color import ColorScheme, color_from_scheme
from ui.design_system.tokens.typography import font_style


class MilestoneType(Enum):
    PR = "pr"
    STREAK = "streak"
    VOLUME = "volume"
    CONSISTENCY = "consistency"
    CUSTOM = "custom"


class MicroUX(QWidget):
    """Decorator widget that adds micro-interactions to existing content."""

    dismissed = Signal()

    def __init__(
        self,
        content_widget: QWidget,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._content = content_widget
        self._build_ui()

    def _build_ui(self) -> None:
        colors = color_from_scheme(ColorScheme.DARK)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        mini_bar = QFrame()
        mini_bar.setFixedHeight(4)
        mini_bar.setStyleSheet(f"background-color: {colors.primary}; border-radius: 2px;")
        layout.addWidget(mini_bar)

        container = QFrame()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.addWidget(self._content)
        layout.addWidget(container)

        self._opacity = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self._opacity)
        self._anim = QPropertyAnimation(self._opacity, b"opacity")
        self._anim.setDuration(300)
        self._anim.setStartValue(0.0)
        self._anim.setEndValue(1.0)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)

    def showEvent(self, event: object) -> None:
        super().showEvent(event)
        self._anim.start()


class CelebrationOverlay(QFrame):
    """Full-bleed celebration overlay for milestone achievements."""

    closed = Signal()

    def __init__(
        self,
        title: str,
        subtitle: str = "",
        milestone_type: MilestoneType = MilestoneType.CUSTOM,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._milestone_type = milestone_type
        self._build_ui(title, subtitle)

    def _build_ui(self, title: str, subtitle: str) -> None:
        colors = color_from_scheme(ColorScheme.DARK)

        self.setObjectName("CelebrationOverlay")
        self.setStyleSheet(
            f"""
            #CelebrationOverlay {{
                background-color: {colors.surface};
                border: 2px solid {colors.primary};
                border-radius: 12px;
            }}
            """
        )

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(8)
        layout.setContentsMargins(16, 16, 16, 16)

        icon_map = {
            MilestoneType.PR: "\U0001F3C6",
            MilestoneType.STREAK: "\U0001F525",
            MilestoneType.VOLUME: "\U0001F4AA",
            MilestoneType.CONSISTENCY: "\U0001F4CA",
            MilestoneType.CUSTOM: "\u2B50",
        }
        icon_label = QLabel(icon_map.get(self._milestone_type, "\u2B50"))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("font-size: 48px;")
        layout.addWidget(icon_label)

        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(font_style("h3", weight=700))
        title_label.setWordWrap(True)
        layout.addWidget(title_label)

        if subtitle:
            sub_label = QLabel(subtitle)
            sub_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            sub_label.setStyleSheet(font_style("body") + f" color: {colors.text_secondary};")
            sub_label.setWordWrap(True)
            layout.addWidget(sub_label)

        close_btn = QPushButton("Continue")
        close_btn.setFixedWidth(200)
        close_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {colors.primary};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 24px;
                font-size: 14px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {colors.primary_hover};
            }}
            """
        )
        close_btn.clicked.connect(self.closed.emit)
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)


class AchievementBadge(QFrame):
    """Compact badge for achievement feed items."""

    clicked = Signal(str)

    def __init__(
        self,
        name: str,
        description: str = "",
        points: int = 0,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._name = name
        self._build_ui(description, points)

    def _build_ui(self, description: str, points: int) -> None:
        colors = color_from_scheme(ColorScheme.DARK)

        self.setObjectName("AchievementBadge")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(
            f"""
            #AchievementBadge {{
                background-color: {colors.surface};
                border: 1px solid {colors.border};
                border-radius: 8px;
                padding: 8px;
            }}
            #AchievementBadge:hover {{
                border-color: {colors.primary};
            }}
            """
        )

        layout = QVBoxLayout(self)
        layout.setSpacing(4)

        header = QHBoxLayout()
        name_label = QLabel(self._name)
        name_label.setStyleSheet(font_style("subtitle", weight=600))
        header.addWidget(name_label, 1)

        if points:
            pts_label = QLabel(f"{points} pts")
            pts_label.setStyleSheet(font_style("caption", weight=600) + f" color: {colors.primary};")
            header.addWidget(pts_label)

        layout.addLayout(header)

        if description:
            desc_label = QLabel(description)
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet(font_style("caption") + f" color: {colors.text_secondary};")
            layout.addWidget(desc_label)

    def mousePressEvent(self, event: object) -> None:
        super().mousePressEvent(event)
        self.clicked.emit(self._name)


class MilestoneIndicator(QFrame):
    """Compact indicator for milestone progress in a list."""

    def __init__(
        self,
        label: str,
        progress: float = 0.0,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._progress = progress
        self._build_ui(label)

    def _build_ui(self, label: str) -> None:
        colors = color_from_scheme(ColorScheme.DARK)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        label_widget = QLabel(label)
        label_widget.setStyleSheet(font_style("caption"))
        layout.addWidget(label_widget)

        bar_bg = QFrame()
        bar_bg.setFixedHeight(6)
        bar_bg.setStyleSheet(f"background-color: {colors.border}; border-radius: 3px;")

        bar_fill = QFrame(bar_bg)
        bar_fill.setFixedHeight(6)
        pct = max(0, min(100, self._progress * 100))
        fill_color = (
            colors.success if pct >= 100
            else colors.primary if pct >= 50
            else colors.warning
        )
        bar_fill.setStyleSheet(f"background-color: {fill_color}; border-radius: 3px;")
        bar_fill.setFixedWidth(int(pct / 100 * 200))

        layout.addWidget(bar_bg)
