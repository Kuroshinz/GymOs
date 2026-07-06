"""Project-wide test fixtures and configuration."""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import pytest

from shared.interfaces import INutritionProvider

# ── Event bus fixture ──────────────────────────────────────────────

@pytest.fixture
def event_bus():
    """Return a fresh mock EventBus for testing."""
    from shared.events.event_bus import EventBus
    return EventBus()


# ── Mock provider fixtures ─────────────────────────────────────────

@pytest.fixture
def mock_nutrition_provider() -> MagicMock:
    """Return a mock conforming to INutritionProvider."""
    mock = MagicMock(spec=INutritionProvider)
    mock.get_today.return_value = None
    mock.get_day.return_value = None
    mock.get_recent_days.return_value = []
    mock.has_data.return_value = False
    mock.get_average_calories.return_value = 0.0
    mock.get_average_protein.return_value = 0.0
    mock.get_body_weight_history.return_value = []
    mock.get_latest_body_weight.return_value = None

    class _FakeTarget:
        calories = 2500.0
        protein_g = 150.0
        carbs_g = 300.0
        fat_g = 60.0
        fiber_g = 30.0
        water_ml = 3000.0

    mock.get_default_target.return_value = _FakeTarget()
    return mock


# ── Pytest configuration hooks ─────────────────────────────────────

def pytest_configure(config: Any) -> None:
    """Configure pytest markers."""
    config.addinivalue_line("markers", "integration: marks tests as integration tests (slow, need DB)")
    config.addinivalue_line("markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')")
    config.addinivalue_line("markers", "ui: marks tests as UI tests (need Qt/PySide6)")
