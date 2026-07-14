from __future__ import annotations

from PySide6.QtCore import QPoint, Qt, Signal
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QFrame, QSizePolicy, QWidget

from ui.command_center.theme import C


class ResizableWidget(QFrame):
    resized = Signal(int, int)

    RESIZE_MARGIN = 6

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._resizing = False
        self._resize_edge = 0
        self._drag_start = QPoint()
        self._drag_start_size = (0, 0)
        self._min_w = 200
        self._min_h = 100
        self.setMouseTracking(True)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setStyleSheet(f"""
            ResizableWidget {{
                background-color: {C.CARD_BG};
                border-radius: 8px;
                border: 1px solid {C.BORDER};
            }}
        """)

    def set_minimum_size(self, w: int, h: int) -> None:
        self._min_w = w
        self._min_h = h

    def mousePressEvent(self, event: QMouseEvent | None) -> None:  # noqa: N802
        if event and event.button() == Qt.LeftButton:
            edge = self._hit_edge(event.position().toPoint())
            if edge:
                self._resizing = True
                self._resize_edge = edge
                self._drag_start = event.position().toPoint()
                self._drag_start_size = (self.width(), self.height())
                self.setCursor(self._edge_cursor(edge))

    def mouseMoveEvent(self, event: QMouseEvent | None) -> None:  # noqa: N802
        if not event:
            return
        if self._resizing:
            dx = event.position().toPoint().x() - self._drag_start.x()
            dy = event.position().toPoint().y() - self._drag_start.y()
            new_w, new_h = self._drag_start_size
            edge = self._resize_edge

            if edge & 1:
                new_w = max(self._min_w, new_w + dx)
            if edge & 2:
                new_h = max(self._min_h, new_h + dy)

            self.resize(new_w, new_h)
            self.resized.emit(new_w, new_h)
        else:
            edge = self._hit_edge(event.position().toPoint())
            self.setCursor(self._edge_cursor(edge))

    def mouseReleaseEvent(self, event: QMouseEvent | None) -> None:  # noqa: N802
        self._resizing = False
        self._resize_edge = 0
        self.setCursor(Qt.ArrowCursor)

    def _hit_edge(self, pos: QPoint) -> int:
        w, h = self.width(), self.height()
        edge = 0
        if pos.x() >= w - self.RESIZE_MARGIN:
            edge |= 1
        if pos.y() >= h - self.RESIZE_MARGIN:
            edge |= 2
        return edge

    def _edge_cursor(self, edge: int) -> Qt.CursorShape:
        if edge == 1:
            return Qt.SizeHorCursor
        if edge == 2:
            return Qt.SizeVerCursor
        if edge == 3:
            return Qt.SizeFDiagCursor
        return Qt.ArrowCursor
