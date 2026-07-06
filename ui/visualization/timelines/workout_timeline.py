from __future__ import annotations

from collections.abc import Sequence

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QWidget

from ui.visualization.core.base import RADIUS, BaseVisualization, radius_to_px


class WorkoutTimeline(BaseVisualization):
    """Workout volume/intensity bars over recent sessions."""

    def __init__(
        self,
        color_scheme=None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(color_scheme, parent)
        self._sessions: list[tuple[str, float]] = []
        self._max_volume = 100.0
        self.setFixedHeight(90)

    def set_data(self, sessions: Sequence[tuple[str, float]] | None = None, max_volume: float = 100.0) -> None:
        self._sessions = list(sessions) if sessions else []
        self._max_volume = max(max_volume, 1.0)
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        colors = self._colors()
        w = self.width()
        h = 70
        n = len(self._sessions)
        if n == 0:
            return

        bar_w = min(28, (w - 20) // n - 4)
        spacing = max((w - 20 - bar_w * n) // max(n - 1, 1), 3)
        start_x = 10

        for i, (label, vol) in enumerate(self._sessions):
            x = start_x + i * (bar_w + spacing)
            fraction = min(vol / self._max_volume, 1.0)
            bar_h = max(int(fraction * (h - 20)), 0)
            bar_y = h - 10 - bar_h

            color = colors.primary
            if fraction < 0.3:
                color = colors.error
            elif fraction < 0.6:
                color = colors.warning

            r = radius_to_px(RADIUS.sm)
            painter.setBrush(QColor(color))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(x, bar_y, bar_w, bar_h, r, r)

            painter.setFont(self._make_font(8))
            painter.setPen(QColor(colors.text_disabled))
            painter.drawText(QRectF(x, h - 8, bar_w, 14), Qt.AlignCenter, label)

        painter.end()
