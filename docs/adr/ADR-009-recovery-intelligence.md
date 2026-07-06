# ADR-009: Recovery Intelligence as First-Class Domain

## Status

Accepted

## Context

Recovery was previously a utility within the workout module. The GymOS platform needed recovery to become a full product pillar alongside Training and Nutrition, with its own domain model, persistence, scoring engines, and UI.

## Decision

Create `modules/recovery/` following Clean Architecture:

- **Domain layer**: 13 entity types, 7 enums — pure Python dataclasses
- **Application layer**: `RecoveryService` orchestrating all operations
- **Infrastructure layer**: 7 SQLAlchemy models, full CRUD repository
- **Engines layer**: 7 deterministic computation engines
- **Providers layer**: `IRecoveryProvider` ABC + `ProductionRecoveryProvider`
- **Presentation layer**: View model + formatter

Integration points:
- GymBrain consumes recovery via `DataProvider.recovery_provider`
- Events: `RecoveryUpdated`, `RecoveryScoreChanged`, `ReadinessChanged`, `DeloadRecommended`
- UI: Full `RecoveryDashboard` with 8 widgets
- Database: 7 new tables via Alembic migration 003

## Consequences

Positive:
- Recovery is independently testable (359 tests)
- GymBrain rules can consume recovery data through the provider interface
- Dashboard shows live recovery metrics
- Deload management is automated and evidence-based

Negative:
- Existing `RecoveryEngine` in workout module is now deprecated
- `FatigueAnalyzer` in GymBrain duplicates some logic with new FatigueAggregator
