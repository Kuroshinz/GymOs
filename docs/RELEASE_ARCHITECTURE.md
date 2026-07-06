# GymOS Release Architecture

**Single source of truth** describing how GymOS is built, versioned, migrated, recovered, and shipped.

---

## 1. Version System

### Canonical Source

Every version string in the application imports from `shared/version.py`.

| Field | Source | Example |
|-------|--------|---------|
| App version | `shared.version.APP_VERSION` | `"0.5.0"` |
| Build number | `shared.version.BUILD_NUMBER` | `1` |
| Build date | `shared.version.BUILD_DATE` | `"2026-07-06"` |
| Schema version | `shared.version.SCHEMA_VERSION` | `3` |
| Database version | `shared.version.DATABASE_VERSION` | `3` |
| Protocol version | `shared.version.PROTOCOL_VERSION` | `"1.0"` |
| Release channel | `shared.version.RELEASE_CHANNEL` | `"alpha"` |
| Alembic head | `shared.version.ALEMBIC_HEAD` | `"003"` |

### Version Info Dataclass

`shared.version.VersionInfo` bundles all version information for serialization.
Access the current version via `shared.version.CURRENT`.

### Updating Version (for releases)

```
1. Edit shared/version.py — bump MAJOR, MINOR, PATCH, BUILD_NUMBER, BUILD_DATE
2. Update pyproject.toml version field
3. Run: python scripts/migrate_db.py  (if schema changed)
4. Tag: git tag v0.5.0 && git push origin v0.5.0
```

---

## 2. Database Architecture

### Engine Factory

All SQLite engines are created via `shared/database/engine.py`:

```python
from shared.database.engine import create_safe_engine
engine = create_safe_engine("data/gymos.db")
```

This configures:
- **WAL mode** (`PRAGMA journal_mode=WAL`) — crash-safe writes
- **Foreign keys** (`PRAGMA foreign_keys=ON`) — referential integrity
- **Busy timeout** (`PRAGMA busy_timeout=5000`) — concurrency safety
- **Schema version** (`PRAGMA user_version=N`) — migration tracking

### Schema Versioning

- `PRAGMA user_version` stores the current schema version as an integer.
- Read via `shared.database.engine.get_schema_version(engine)`
- Write via `shared.database.engine.set_schema_version(engine, version)`
- Must match `shared.version.SCHEMA_VERSION` for compatibility.

### Database Files

| File | Purpose |
|------|---------|
| `data/gymos.db` | Live database |
| `data/backups/*.db` | Backup archives |
| `data/crashes/crash_*.log` | Crash reports |
| `data/crashes/*.recovered` | Recovery markers |

---

## 3. Migration Flow

```
Startup
  │
  ├─ init_infrastructure()
  │    ├─ Compatibility check (shared/database/compatibility.py)
  │    │    ├─ schema version match?               -> OK
  │    │    ├─ user_version < SCHEMA_VERSION?       -> NEEDS MIGRATION
  │    │    ├─ user_version > SCHEMA_VERSION?       -> APP TOO OLD
  │    │    └─ user_version == 0?                   -> FRESH DB
  │    │
  │    ├─ needs_migration()?
  │    │    ├─ backup_before_migration()            -> AUTO BACKUP
  │    │    └─ migrate_upgrade()                    -> RUN ALEMBIC
  │    │
  │    └─ set_schema_version()                      -> UPDATE PRAGMA
  │
  └─ Normal startup continues...
```

### Migration Tool

```bash
# Check status
python scripts/migrate_db.py --status

# Check if migration needed
python scripts/migrate_db.py --check

# Upgrade to latest
python scripts/migrate_db.py

# Upgrade to specific version
python scripts/migrate_db.py --target 2

# Downgrade
python scripts/migrate_db.py --downgrade 0

# Custom database path
python scripts/migrate_db.py --db /path/to/custom.db
```

### Alembic

- Configuration: `alembic.ini`
- Scripts: `scripts/migration/versions/`
- Environment: `scripts/migration/env.py`
- Head revision: `003`
- Target: `data/gymos.db` (fixed from `data/nexus.db`)

---

## 4. Backup Flow

```
Backup
  ├─ WAL checkpoint (PRAGMA wal_checkpoint(FULL))
  ├─ Copy gymos.db -> data/backups/gymos_backup_{timestamp}.db
  └─ Write metadata to data/backups/backup_meta.json

Automatic Backup (pre-migration)
  ├─ Same as manual backup
  └─ Label: "pre-migration"

Restore
  ├─ Validate backup (integrity check)
  ├─ Backup current live DB (pre-restore safety net)
  └─ Copy backup -> gymos.db
```

### Backup Manager API

