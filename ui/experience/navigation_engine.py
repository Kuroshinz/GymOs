from __future__ import annotations

import logging
from dataclasses import dataclass

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QWidget

logger = logging.getLogger("experience.navigation")


@dataclass
class Route:
    route_id: str
    widget: QWidget | None = None
    parent_id: str = ""
    title: str = ""
    icon: str = ""
    category: str = ""
    description: str = ""


@dataclass
class BreadcrumbEntry:
    route_id: str
    title: str


class NavigationEngine(QObject):
    navigated = Signal(str, str)
    back_available = Signal(bool)
    forward_available = Signal(bool)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._routes: dict[str, Route] = {}
        self._history: list[str] = []
        self._forward_stack: list[str] = []
        self._current_id: str = ""
        self._max_history: int = 50

    def register_route(self, route: Route) -> None:
        self._routes[route.route_id] = route

    def register_routes(self, routes: list[Route]) -> None:
        for r in routes:
            self._routes[r.route_id] = r

    def unregister_route(self, route_id: str) -> None:
        self._routes.pop(route_id, None)

    def route(self, route_id: str) -> Route | None:
        return self._routes.get(route_id)

    @property
    def current_route_id(self) -> str:
        return self._current_id

    @property
    def current_route(self) -> Route | None:
        return self._routes.get(self._current_id)

    def navigate(self, route_id: str, source: str = "") -> bool:
        if route_id not in self._routes:
            logger.warning("Route '%s' not registered", route_id)
            return False
        if self._current_id:
            self._history.append(self._current_id)
            if len(self._history) > self._max_history:
                self._history.pop(0)
            self._forward_stack.clear()
        self._current_id = route_id
        self.navigated.emit(route_id, source)
        self.back_available.emit(len(self._history) > 0)
        self.forward_available.emit(False)
        return True

    def go_back(self) -> bool:
        if not self._history:
            return False
        if self._current_id:
            self._forward_stack.append(self._current_id)
        self._current_id = self._history.pop()
        self.navigated.emit(self._current_id, "back")
        self.back_available.emit(len(self._history) > 0)
        self.forward_available.emit(True)
        return True

    def go_forward(self) -> bool:
        if not self._forward_stack:
            return False
        if self._current_id:
            self._history.append(self._current_id)
        self._current_id = self._forward_stack.pop()
        self.navigated.emit(self._current_id, "forward")
        self.back_available.emit(len(self._history) > 0)
        self.forward_available.emit(len(self._forward_stack) > 0)
        return True

    def breadcrumb(self) -> list[BreadcrumbEntry]:
        trail: list[BreadcrumbEntry] = []
        if not self._current_id:
            return trail
        route = self._routes.get(self._current_id)
        if not route:
            return trail
        if route.parent_id:
            parent = self._routes.get(route.parent_id)
            if parent:
                trail.append(BreadcrumbEntry(parent.route_id, parent.title or parent.route_id))
        trail.append(BreadcrumbEntry(route.route_id, route.title or route.route_id))
        return trail

    def breadcrumb_path(self) -> str:
        return " / ".join(e.title for e in self.breadcrumb())

    def routes_by_category(self, category: str) -> list[Route]:
        return [r for r in self._routes.values() if r.category == category]

    @property
    def all_routes(self) -> list[Route]:
        return list(self._routes.values())

    def search_routes(self, query: str) -> list[Route]:
        q = query.lower()
        return [
            r for r in self._routes.values()
            if q in r.title.lower() or q in r.route_id.lower() or q in r.description.lower()
        ]

    def clear_history(self) -> None:
        self._history.clear()
        self._forward_stack.clear()
        self.back_available.emit(False)
        self.forward_available.emit(False)
