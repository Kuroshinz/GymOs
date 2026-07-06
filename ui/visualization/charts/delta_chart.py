from __future__ import annotations

from collections.abc import Sequence

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QWidget

from ui.visualization.core.base import BaseVisualization


class DeltaChart(BaseVisualization):
    """Up/down bar chart showing changes (delta) per period."""

    def __init__(
        self,
        color_scheme=None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(color_scheme, parent)
        self._deltas: list[tuple[str, float]] = []
        self.setFixedHeight(80)

    def set_data(self, deltas: Sequence[tuple[str, float]] | None = None) -> None:
        self._deltas = list(deltas) if deltas else []
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        colors = self._colors()
        w = self.width()
        h = 65
        n = len(self._deltas)
        if n == 0:
            return

        mid = h / 2
        bar_w = min(24, (w - 20) // n - 4)
        spacing = max((w - 20 - bar_w * n) // max(n - 1, 1), 3)
        max_d = max(abs(d[1]) for d in self._deltas) or 1.0

        for i, (label, delta) in enumerate(self._deltas):
            x = 10 + i * (bar_w + spacing)
            frac = abs(delta) / max_d
            bar_h = max(int(frac * (mid - 10)), 1)
            if delta >= 0:
                painter.setBrush(QColor(colors.success))
                painter.drawRect(x, int(mid - bar_h), bar_w, bar_h)
            else:
                painter.setBrush(QColor(colors.error))
                painter.drawRect(x, int(mid), bar_w, bar_h)

            painter.setFont(self._make_font(8))
            painter.setPen(QColor(colors.text_disabled))
            painter.drawText(int(x), h - 2, int(bar_w), 14, Qt.AlignCenter, label)

        painter.end()
