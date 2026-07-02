from abc import ABC, abstractmethod
from typing import Any


class Widget(ABC):
    @abstractmethod
    def render(self) -> Any: ...

    @abstractmethod
    def update(self, data: dict) -> None: ...
