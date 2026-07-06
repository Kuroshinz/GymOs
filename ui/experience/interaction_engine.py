from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from PySide6.QtCore import QEvent, QObject, Qt, Signal
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import QApplication, QWidget

from ui.command_center.theme import C

logger = logging.getLogger("experience.interaction")


@dataclass
class HoverEffect:
    widget_id: str
    enter_style: str = ""
    leave_style: str = ""
    scale_on_hover: float = 1.0
    opacity_on_hover: float = 1.0
    cursor_shape: int = Qt.CursorShape.PointingHandCursor


@dataclass
class DragDropConfig:
    widget_id: str
    drag_enabled: bool = False
    drop_enabled: bool = False
    mime_type: str = "application/x-gymos-widget"
    drag_data_fn: Callable[[], Any] | None = None
    accept_fn: Callable[[Any], bool] | None = None
    drop_fn: Callable[[Any], None] | None = None


class HoverWatcher(QObject):
    entered = Signal(str)
    exited = Signal(str)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._effects: dict[str, HoverEffect] = {}
        self._installed: dict[str, QWidget] = {}

    def register(self, widget: QWidget, effect: HoverEffect) -> None:
        self._effects[effect.widget_id] = effect
        self._installed[effect.widget_id] = widget
        widget.installEventFilter(self)
        widget.setCursor(QCursor(effect.cursor_shape))

    def unregister(self, widget_id: str) -> None:
        widget = self._installed.pop(widget_id, None)
        if widget:
            widget.removeEventFilter(self)
        self._effects.pop(widget_id, None)

    def eventFilter(self, obj: QWidget | None, event: QEvent | None) -> bool:
        if event is None or obj is None:
            return super().eventFilter(obj, event)

        for wid, widget in self._installed.items():
            if widget is obj:
                effect = self._effects.get(wid)
                if effect is None:
                    continue
                if event.type() == QEvent.Type.Enter:
                    self.entered.emit(wid)
                    if effect.enter_style:
                        widget.setStyleSheet(effect.enter_style)
                    return True
                elif event.type() == QEvent.Type.Leave:
                    self.exited.emit(wid)
                    if effect.leave_style:
                        widget.setStyleSheet(effect.leave_style)
                    return True
                elif event.type() == QEvent.Type.MouseButtonPress:
                    QApplication.setOverrideCursor(QCursor(Qt.CursorShape.ClosedHandCursor))
                elif event.type() == QEvent.Type.MouseButtonRelease:
                    QApplication.restoreOverrideCursor()
                break
        return super().eventFilter(obj, event)


class TooltipManager(QObject):
    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)

    def register_tooltip(self, widget: QWidget, text: str, delay: int = 500) -> None:
        widget.setToolTip(text)
        widget.setToolTipDuration(delay)


class InteractionEngine(QObject):
    hover_entered = Signal(str)
    hover_exited = Signal(str)
    drag_started = Signal(str)
    drop_completed = Signal(str, str)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._hover = HoverWatcher(self)
        self._tooltips = TooltipManager(self)
        self._drag_drop: dict[str, DragDropConfig] = {}
        self._hover.entered.connect(self.hover_entered.emit)
        self._hover.exited.connect(self.hover_exited.emit)

    @property
    def hover(self) -> HoverWatcher:
        return self._hover

    @property
    def tooltips(self) -> TooltipManager:
        return self._tooltips

    def register_hover(
        self,
        widget: QWidget,
        widget_id: str,
        enter_style: str = "",
        leave_style: str = "",
        cursor: int = Qt.CursorShape.PointingHandCursor,
    ) -> None:
        effect = HoverEffect(
            widget_id=widget_id,
            enter_style=enter_style or f"""
                {widget.__class__.__name__} {{
                    background-color: {C.CARD_HOVER};
                    border-radius: 8px;
                    border: 1px solid {C.BORDER_HOVER};
                }}
            """,
            leave_style=leave_style or "",
            cursor_shape=cursor,
        )
        self._hover.register(widget, effect)

    def register_tooltip(self, widget: QWidget, text: str, delay: int = 500) -> None:
        self._tooltips.register_tooltip(widget, text, delay)

    def register_drag_drop(self, config: DragDropConfig) -> None:
        self._drag_drop[config.widget_id] = config

    def unregister_drag_drop(self, widget_id: str) -> None:
        self._drag_drop.pop(widget_id, None)

    def clear_all(self) -> None:
        self._hover._effects.clear()
        self._hover._installed.clear()
        self._drag_drop.clear()
