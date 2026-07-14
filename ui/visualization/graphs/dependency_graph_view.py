from __future__ import annotations

import math
from collections.abc import Sequence

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget

from ui.visualization.core.base import BaseVisualization


class DependencyGraphView(BaseVisualization):
    """DAG visualization showing module/component dependencies."""

    def __init__(
        self,
        color_scheme=None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(color_scheme, parent)
        self._nodes: list[tuple[str, str]] = []
        self._edges: list[tuple[int, int]] = []
        self.setMinimumSize(200, 150)

    def set_data(
        self,
        nodes: Sequence[tuple[str, str]] | None = None,
        edges: Sequence[tuple[int, int]] | None = None,
    ) -> None:
        self._nodes = list(nodes) if nodes else []
        self._edges = list(edges) if edges else []
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        colors = self._colors()
        w, h = self.width(), self.height()
        n = len(self._nodes)
        if n == 0:
            return

        cx, cy = w / 2, h / 2
        r = min(cx, cy) - 15
        positions = [(cx + r * math.cos(-math.pi / 2 + i * 2 * math.pi / n), cy + r * math.sin(-math.pi / 2 + i * 2 * math.pi / n)) for i in range(n)]

        for u, v in self._edges:
            if u < len(positions) and v < len(positions):
                x1, y1 = positions[u]
                x2, y2 = positions[v]
                painter.setPen(QPen(QColor(colors.border), 1))
                painter.drawLine(int(x1), int(y1), int(x2), int(y2))
                dx, dy = x2 - x1, y2 - y1
                dist = math.sqrt(dx * dx + dy * dy) or 1
                ax, ay = dx / dist * 8, dy / dist * 8
                painter.setBrush(QColor(colors.border))
                painter.drawEllipse(int(x2 - ax) - 3, int(y2 - ay) - 3, 6, 6)

        for i, (name, status) in enumerate(self._nodes):
            x, y = positions[i]
            c = colors.success if status == "ready" else (colors.warning if status == "pending" else colors.error)
            painter.setBrush(QColor(c + "99"))
            painter.setPen(QPen(QColor(c), 1))
            painter.drawEllipse(int(x) - 10, int(y) - 10, 20, 20)
            painter.setFont(self._make_font(7, True))
            painter.setPen(QColor(colors.text_inverse))
            painter.drawText(int(x) - 10, int(y) - 4, 20, 12, Qt.AlignCenter, name[:6])

        painter.end()
