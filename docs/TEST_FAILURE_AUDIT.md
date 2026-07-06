# Test Failure Audit — REP-001H Phase 1

**Date:** 2026-07-06  
**Result:** 48 failed, 3327 passed, 2 skipped (56.86s)

---

## Classification Summary

| Category | Count | Description |
|----------|-------|-------------|
| **Real Bug** | 8 | Production code has incorrect behavior |
| **Test Bug** | 34 | Tests reference wrong attributes, mocks, or outdated expectations |
| **Environment** | 0 | All failures are deterministic and reproducible |
| **Legacy** | 6 | Tests validate superseded/renamed interfaces |

---

## Real Bugs (8)

### 1. AdaptiveTimelineWidget missing `update_data` method
- **File:** `tests/ui/command_center/test_all_widgets.py:77`, `test_widgets.py:54`
- **Root cause:** `AdaptiveTimelineWidget` (in `ui/command_center/widgets/adaptive_timeline_widget.py`) was created without the `update_data` method that all other widgets have
- **Fix:** Add `update_data` method to `AdaptiveTimelineWidget`

### 2. DashboardData field mismatch — `goal_progress` vs `goal_progress_percent`
- **File:** `tests/ui/test_dashboard.py:126`
- **Root cause:** Test expects `data.goal_progress` but the model field is `goal_progress_percent`
- **Fix:** Either update test to use correct field name or add alias

### 3. DashboardData unexpected `goal_weight` keyword
- **File:** `tests/ui/test_dashboard.py:228`
- **Root cause:** `DashboardData.__init__()` doesn't accept `goal_weight` parameter
- **Fix:** Test passes wrong keyword argument

### 4. QWidget.update called with DashboardData instead of update_data
- **File:** `tests/ui/test_dashboard.py:243`
- **Root cause:** Test calls `.update(data)` but PySide6's `QWidget.update()` only accepts geometry args
- **Fix:** Test should call `.update_data(data)`

### 5. Dashboard fetch exceeds 100ms performance budget
- **File:** `tests/ui/test_dashboard.py:287`
- **Root cause:** Real DB queries average 137ms instead of <100ms target
- **Fix:** Either increase budget or optimize queries

### 6. RecoverySubscriber constructor change
- **File:** `tests/unit/test_event_platform.py:706`
- **Root cause:** `RecoverySubscriber.__init__` no longer accepts `recovery_engine` keyword
- **Fix:** Update test constructor call

### 7. Theme default changed from 'light' to 'dark'
- **File:** `tests/unit/test_theme.py:7`
- **Root cause:** Application default theme changed but test not updated
- **Fix:** Update expected value

### 8. Theme color values mismatch
- **File:** `tests/unit/command_center/test_theme.py:14`
- **Root cause:** `COLORS` dict changed (yellow shade: `#FBBF24` → `#FACC15`)
- **Fix:** Update expected values

---

## Test Bugs (34)

### CommandCenter Tests (6 tests — attribute references)
| File | Method | Wrong Reference | Correct |
|------|--------|----------------|---------|
| `test_command_center.py:80` | `test_sidebar_navigation` | `cc._sidebar` | `cc._nav_rail` |
| `test_command_center.py:106` | `test_sidebar_active_on_navigate` | `cc._sidebar` | `cc._nav_rail` |
| `test_command_center_edge.py:47` | `test_modal_palette_creates` | `cc._create_palette` | `CommandPalette(cc)` |
| `test_command_center_edge.py:70` | `test_search_navigates` | `search_bar.navigated` | `search_bar.search_submitted` |
| `test_command_center_edge.py:76` | `test_sidebar_propagation` | `cc._sidebar` | `cc._nav_rail` |
| `test_navigation.py:73` | `test_focus` | Focus assertion timing issue | Use `QTest.qWait()` |

### Layout Tests (10 tests — MagicMock not compatible with PySide6)
| File | Test(s) | Root Cause |
|------|---------|------------|
| `test_layout.py` | 5 tests | `addWidget(MagicMock(), 0, 0, 1, 1)` fails because PySide6 bindings check `isinstance(w, QWidget)` |
| `test_layout_edge.py` | 5 tests | Same issue |

**Classification:** PySide6 v6 type-checking is stricter than mock objects. Mocks don't pass `isinstance` checks. Fix by passing actual `QWidget()` instances.

### Navigation Tests (3 tests — count mismatch)
| File | Test | Expected | Actual | Root Cause |
|------|------|----------|--------|------------|
| `test_navigation.py:13` | `test_nav_items_match_labels` | 9 | 10 | New 'intelligence' nav item added |
| `test_navigation.py:32` | `test_commands_include_all_pages` | missing 'intelligence' | — | Command palette updated to include intelligence |
| `test_navigation.py:19,23` | `test_page_index_prs/settings` | 3→5, 4→6 | Changed | Sidebar reordered; tests use old mapping |

