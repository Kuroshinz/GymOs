# Recovery Architecture

## Module Structure

```
modules/recovery/
├── __init__.py              # Public API re-exports
├── domain/
│   └── __init__.py          # Entities, value objects, enums
├── application/
│   └── __init__.py          # RecoveryService (orchestration)
├── infrastructure/
│   ├── __init__.py
│   ├── models.py            # SQLAlchemy ORM models
│   └── repository.py        # RecoveryRepository (CRUD)
├── engines/
│   └── __init__.py          # Deterministic computation engines
├── providers/
│   └── __init__.py          # IRecoveryProvider + ProductionRecoveryProvider
├── presentation/
│   └── __init__.py          # RecoveryViewModel + RecoveryFormatter
```

## Layer Dependencies

```
Domain (pure Python)
    ↓
Application (orchestrates engines + repository)
    ↓
Infrastructure (SQLAlchemy models, repository)
    ↓
Presentation (UI view models, formatters)

Providers are consumed by GymBrain (not by UI)
```

## Integration Points

### GymBrain Integration

```python
DecisionEngine.from_production(
    db=db,
    nutrition_provider=nutrition_service.provider,
    recovery_provider=recovery_service.provider,
)
```

The `recovery_provider` is set on `DataProvider.recovery_provider` and consumed by GymBrain recovery rules.

### Event Integration

The `RecoverySubscriber` listens for `WorkoutCompleted` events and recomputes recovery scores. The `DashboardController` subscribes to `RecoveryUpdated` and `RecoveryScoreChanged` events for live dashboard updates.

### UI Integration

The `RecoveryDashboard` is added as a navigation page in `MainWindow` alongside Dashboard, Workout, Progress, PRs, and Settings.
