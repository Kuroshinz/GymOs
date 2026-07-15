"""Recent Workouts card — list of sessions with score rings."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from ui.dashboard.dashboard_models import DashboardData
from ui.dashboard.dashboard_widgets.card_kit import PanelCard, make_label, qcolor
from ui.design_system.tokens.color import ColorScheme, color_from_scheme, resolve_alpha

C = color_from_scheme(ColorScheme.DARK)


class MiniScoreRing(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._value = 0
        self._color = C.primary
        self.setFixedSize(44, 44)

    def set_value(self, value: int, color: str) -> None:
        self._value = value
        self._color = color
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        stroke = 4
        rect = QRectF(stroke, stroke, self.width() - stroke * 2, self.height() - stroke * 2)

        bg = QPen(qcolor(self._color, 0.18), stroke)
        bg.setCapStyle(Qt.RoundCap)
        painter.setPen(bg)
        painter.drawArc(rect, 0, 360 * 16)

        fg = QPen(QColor(self._color), stroke)
        fg.setCapStyle(Qt.RoundCap)
        painter.setPen(fg)
        span = int(min(self._value / 100.0, 1.0) * 360 * 16)
        painter.drawArc(rect, 90 * 16, -span)

        f = QFont("Inter")
        f.setPixelSize(13)
        f.setBold(True)
        painter.setFont(f)
        painter.setPen(QColor(C.text_primary))
        painter.drawText(self.rect(), Qt.AlignCenter, str(self._value))
        painter.end()


class WorkoutRow(QFrame):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("WorkoutRow")
        self.setStyleSheet(
            f"""
            QFrame#WorkoutRow {{ background: transparent; border-radius: 12px; }}
            QFrame#WorkoutRow:hover {{ background: {resolve_alpha(C.primary, 0.07)}; }}
            """
        )
        row = QHBoxLayout(self)
        row.setContentsMargins(8, 8, 8, 8)
        row.setSpacing(12)

        self._icon = QLabel()
        self._icon.setFixedSize(40, 40)
        self._icon.setAlignment(Qt.AlignCenter)
        row.addWidget(self._icon)

        text = QVBoxLayout()
        text.setContentsMargins(0, 0, 0, 0)
        text.setSpacing(2)
        self._name = make_label("", size=14, weight=700, color=C.text_primary)
        self._focus = make_label("", size=12, weight=400, color=C.text_secondary)
        text.addWidget(self._name)
        text.addWidget(self._focus)
        row.addLayout(text, 1)

        self._ring = MiniScoreRing()
        row.addWidget(self._ring)

    def set_workout(self, wk: dict) -> None:
        color = wk.get("color", C.primary)
        self._icon.setStyleSheet(
            f"background: {resolve_alpha(color, 0.20)}; color: {color}; "
            f"border-radius: 12px; font-size: 18px;"
        )
        self._icon.setText("\U0001F3CB")
        self._name.setText(wk.get("name", ""))
        self._focus.setText(wk.get("focus", ""))
        self._ring.set_value(int(wk.get("score", 0)), color)


class RecentWorkoutsWidget(PanelCard):
    def __init__(self, motion: Any = None, parent: QWidget | None = None) -> None:
        super().__init__(title="Recent Workouts", action="View All", parent=parent)
        self._motion = motion
        self._rows: list[WorkoutRow] = []
        for _ in range(4):
            row = WorkoutRow()
            row.hide()
            self._rows.append(row)
            self.add_widget(row)
        self.add_stretch()

    def set_motion_service(self, motion: Any) -> None:
        self._motion = motion

    def update_data(self, data: DashboardData) -> None:
        workouts = data.recent_workouts or []
        for i, row in enumerate(self._rows):
            if i < len(workouts):
                row.set_workout(workouts[i])
                row.show()
            else:
                row.hide()