### Navigation Consistency Tests (1 test — sidebar order)
- `test_navigation.py:42` — `test_nav_items_order_matches_page_index`  
- Root cause: Sidebar button order no longer matches `PAGE_INDEX`

### Capabilities Tests (4 tests — registry grew from 13 to 19)
| File | Test | Old Count | New Count |
|------|------|-----------|-----------|
| `test_init.py:23` | `test_registry_has_all_13_capabilities` | 13 | 19 |
| `test_init.py:56` | `test_all_major_capabilities_present` | 13 | 19 |
| `test_init.py:90` | `test_platform_state_produces_report` | 13 | 19 |
| `test_init.py:103` | `test_report_generates_json` | 13 | 19 |

### Kernel Tests (8 tests — count mismatch, same root cause)
| File | Test(s) | Old Count | New Count |
|------|---------|-----------|-----------|
| `test_kernel_context.py` | 3 tests | 13 | 19 |
| `test_kernel_metrics.py` | 4 tests | 13 | 19 |
| `test_kernel_runtime.py` | 2 tests | 13 | 19 |

### Theme Tests (3 tests — values changed)
| File | Test | Issue |
|------|------|-------|
| `test_theme.py:20` | `test_all_colors_non_empty` | Tests expect all values to be strings; some are now `ColorScheme` objects |
| `test_theme.py:47` | `test_page_labels_complete` | Expected 9 labels, got 10 (intelligence added) |

### Theme Test (1 test — default)
| File | Test | Issue |
|------|------|-------|
| `test_theme.py:7` | `test_default_theme` | Expected `'light'`, actual `'dark'` |

---

## Legacy Issues (6)

| # | Test | File | Details |
|---|------|------|---------|
| 1 | `test_sidebar_navigation` | `test_command_center.py` | Tests reference `_sidebar` which was renamed to `_nav_rail` |
| 2 | `test_sidebar_active_on_navigate` | `test_command_center.py` | Same |
| 3 | `test_modal_palette_creates` | `test_command_center_edge.py` | References `_create_palette` which never existed in final code |
| 4 | `test_sidebar_propagation` | `test_command_center_edge.py` | Same `_sidebar` issue |
| 5 | `test_search_navigates` | `test_command_center_edge.py` | Uses old `navigated` signal name |
| 6 | `test_theme.py` theme values | `test_theme.py` | Expected `'light'`, actual `'dark'` |

---

## Failed Tests by File

| File | Failures | Root Cause Category |
|------|----------|-------------------|
| `tests/ui/command_center/test_all_widgets.py` | 1 | Real Bug |
| `tests/ui/command_center/test_command_center.py` | 2 | Test Bug (wrong attribute) |
| `tests/ui/command_center/test_command_center_edge.py` | 3 | Test Bug (wrong attribute/signal) |
| `tests/ui/command_center/test_navigation.py` | 1 | Test Bug (timing) |
| `tests/ui/command_center/test_widgets.py` | 2 | Real Bug |
| `tests/ui/test_dashboard.py` | 4 | Real Bug (3) + Performance (1) |
| `tests/unit/capabilities/test_init.py` | 4 | Test Bug (stale counts) |
| `tests/unit/command_center/test_layout.py` | 5 | Test Bug (mock incomp.) |
| `tests/unit/command_center/test_layout_edge.py` | 5 | Test Bug (mock incomp.) |
| `tests/unit/command_center/test_navigation.py` | 2 | Test Bug (stale counts) |
| `tests/unit/command_center/test_theme.py` | 3 | Test Bug (stale values) |
| `tests/unit/kernel/test_kernel_context.py` | 3 | Test Bug (stale counts) |
| `tests/unit/kernel/test_kernel_metrics.py` | 4 | Test Bug (stale counts) |
| `tests/unit/kernel/test_kernel_runtime.py` | 2 | Test Bug (stale counts) |
| `tests/unit/test_event_platform.py` | 1 | Real Bug |
| `tests/unit/test_navigation.py` | 3 | Test Bug (stale order) |
| `tests/unit/test_theme.py` | 1 | Test Bug (stale default) |

---

## Recommended Fix Path

1. **P0 — Fix test attribute references** (6 tests, ~30 min): Fix `_sidebar` → `_nav_rail`, `_create_palette` → `CommandPalette`, `navigated` → `search_submitted`
2. **P0 — Fix stale counts** (19 tests, ~15 min): Update all `13 → 19` and `9 → 10` in capabilities/kernel/navigation/theme tests
3. **P1 — Fix mock compatibility** (10 tests, ~1 hr): Replace `MagicMock()` with `QWidget()` in layout tests
4. **P1 — Fix DashboardData tests** (3 tests, ~30 min): Correct field names and call signatures
5. **P2 — Fix AdaptiveTimelineWidget** (3 tests, ~30 min): Add `update_data` method
6. **P2 — Fix performance budget** (1 test, ~15 min): Increase timeout or optimize queries
7. **P2 — Fix theme values** (4 tests, ~15 min): Update expected values to match current theme
