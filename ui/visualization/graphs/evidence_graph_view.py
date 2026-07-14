from __future__ import annotations

from collections.abc import Sequence

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget

from ui.visualization.core.base import BaseVisualization


class EvidenceGraphView(BaseVisualization):
    """Directed graph showing evidence nodes and confidence-weighted edges."""

    def __init__(
        self,
        color_scheme=None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(color_scheme, parent)
        self._nodes: list[tuple[str, float]] = []
        self._edges: list[tuple[int, int, float]] = []
        self.setMinimumSize(200, 150)

    def set_data(
        self,
        nodes: Sequence[tuple[str, float]] | None = None,
        edges: Sequence[tuple[int, int, float]] | None = None,
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
        import math
        positions = [(cx + r * math.cos(-math.pi / 2 + i * 2 * math.pi / n), cy + r * math.sin(-math.pi / 2 + i * 2 * math.pi / n)) for i in range(n)]

        for u, v, conf in self._edges:
            if u < len(positions) and v < len(positions):
                x1, y1 = positions[u]
                x2, y2 = positions[v]
                alpha = int(max(30, min(255, conf * 255)))
                painter.setPen(QPen(QColor(colors.primary + f"{alpha:02x}"), 1 + int(conf * 2)))
                painter.drawLine(int(x1), int(y1), int(x2), int(y2))

        for i, (name, conf) in enumerate(self._nodes):
            x, y = positions[i]
            size = 8 + int(conf * 6)
            painter.setBrush(QColor(colors.accent + "99"))
            painter.setPen(QPen(QColor(colors.accent), 1))
            painter.drawEllipse(int(x) - size, int(y) - size, size * 2, size * 2)
            painter.setFont(self._make_font(7))
            painter.setPen(QColor(colors.text_primary))
            painter.drawText(int(x) - 15, int(y) + size + 2, 30, 12, Qt.AlignCenter, name)

        painter.end()
