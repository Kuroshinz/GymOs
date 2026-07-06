from __future__ import annotations

from collections.abc import Sequence

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget

from ui.visualization.core.base import BaseVisualization


class AdaptationTimeline(BaseVisualization):
    """Event-based timeline showing adaptations and decisions as nodes."""

    def _status_color(self, status: str) -> str:
        colors = self._colors()
        return {
            "approved": colors.success,
            "rejected": colors.error,
            "pending": colors.warning,
            "active": colors.info,
            "completed": colors.success,
            "failed": colors.error,
        }.get(status, colors.text_disabled)

    def __init__(
        self,
        color_scheme=None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(color_scheme, parent)
        self._items: list[tuple[str, str, str]] = []
        self.setFixedHeight(80)

    def set_data(self, items: Sequence[tuple[str, str, str]] | None = None) -> None:
        self._items = list(items) if items else []
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        colors = self._colors()
        w = self.width()
        h = 60
        n = len(self._items)
        if n == 0:
            return

        mid_y = h // 2
        painter.setPen(QPen(QColor(colors.border), 1))
        painter.drawLine(20, mid_y, w - 20, mid_y)

        spacing = (w - 40) / max(n, 1)

        for i, (label, status, date) in enumerate(self._items):
            x = 20 + i * spacing + spacing / 2
            c = self._status_color(status)
            painter.setBrush(QColor(c))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(int(x) - 6, mid_y - 6, 12, 12)

            painter.setFont(self._make_font(9))
            painter.setPen(QColor(colors.text_primary))
            painter.drawText(QRectF(int(x) - 25, mid_y + 10, 50, 14), Qt.AlignCenter, label)

            painter.setFont(self._make_font(7))
            painter.setPen(QColor(colors.text_disabled))
            painter.drawText(QRectF(int(x) - 25, mid_y - 22, 50, 12), Qt.AlignCenter, date)

        painter.end()
