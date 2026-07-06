# REP-001I — Release Infrastructure

**Date:** 2026-07-06  
**Status:** Complete  
**Preceding:** REP-001H (production hardening — identified gaps)

---

## Summary

Built the infrastructure required to safely ship GymOS: version system, database versioning, backup/restore, compatibility checks, crash safety, and CI/CD.

**No new business logic, no new engines, no architectural redesign.**

---

## Part A — Version System

### What Changed

Created `shared/version.py` as the **single canonical version source**.

All version strings now import from `shared.version`:
- `shared/constants/__init__.py` — imports `APP_VERSION, APP_NAME, APP_DESCRIPTION`
- `shared/kernel/kernel_context.py` — imports `APP_VERSION`
- `ui/dialogs/about_gymos_dialog.py` — imports `APP_VERSION, BUILD_DATE, COPYRIGHT`

### Version Fields

| Field | Value | Purpose |
|-------|-------|---------|
| `MAJOR.MINOR.PATCH` | `0.5.0` | SemVer app version |
| `BUILD_NUMBER` | `1` | Incrementing build counter |
| `SCHEMA_VERSION` | `3` | PRAGMA user_version target |
| `DATABASE_VERSION` | `3` | Breaking format version |
| `PROTOCOL_VERSION` | `1.0` | IPC protocol |
| `RELEASE_CHANNEL` | `alpha` | Channel gate |
| `ALEMBIC_HEAD` | `003` | Expected Alembic head |

### Files Changed
- `shared/version.py` — **CREATED**
- `shared/constants/__init__.py` — updated to import
- `shared/kernel/kernel.py` — version default removed
- `shared/kernel/kernel_context.py` — imports `APP_VERSION`
- `ui/dialogs/about_gymos_dialog.py` — class constants replaced with imports
- `main.py` — imports `APP_VERSION`
- `pyproject.toml` — version bumped to `0.5.0`, authors/license/classifiers added

---

## Part B — Database Versioning

### What Changed

Fixed Alembic configuration and implemented schema version tracking.

### Alembic Fixes

| Issue | Before | After |
|-------|--------|-------|
| DB path | `data/nexus.db` | `data/gymos.db` |
| Engine type | Async | Sync (matching app) |
| `target_metadata` | `None` | Combined ORM models |
| Autogenerate | Broken | Works |

### Schema Version Tracking

- `create_safe_engine()` in `shared/database/engine.py` — factory with WAL, foreign_keys, busy_timeout
- `get_schema_version()` / `set_schema_version()` — read/write `PRAGMA user_version`
- `verify_schema_version()` — compare DB version to `SCHEMA_VERSION`

### New Files
- `shared/database/__init__.py`
- `shared/database/engine.py` — engine factory + pragma versioning
- `shared/database/compatibility.py` — schema/version checks
- `scripts/migrate_db.py` — CLI migration runner (upgrade/downgrade/status)

### Migration Scripts
- `scripts/migration/env.py` — REWRITTEN (sync engine, correct metadata)
- `alembic.ini` — REWRITTEN (correct DB path)

---

## Part C — Backup

### What Changed

Implemented full backup/restore/validation with metadata tracking.

### New Files
- `scripts/backup/manager.py` — backup/restore/validate
- `scripts/backup/__init__.py` — public API re-exports

### Backup Flow
```
backup_database(db_path)
  ├─ PRAGMA wal_checkpoint(FULL)      → consistent snapshot
  ├─ shutil.copy2()                    → data/backups/{name}_{ts}.db
  └─ Write metadata to backup_meta.json
```

### Options
| Feature | Method | Description |
|---------|--------|-------------|
| Manual backup | `backup_database(path)` | Full DB copy with WAL checkpoint |
| Pre-migration | `backup_before_migration(path)` | Auto-backup with "pre-migration" label |
| Restore | `restore_database(src, dst)` | Validate + backup current + copy |
| Validate | `validate_backup(path)` | File check + integrity_check + schema read |
| List | `list_backups()` | Read backup_meta.json |
| Latest | `get_latest_backup()` | Most recent backup path |

---

## Part D — Compatibility

### What Changed

Startup compatibility checks in `shared/database/compatibility.py`.

### Matrix

| DB State | Result | Action |
|----------|--------|--------|
| `user_version == SCHEMA_VERSION` | ✅ OK | Normal startup |
| `user_version == 0` | ✅ OK | Fresh DB, will init |
| `user_version < SCHEMA_VERSION` | ⚠️ Needs migration | Auto-backup + upgrade |
| `user_version > SCHEMA_VERSION` | ❌ App too old | Block startup |
| `user_version > DATABASE_VERSION` | ❌ Breaking format | Block startup |

