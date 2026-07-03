# Knowledge Platform

**Part of:** Sprint 3.2.5 Platform Standardization

---

## 1. Architecture

Knowledge is a **platform subsystem** — not a module. Every module reads domain knowledge through this pipeline, never directly from `knowledge/` files.

```
┌────────────────────────────────────────────────────────────────┐
│                      knowledge/ (files)                         │
│  exercises/*.json  muscles/*.json  nutrition/*.{md,yaml}        │
│  recovery/*.md     progression/*.{md,json}  aliases.yaml       │
└────────────────────────┬───────────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────────┐
│              Knowledge Repository (KnowledgeLoader)              │
│  - Reads & caches raw data from knowledge/                      │
│  - Handles YAML/JSON/Markdown parsing                           │
│  - Lazy-loads on first access                                   │
└────────────────────────┬───────────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────────┐
│              Knowledge Cache (built into KnowledgeLoader)        │
│  - In-memory cache of all parsed knowledge                      │
│  - TTL: session lifetime (call reload() to refresh)             │
└────────────────────────┬───────────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────────┐
│              Knowledge Validator (KnowledgeValidator)            │
│  - Validates file structure against JSON schemas                │
│  - Checks: duplicate IDs, orphan references, contribution totals│
│  - Checks: alias consistency, tag format, reference format      │
└────────────────────────┬───────────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────────┐
│              Knowledge Service (KnowledgeService)                │
│  - Typed accessor for application code                          │
│  - Wraps repositories: ExerciseRepository, MuscleRepository,    │
│    ProgramRepository                                            │
│  - Provides: VolumeEngine, TagEngine, resolve_alias()           │
└────────────────────────┬───────────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────────┐
│                     Application Modules                          │
│  modules/workout/    modules/gymbrain/    modules/nutrition/    │
│  modules/recovery/   modules/workout_program/                   │
└────────────────────────────────────────────────────────────────┘
```

---

## 2. Pipeline Components

### 2.1 Knowledge Repository

**File:** `shared/knowledge_loader.py`  
**Class:** `KnowledgeLoader`

Responsibilities:
- Read all JSON files from `knowledge/exercises/` and `knowledge/muscles/`
- Read `knowledge/aliases.yaml`
- Read `data/program.json`
- Provide accessor methods: `get_exercise()`, `get_muscle()`, `resolve_alias()`, etc.
- Lazy-load on first access; cache until `reload()` is called

### 2.2 Knowledge Cache

The `KnowledgeLoader` IS the cache. It stores parsed data in instance dicts (`_exercises`, `_muscles`, `_aliases`).

**Lifetime:** Application session. Call `reload()` to force refresh.

**Future:** Add TTL-based expiration and change-watcher for hot-reload.

### 2.3 Knowledge Validator

**File:** `shared/domain/validator.py`  
**Class:** `KnowledgeValidator`

Validation checks:
- Duplicate exercise/muscle IDs
- Duplicate exercise names
- File name matches ID
- Alias resolves to existing exercise
- JSON Schema compliance (exercise, muscle, program)
- No orphan muscle references in exercises
- No orphan exercise references in program
- Muscle contribution percentages sum to ~100%
- Tag format (non-empty, single-space)
- Reference format (non-empty title)

### 2.4 Knowledge Service

**File:** `shared/domain/service.py`  
**Class:** `KnowledgeService`

Public API:
- `resolve_alias(name: str) -> list[str]`
- `get_exercise_volume(exercise_id: str, sets: int) -> list[VolumeResult]`
- `get_weekly_volume(exercise_set_pairs: list[tuple[str, int]]) -> dict[str, float]`
- `get_exercises_with_tag(tag: str) -> list[ExerciseData]`
- `validate() -> list[ValidationError]`

---

## 3. Subsystem Boundaries

### 3.1 Who Consumes Knowledge

| Consumer | How | What |
|----------|-----|------|
| `modules/workout/` | Via `KnowledgeService` (injected) | Exercise definitions, muscle data, RM estimation |
| `modules/workout_program/` | Via `ProgramRepository` (wraps KnowledgeLoader) | Program validation, exercise ID resolution |
| `modules/gymbrain/` | Via `DataProvider` (wraps KnowledgeService) | Exercise/muscle lookups for rule evaluation |
| `modules/nutrition/` | *(planned)* Nutrition thresholds from `knowledge/nutrition/` | Macro targets, hydration guidelines |

### 3.2 Who Produces Knowledge

| Producer | Files |
|----------|-------|
| Human editors | Exercise JSON, muscle JSON, markdown docs |
| `scripts/` | *(planned)* Import tools for third-party exercise libraries |

### 3.3 What Knowledge is NOT

Knowledge is NOT:
- User data (sessions, body weight, meals) → goes in SQLite via repositories
- Application configuration (theme, preferences) → goes in `settings/`
- Derived analytics (PRs, fatigue scores) → goes in analysis engines

---

## 4. Extension Points

### 4.1 New Knowledge Domain

To add a new knowledge domain (e.g., `knowledge/recovery/`):
1. Create `knowledge/recovery/index.json` with file metadata
2. Create knowledge files with a `version` field
3. Add schema in `schemas/recovery.schema.json`
4. Add accessor methods to `KnowledgeLoader`
5. Add validation to `KnowledgeValidator`
6. Add typed service methods to `KnowledgeService`

### 4.2 Custom Exercise Library

Replace `knowledge/exercises/` with a custom library:
1. Keep the same JSON schema
2. Point `PROJECT_ROOT` to a different base path
3. Validator automatically picks up new files

---

## 5. Compliance

- No module may import `pathlib.Path` to read `knowledge/` files
- No module may hard-code scientific thresholds that exist in `knowledge/`
- All knowledge access goes through `KnowledgeLoader` or `KnowledgeService`
- Violations are caught by code review and automated import linter

## 6. Related

- ADR-002: Knowledge System
- Architecture Constitution Article V
- `shared/knowledge_loader.py`
- `shared/domain/service.py`
- `shared/domain/validator.py`
