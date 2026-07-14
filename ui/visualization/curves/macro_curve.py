from __future__ import annotations

from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget

from ui.visualization.core.base import BaseVisualization


class MacroCurve(BaseVisualization):
    """Macronutrient tracking curve — supports multiple macro series."""

    def __init__(
        self,
        color_scheme=None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(color_scheme, parent)
        self._series: dict[str, list[tuple[str, float]]] = {}
        self._colors_map: dict[str, str] = {}
        self.setFixedHeight(100)

    def set_data(
        self,
        series: dict[str, list[tuple[str, float]]] | None = None,
        colors_map: dict[str, str] | None = None,
    ) -> None:
        self._series = dict(series) if series else {}
        self._colors_map = dict(colors_map) if colors_map else {}
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        colors = self._colors()
        w, h = self.width(), 85
        if not self._series:
            return

        pad = 35
        pw = w - pad * 2
        all_vals = [v for s in self._series.values() for _, v in s]
        mx = max(all_vals) * 1.1 if all_vals else 100

        def yp(v): return h - 10 - (v / mx) * (h - 20) if mx > 0 else h / 2

        for si, (_sname, spts) in enumerate(self._series.items()):
            n = len(spts)
            if n < 2:
                continue
            sc = list(self._colors_map.values())[si] if self._colors_map else [colors.primary, colors.accent, colors.success][si % 3]
            step_x = pw / (n - 1) if n > 1 else 0

            for i in range(n - 1):
                x1, y1 = pad + i * step_x, yp(spts[i][1])
                x2, y2 = pad + (i + 1) * step_x, yp(spts[i + 1][1])
                painter.setPen(QPen(QColor(sc), 2))
                painter.drawLine(int(x1), int(y1), int(x2), int(y2))

        painter.end()