### API
```python
check_schema_compatibility(engine)   → CompatibilityResult
check_database_compatibility(engine) → CompatibilityResult
check_all(engine)                    → list[CompatibilityResult]
all_compatible(engine)               → bool
```

---

## Part E — Crash Safety

### What Changed

Global exception handler with crash reports, safe shutdown, and session recovery.

### New Files
- `shared/crash/__init__.py`
- `shared/crash/handler.py` — excepthook, report writer, cleanup registry
- `shared/crash/recovery.py` — last-session recovery dialog

### Crash Flow
```
Unhandled exception
  ├─ excepthook logs exception + writes crash_{ts}.log to data/crashes/
  ├─ Runs all registered cleanup callbacks (db.dispose, service.dispose)
  ├─ Shows QMessageBox with crash path
  └─ Exits

Next startup
  └─ show_recovery_dialog_if_needed()
       └─ If unrecovered crash: shows dialog, marks .recovered file
```

### Registration API
```python
install_global_handler()          # Called in main.py
register_cleanup(my_obj.close)    # Services self-register
safe_shutdown()                   # Runs all, connected to aboutToQuit
```

### Files Changed
- `main.py` — calls `install_global_handler()`, wraps services with `register_cleanup()`, connects `aboutToQuit`

---

## Part F — CI/CD

### What Changed

Fixed CI configuration errors and added release workflow.

### CI Fixes

| Line | Before | After |
|------|--------|-------|
| `--cov=` | `core nexus sdk` | `modules ui shared main.py` |
| `mypy` | `core/ nexus/ sdk/` | `modules/ ui/ shared/` |
| `--cov-fail-under` | Missing | `70` |
| Codecov | `v3` (deprecated) | `v5` |
| Release job | Missing | Tag-triggered workflow |

### Release Workflow
1. Push tag `v0.5.0`
2. CI verifies tag matches `APP_VERSION`
3. Runs lint + test + typecheck
4. Creates release zip archive + SHA256 checksum
5. Creates GitHub Release with changelog

### Config Changes
- `.github/workflows/ci.yml` — REWRITTEN (correct paths, new job)
- `pyproject.toml` — added `[tool.mypy]` section, coverage `fail_under`

---

## Output

### New Files Created

| File | Purpose |
|------|---------|
| `shared/version.py` | Canonical version source |
| `shared/database/__init__.py` | Package init |
| `shared/database/engine.py` | Safe engine factory + pragma versioning |
| `shared/database/compatibility.py` | Schema/version compatibility checks |
| `shared/crash/__init__.py` | Package init |
| `shared/crash/handler.py` | Global excepthook + crash reports |
| `shared/crash/recovery.py` | Last session recovery dialog |
| `scripts/__init__.py` | Package init |
| `scripts/migrate_db.py` | Migration runner (CLI + programmatic) |
| `scripts/backup/manager.py` | Backup/restore/validate |

### Files Modified

| File | Changes |
|------|---------|
| `main.py` | +infrastructure init, crash handler, cleanup registry |
| `shared/constants/__init__.py` | Imports from shared.version |
| `shared/kernel/kernel.py` | Removed hardcoded version |
| `shared/kernel/kernel_context.py` | Imports APP_VERSION |
| `ui/dialogs/about_gymos_dialog.py` | Imports from shared.version |
| `pyproject.toml` | v0.5.0, metadata, coverage threshold, mypy config |
| `alembic.ini` | Correct DB path |
| `scripts/migration/env.py` | Sync engine, combined metadata |
| `.github/workflows/ci.yml` | Correct paths, release job |

### Documentation Generated
- `docs/RELEASE_ARCHITECTURE.md` — Single source of truth for build/version/migration/recovery/ship

---

## Success Criteria

| Criterion | Status |
|-----------|--------|
| GymOS survives **update** | ✅ Auto-backup + migration before schema change |
| GymOS survives **downgrade** | ✅ `migrate_db.py --downgrade` with pre-restore backup |
| GymOS survives **crash** | ✅ Global excepthook + crash reports + safe shutdown |
| GymOS survives **backup** | ✅ Manual + pre-migration auto-backup |
| GymOS survives **restore** | ✅ Backup validation + pre-restore safety net |
| GymOS survives **schema evolution** | ✅ PRAGMA user_version + compatibility checks |

---

*End of REP-001I — Release Infrastructure*
