from __future__ import annotations

import logging

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QWidget

from ui.command_center.models import CommandCenterData
from ui.experience.animation_manager import AnimationManager
from ui.experience.command_palette_engine import CommandItem, CommandPaletteEngine
from ui.experience.empty_state_manager import EmptyStateManager
from ui.experience.focus_mode import FocusMode
from ui.experience.interaction_engine import InteractionEngine
from ui.experience.layout_engine import LayoutEngine
from ui.experience.loading_state_manager import LoadingStateManager
from ui.experience.navigation_engine import NavigationEngine, Route
from ui.experience.notification_center import NotificationCenter
from ui.experience.search_provider import SearchProvider, SearchResult
from ui.experience.shortcut_manager import Shortcut, ShortcutManager
from ui.experience.theme_transition_manager import ThemeTransitionManager
from ui.experience.window_layout_manager import WindowLayoutManager
from ui.experience.workflow_engine import WorkflowEngine
from ui.experience.workspace_manager import WorkspaceManager

logger = logging.getLogger("experience.manager")


class ExperienceManager(QObject):
    initialized = Signal()
    shutdown_started = Signal()
    data_updated = Signal(object)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)

        self.animation = AnimationManager(self)
        self.layout = LayoutEngine(self)
        self.navigation = NavigationEngine(self)
        self.interaction = InteractionEngine(self)
        self.shortcuts = ShortcutManager(self)
        self.command_palette = CommandPaletteEngine(self)
        self.search = SearchProvider(self)
        self.notifications = NotificationCenter(self)
        self.loading = LoadingStateManager(self)
        self.empty_states = EmptyStateManager(self)
        self.focus = FocusMode(self)
        self.window_layout = WindowLayoutManager(self)
        self.workspaces = WorkspaceManager(self)
        self.workflows = WorkflowEngine(self)
        self.theme_transition = ThemeTransitionManager(self)

        self._builtin_shortcuts_registered = False
        self._builtin_commands_registered = False

    def initialize(self) -> None:
        self._register_builtin_shortcuts()
        self._register_builtin_commands()
        self._register_search_providers()
        self.theme_transition.set_animation_manager(self.animation)
        logger.info("Experience Platform initialized")
        self.initialized.emit()

    def _register_builtin_shortcuts(self) -> None:
        if self._builtin_shortcuts_registered:
            return

        self.shortcuts.register_many([
            Shortcut("toggle_command_palette", "Ctrl+K", self._open_command_palette, "Open command palette", "navigation"),
            Shortcut("toggle_focus", "Ctrl+Shift+F", self.focus.toggle, "Toggle focus mode", "navigation"),
            Shortcut("go_back", "Alt+Left", self.navigation.go_back, "Go back", "navigation"),
            Shortcut("go_forward", "Alt+Right", self.navigation.go_forward, "Go forward", "navigation"),
            Shortcut("global_search", "Ctrl+Shift+P", self._open_global_search, "Global search", "navigation"),
            Shortcut("refresh", "Ctrl+R", self._refresh_current, "Refresh current view", "navigation"),
            Shortcut("escape_focus", "Escape", self._handle_escape, "Exit focus/close palette", "navigation"),
        ])
        self._builtin_shortcuts_registered = True

    def _register_builtin_commands(self) -> None:
        if self._builtin_commands_registered:
            return

        self.command_palette.register_many([
            CommandItem("focus_mode", "Toggle Focus Mode", "Enter or exit distraction-free mode", "navigation", "Ctrl+Shift+F", "", self.focus.toggle),
            CommandItem("go_back", "Go Back", "Navigate to previous page", "navigation", "Alt+Left", "", lambda: self.navigation.go_back()),
            CommandItem("go_forward", "Go Forward", "Navigate to next page", "navigation", "Alt+Right", "", lambda: self.navigation.go_forward()),
            CommandItem("refresh", "Refresh", "Refresh current view", "navigation", "Ctrl+R", "", self._refresh_current),
            CommandItem("toggle_sidebar", "Toggle Sidebar", "Show or hide the sidebar", "layout", "", "", self._toggle_sidebar),
            CommandItem("clear_notifications", "Clear Notifications", "Dismiss all notifications", "notifications", "", "", self.notifications.clear_all),
            CommandItem("mark_all_read", "Mark All Read", "Mark all notifications as read", "notifications", "", "", self.notifications.mark_all_read),
        ])
        self._builtin_commands_registered = True

    def _register_search_providers(self) -> None:
        def search_commands(query: str) -> list[SearchResult]:
            return [
                SearchResult(
                    result_id=f"cmd_{c.command_id}",
                    title=c.label,
                    description=c.description,
                    category="commands",
                    icon="⚡",
                    data={"command_id": c.command_id},
                    action=c.callback,
                )
                for c in self.command_palette.search(query)
            ]

        def search_pages(query: str) -> list[SearchResult]:
            return [
                SearchResult(
                    result_id=f"page_{r.route_id}",
                    title=r.title or r.route_id,
                    description=r.description,
                    category="pages",
                    icon="📄",
                    data={"route_id": r.route_id},
                    action=lambda rid=r.route_id: self.navigation.navigate(rid, "search"),
                )
                for r in self.navigation.search_routes(query)
            ]

        def search_shortcuts(query: str) -> list[SearchResult]:
            return [
                SearchResult(
                    result_id=f"shortcut_{s.shortcut_id}",
                    title=s.description or s.shortcut_id,
                    description=f"Shortcut: {s.key_sequence}",
                    category="shortcuts",
                    icon="⌨",
                    data={"shortcut_id": s.shortcut_id},
                )
                for s in self.shortcuts.search(query)
            ]

        self.search.register_provider("commands", search_commands, priority=10, description="Search commands")
        self.search.register_provider("pages", search_pages, priority=8, description="Search pages")
        self.search.register_provider("shortcuts", search_shortcuts, priority=5, description="Search shortcuts")

    def _open_command_palette(self) -> None:
        parent = self._find_parent_widget()
        self.command_palette.open_palette(parent)

    def _open_global_search(self) -> None:
        parent = self._find_parent_widget()
        self.command_palette.open_palette(parent)

    def _refresh_current(self) -> None:
        self.data_updated.emit(None)

    def _handle_escape(self) -> None:
        if self.focus.is_active:
            self.focus.exit()

    def _toggle_sidebar(self) -> None:
        parent = self._find_parent_widget()
        if parent is None:
            return
        sidebar = getattr(parent, "_sidebar", None) or getattr(parent, "_nav_rail", None)
        if sidebar is not None:
            visible = sidebar.isVisible()
            sidebar.setVisible(not visible)

    def register_default_page_routes(self, page_labels: dict[str, str]) -> None:
        routes = [
            Route(route_id=page_id, title=label, category="pages")
            for page_id, label in page_labels.items()
        ]
        self.navigation.register_routes(routes)

    def register_default_command_palette_pages(self, page_labels: dict[str, str]) -> None:
        commands = [
            CommandItem(
                command_id=f"navigate_{page_id}",
                label=f"Go to {label}",
                description=f"Navigate to {label}",
                category="navigation",
                icon="📄",
                callback=lambda pid=page_id: self.navigation.navigate(pid, "palette"),
            )
            for page_id, label in page_labels.items()
        ]
        self.command_palette.register_many(commands)

    def propagate_data(self, data: CommandCenterData) -> None:
        self.data_updated.emit(data)

    def shutdown(self) -> None:
        self.shutdown_started.emit()
        self.window_layout.save_persistent()
        self.loading.hide_all()
        self.empty_states.hide_all()
        self.shortcuts.clear_all()
        logger.info("Experience Platform shutdown complete")

    def _find_parent_widget(self) -> QWidget | None:
        parent = self.parent()
        if isinstance(parent, QWidget):
            return parent
        return None
