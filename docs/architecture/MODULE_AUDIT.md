# Module Responsibility Audit

**Sprint:** 3.2.5 Platform Standardization  
**Date:** 2026-07-03

---

## Audit Criteria

Each module is audited against:
1. **Single Responsibility** — Does the module do one thing?
2. **Clean Architecture** — Does it follow Domain → Application → Presentation → Infrastructure?
3. **Hidden Coupling** — Does it import from other modules directly?
4. **Dead Abstractions** — Are there empty files, unused classes, or unimplemented interfaces?
5. **Oversized Services** — Are any classes too large (responsibility sprawl)?

---

## Module: `workout/`

### Responsibility
Training session tracking: log workouts, exercises, sets, body weight.

### Architecture
✅ Domain → Application → Infrastructure → Presentation layers present.

### Issues
| Severity | Issue | Recommendation |
|----------|-------|----------------|
| Low | `GymDatabase` is both repository and connection manager | Split into `DatabaseConnection` + `WorkoutRepository` |
| Low | Some application services (`PREngine`, `RecoveryEngine`) live here but serve GymBrain | Move to `gymbrain/` when GymBrain is fully extracted |

### Verdict: ✅ HEALTHY

---

## Module: `workout_program/`

### Responsibility
Import, validate, store, and activate workout programs.

### Architecture
⚠️ **Flat** — not 4-layered. Uses flat files (`domain.py`, `validator.py`, `importer.py`, `repository.py`, `manager.py`).

### Issues
| Severity | Issue | Recommendation |
|----------|-------|----------------|
| Low | Flat structure instead of DDD layers | Restructure if complexity grows beyond 5 files |
| Note | `manager.py` is the public facade | OK for current scope |

### Verdict: ✅ ACCEPTABLE (low complexity justifies flat structure)

---

## Module: `nutrition/`

### Responsibility
Nutrition intelligence: track meals, macros, hydration, lean bulk analysis.

### Architecture
✅ Domain → Application → Infrastructure → Presentation + Providers + Services.

### Issues
| Severity | Issue | Recommendation |
|----------|-------|----------------|
| Fixed | `application/` directory was dead (Sprint 3.2) | **Deleted** in this sprint |
| Low | `presentation/` is empty (no widgets yet) | Document as planned, not dead |
| Medium | `NutritionService` depends on both `NutritionRepository` AND `GymDatabase` | Acceptable for now; extract body-weight queries to a shared gateway |

### Verdict: ✅ HEALTHY (active development ongoing)

---

## Module: `gymbrain/`

### Responsibility
Evidence-based training intelligence: analyze data, evaluate rules, produce recommendations.

### Architecture
✅ Custom structure: `analysis/`, `cache/`, `models/`, `providers/`, `rules/`, `services/`.

### Issues
| Severity | Issue | Recommendation |
|----------|-------|----------------|
| **HIGH** | `DataProvider` is oversized (~30 methods across 6 domains) | Extract `ITrainingProvider` subset into a dedicated `TrainingDataProvider` facade; keep `DataProvider` as composite |
| **HIGH** | `ProductionDataProvider` duplicates 90% of `DataProvider` methods with try/except wrappers | Refactor base `DataProvider` to use null-safe decorators or error-handling mixin |
| Low | `_import_rule()` uses `getattr()` on lazy-imported modules | Acceptable for dynamic rule loading; replace with registry dict if more rules added |
| Low | `DecisionEngine` instantiates analyzers internally | Inject analyzers through constructor for testability |

### Verdict: ⚠️ NEEDS REFACTOR (DataProvider split and ProductionDataProvider dedup)

---

## Module: `recovery/`

### Responsibility
*(Planned)* Recovery tracking: sleep, HRV, fatigue, readiness scores.

### Architecture
⚠️ **Empty scaffolding** — all 5 `__init__.py` files are empty (0 bytes, no docstrings).

### Issues
| Severity | Issue | Recommendation |
|----------|-------|----------------|
| **HIGH** | Orphaned scaffolding — violates Constitution Article VI.4 | Either implement the module or document the scaffolding as planned |
| Low | `RecoveryScoreUpdated` event exists but no producer | Event will be wired when recovery module is implemented |

### Verdict: ❌ UNHEALTHY (empty scaffolding, no implementation, not documented)

---

## Module: `settings/`

### Responsibility
*(Unknown)* — no documentation, no code.

### Architecture
⚠️ **Empty scaffolding** — all 5 `__init__.py` files are empty (0 bytes, no docstrings).

### Issues
| Severity | Issue | Recommendation |
|----------|-------|----------------|
| **HIGH** | Orphaned scaffolding — violates Constitution Article VI.4 | Either implement or document as planned; remove if never needed |

### Verdict: ❌ UNHEALTHY (empty scaffolding, no implementation, no documentation)

---

## Module: `devtools/`

### Responsibility
Developer console, settings, state, overlay — isolated from production.

### Architecture
✅ Custom structure: `controller/`, `models/`, `plugins/`, `services/`, `views/`, `widgets/`.

### Issues
| Severity | Issue | Recommendation |
|----------|-------|----------------|
| None | Well-structured, documented, isolated | — |

### Verdict: ✅ HEALTHY

---

## Module: `shared/`

### Responsibility
Cross-cutting concerns: events, interfaces, domain models, knowledge.

### Architecture
✅ Flat structure with clear subpackages.

### Issues
| Severity | Issue | Recommendation |
|----------|-------|----------------|
| Low | `shared/__init__.py` does not exist | Create with re-exports of stable public API |
| Note | `shared/domain/` contains both knowledge repositories AND knowledge service | OK for current scope; split if `shared/domain/` grows |

### Verdict: ✅ HEALTHY

---

## Summary

| Module | Health | Action Required |
|--------|--------|----------------|
| `workout/` | ✅ Healthy | Minor splitting |
| `workout_program/` | ✅ Acceptable | None |
| `nutrition/` | ✅ Healthy | None |
| `gymbrain/` | ⚠️ Needs refactor | Split DataProvider, dedup ProductionDataProvider |
| `recovery/` | ❌ Unhealthy | Implement or document scaffolding |
| `settings/` | ❌ Unhealthy | Implement or document or delete scaffolding |
| `devtools/` | ✅ Healthy | None |
| `shared/` | ✅ Healthy | Create `__init__.py` |

## Blocking Issues (Constitution Violations)

1. **recovery/** and **settings/** empty scaffolding — violates Article VI.4 (No Orphaned Scaffolding)
2. **gymbrain/DataProvider** oversized — violates Article II.3 indirectly (hard to test, easy to create circular deps)
3. **gymbrain/ProductionDataProvider** duplicates base class — violates Article III.4 (maintainability)

## Recommended Actions

1. **Immediate**: Add docstrings to `recovery/` and `settings/` `__init__.py` files documenting planned scope (this sprint)
2. **Sprint 3.3**: Split `DataProvider` into `TrainingDataProvider` (exercise/muscle/session queries) and keep `DataProvider` as composite
3. **Sprint 3.3**: Extract ProductionDataProvider error handling into a reusable decorator/mixin
4. **Ongoing**: Create `shared/__init__.py` with public API re-exports