```python
from scripts.backup.manager import (
    backup_database,      # Create backup
    restore_database,     # Restore from backup
    validate_backup,      # Validate backup integrity
    list_backups,         # List all backups
    get_latest_backup,    # Get latest backup path
)
```

---

## 5. Compatibility Matrix

| DB Version | Schema v1 | Schema v2 | Schema v3 | Unknown |
|------------|-----------|-----------|-----------|---------|
| **App v0.1.0** | Compatible | --- | --- | --- |
| **App v0.5.0** | Needs migration | Needs migration | Compatible | Too old |
| **App v0.6.0** | Needs migration | Needs migration | Needs migration | Too old |

### Rules

| Condition | Result | Action |
|-----------|--------|--------|
| `user_version == 0` | Compatible | Fresh DB, will be initialized |
| `user_version == SCHEMA_VERSION` | Compatible | Normal operation |
| `user_version < SCHEMA_VERSION` | Incompatible | Auto-backup + migration |
| `user_version > SCHEMA_VERSION` | Incompatible | Application too old for this DB |
| `user_version > DATABASE_VERSION` | Incompatible | Breaking format change |

---

## 6. Crash Safety Flow

```
Unhandled Exception
  │
  ├─ sys.excepthook (_global_excepthook)
  │    ├─ Log exception with full traceback
  │    ├─ Write crash report to data/crashes/crash_{timestamp}.log
  │    ├─ Run cleanup callbacks (dispose engines, close files)
  │    └─ Show recovery dialog (Qt GUI mode)
  │
  └─ Next startup
       ├─ show_recovery_dialog_if_needed()
       │    ├─ Check for unrecovered crash reports
       │    └─ Show recovery dialog with crash path
       │
       └─ Normal startup continues...
```

### Registration

```python
from shared.crash.handler import install_global_handler, register_cleanup

install_global_handler()           # Install excepthook (called in main.py)
register_cleanup(my_service.close) # Register cleanup callbacks
safe_shutdown()                    # Run all cleanups manually
```

---

## 7. Release Workflow

```
Developer pushes tag v0.5.0
  │
  └─ GitHub Actions (release job)
       ├─ Verify tag == APP_VERSION
       ├─ Run lint + test + typecheck
       ├─ Create release zip archive
       ├─ Generate SHA256 checksum
       └─ Create GitHub Release with changelog
```

### Release Checklist

1. [ ] Update `shared/version.py` with new version, build number, date
2. [ ] Update `pyproject.toml` version field
3. [ ] Update `docs/CHANGELOG.md`
4. [ ] Run `python scripts/migrate_db.py --status` to verify schema
5. [ ] Run full test suite: `python -m pytest tests/`
6. [ ] Run lint: `ruff check .`
7. [ ] Run typecheck: `mypy modules/ ui/ shared/`
8. [ ] Commit and push
9. [ ] Tag: `git tag v0.5.0 && git push origin v0.5.0`

---

## 8. File Layout

```
gymos/
├── shared/
│   ├── version.py                 # CANONICAL VERSION SOURCE
│   ├── constants/__init__.py      # Imports from shared.version
│   ├── database/
│   │   ├── engine.py              # Safe engine factory + pragma versioning
│   │   └── compatibility.py       # Schema/version compatibility checks
│   ├── crash/
│   │   ├── handler.py             # Global excepthook + crash reports
│   │   └── recovery.py            # Last session recovery dialog
│   └── kernel/
│       ├── kernel.py              # ProductIdentity (version from shared.version)
│       └── kernel_context.py      # Uses APP_VERSION from shared.version
├── scripts/
│   ├── migate_db.py               # Migration runner (upgrade/downgrade/status)
│   ├── migration/
│   │   ├── env.py                 # Alembic env (sync engine, correct metadata)
│   │   └── versions/              # Migration scripts (001, 002, 003)
│   └── backup/
│       ├── __init__.py            # Public API exports
│       └── manager.py             # Backup/restore/validate
├── ui/
│   └── dialogs/
│       └── about_gymos_dialog.py  # Imports from shared.version
├── main.py                        # Wires all infrastructure
├── pyproject.toml
├── alembic.ini                    # Fixed: points to gymos.db
└── data/
    ├── gymos.db                   # Live database
    ├── backups/                   # Backup archives
    └── crashes/                   # Crash reports
```

---

## 9. Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| Single version source | Eliminates drift; one place to update |
| PRAGMA user_version | Embedded version tracking survives file moves |
| Sync engine in Alembic | Matches application's sync SQLAlchemy usage |
| Auto-backup before migration | Crash-safe schema changes |
| Callable cleanup registry | Services self-register; no manual list |
| Crash report + dialog | User sees actionable info; file for debugging |
| Version verification in CI | Tags must match pyproject.toml |
| WAL mode | Crash-safe concurrent reads/writes |
