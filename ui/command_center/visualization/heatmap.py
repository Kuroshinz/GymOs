from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor, QPainter
from PySide6.QtWidgets import QFrame, QWidget

from ui.command_center.theme import C


class HeatmapWidget(QFrame):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._data: list[list[float]] = []
        self._row_labels: list[str] = []
        self._col_labels: list[str] = []
        self._cell_size = 24
        self._gap = 2
        self._build_ui()

    def _build_ui(self) -> None:
        self.setMinimumHeight(120)
        self.setStyleSheet(f"background-color: {C.CARD_BG}; border-radius: 8px;")

    def set_data(self, data: list[list[float]],
                 row_labels: list[str] | None = None,
                 col_labels: list[str] | None = None) -> None:
        self._data = data
        self._row_labels = row_labels or []
        self._col_labels = col_labels or []
        self.update()

    def paintEvent(self, event) -> None:
        if not self._data:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rows = len(self._data)
        cols = max(len(row) for row in self._data) if self._data else 0
        label_w = 60
        x_start = label_w + 8
        y_start = 20

        for r in range(rows):
            if r < len(self._row_labels):
                painter.setPen(QColor(C.TEXT_MUTED))
                font = painter.font()
                font.setPixelSize(9)
                painter.setFont(font)
                painter.drawText(4, y_start + r * (self._cell_size + self._gap),
                                 label_w - 4, self._cell_size,
                                 Qt.AlignRight | Qt.AlignVCenter,
                                 self._row_labels[r])

            for c in range(min(cols, len(self._data[r]))):
                val = self._data[r][c]
                intensity = max(0.0, min(1.0, val))
                r_val = int(30 + (129 - 30) * intensity)
                g_val = int(41 + (140 - 41) * (1 - intensity))
                b_val = int(59 + (248 - 59) * intensity)
                cell_color = QColor(r_val, g_val, b_val)
                painter.setBrush(QBrush(cell_color))
                painter.setPen(Qt.NoPen)
                x = x_start + c * (self._cell_size + self._gap)
                y = y_start + r * (self._cell_size + self._gap)
                painter.drawRoundedRect(x, y, self._cell_size, self._cell_size, 3, 3)

                if val >= 0.7:
                    painter.setPen(QColor(C.TEXT_PRIMARY))
                else:
                    painter.setPen(QColor(C.TEXT_MUTED))
                pct = int(val * 100)
                painter.drawText(x, y, self._cell_size, self._cell_size,
                                 Qt.AlignCenter, str(pct))

        painter.end()
