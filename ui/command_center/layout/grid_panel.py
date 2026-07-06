from __future__ import annotations

from PySide6.QtWidgets import QGridLayout, QWidget


class GridPanel(QWidget):
    """Responsive grid layout that arranges widgets in columns."""

    def __init__(self, columns: int = 3, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._columns = columns
        self._grid = QGridLayout()
        self._grid.setContentsMargins(0, 0, 0, 0)
        self._grid.setSpacing(12)
        self.setLayout(self._grid)
        self._widgets: list[QWidget] = []

    def add_widget(self, widget: QWidget, col_span: int = 1) -> None:
        idx = len(self._widgets)
        row = idx // self._columns
        col = idx % self._columns
        self._grid.addWidget(widget, row, col, 1, col_span)
        self._widgets.append(widget)

    def add_widget_at(self, widget: QWidget, row: int, col: int,
                      row_span: int = 1, col_span: int = 1) -> None:
        self._grid.addWidget(widget, row, col, row_span, col_span)
        self._widgets.append(widget)

    def clear(self) -> None:
        while self._grid.count():
            item = self._grid.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()
        self._widgets.clear()

    def set_columns(self, columns: int) -> None:
        self._columns = columns
        self._relayout()

    def _relayout(self) -> None:
        old_widgets = list(self._widgets)
        self.clear()
        for w in old_widgets:
            idx = len(self._widgets)
            row = idx // self._columns
            col = idx % self._columns
            self._grid.addWidget(w, row, col)
            self._widgets.append(w)

    def column_count(self) -> int:
        return self._columns
