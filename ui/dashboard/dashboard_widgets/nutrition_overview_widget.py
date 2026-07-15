"""Nutrition Overview card — macro donut + macro bars + details action."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import QRectF, Qt, Signal
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import QHBoxLayout, QProgressBar, QVBoxLayout, QWidget

from ui.dashboard.dashboard_models import DashboardData
from ui.dashboard.dashboard_widgets.card_kit import PanelCard, make_label, qcolor
from ui.dashboard.dashboard_widgets.recovery_status_widget import ghost_button
from ui.design_system.tokens.color import ColorScheme, color_from_scheme, resolve_alpha

C = color_from_scheme(ColorScheme.DARK)

_PROTEIN = "#F472B6"
_CARBS = "#38BDF8"
_FATS = "#34D399"


class MacroDonut(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._segments: list[tuple[float, str]] = []
        self._center_value = "0"
        self._center_caption = "kcal left"
        self.setFixedSize(150, 150)

    def set_data(self, segments: list[tuple[float, str]], center_value: str) -> None:
        self._segments = segments
        self._center_value = center_value
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        stroke = 14
        rect = QRectF(stroke, stroke, self.width() - stroke * 2, self.height() - stroke * 2)

        painter.setPen(QPen(qcolor(C.text_secondary, 0.10), stroke))
        painter.drawArc(rect, 0, 360 * 16)

        total = sum(v for v, _ in self._segments) or 1.0
        start = 90 * 16
        for value, color in self._segments:
            span = -int(value / total * 360 * 16)
            pen = QPen(QColor(color), stroke)
            pen.setCapStyle(Qt.FlatCap)
            painter.setPen(pen)
            painter.drawArc(rect, start, span)
            start += span

        f = QFont("Inter")
        f.setPixelSize(24)
        f.setBold(True)
        painter.setFont(f)
        painter.setPen(QColor(C.text_primary))
        painter.drawText(
            QRectF(0, self.height() / 2 - 22, self.width(), 28),
            Qt.AlignCenter,
            self._center_value,
        )
        f2 = QFont("Inter")
        f2.setPixelSize(11)
        painter.setFont(f2)
        painter.setPen(QColor(C.text_disabled))
        painter.drawText(
            QRectF(0, self.height() / 2 + 6, self.width(), 16),
            Qt.AlignCenter,
            self._center_caption,
        )
        painter.end()


def _macro_bar(name: str, color: str):
    container = QWidget()
    container.setStyleSheet("background: transparent;")
    lay = QVBoxLayout(container)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setSpacing(5)

    head = QHBoxLayout()
    head.setContentsMargins(0, 0, 0, 0)
    head.addWidget(make_label(name, size=13, weight=600, color=C.text_primary))
    head.addStretch()
    value_lbl = make_label("-- / --", size=13, weight=600, color=C.text_secondary)
    head.addWidget(value_lbl)
    lay.addLayout(head)

    bar = QProgressBar()
    bar.setTextVisible(False)
    bar.setFixedHeight(8)
    bar.setRange(0, 100)
    bar.setStyleSheet(
        f"""
        QProgressBar {{ background: {resolve_alpha(color, 0.15)}; border: none; border-radius: 4px; }}
        QProgressBar::chunk {{ background: {color}; border-radius: 4px; }}
        """
    )
    lay.addWidget(bar)
    return container, value_lbl, bar


class NutritionOverviewWidget(PanelCard):
    view_details_clicked = Signal()

    def __init__(self, motion: Any = None, parent: QWidget | None = None) -> None:
        super().__init__(title="Nutrition Overview", parent=parent)
        self._motion = motion

        content = QHBoxLayout()
        content.setContentsMargins(0, 0, 0, 0)
        content.setSpacing(18)

        self._donut = MacroDonut()
        content.addWidget(self._donut, 0, Qt.AlignVCenter)

        bars = QVBoxLayout()
        bars.setContentsMargins(0, 0, 0, 0)
        bars.setSpacing(12)
        self._protein, self._protein_val, self._protein_bar = _macro_bar("Protein", _PROTEIN)
        self._carbs, self._carbs_val, self._carbs_bar = _macro_bar("Carbs", _CARBS)
        self._fats, self._fats_val, self._fats_bar = _macro_bar("Fats", _FATS)
        bars.addStretch()
        bars.addWidget(self._protein)
        bars.addWidget(self._carbs)
        bars.addWidget(self._fats)
        bars.addStretch()
        content.addLayout(bars, 1)

        self.add_layout(content)

        self._button = ghost_button("\U0001F37D  View Nutrition Details")
        self._button.clicked.connect(self.view_details_clicked.emit)
        self.add_widget(self._button)

    def set_motion_service(self, motion: Any) -> None:
        self._motion = motion

    def update_data(self, data: DashboardData) -> None:
        nd = data.nutrition_data or {}
        protein = nd.get("protein", {"current": 125, "target": 150})
        carbs = nd.get("carbs", {"current": 180, "target": 250})
        fats = nd.get("fat", {"current": 65, "target": 80})
        calories = nd.get("calories", {"current": 0, "target": 2600})

        self._set_bar(self._protein_val, self._protein_bar, protein, "g")
        self._set_bar(self._carbs_val, self._carbs_bar, carbs, "g")
        self._set_bar(self._fats_val, self._fats_bar, fats, "g")

        p = float(protein.get("current", 0)) * 4
        c = float(carbs.get("current", 0)) * 4
        f = float(fats.get("current", 0)) * 9
        left = max(0.0, float(calories.get("target", 0)) - float(calories.get("current", 0)))
        if p + c + f <= 0:
            p, c, f = 500, 720, 585  # representative macro split
            if left <= 0:
                left = 1842
        self._donut.set_data([(p, _PROTEIN), (c, _CARBS), (f, _FATS)], f"{left:,.0f}")

    @staticmethod
    def _set_bar(label, bar, macro: dict, unit: str) -> None:
        current = float(macro.get("current", 0) or 0)
        target = float(macro.get("target", 0) or 0)
        label.setText(f"{current:.0f} / {target:.0f}{unit}")
        bar.setValue(int(min(current / target * 100, 100)) if target else 0)
