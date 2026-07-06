# Dashboard Architecture

## Overview

The Dashboard follows a **Model-View-Controller (MVC)** pattern adapted for
Qt/PySide6. The architecture enforces a strict separation of concerns:

- **Models** (`dashboard_models.py`) — Pure dataclasses, no logic
- **View** (`dashboard_view.py` + `dashboard_widgets/`) — Presentation only
- **Controller** (`dashboard_controller.py`) — Orchestration and event handling
- **Service** (`dashboard_services/`) — Data fetching (bridge to GymBrain)

## File Structure

```
ui/dashboard/
├── __init__.py                          # Exports DashboardView
├── dashboard_models.py                  # DashboardData dataclass
├── dashboard_view.py                    # Main dashboard widget (scroll layout)
├── dashboard_controller.py              # Data flow + event subscriptions
├── dashboard_services/
│   ├── __init__.py
│   └── dashboard_data_service.py        # Centralized data fetching
└── dashboard_widgets/
    ├── __init__.py
    ├── base_card.py                     # DashboardCard base class
    ├── header_widget.py                 # User greeting + key stats
    ├── goal_progress_widget.py          # Bodyweight goal tracking
    ├── recommendation_widget.py         # Top GymBrain recommendation
    ├── workout_widget.py                # Today's scheduled workout
    ├── priority_muscles_widget.py       # Per-muscle volume status
    ├── recovery_widget.py               # Fatigue/recovery status
    ├── volume_widget.py                 # Weekly volume by muscle
    ├── pr_widget.py                     # Recent personal records
    ├── nutrition_widget.py              # Placeholder for Nutrition module
    └── quick_actions_widget.py          # Action buttons
```

## Architectural Decisions

### 1. Dashboard never duplicates GymBrain logic

**Decision:** The `DashboardDataService` calls `DecisionEngine` methods
exclusively. It never performs its own analysis or calculations beyond
data aggregation.

**Rationale:** Prevents logic drift. All business intelligence flows through
a single code path (GymBrain). The Dashboard is a consumer, not a producer,
of analysis.

### 2. Stateless data service

**Decision:** `DashboardDataService` has no state. Every `fetch_all()` call
returns fresh data directly from GymBrain and the database.

**Rationale:** Simplifies caching (handled by GymBrain's `AnalysisCache`).
Eliminates stale data issues.

### 3. Signal-based widget updates

**Decision:** The controller emits a single `data_updated(DashboardData)`
signal. All widgets listen and update from the same payload.

**Rationale:** Single source of truth for the current dashboard state.
Widgets never fetch data independently.

### 4. Event-driven live updates

**Decision:** The controller subscribes to domain events and refreshes
only affected sections.

**Rationale:** No polling. No manual refresh button. Dashboard updates
automatically after workouts, weight logs, program changes, etc.

### 5. Section-level partial refresh

**Decision:** The controller supports `refresh_section(section_name)` to
refresh individual sections without a full data fetch.

**Rationale:** After a `BodyWeightUpdated` event, we only need to refresh
the header and goal progress — not recommendations or volume.

### 6. Extremely defensive error handling

**Decision:** Every data fetch method catches all exceptions and returns
sensible defaults. The Dashboard never crashes.

**Rationale:** The Dashboard must always be available, even when
GymBrain or the database is temporarily unavailable.

## Extension Points

### Adding a New Widget

1. Create `dashboard_widgets/new_widget.py` extending `DashboardCard`
2. Implement an `update(data)` method that reads from `DashboardData`
3. Add the widget to `dashboard_view.py`:
   - Create it in `_build_ui()`
   - Call `self._new_widget.update(data)` in `_on_data_updated()`
4. Add any new fields to `dashboard_models.DashboardData`
5. Populate those fields in `dashboard_data_service.py`

### Adding a New Event Subscription

1. In `dashboard_controller._subscribe_to_events()`, call:
   ```python
   self._event_bus.subscribe("YourEventName", self._on_your_event)
   ```
2. Implement the handler:
   ```python
   def _on_your_event(self, event: Any) -> None:
       try:
           data = self._last_data
           self._data_service.refresh_section(data, "relevant_section")
           self.data_updated.emit(data)
       except Exception:
           self.refresh()
   ```

### Integrating Nutrition Intelligence

When the Nutrition module is implemented:

1. Set `data.nutrition_configured = True` in `dashboard_data_service.py`
2. Populate `data.nutrition_data` with `calories`, `protein`, `carbs`,
   `fat`, and `hydration` dicts (each with `current` and `target` values)
3. The existing `NutritionWidget._render_nutrition()` will display them

## Performance

- `AnalysisCache` (300s TTL) in GymBrain prevents repeated analysis
- Section-level refresh avoids full data fetches for minor updates
- Widgets use simple string/num updates (no heavy re-rendering)
- SQLite queries are scoped with LIMIT clauses

---

*See also: [DASHBOARD.md](DASHBOARD.md), [DASHBOARD_WIDGETS.md](DASHBOARD_WIDGETS.md)*
