from __future__ import annotations

from collections.abc import Sequence

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QWidget

from ui.design_system.tokens.radius import radius_to_px
from ui.visualization.core.base import RADIUS, BaseVisualization


class ComparisonChart(BaseVisualization):
    """Grouped bar chart comparing values across categories."""

    def __init__(
        self,
        color_scheme=None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(color_scheme, parent)
        self._groups: list[tuple[str, list[tuple[str, float]]]] = []
        self._max_val = 100.0
        self.setFixedHeight(100)

    def set_data(self, groups: Sequence[tuple[str, list[tuple[str, float]]]] | None = None, max_val: float = 100.0) -> None:
        self._groups = list(groups) if groups else []
        self._max_val = max(max_val, 1.0)
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        colors = self._colors()
        w = self.width()
        h = 85
        ng = len(self._groups)
        if ng == 0:
            return

        group_w = (w - 20) / ng
        r = radius_to_px(RADIUS.sm)

        group_colors = [colors.primary, colors.secondary, colors.accent, colors.success]

        for gi, (glabel, items) in enumerate(self._groups):
            ni = len(items)
            bar_w = max(4, (group_w - 8) / max(ni, 1))
            base_x = 10 + gi * group_w

            for ii, (ilabel, ival) in enumerate(items):
                x = base_x + ii * bar_w + 2
                fraction = min(ival / self._max_val, 1.0)
                bar_h = max(int(fraction * (h - 20)), 0)
                bar_y = h - 10 - bar_h
                c = group_colors[ii % len(group_colors)]
                painter.setBrush(QColor(c))
                painter.setPen(Qt.NoPen)
                painter.drawRoundedRect(x, bar_y, bar_w - 2, bar_h, r, r)

            painter.setFont(self._make_font(8))
            painter.setPen(QColor(colors.text_disabled))
            painter.drawText(QRectF(base_x, h - 8, group_w, 14), Qt.AlignCenter, glabel)

        painter.end()
