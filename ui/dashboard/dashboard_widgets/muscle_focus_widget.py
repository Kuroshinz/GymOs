"""Muscle Group Focus card — stylized front/back body heat map."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QPainter, QPainterPath
from PySide6.QtWidgets import QHBoxLayout, QWidget

from ui.dashboard.dashboard_models import DashboardData
from ui.dashboard.dashboard_widgets.card_kit import PanelCard, make_label, qcolor
from ui.design_system.tokens.color import ColorScheme, color_from_scheme

C = color_from_scheme(ColorScheme.DARK)

_PRIMARY = "#A855F7"
_SECONDARY = "#38BDF8"
_UNTARGETED = "#3B3F63"

# Muscle regions as normalized ellipses (cx, cy, rx, ry) inside a figure box,
# keyed by the front/back view. Each maps to a muscle-focus key.
_FRONT_REGIONS: list[tuple[str, tuple[float, float, float, float]]] = [
    ("traps", (0.50, 0.20, 0.10, 0.03)),
    ("shoulders", (0.30, 0.25, 0.09, 0.05)),
    ("shoulders", (0.70, 0.25, 0.09, 0.05)),
    ("chest", (0.40, 0.31, 0.09, 0.06)),
    ("chest", (0.60, 0.31, 0.09, 0.06)),
    ("biceps", (0.24, 0.36, 0.055, 0.07)),
    ("biceps", (0.76, 0.36, 0.055, 0.07)),
    ("abs", (0.50, 0.44, 0.10, 0.10)),
    ("forearms", (0.19, 0.49, 0.05, 0.07)),
    ("forearms", (0.81, 0.49, 0.05, 0.07)),
    ("quads", (0.41, 0.66, 0.08, 0.12)),
    ("quads", (0.59, 0.66, 0.08, 0.12)),
    ("calves", (0.42, 0.87, 0.055, 0.08)),
    ("calves", (0.58, 0.87, 0.055, 0.08)),
]

_BACK_REGIONS: list[tuple[str, tuple[float, float, float, float]]] = [
    ("traps", (0.50, 0.22, 0.12, 0.05)),
    ("shoulders", (0.30, 0.26, 0.09, 0.05)),
    ("shoulders", (0.70, 0.26, 0.09, 0.05)),
    ("lats", (0.40, 0.36, 0.10, 0.09)),
    ("lats", (0.60, 0.36, 0.10, 0.09)),
    ("triceps", (0.24, 0.36, 0.055, 0.07)),
    ("triceps", (0.76, 0.36, 0.055, 0.07)),
    ("back", (0.50, 0.47, 0.11, 0.07)),
    ("glutes", (0.42, 0.58, 0.08, 0.06)),
    ("glutes", (0.58, 0.58, 0.08, 0.06)),
    ("hamstrings", (0.41, 0.72, 0.08, 0.10)),
    ("hamstrings", (0.59, 0.72, 0.08, 0.10)),
    ("calves", (0.42, 0.88, 0.055, 0.08)),
    ("calves", (0.58, 0.88, 0.055, 0.08)),
]


class BodyMapView(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._focus: dict[str, str] = {}
        self.setMinimumHeight(300)
        self.setStyleSheet("background: transparent;")

    def set_focus(self, focus: dict[str, str]) -> None:
        self._focus = dict(focus)
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()
        fig_w = w / 2
        front_box = QRectF(fig_w * 0.10, 10, fig_w * 0.80, h - 20)
        back_box = QRectF(fig_w + fig_w * 0.10, 10, fig_w * 0.80, h - 20)

        self._draw_figure(painter, front_box, _FRONT_REGIONS)
        self._draw_figure(painter, back_box, _BACK_REGIONS)
        painter.end()

    def _draw_figure(self, painter: QPainter, box: QRectF, regions) -> None:
        # Base silhouette.
        painter.setPen(Qt.NoPen)
        painter.setBrush(qcolor("#5B5F88", 0.22))
        for shape in self._silhouette(box):
            painter.drawPath(shape)

        # Muscle overlays.
        for key, (cx, cy, rx, ry) in regions:
            level = self._focus.get(key, "untargeted")
            if level == "primary":
                color = _PRIMARY
                alpha = 0.92
            elif level == "secondary":
                color = _SECONDARY
                alpha = 0.85
            else:
                color = _UNTARGETED
                alpha = 0.55
            painter.setBrush(qcolor(color, alpha))
            rect = QRectF(
                box.x() + (cx - rx) * box.width(),
                box.y() + (cy - ry) * box.height(),
                rx * 2 * box.width(),
                ry * 2 * box.height(),
            )
            painter.drawRoundedRect(rect, rect.width() * 0.4, rect.height() * 0.4)

    @staticmethod
    def _silhouette(box: QRectF) -> list[QPainterPath]:
        x, y, w, h = box.x(), box.y(), box.width(), box.height()

        def rr(cx, cy, rx, ry, radius=None):
            path = QPainterPath()
            rect = QRectF(x + (cx - rx) * w, y + (cy - ry) * h, rx * 2 * w, ry * 2 * h)
            r = radius if radius is not None else min(rect.width(), rect.height()) * 0.45
            path.addRoundedRect(rect, r, r)
            return path

        paths = []
        # Head
        paths.append(rr(0.50, 0.09, 0.075, 0.06))
        # Torso (shoulders -> waist)
        torso = QPainterPath()
        torso.moveTo(x + 0.22 * w, y + 0.22 * h)
        torso.lineTo(x + 0.78 * w, y + 0.22 * h)
        torso.lineTo(x + 0.66 * w, y + 0.55 * h)
        torso.lineTo(x + 0.34 * w, y + 0.55 * h)
        torso.closeSubpath()
        paths.append(torso)
        # Arms
        paths.append(rr(0.22, 0.40, 0.055, 0.17))
        paths.append(rr(0.78, 0.40, 0.055, 0.17))
        # Legs
        paths.append(rr(0.41, 0.78, 0.075, 0.22))
        paths.append(rr(0.59, 0.78, 0.075, 0.22))
        return paths


class MuscleFocusWidget(PanelCard):
    def __init__(self, motion: Any = None, parent: QWidget | None = None) -> None:
        super().__init__(title="Muscle Group Focus", parent=parent)
        self._motion = motion

        self._body = BodyMapView()
        self.add_widget(self._body, 1)

        legend = QHBoxLayout()
        legend.setContentsMargins(0, 0, 0, 0)
        legend.setSpacing(16)
        legend.addStretch()
        legend.addLayout(_legend("Primary", _PRIMARY))
        legend.addLayout(_legend("Secondary", _SECONDARY))
        legend.addLayout(_legend("Untargeted", _UNTARGETED))
        legend.addStretch()
        self.add_layout(legend)

    def set_motion_service(self, motion: Any) -> None:
        self._motion = motion

    def update_data(self, data: DashboardData) -> None:
        self._body.set_focus(data.muscle_focus)


def _legend(text: str, color: str) -> QHBoxLayout:
    row = QHBoxLayout()
    row.setContentsMargins(0, 0, 0, 0)
    row.setSpacing(6)
    row.addWidget(make_label("\u25CF", size=10, color=color))
    row.addWidget(make_label(text, size=11, weight=500, color=C.text_secondary))
    return row
