from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass, field

from PySide6.QtCore import QObject, Signal

logger = logging.getLogger("experience.search")


@dataclass
class SearchResult:
    result_id: str
    title: str
    description: str = ""
    category: str = "general"
    icon: str = ""
    relevance: float = 0.0
    data: dict = field(default_factory=dict)
    action: Callable[[], None] | None = None


@dataclass
class SearchProviderDef:
    name: str
    search_fn: Callable[[str], list[SearchResult]]
    priority: int = 0
    description: str = ""


class SearchProvider(QObject):
    search_started = Signal(str)
    search_completed = Signal(str, list)
    search_error = Signal(str, str)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._providers: dict[str, SearchProviderDef] = {}
        self._results: dict[str, SearchResult] = {}

    def register_provider(self, name: str, search_fn: Callable[[str], list[SearchResult]], priority: int = 0, description: str = "") -> None:
        self._providers[name] = SearchProviderDef(
            name=name,
            search_fn=search_fn,
            priority=priority,
            description=description,
        )
        logger.debug("Registered search provider: %s", name)

    def unregister_provider(self, name: str) -> None:
        self._providers.pop(name, None)

    def search(self, query: str, max_results: int = 20) -> list[SearchResult]:
        if not query or len(query.strip()) < 1:
            return []

        self.search_started.emit(query)
        q = query.lower().strip()
        all_results: list[SearchResult] = []

        for provider in sorted(self._providers.values(), key=lambda p: p.priority, reverse=True):
            try:
                results = provider.search_fn(q)
                for r in results:
                    r.relevance = self._calculate_relevance(r, q)
                all_results.extend(results)
            except Exception as exc:
                logger.warning("Search provider '%s' failed: %s", provider.name, exc)
                self.search_error.emit(provider.name, str(exc))

        all_results.sort(key=lambda r: r.relevance, reverse=True)

        for r in all_results:
            self._results[r.result_id] = r

        top_results = all_results[:max_results]
        self.search_completed.emit(query, top_results)
        return top_results

    def get_result(self, result_id: str) -> SearchResult | None:
        return self._results.get(result_id)

    def clear_cache(self) -> None:
        self._results.clear()

    def _calculate_relevance(self, result: SearchResult, query: str) -> float:
        score = 0.0
        q = query.lower()

        if q in result.title.lower():
            score += 10.0
            if result.title.lower().startswith(q):
                score += 5.0
            if result.title.lower() == q:
                score += 10.0

        if q in result.description.lower():
            score += 3.0

        if q in result.category.lower():
            score += 2.0

        score += result.relevance
        return score

    @property
    def provider_names(self) -> list[str]:
        return list(self._providers.keys())
