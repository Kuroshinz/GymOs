# Knowledge Versioning

## Overview

The Knowledge Evolution Engine uses semantic versioning (vX.Y.Z) with immutable history, parent tracking, point-in-time snapshots, and full rollback support. Every evolution cycle produces new versions and snapshots, establishing a complete audit trail of how knowledge has changed over time.

## Semantic Versioning Scheme

Versions follow the format `vX.Y.Z`:

- **X (Major)** — Reserved for breaking knowledge structure changes (not currently auto-incremented)
- **Y (Minor)** — Auto-incremented on each evolution cycle for existing records
- **Z (Patch)** — Reserved for hotfix/manual patches (not currently auto-incremented)

### Version Lifecycle

| Stage | Version | Description |
|-------|---------|-------------|
| First creation | `v1.0.0` | Initial version assigned via `VersionManager.create_version()` with empty parent |
| First evolution | `v1.1.0` | Minor bump from `v1.0.0` |
| Second evolution | `v1.2.0` | Minor bump from `v1.1.0` |
| Nth evolution | `v1.N.0` | Minor bump from `v1.(N-1).0` |

### Increment Logic

```python
# VersionManager creates versions via _increment_minor()
def _increment_minor(major: int, minor: int, _patch: int) -> str:
    return f"v{major}.{minor + 1}.0"
```

The parent version is parsed with regex `^v(\d+)\.(\d+)\.(\d+)$` to extract the numeric components, then the minor digit is incremented and patch is reset to 0.

## Immutable History

Once a version is published, it is **never mutated**. The `KnowledgeVersion` domain model is a frozen dataclass:

```python
@dataclass(frozen=True)
class KnowledgeVersion:
    version_id: str
    knowledge_id: str
    version: str          # "v1.2.0"
    parent_version: str   # "v1.1.0"
    record: KnowledgeRecord
    created_at: str
    description: str
```

The repository stores versions in an append-only dictionary keyed by `version_id`:

```python
class KnowledgeEvolutionRepository:
    def store_version(self, version: KnowledgeVersion) -> None:
        self._versions[version.version_id] = version
```

Once stored, a version can be retrieved but never modified or deleted. The `clear_all()` method is the only way to reset state, and it is intended for testing only.

## Parent Tracking

Each version records its `parent_version`, forming an immutable chain:

```
v1.0.0 ← v1.1.0 ← v1.2.0 ← v1.3.0 ← ...
```

- First version has `parent_version = ""` (empty string)
- Subsequent versions set `parent_version` to the previous version string
- The chain provides a complete lineage for every knowledge record

### Version History Query

```python
# Get all versions for a record, sorted by semver
versions = orch.get_version_history("rec_1")
# Returns [v1.0.0, v1.1.0, v1.2.0, ...]

# Get the latest version
latest = orch.get_latest_version("rec_1")

# Get a specific historical version
historical = orch.get_historical_version("rec_1", "v1.1.0")
```

The `VersionManager.get_version_history()` sorts versions by parsed semver tuple `(major, minor, patch)`:

```python
def get_version_history(self, all_versions, knowledge_id):
    return sorted(
        (v for v in all_versions if v.knowledge_id == knowledge_id),
        key=lambda v: _parse_version(v.version),
    )
```

## Rollback Support

Rollback is a read-only query that retrieves a historical version. It does not mutate state — the caller is responsible for applying the rollback.

```python
class VersionManager:
    def rollback_to_version(
        self,
        all_versions: list[KnowledgeVersion],
        knowledge_id: str,
        target_version: str,
    ) -> Optional[KnowledgeVersion]:
        _parse_version(target_version)  # validates format
        for v in all_versions:
            if v.knowledge_id == knowledge_id and v.version == target_version:
                return v
        return None
```

**Usage example:**

```python
# Current version is v1.3.0, but we need to roll back to v1.1.0
all_versions = orch.get_version_history("rec_1")
rollback_version = orch.engine.version_manager.rollback_to_version(
    all_versions, "rec_1", "v1.1.0"
)
if rollback_version:
    restored_record = rollback_version.record
    orch.add_record(restored_record)
    print(f"Rolled back to v1.1.0, confidence was {restored_record.confidence.score}")
```

