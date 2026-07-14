from __future__ import annotations

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
    QApplication,
)

from ui.design_system.components.command_bar import CommandBar
from ui.design_system.components.dialog_template import DialogTemplate
from ui.design_system.components.notification_toast import NotificationToast, ToastType
from ui.design_system.tokens.color import ColorScheme, color_from_scheme
from ui.design_system.tokens.spacing import SpacingTokens
from ui.experience.motion_service import MotionService
from ui.shell.header import ShellHeader
from ui.shell.sidebar import ShellSidebar, COLLAPSED_WIDTH, EXPANDED_WIDTH

SPACE = SpacingTokens()

PAGE_TITLES: dict[str, str] = {
    "dashboard": "Dashboard",
    "workout": "Workout",
    "workout_detail": "Workout",
    "progress": "Progress",
    "recovery": "Recovery",
    "predictions": "Predictions",
    "prs": "Records",
    "settings": "Settings",
}

NAV_ORDER: list[str] = [
    "dashboard", "workout", "workout_detail", "progress",
    "recovery", "predictions", "prs", "settings",
]


class AppShell(QFrame):
    page_switched = Signal(str, str)

    def __init__(self, motion: MotionService | None = None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._motion = motion
        self._active_page: str = ""
        self._toasts: list[NotificationToast] = []
        self._command_bar: CommandBar | None = None
        self._dialog_backdrop: QFrame | None = None
        self._page_indices: dict[str, int] = {}

        self._build_ui()
        self._install_shortcuts()

    def _get_colors(self):
        return color_from_scheme(ColorScheme.DARK)

    def _build_ui(self) -> None:
        c = self._get_colors()

        self.setStyleSheet(f"AppShell {{ background-color: {c.background}; }}")

        root_layout = QHBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        self._sidebar = ShellSidebar(self)
        self._sidebar.page_selected.connect(self._on_sidebar_page_selected)
        root_layout.addWidget(self._sidebar)

        right_column = QVBoxLayout()
        right_column.setContentsMargins(0, 0, 0, 0)
        right_column.setSpacing(0)

        self._header = ShellHeader(self)
        self._header.palette_triggered.connect(self._open_command_palette)
        right_column.addWidget(self._header)

        self._content = QStackedWidget()
        self._content.setAccessibleName("Content area")
        self._content.setStyleSheet(f"background-color: {c.background};")
        right_column.addWidget(self._content, 1)

        root_layout.addLayout(right_column, 1)

        self._toast_container = QFrame(self)
        self._toast_container.setStyleSheet("background-color: transparent;")
        self._toast_container.setGeometry(0, 0, 0, 0)
        self._toast_container.raise_()

        self._overlay_container = QFrame(self)
        self._overlay_container.setStyleSheet("background-color: transparent;")
        self._overlay_container.setVisible(False)
        self._overlay_container.raise_()

    def _install_shortcuts(self) -> None:
        pass

    @property
    def sidebar(self) -> ShellSidebar:
        return self._sidebar

    @property
    def header(self) -> ShellHeader:
        return self._header

    @property
    def content(self) -> QStackedWidget:
        return self._content

    def add_page(self, widget: QWidget, page_id: str) -> None:
        if self._content.indexOf(widget) == -1:
            self._content.addWidget(widget)
            idx = self._content.indexOf(widget)
            self._page_indices[page_id] = idx

    def switch_to(self, page_id: str, source: str = "sidebar") -> None:
        if page_id == self._active_page:
            return

        old_page = self._content.currentWidget()
        self._active_page = page_id
        self._sidebar.set_active(page_id)

        title = PAGE_TITLES.get(page_id, page_id.replace("_", " ").title())
        self._header.set_page_title(title)
        self._header.set_breadcrumb("")

        if page_id not in self._page_indices:
            self.page_switched.emit(page_id, source)
            return

        idx = self._page_indices[page_id]
        new_page = self._content.widget(idx)

        if self._motion:
            def _do_switch() -> None:
                self._content.setCurrentIndex(idx)
                self.page_switched.emit(page_id, source)
            self._motion.transition_page(old_page, new_page, _do_switch)
        else:
            self._content.setCurrentIndex(idx)
            self.page_switched.emit(page_id, source)

    def page_index(self, page_id: str) -> int | None:
        return self._page_indices.get(page_id)

    def _on_sidebar_page_selected(self, page_id: str) -> None:
        self.switch_to(page_id, "sidebar")

    @property
    def active_page(self) -> str:
        return self._active_page

    def toggle_sidebar(self) -> None:
        expanded = not self._sidebar.is_expanded
        target_w = EXPANDED_WIDTH if expanded else COLLAPSED_WIDTH
        self._sidebar.set_expanded(expanded)
        if self._motion:
            self._motion.animate_width(self._sidebar, target_w, duration=200)
        else:
            self._sidebar.setFixedWidth(target_w)

    def show_notification(
        self,
        message: str,
        title: str = "",
        toast_type: ToastType = ToastType.INFO,
        duration_ms: int = 4000,
    ) -> None:
        toast = NotificationToast(
            message=message,
            title=title,
            toast_type=toast_type,
            duration_ms=duration_ms,
            parent=self._toast_container,
        )
        toast.dismissed.connect(lambda: self._remove_toast(toast))
        self._toasts.append(toast)
        self._reposition_toasts()

        toast.show()

    def _remove_toast(self, toast: NotificationToast) -> None:
        if toast in self._toasts:
            self._toasts.remove(toast)
        self._reposition_toasts()

    def _reposition_toasts(self) -> None:
        parent_w = self.width()
        toast_w = 360
        x = parent_w - toast_w - 20
        y = 60
        for toast in self._toasts:
            toast.setGeometry(x, y, toast_w - 10, 0)
            toast.adjustSize()
            toast.setFixedWidth(toast_w - 10)
            toast.setGeometry(x, y, toast_w - 10, toast.height())
            y += toast.height() + 8

    def show_dialog(
        self,
        title: str,
        message: str,
        confirm_text: str = "Confirm",
        destructive: bool = False,
    ) -> bool:
        dlg = DialogTemplate(
            title=title,
            message=message,
            confirm_text=confirm_text,
            destructive=destructive,
            parent=self,
        )
        dlg.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        dlg.setModal(True)

        self._show_backdrop()

        result = dlg.exec()

        self._hide_backdrop()
        return dlg.result()

    def _show_backdrop(self) -> None:
        backdrop = QFrame(self)
        c = self._get_colors()
        backdrop.setStyleSheet(
            f"background-color: rgba(0, 0, 0, 140); border: none;"
        )
        backdrop.setGeometry(self.rect())
        backdrop.raise_()
        backdrop.show()
        self._dialog_backdrop = backdrop

    def _hide_backdrop(self) -> None:
        if self._dialog_backdrop:
            self._dialog_backdrop.deleteLater()
            self._dialog_backdrop = None

    def _open_command_palette(self) -> None:
        if self._command_bar and self._command_bar.isVisible():
            self._command_bar.hide_command_bar()
            return

        if not self._command_bar:
            self._command_bar = CommandBar(
                placeholder="Type a command or page name...",
                commands=[
                    ("dashboard", "Go to Dashboard"),
                    ("workout", "Go to Workout"),
                    ("progress", "Go to Progress"),
                    ("recovery", "Go to Recovery"),
                    ("predictions", "Go to Predictions"),
                    ("prs", "Go to Records"),
                    ("settings", "Go to Settings"),
                ],
                parent=self,
            )
            self._command_bar.command_selected.connect(self._on_command_selected)
            self._command_bar.dismissed.connect(self._on_palette_dismissed)

        bar_w = 520
        bar_h = 360
        x = (self.width() - bar_w) // 2
        y = self._header.height() + 40
        self._command_bar.setGeometry(x, y, bar_w, bar_h)
        self._command_bar.show_command_bar()
        self._command_bar.raise_()

    def _on_command_selected(self, command_id: str) -> None:
        if command_id in NAV_ORDER:
            self._on_sidebar_page_selected(command_id)

    def _on_palette_dismissed(self) -> None:
        pass

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        if self._command_bar and self._command_bar.isVisible():
            bar_w = 520
            x = (self.width() - bar_w) // 2
            y = self._header.height() + 40
            self._command_bar.setGeometry(x, y, bar_w, 360)

        self._reposition_toasts()

        if self._dialog_backdrop:
            self._dialog_backdrop.setGeometry(self.rect())
