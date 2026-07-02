# NEXUS — Task Template

## Pre-Flight

Before writing any code:
1. Read `.ai/AGENT.md`
2. Read `.ai/PROJECT_VISION.md` (if first task)
3. Read `.ai/CURRENT_MILESTONE.md`
4. Read `.ai/ARCHITECTURE_RULES.md` (if new module)
5. Read `docs/PRODUCT_REQUIREMENTS.md` (relevant section)
6. Read `docs/ARCHITECTURE.md`
7. Read `docs/DATABASE.md` (if DB changes)
8. Check `knowledge/` for domain data
9. Check if existing code already does this

## Execution

```
1. Understand the requirement
   └─ Write down the goal in 1-2 sentences
2. Check what exists
   └─ Search codebase for related code
3. Plan
   └─ Files to create/modify (list them)
   └─ Architecture impact (if any)
4. Implement
   └─ Follow Clean Architecture
   └─ Type hints everywhere
   └─ Write tests alongside code
5. Self-Review
   └─ Run through REVIEW_CHECKLIST.md
6. Verify
   └─ Run: ruff check .
   └─ Run: mypy .
   └─ Run: pytest
7. Document
   └─ Update CHANGELOG.md
   └─ Update relevant docs
   └─ Commit with conventional message
```

## Template — New Feature

```markdown
## Feature: <name>

### Goal
<one sentence>

### Files
- `src/modules/<name>/domain/entities.py` — Entity
- `src/modules/<name>/application/use_cases.py` — Use case
- `src/modules/<name>/infrastructure/repositories.py` — Repository
- `src/modules/<name>/presentation/views.py` — UI

### Events
- `<domain>.<action>` — emitted when ...

### Tests
- `tests/unit/test_<name>_service.py`

### Notes
<anything non-obvious>
```

## Template — Bug Fix

```markdown
## Bug: <description>

### Symptoms
<what happens>

### Root Cause
<why it happens>

### Fix
<what changed>

### Tests Added
<test names>
```
