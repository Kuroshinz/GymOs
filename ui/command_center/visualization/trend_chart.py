from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from ui.command_center.theme import C, Font


class TrendChart(QFrame):
    MIN_DATA_POINTS = 2

    def __init__(self, title: str = "", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._title = title
        self._data: list[float] = []
        self._labels: list[str] = []
        self._line_color = QColor(C.ACCENT)
        self._fill_color = QColor(C.ACCENT)
        self._fill_color.setAlpha(30)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)

        if self._title:
            header = QHBoxLayout()
            title_label = QLabel(self._title)
            title_label.setStyleSheet(Font.LABEL)
            header.addWidget(title_label)
            header.addStretch()
            self._trend_label = QLabel("")
            self._trend_label.setStyleSheet("font-size: 12px;")
            header.addWidget(self._trend_label)
            layout.addLayout(header)

        self._canvas = _ChartCanvas(self._line_color, self._fill_color)
        self._canvas.setMinimumHeight(80)
        layout.addWidget(self._canvas, 1)

    def set_data(self, data: list[float], labels: list[str] | None = None) -> None:
        self._data = data
        self._labels = labels or []
        self._update_trend()
        self._canvas.set_data(data)
        self._canvas.update()

    def set_colors(self, line_color: str, fill_color: str | None = None) -> None:
        self._line_color = QColor(line_color)
        self._fill_color = QColor(fill_color or line_color)
        self._fill_color.setAlpha(30)
        self._canvas.set_colors(self._line_color, self._fill_color)

    def _update_trend(self) -> None:
        if len(self._data) < 2:
            self._trend_label.setText("")
            return
        slope = self._data[-1] - self._data[0]
        if slope > 0.01:
            self._trend_label.setText("↑ Trending Up")
            self._trend_label.setStyleSheet(f"font-size: 12px; color: {C.TEXT_SUCCESS};")
        elif slope < -0.01:
            self._trend_label.setText("↓ Trending Down")
            self._trend_label.setStyleSheet(f"font-size: 12px; color: {C.TEXT_DANGER};")
        else:
            self._trend_label.setText("→ Stable")
            self._trend_label.setStyleSheet(f"font-size: 12px; color: {C.TEXT_MUTED};")


class _ChartCanvas(QFrame):
    def __init__(self, line_color: QColor, fill_color: QColor, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._data: list[float] = []
        self._line_color = line_color
        self._fill_color = fill_color
        self.setStyleSheet(f"background-color: {C.CARD_BG}; border-radius: 8px;")

    def set_data(self, data: list[float]) -> None:
        self._data = data

    def set_colors(self, line_color: QColor, fill_color: QColor) -> None:
        self._line_color = line_color
        self._fill_color = fill_color

    def paintEvent(self, event) -> None:
        if len(self._data) < 2:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()
        padding = 4
        plot_w = w - padding * 2
        plot_h = h - padding * 2

        data_min = min(self._data)
        data_max = max(self._data)
        data_range = data_max - data_min or 1.0

        points: list[tuple[float, float]] = []
        for i, val in enumerate(self._data):
            x = padding + (i / max(len(self._data) - 1, 1)) * plot_w
            y = padding + plot_h - ((val - data_min) / data_range) * plot_h
            points.append((x, y))

        pen = QPen(self._line_color, 2)
        painter.setPen(pen)
        for i in range(len(points) - 1):
            painter.drawLine(
                int(points[i][0]), int(points[i][1]),
                int(points[i + 1][0]), int(points[i + 1][1]),
            )

        fill_pen = QPen(Qt.NoPen)
        painter.setPen(fill_pen)
        painter.setBrush(self._fill_color)
        path_poly = [QPoint(padding, int(padding + plot_h))] if False else []
        from PySide6.QtCore import QPointF
        from PySide6.QtGui import QPainterPath

        path = QPainterPath()
        path.moveTo(QPointF(points[0][0], padding + plot_h))
        for px, py in points:
            path.lineTo(QPointF(px, py))
        path.lineTo(QPointF(points[-1][0], padding + plot_h))
        path.closeSubpath()
        painter.drawPath(path)

        painter.end()
