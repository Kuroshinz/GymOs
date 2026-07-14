from __future__ import annotations

import math
from collections.abc import Sequence

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget

from ui.visualization.core.base import BaseVisualization


class KnowledgeGraphView(BaseVisualization):
    """Node-link diagram for knowledge domain relationships."""

    def __init__(
        self,
        color_scheme=None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(color_scheme, parent)
        self._nodes: list[tuple[str, float]] = []
        self._edges: list[tuple[int, int, str]] = []
        self._positions: list[tuple[float, float]] = []
        self.setMinimumSize(200, 150)

    def set_data(
        self,
        nodes: Sequence[tuple[str, float]] | None = None,
        edges: Sequence[tuple[int, int, str]] | None = None,
    ) -> None:
        self._nodes = list(nodes) if nodes else []
        self._edges = list(edges) if edges else []
        self._layout_nodes()
        self.update()

    def _layout_nodes(self) -> None:
        n = len(self._nodes)
        w = self.width() - 20
        h = self.height() - 20
        cx, cy = w / 2 + 10, h / 2 + 10
        r = min(w, h) / 2 - 10
        self._positions = []
        for i in range(n):
            a = -math.pi / 2 + i * 2 * math.pi / max(n, 1)
            self._positions.append((cx + r * math.cos(a), cy + r * math.sin(a)))

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        colors = self._colors()
        if not self._positions:
            self._layout_nodes()

        for u, v, _rel in self._edges:
            if u < len(self._positions) and v < len(self._positions):
                x1, y1 = self._positions[u]
                x2, y2 = self._positions[v]
                painter.setPen(QPen(QColor(colors.border), 1))
                painter.drawLine(int(x1), int(y1), int(x2), int(y2))

        for i, (name, weight) in enumerate(self._nodes):
            x, y = self._positions[i]
            size = max(8, int(12 * min(weight / max(w for _, w in self._nodes), 1.0))) if self._nodes else 8
            painter.setBrush(QColor(colors.primary + "80"))
            painter.setPen(QPen(QColor(colors.primary), 1))
            painter.drawEllipse(int(x) - size, int(y) - size, size * 2, size * 2)

            painter.setFont(self._make_font(8))
            painter.setPen(QColor(colors.text_primary))
            painter.drawText(int(x) - 20, int(y) + size + 4, 40, 14, Qt.AlignCenter, name)

        painter.end()

    def resizeEvent(self, event) -> None:  # noqa: N802
        self._layout_nodes()
        super().resizeEvent(event)
