from __future__ import annotations

from collections.abc import Sequence

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QFont, QPainter
from PySide6.QtWidgets import QFrame, QWidget

from ui.design_system.tokens.color import ColorScheme, color_from_scheme
from ui.design_system.tokens.radius import RadiusTokens, radius_to_px

R = RadiusTokens()


class MuscleHeatmap(QFrame):
    def __init__(
        self,
        muscles: Sequence[tuple[str, float]] | None = None,
        color_scheme: ColorScheme = ColorScheme.DARK,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._color_scheme = color_scheme
        self._muscles: list[tuple[str, float]] = list(muscles) if muscles else []
        self._max_volume = 100.0
        self.setFixedHeight(60)

    def _colors(self):
        return color_from_scheme(self._color_scheme)

    def set_data(self, muscles: Sequence[tuple[str, float]], max_volume: float = 100.0) -> None:
        self._muscles = list(muscles)
        self._max_volume = max(max_volume, 1.0)
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        colors = self._colors()
        w = self.width()
        h = 50
        n = len(self._muscles)
        if n == 0:
            return

        cell_w = min(80, (w - 20) // n - 4)
        start_x = 10

        for i, (name, volume) in enumerate(self._muscles):
            x = start_x + i * (cell_w + 4)
            fraction = min(volume / self._max_volume, 1.0) if self._max_volume > 0 else 0.0

            r = int(255 * fraction)
            g = int(80 * (1 - fraction))
            b = int(240 * (1 - fraction))
            cell_color = QColor(min(r + g, 255), min(g + 80, 255), min(b + 80, 255))

            painter.setBrush(cell_color)
            painter.setPen(Qt.NoPen)
            r = radius_to_px(R.md)
            painter.drawRoundedRect(x, 0, cell_w, h, r, r)

            font = QFont()
            font.setPixelSize(9)
            font.setBold(True)
            painter.setFont(font)
            painter.setPen(QColor(colors.text_inverse))
            painter.drawText(QRectF(x, 0, cell_w, h), Qt.AlignCenter, name)

        painter.end()
