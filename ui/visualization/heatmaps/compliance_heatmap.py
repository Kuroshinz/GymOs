from __future__ import annotations

from collections.abc import Sequence

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QWidget

from ui.visualization.core.base import BaseVisualization
from ui.visualization.core.utils import interpolate_color


class ComplianceHeatmap(BaseVisualization):
    """Compliance/adherence rate per day or program area."""

    def __init__(
        self,
        color_scheme=None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(color_scheme, parent)
        self._entries: list[tuple[str, float]] = []
        self.setFixedHeight(50)

    def set_data(self, entries: Sequence[tuple[str, float]] | None = None) -> None:
        self._entries = list(entries) if entries else []
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        colors = self._colors()
        w = self.width()
        h = 40
        n = len(self._entries)
        if n == 0:
            return

        cell_w = max(28, (w - 10) // max(n, 1))
        for i, (_label, rate) in enumerate(self._entries):
            x = i * cell_w
            fraction = max(0.0, min(1.0, rate))
            c = interpolate_color(colors.error, colors.success, fraction)
            painter.setBrush(QColor(c))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(x + 1, 2, cell_w - 2, h - 4, 3, 3)

            painter.setFont(self._make_font(8, True))
            painter.setPen(QColor(colors.text_inverse))
            painter.drawText(QRectF(x, 0, cell_w, h), Qt.AlignCenter, f"{int(fraction * 100)}%")

        painter.end()