**Important:** Rollback retrieves the version's record snapshot; it does not undo subsequent versions. To fully revert, you would:
1. Retrieve the target version's record
2. Replace the current record in the repository
3. Optionally create a new version representing the rollback

## Snapshot Creation

Snapshots capture the complete state of all knowledge at a point in time. They are automatically created during each `evolve()` call.

### Snapshot Model

```python
@dataclass(frozen=True)
class KnowledgeSnapshot:
    snapshot_id: str       # "snap_uuid"
    version: str           # "snap_20240101_120000_abc123"
    records: list[KnowledgeRecord]
    conflicts: list[KnowledgeConflict]
    created_at: str
    description: str
```

### Snapshot Version Format

Snapshots use a timestamp-based version string:

```
snap_YYYYMMDD_HHMMSS_xxxxxx
```

Generated by `VersionManager.create_snapshot()`:

```python
def create_snapshot(self, records, conflicts, description=""):
    now = datetime.now(timezone.utc)
    version = f"snap_{now.strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
    return KnowledgeSnapshot(
        snapshot_id=f"snap_{uuid.uuid4().hex}",
        version=version,
        records=records,
        conflicts=conflicts,
        created_at=now.isoformat(),
        description=description,
    )
```

### Auto-Snapshot on Evolution

Every `evolve()` call produces one snapshot:

```python
snapshot = KnowledgeSnapshot(
    snapshot_id=_generate_id(),
    version=timestamp,
    records=updated,
    conflicts=resolved_conflicts,
    created_at=timestamp,
    description="Auto-evolution snapshot",
)
```

### Manual Snapshots

Snapshots can also be created manually via the VersionManager:

```python
snapshot = version_manager.create_snapshot(
    records=[rec1, rec2],
    conflicts=[conflict1],
    description="Pre-migration backup",
)
```

### Snapshot Retrieval

```python
# List all snapshots
snapshots = repository.list_snapshots()

# Get a specific snapshot
snapshot = repository.get_snapshot("snap_uuid")
```

## Version Chain Examples

### Single Record Over Multiple Evolutions

```
Evolve #1:  rec_1 → v1.0.0  (parent: "")
Evolve #2:  rec_1 → v1.1.0  (parent: "v1.0.0")
Evolve #3:  rec_1 → v1.2.0  (parent: "v1.1.0")

Version chain: v1.0.0 ← v1.1.0 ← v1.2.0
```

### Multiple Records

```
rec_1:  v1.0.0 ← v1.1.0 ← v1.2.0
rec_2:  v1.0.0 ← v1.1.0
rec_3:  v1.0.0
```

Each record tracks its own independent version chain.

## Conflict Versioning

When conflicts are resolved, the superseded record's lifecycle stage is set to `SUPERSEDED`. The conflict resolution is stored as a `KnowledgeConflict` with:

```python
conflict.resolved = True
conflict.resolved_at = "2024-01-01T00:00:00"
conflict.superseded_knowledge_id = "rec_b"
```

The superseded record retains its version history but is no longer considered active.

## Revision Tracking

Each confidence score change produces a `KnowledgeRevision`:

```python
@dataclass(frozen=True)
class KnowledgeRevision:
    revision_id: str
    knowledge_id: str
    version: str
    reason: RevisionReason      # CONFIDENCE_UPDATE, DEPRECATION, CONFLICT_RESOLUTION, etc.
    previous_score: float
    new_score: float
    confidence_change: float
    timestamp: str
    evidence_ids: list[str]
```

Revisions are append-only per `knowledge_id` in the repository.

## Repository Storage

The `KnowledgeEvolutionRepository` maintains separate in-memory stores:

| Store | Key | Mutability |
|-------|-----|------------|
| `_records` | `knowledge_id` | Overwritable (latest) |
| `_versions` | `version_id` | Append-only |
| `_conflicts` | `conflict_id` | Append-only |
| `_revisions` | `knowledge_id` → list | Append-only |
| `_snapshots` | `snapshot_id` | Append-only |

## Validation

Version strings are validated with the regex `^v(\d+)\.(\d+)\.(\d+)$`. Invalid formats raise `ValueError`:

```python
_parse_version("invalid")  # raises ValueError
_parse_version("v1.0.0")   # returns (1, 0, 0)
_parse_version("v0.0.0")   # returns (0, 0, 0)
_parse_version("v999.888.777")  # returns (999, 888, 777)
```
