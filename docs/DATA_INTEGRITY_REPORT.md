# Data Integrity Report — REP-001H Phase 4

**Date:** 2026-07-06  
**Database engine:** SQLite 3 (via SQLAlchemy 2.x)  

---

## Risk Register

| # | Finding | Severity | Description |
|---|---------|----------|-------------|
| R1 | No WAL mode | **HIGH** | Default journal=delete; crash can corrupt DB |
| R2 | Foreign keys not enforced | **HIGH** | `PRAGMA foreign_keys=OFF` — FK constraints silently ignored |
| R3 | No busy timeout | **MEDIUM** | Immediate "database is locked" on contention |
| R4 | Migration vs ORM schema mismatch | **CRITICAL** | Alembic creates wrong tables; ORM creates different tables at runtime |
| R5 | No migration run on startup | **CRITICAL** | `Base.metadata.create_all()` is NOT a migration strategy |
| R6 | Alembic points to wrong DB | **HIGH** | `alembic.ini` → `nexus.db` vs actual `gymos.db` |
| R7 | No database backup | **CRITICAL** | Zero backup exists |
| R8 | No database restore | **CRITICAL** | No recovery path exists |
| R9 | No schema version tracking | **CRITICAL** | No `PRAGMA user_version`, no `alembic_version` |
| R10 | No compatibility checks | **CRITICAL** | Older DB will crash newer code |
| R11 | No integrity check | **HIGH** | Silent corruption not detected |
| R12 | No VACUUM | **MEDIUM** | File grows indefinitely |
| R13 | No corruption recovery | **CRITICAL** | No recovery mechanism exists |
| R14 | 5 separate engines to same DB | **MEDIUM** | Potential locking issues |
| R15 | No event store size management | **MEDIUM** | JSONL files grow unbounded |

---

## Key Details

### SQLite Initialization
Every repository uses the bare minimum:
```python
create_engine(f"sqlite:///{db_path}")
```
No `connect_args`, no `pool_size`, no `isolation_level`.

### Migration Chain
- 3 migration scripts exist but create tables that DON'T match the ORM models
- The application uses `Base.metadata.create_all()` on startup (create-if-not-exists)
- `alembic.ini` points to `data/nexus.db` but app uses `data/gymos.db`

### Backup / Restore
- **None.** `scripts/backup/__init__.py` is empty
- Only manual export via SettingsView (workout JSON/CSV export)

### Version Tracking
- No `PRAGMA user_version` usage
- No schema version stored anywhere
- No compatibility check on database open

---

## Recommended Fixes (Priority Order)

1. **Enable WAL mode + foreign keys + busy timeout** on every engine connection
2. **Fix migration chain** — align Alembic with actual ORM schema OR remove Alembic
3. **Implement database backup** — copy `gymos.db` with WAL checkpoint
4. **Add schema version tracking** — `PRAGMA user_version` on startup
5. **Add integrity check** — run `PRAGMA integrity_check` at startup
6. **Fix alembic.ini DB path** — point to `gymos.db` instead of `nexus.db`
7. **Add event store rotation** — archive/truncate old JSONL files
