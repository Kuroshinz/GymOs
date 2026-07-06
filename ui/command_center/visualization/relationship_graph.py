from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QFrame, QWidget

from ui.command_center.theme import C


class RelationshipGraph(QFrame):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._nodes: list[dict[str, Any]] = []
        self._edges: list[tuple[int, int]] = []
        self.setMinimumHeight(200)
        self.setStyleSheet(f"background-color: {C.CARD_BG}; border-radius: 12px;")

    def set_graph(self, nodes: list[dict], edges: list[tuple[int, int]]) -> None:
        self._nodes = nodes
        self._edges = edges
        self.update()

    def paintEvent(self, event) -> None:
        if not self._nodes:
            painter = QPainter(self)
            painter.setPen(QColor(C.TEXT_MUTED))
            painter.drawText(self.rect(), Qt.AlignCenter, "No graph data")
            painter.end()
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()
        cx, cy = w / 2, h / 2
        radius = min(w, h) / 2 - 30
        angle_step = 360.0 / max(len(self._nodes), 1)

        positions: list[tuple[float, float]] = []
        for i in range(len(self._nodes)):
            import math
            angle = math.radians(angle_step * i - 90)
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)
            positions.append((x, y))

        node_colors = [
            QColor(C.ACCENT), QColor(C.TEXT_SUCCESS), QColor(C.TEXT_WARN),
            QColor(C.TEXT_INFO), QColor(C.TEXT_DANGER), QColor("#C084FC"),
        ]

        for src, dst in self._edges:
            if src < len(positions) and dst < len(positions):
                painter.setPen(QPen(QColor(C.BORDER), 1))
                painter.drawLine(
                    int(positions[src][0]), int(positions[src][1]),
                    int(positions[dst][0]), int(positions[dst][1]),
                )

        for i, (px, py) in enumerate(positions):
            color = node_colors[i % len(node_colors)]
            painter.setBrush(color)
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(int(px - 6), int(py - 6), 12, 12)

            name = self._nodes[i].get("label", str(i))
            painter.setPen(QColor(C.TEXT_SECONDARY))
            painter.drawText(int(px) - 30, int(py) + 16, 60, 16, Qt.AlignCenter, name)

        painter.end()
