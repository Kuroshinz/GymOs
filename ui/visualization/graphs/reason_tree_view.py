from __future__ import annotations

from collections.abc import Sequence

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget

from ui.visualization.core.base import BaseVisualization


class ReasonTreeView(BaseVisualization):
    """Tree visualization for reasoning chains (root → branches → leaves)."""

    def __init__(
        self,
        color_scheme=None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(color_scheme, parent)
        self._nodes: list[tuple[str, str]] = []
        self._root: int = -1
        self._children: dict[int, list[int]] = {}
        self.setMinimumSize(200, 150)

    def set_data(
        self,
        nodes: Sequence[tuple[str, str]] | None = None,
        root: int = 0,
        children: dict[int, list[int]] | None = None,
    ) -> None:
        self._nodes = list(nodes) if nodes else []
        self._root = root if root < len(self._nodes) else 0
        self._children = {int(k): list(v) for k, v in (children or {}).items()}
        self.update()

    def _layout(self) -> dict[int, tuple[float, float]]:
        positions: dict[int, tuple[float, float]] = {}
        w, h = self.width(), self.height()
        if not self._nodes:
            return positions

        def dfs(node_id: int, x: float, y: float, dx: float) -> None:
            positions[node_id] = (x, y)
            kids = self._children.get(node_id, [])
            if not kids:
                return
            child_dx = dx / len(kids)
            for i, kid in enumerate(kids):
                dfs(kid, x - dx / 2 + child_dx * (i + 0.5), y + 40, child_dx)

        dfs(self._root, w / 2, 20, w / 3)
        return positions

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        colors = self._colors()
        pos = self._layout()
        if not pos:
            return

        for parent_id, kids in self._children.items():
            if parent_id in pos:
                px, py = pos[parent_id]
                for kid in kids:
                    if kid in pos:
                        kx, ky = pos[kid]
                        painter.setPen(QPen(QColor(colors.border), 1))
                        painter.drawLine(int(px), int(py), int(kx), int(ky))

        for i, (name, ntype) in enumerate(self._nodes):
            if i not in pos:
                continue
            x, y = pos[i]
            c = colors.primary if ntype == "conclusion" else (colors.accent if ntype == "premise" else colors.text_disabled)
            painter.setBrush(QColor(c + "80"))
            painter.setPen(QPen(QColor(c), 1))
            painter.drawEllipse(int(x) - 8, int(y) - 8, 16, 16)
            painter.setFont(self._make_font(7))
            painter.setPen(QColor(colors.text_primary))
            painter.drawText(int(x) - 15, int(y) + 12, 30, 12, Qt.AlignCenter, name[:12])

        painter.end()
