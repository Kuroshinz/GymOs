# ADR-002: Knowledge System

**Status:** Accepted

**Date:** 2026-07-03

---

## Context

GymOS requires a reliable source of domain knowledge for exercise science, nutrition protocols, recovery science, and progression methods. This knowledge must be:

- Authoritative (single source of truth for scientific thresholds)
- Versioned (track changes over time)
- Machine-readable (consumed by Python code, not just humans)
- Auditable (reviewable via git diff)
- Accessible through a consistent pipeline

The initial prototype had hard-coded thresholds in Python code (e.g., protein targets, hydration ranges) and Markdown files in `knowledge/` that were not consumed by any code — they were human-reference only.

## Decision

### 1. Knowledge Repository as Single Source of Truth

All domain knowledge MUST reside in `knowledge/` as structured files (YAML for configuration/ thresholds, Markdown for prose/reasoning, JSON for structured data). Hard-coded scientific thresholds in Python code are forbidden.

### 2. Layered Access Pipeline

All knowledge access MUST go through this pipeline:

```
Knowledge Repository  →  Knowledge Cache  →  Knowledge Validator  →  Knowledge Service  →  Application
```

- **Knowledge Repository**: Reads raw files from `knowledge/`. Handles file I/O and parsing.
- **Knowledge Cache**: Caches parsed knowledge in memory with TTL-based invalidation.
- **Knowledge Validator**: Validates knowledge structure and values (e.g., thresholds within expected ranges).
- **Knowledge Service**: Provides typed access methods to application code (e.g., `get_protein_target(goal: str) -> float`).

No module may read `knowledge/` files directly.

### 3. Versioning

Every knowledge file MUST contain a `version` field. The version MUST follow [SemVer](https://semver.org/). Breaking changes to knowledge format or thresholds MUST increment the major version.

### 4. Index Files

Each knowledge subdirectory MUST contain an `_index.json` or `index.json` enumerating its files with metadata (purpose, author, version, last_updated).

### 5. Aliases

Cross-references between knowledge domains (e.g., an exercise referencing a muscle group) MUST use aliases defined in `knowledge/aliases.yaml`. No hard-coded name matching.

## Consequences

- **Positive:** Knowledge changes are versioned, auditable via git, and reviewable
- **Positive:** Application code uses typed service methods, not raw file I/O
- **Positive:** Validation catches structural errors at startup
- **Negative:** Requires the full pipeline implementation (4 components) before first use
- **Negative:** Migration from hard-coded to knowledge-backed thresholds is incremental

## Compliance

All modules MUST:
- Access knowledge through `KnowledgeService` (or a module-specific facade)
- Never import `knowledge/` files directly
- Define thresholds in knowledge files, not Python constants

## Related

- ADR-004: Provider Interfaces
- Architecture Constitution Article V
- `docs/KNOWLEDGE_SYSTEM.md` (integration guide)
