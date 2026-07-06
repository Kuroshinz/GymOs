# Type Safety Report — REP-001H Phase 3

**Date:** 2026-07-06  
**Total `Any` occurrences found:** ~250 across 65+ files  

---

## Classification

| Category | Count | % |
|----------|-------|---|
| **JUSTIFIED** — truly dynamic (Qt signals, event data, plugin boundaries) | ~90 | 36% |
| **INTERFACE** — by design (protocols, DI constructors, integration bridges) | ~115 | 46% |
| **TEMPORARY** — could be typed but wasn't (widget `update(data)` methods) | ~30 | 12% |
| **AVOIDABLE** — clearly should be typed (specific known types) | ~15 | 6% |

---

## P0 Fixes — Highest Cascading Impact

### 1. `shared/interfaces/__init__.py` (all 6 protocols)
Replace `Any` with existing domain types throughout:
- `ITrainingProvider` — return types should be `SessionData`, `BodyWeight`, `Muscle`, `Exercise`
- `INutritionProvider` — return types should be `DailyNutrition`, `MacroTarget`, `NutritionSummary`
- `IRecoveryProvider` — return types should be `RecoveryScore`, `SleepLog`, `RecoveryTrend`
- `IRecommendationEngine` — return types should be `Recommendation`, `WeeklyReview`
- `IPredictionProvider` — return types should be `Prediction`, `Forecast`
- `IAdaptiveProvider` — return types should be `Adaptation`, `DecisionTimelineItem`

**Impact:** Fixing these 6 protocol definitions eliminates ~50 `Any` usages across all consumers.

### 2. `modules/gymbrain/providers/data_provider.py` and `production_provider.py`
Type all 28 method parameters and return values. These are the bridge between GymBrain and all data sources.

**Impact:** Types ~25+ methods that currently use `Any`.

### 3. `modules/gymbrain/providers/data_provider.py:49,59` — property setters
- `nutrition_provider(self, value: Any)` → `value: INutritionProvider | None`
- `recovery_provider(self, value: Any)` → `value: IRecoveryProvider | None`

---

## P1 Fixes — Clear Types Exist

| File | Line | Current | Should Be |
|------|------|---------|-----------|
| `ui/dashboard/dashboard_models.py` | 53 | `recovery_status: Any` | `RecoveryStatus \| None` |
| `ui/recovery/recovery_dashboard.py` | 38 | `recovery_trend: Any` | `RecoveryTrend \| None` |
| `ui/recovery/recovery_dashboard.py` | 39 | `recovery_active_deload: Any` | `DeloadPlan \| None` |
| `ui/dashboard/dashboard_widgets/base_card.py` | 72 | `widget: Any` | `QWidget` |
| `ui/dashboard/dashboard_widgets/base_card.py` | 75 | `layout: Any` | `QLayout` |
| `ui/design_system/components/app_card.py` | 103 | `layout: Any` | `QLayout` |
| `shared/runtime/context.py` | 61 | `SectionProvider = Any` | `Callable[[], dict \| Awaitable[dict]]` |
| `shared/runtime/runtime.py` | 25 | `config: Any \| None` | `RuntimeConfig \| None` |

---

## P2 Fixes — Widget `update(data)` Methods

All widget update methods should use specific types:

| Widget Group | Count | Current | Should Be |
|-------------|-------|---------|-----------|
| Dashboard widget `update(data)` | 10 | `data: Any` | `data: DashboardData` |
| Recovery widget `update_data(data)` | 9 | `data: Any` | `data: RecoveryDashboardData` |
| CommandCenter page `update_data(data)` | 10 | `data: Any` | `data: CommandCenterData` |

---

## P3 Fixes — Low Impact

| File | Line | Current | Should Be |
|------|------|---------|-----------|
| `ui/dashboard/dashboard_widgets/volume_widget.py` | 74 | `muscle: Any` | `MuscleAnalysisData \| dict[str, Any]` |
| `ui/dashboard/dashboard_widgets/priority_muscles_widget.py` | 105 | `muscle: Any` | `MuscleAnalysisData \| dict[str, Any]` |
| `shared/events/subscribers/gymbrain_subscriber.py` | 35 | `self._engine: Any` | `DecisionEngine \| None` |
| `modules/devtools/` | 5 methods | Various | Specific types |

---

## Summary

47 `Any` annotations (19% of total) are actionable and should be replaced with specific types. The top 3 fixes (interfaces, data provider methods, and widget update signatures) would eliminate ~80 `Any` usages and type the entire module boundary layer.
