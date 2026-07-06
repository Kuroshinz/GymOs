from __future__ import annotations

from collections.abc import Sequence

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget

from ui.design_system.tokens.radius import radius_to_px
from ui.visualization.core.base import RADIUS, BaseVisualization


class MesocycleTimeline(BaseVisualization):
    """Visualizes a mesocycle as segments (deload, build, peak, etc.)."""

    @staticmethod
    def _phase_color(phase: str, colors) -> str:
        return {
            "deload": colors.error,
            "build": colors.info,
            "peak": colors.warning,
            "overreach": "#F97316",
            "rest": colors.success,
            "transition": "#A78BFA",
        }.get(phase, colors.primary)

    def __init__(
        self,
        color_scheme=None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(color_scheme, parent)
        self._phases: list[tuple[str, str, float]] = []
        self._current_week: int = -1
        self.setFixedHeight(60)

    def set_data(self, phases: Sequence[tuple[str, str, float]] | None = None, current_week: int = -1) -> None:
        self._phases = list(phases) if phases else []
        self._current_week = current_week
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        colors = self._colors()
        w = self.width()
        h = 40
        n = len(self._phases)
        if n == 0:
            return

        seg_w = (w - 20) / n
        r = radius_to_px(RADIUS.sm)

        for i, (name, phase, weeks) in enumerate(self._phases):
            x = 10 + i * seg_w
            c = self._phase_color(phase, colors)
            rect = QRectF(x, 4, seg_w - 4, h - 8)
            painter.setBrush(QColor(c))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(rect, r, r)

            painter.setFont(self._make_font(9, True))
            painter.setPen(QColor(colors.text_inverse))
            painter.drawText(rect, Qt.AlignCenter, name)

            if i == self._current_week:
                painter.setPen(QPen(QColor(colors.accent), 2))
                painter.setBrush(Qt.NoBrush)
                painter.drawRoundedRect(rect.adjusted(-1, -1, 1, 1), r + 1, r + 1)

        painter.end()
