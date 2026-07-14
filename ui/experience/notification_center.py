from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum

from PySide6.QtCore import QObject, Qt, QTimer, Signal
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ui.command_center.theme import C, Font

logger = logging.getLogger("experience.notifications")


class NotificationPriority(Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class NotificationItem:
    notification_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    title: str = ""
    message: str = ""
    priority: NotificationPriority = NotificationPriority.NORMAL
    source: str = "system"
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    read: bool = False
    dismissed: bool = False
    data: dict = field(default_factory=dict)


class NotificationToast(QFrame):
    dismissed = Signal(str)

    def __init__(self, item: NotificationItem, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._item = item
        self._build_ui()
        self._start_auto_dismiss()

    def _build_ui(self) -> None:
        border_color = {
            NotificationPriority.LOW: C.BORDER,
            NotificationPriority.NORMAL: C.ACCENT,
            NotificationPriority.HIGH: C.TEXT_WARN,
            NotificationPriority.CRITICAL: C.TEXT_DANGER,
        }.get(self._item.priority, C.BORDER)

        self.setStyleSheet(f"""
            NotificationToast {{
                background-color: {C.CARD_BG};
                border-radius: 8px;
                border-left: 3px solid {border_color};
                border-top: 1px solid {C.BORDER};
                border-right: 1px solid {C.BORDER};
                border-bottom: 1px solid {C.BORDER};
            }}
        """)
        self.setFixedHeight(70)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(8)

        icon = {
            NotificationPriority.LOW: "ℹ️",
            NotificationPriority.NORMAL: "🔔",
            NotificationPriority.HIGH: "⚠️",
            NotificationPriority.CRITICAL: "🚨",
        }.get(self._item.priority, "🔔")

        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 18px;")
        layout.addWidget(icon_label)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)

        title = QLabel(self._item.title)
        title.setStyleSheet(f"color: {C.TEXT_PRIMARY}; font-size: 13px; font-weight: 600;")
        title.setWordWrap(True)
        text_layout.addWidget(title)

        if self._item.message:
            msg = QLabel(self._item.message)
            msg.setStyleSheet(Font.MUTED)
            msg.setWordWrap(True)
            text_layout.addWidget(msg)

        layout.addLayout(text_layout, 1)

        close_label = QLabel("✕")
        close_label.setStyleSheet(f"color: {C.TEXT_MUTED}; font-size: 14px; padding: 4px;")
        close_label.setCursor(Qt.CursorShape.PointingHandCursor)
        close_label.mousePressEvent = lambda e: self._dismiss()
        layout.addWidget(close_label)

    def _start_auto_dismiss(self) -> None:
        timeout = {
            NotificationPriority.LOW: 3000,
            NotificationPriority.NORMAL: 5000,
            NotificationPriority.HIGH: 8000,
            NotificationPriority.CRITICAL: 12000,
        }.get(self._item.priority, 5000)
        QTimer.singleShot(timeout, self._animate_dismiss)

    def _animate_dismiss(self) -> None:
        self._dismiss()

    def _dismiss(self) -> None:
        self.dismissed.emit(self._item.notification_id)
        self.deleteLater()


class NotificationList(QFrame):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setStyleSheet(f"background-color: {C.CARD_BG}; border-radius: 8px; border: 1px solid {C.BORDER};")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QLabel("NOTIFICATIONS")
        header.setStyleSheet(Font.LABEL)
        header.setContentsMargins(16, 12, 16, 8)
        layout.addWidget(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(f"""
            QScrollArea {{ background-color: transparent; border: none; }}
            QScrollBar:vertical {{ background-color: {C.SCROLLBAR_BG}; width: 6px; border: none; }}
            QScrollBar::handle:vertical {{ background-color: {C.SCROLLBAR_HANDLE}; border-radius: 3px; min-height: 20px; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
        """)
        self._list_widget = QWidget()
        self._list_widget.setStyleSheet("background-color: transparent;")
        self._list_layout = QVBoxLayout(self._list_widget)
        self._list_layout.setContentsMargins(8, 4, 8, 4)
        self._list_layout.setSpacing(4)
        self._list_layout.addStretch()
        scroll.setWidget(self._list_widget)
        layout.addWidget(scroll)

    def add_item(self, item: NotificationItem) -> None:
        frame = self._build_item_frame(item)
        self._list_layout.insertWidget(self._list_layout.count() - 1, frame)

    def _build_item_frame(self, item: NotificationItem) -> QFrame:
        frame = QFrame()
        border_color = {
            NotificationPriority.LOW: C.BORDER,
            NotificationPriority.NORMAL: C.ACCENT,
            NotificationPriority.HIGH: C.TEXT_WARN,
            NotificationPriority.CRITICAL: C.TEXT_DANGER,
        }.get(item.priority, C.BORDER)
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: transparent;
                border-left: 2px solid {border_color};
                border-radius: 4px;
                padding: 4px;
            }}
        """)
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(8, 4, 8, 4)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)

        title = QLabel(item.title)
        title.setStyleSheet(f"color: {C.TEXT_PRIMARY}; font-size: 12px; font-weight: 600;")
        text_layout.addWidget(title)

        if item.message:
            msg = QLabel(item.message)
            msg.setStyleSheet(Font.CAPTION)
            msg.setWordWrap(True)
            text_layout.addWidget(msg)

        layout.addLayout(text_layout, 1)

        time_label = QLabel(item.timestamp.strftime("%H:%M"))
        time_label.setStyleSheet(Font.CAPTION)
        layout.addWidget(time_label)

        return frame

    def clear(self) -> None:
        while self._list_layout.count() > 1:
            item = self._list_layout.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()


class NotificationCenter(QObject):
    notification_received = Signal(str)
    notification_dismissed = Signal(str)
    all_cleared = Signal()

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._history: list[NotificationItem] = []
        self._toasts: dict[str, NotificationToast] = {}
        self._max_history: int = 100
        self._toast_container: QFrame | None = None
        self._setup_toast_container()

    def _setup_toast_container(self) -> None:
        for widget in QApplication.topLevelWidgets():
            if isinstance(widget, QWidget):
                self._toast_container = QFrame(widget)
                self._toast_container.setStyleSheet("background-color: transparent;")
                self._toast_container.setGeometry(widget.width() - 380, 60, 360, 0)
                self._toast_container.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
                self._toast_container.raise_()
                break

    def show_notification(
        self,
        title: str,
        message: str = "",
        priority: NotificationPriority = NotificationPriority.NORMAL,
        source: str = "system",
        duration: int | None = None,
    ) -> str:
        item = NotificationItem(
            title=title,
            message=message,
            priority=priority,
            source=source,
        )
        self._history.append(item)
        if len(self._history) > self._max_history:
            self._history.pop(0)

        if self._toast_container:
            toast = NotificationToast(item, self._toast_container)
            toast.dismissed.connect(self._on_toast_dismissed)
            y_offset = len(self._toasts) * 80
            toast.setGeometry(0, y_offset, 340, 68)
            toast.show()
            self._toasts[item.notification_id] = toast
            self._toast_container.adjustSize()

        self.notification_received.emit(item.notification_id)
        return item.notification_id

    def dismiss(self, notification_id: str) -> None:
        toast = self._toasts.pop(notification_id, None)
        if toast:
            toast.deleteLater()
        for item in self._history:
            if item.notification_id == notification_id:
                item.dismissed = True
                break
        self._reposition_toasts()
        self.notification_dismissed.emit(notification_id)

    def _on_toast_dismissed(self, notification_id: str) -> None:
        self.dismiss(notification_id)

    def _reposition_toasts(self) -> None:
        for i, (_nid, toast) in enumerate(self._toasts.items()):
            toast.setGeometry(0, i * 80, 340, 68)

    def clear_all(self) -> None:
        for toast in self._toasts.values():
            toast.deleteLater()
        self._toasts.clear()
        self._history.clear()
        self.all_cleared.emit()

    def mark_read(self, notification_id: str) -> None:
        for item in self._history:
            if item.notification_id == notification_id:
                item.read = True
                break

    def mark_all_read(self) -> None:
        for item in self._history:
            item.read = True

    @property
    def history(self) -> list[NotificationItem]:
        return list(self._history)

    @property
    def unread_count(self) -> int:
        return sum(1 for item in self._history if not item.read and not item.dismissed)

    @property
    def active_toasts(self) -> int:
        return len(self._toasts)

    def get_visible_items(self, limit: int = 20) -> list[NotificationItem]:
        visible = [item for item in self._history if not item.dismissed]
        return visible[-limit:]
