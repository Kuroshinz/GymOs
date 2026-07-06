from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import Any

from PySide6.QtCore import QObject, Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ui.command_center.theme import C, Font

logger = logging.getLogger("experience.layout")


@dataclass
class Breakpoint:
    name: str
    min_width: int
    columns: int


DEFAULT_BREAKPOINTS = [
    Breakpoint("xs", 0, 1),
    Breakpoint("sm", 640, 2),
    Breakpoint("md", 960, 3),
    Breakpoint("lg", 1280, 4),
    Breakpoint("xl", 1600, 6),
]


@dataclass
class LayoutConfig:
    columns: int = 3
    spacing: int = 12
    margin_h: int = 32
    margin_v: int = 24
    breakpoints: list[Breakpoint] = field(default_factory=lambda: DEFAULT_BREAKPOINTS)
    responsive: bool = True
    persist_key: str = ""


@dataclass
class PanelState:
    widget_id: str
    visible: bool = True
    column: int = 0
    row: int = 0
    width_span: int = 1
    height_span: int = 1
    minimized: bool = False
    floating: bool = False


class PanelContainer(QFrame):
    closed = Signal(str)
    toggled = Signal(str, bool)

    def __init__(
        self,
        widget_id: str,
        widget: QWidget,
        title: str = "",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._id = widget_id
        self._widget = widget
        self._title = title
        self._minimized = False
        self._build_ui()

    def _build_ui(self) -> None:
        self.setStyleSheet(f"""
            PanelContainer {{
                background-color: {C.CARD_BG};
                border-radius: 8px;
                border: 1px solid {C.BORDER};
            }}
            PanelContainer:hover {{
                border-color: {C.BORDER_HOVER};
            }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        if self._title:
            header = QFrame()
            header.setStyleSheet("background-color: transparent; border: none;")
            header_layout = QHBoxLayout(header)
            header_layout.setContentsMargins(12, 8, 12, 8)

            title_label = QLabel(self._title.upper())
            title_label.setStyleSheet(Font.LABEL)
            header_layout.addWidget(title_label)
            header_layout.addStretch()

            layout.addWidget(header)

        self._content = QVBoxLayout()
        self._content.setContentsMargins(12, 8, 12, 12)
        self._content.addWidget(self._widget)
        layout.addLayout(self._content)

    @property
    def widget_id(self) -> str:
        return self._id

    @property
    def minimized(self) -> bool:
        return self._minimized

    def set_minimized(self, minimized: bool) -> None:
        self._minimized = minimized
        self._content.parentWidget().setVisible(not minimized)
        self.toggled.emit(self._id, minimized)


class ResponsiveGrid(QWidget):
    layout_changed = Signal()

    def __init__(self, config: LayoutConfig | None = None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._config = config or LayoutConfig()
        self._panels: dict[str, PanelContainer] = {}
        self._states: dict[str, PanelState] = {}
        self._grid = QGridLayout()
        self._grid.setSpacing(self._config.spacing)
        self._grid.setContentsMargins(
            self._config.margin_h, self._config.margin_v,
            self._config.margin_h, self._config.margin_v,
        )
        self.setLayout(self._grid)

    def add_panel(
        self,
        widget_id: str,
        widget: QWidget,
        title: str = "",
        column: int = 0,
        row: int = -1,
        width_span: int = 1,
        height_span: int = 1,
    ) -> PanelContainer:
        panel = PanelContainer(widget_id, widget, title, self)
        container = self._states.get(widget_id, PanelState(widget_id=widget_id))
        container.column = column
        container.width_span = width_span
        container.height_span = height_span
        if row >= 0:
            container.row = row

        actual_row = container.row if row < 0 else row
        self._grid.addWidget(panel, actual_row, container.column, container.height_span, container.width_span)
        self._panels[widget_id] = panel
        self._states[widget_id] = container
        return panel

    def remove_panel(self, widget_id: str) -> None:
        panel = self._panels.pop(widget_id, None)
        if panel:
            self._grid.removeWidget(panel)
            panel.deleteLater()
        self._states.pop(widget_id, None)

    def clear(self) -> None:
        for panel in self._panels.values():
            self._grid.removeWidget(panel)
            panel.deleteLater()
        self._panels.clear()
        self._states.clear()

    def set_columns(self, count: int) -> None:
        self._config.columns = count
        self._relayout()

    def panel(self, widget_id: str) -> PanelContainer | None:
        return self._panels.get(widget_id)

    def state(self, widget_id: str) -> PanelState | None:
        return self._states.get(widget_id)

    def save_state(self) -> dict:
        return {
            wid: {
                "visible": s.visible,
                "column": s.column,
                "row": s.row,
                "width_span": s.width_span,
                "height_span": s.height_span,
                "minimized": s.minimized,
            }
            for wid, s in self._states.items()
        }

    def load_state(self, state: dict) -> None:
        for wid, data in state.items():
            existing = self._states.get(wid)
            if existing:
                existing.visible = data.get("visible", True)
                existing.column = data.get("column", 0)
                existing.row = data.get("row", 0)
                existing.width_span = data.get("width_span", 1)
                existing.height_span = data.get("height_span", 1)
                existing.minimized = data.get("minimized", False)
        self._relayout()

    def _relayout(self) -> None:
        while self._grid.count():
            item = self._grid.takeAt(0)
            if item and item.widget():
                item.widget().setParent(None)
        for wid, panel in self._panels.items():
            state = self._states.get(wid)
            if state and state.visible:
                self._grid.addWidget(panel, state.row, state.column, state.height_span, state.width_span)
        self.layout_changed.emit()

    def resizeEvent(self, event: Any) -> None:
        super().resizeEvent(event)
        if self._config.responsive:
            self._adjust_columns()

    def _adjust_columns(self) -> None:
        width = self.width()
        best = self._config.columns
        for bp in sorted(self._config.breakpoints, key=lambda x: x.min_width, reverse=True):
            if width >= bp.min_width:
                best = bp.columns
                break
        if best != self._config.columns:
            self._config.columns = best
            self._relayout()


class LayoutEngine(QObject):
    layout_saved = Signal(str)
    layout_loaded = Signal(str)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._grids: dict[str, ResponsiveGrid] = {}
        self._layouts: dict[str, dict] = {}

    def register_grid(self, grid_id: str, grid: ResponsiveGrid) -> None:
        self._grids[grid_id] = grid

    def unregister_grid(self, grid_id: str) -> None:
        self._grids.pop(grid_id, None)

    def grid(self, grid_id: str) -> ResponsiveGrid | None:
        return self._grids.get(grid_id)

    def save_layout(self, name: str) -> dict:
        layout = {
            grid_id: grid.save_state()
            for grid_id, grid in self._grids.items()
        }
        self._layouts[name] = layout
        self.layout_saved.emit(name)
        return layout

    def load_layout(self, name: str) -> bool:
        layout = self._layouts.get(name)
        if not layout:
            return False
        for grid_id, state in layout.items():
            grid = self._grids.get(grid_id)
            if grid:
                grid.load_state(state)
        self.layout_loaded.emit(name)
        return True

    def serialize_layout(self, name: str) -> str | None:
        layout = self._layouts.get(name)
        if layout is None:
            return None
        return json.dumps(layout, indent=2)

    def deserialize_layout(self, name: str, data: str) -> bool:
        try:
            layout = json.loads(data)
            self._layouts[name] = layout
            return True
        except (json.JSONDecodeError, TypeError):
            logger.warning("Failed to deserialize layout '%s'", name)
            return False

    def list_layouts(self) -> list[str]:
        return list(self._layouts.keys())

    def delete_layout(self, name: str) -> None:
        self._layouts.pop(name, None)

    def create_scroll_page(self, parent: QWidget | None = None) -> tuple[QScrollArea, QWidget]:
        scroll = QScrollArea(parent)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(f"""
            QScrollArea {{ background-color: {C.BG}; border: none; }}
            QScrollBar:vertical {{ background-color: {C.SCROLLBAR_BG}; width: 8px; border: none; }}
            QScrollBar::handle:vertical {{ background-color: {C.SCROLLBAR_HANDLE}; border-radius: 4px; min-height: 30px; }}
            QScrollBar::handle:vertical:hover {{ background-color: {C.SCROLLBAR_HOVER}; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
        """)
        content = QWidget()
        content.setStyleSheet(f"background-color: {C.BG};")
        scroll.setWidget(content)
        return scroll, content
