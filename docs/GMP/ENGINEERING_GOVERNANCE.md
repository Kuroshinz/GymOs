# Engineering Governance

Defines the lifecycle and governance policies for all GymOS RFCs, milestones, capabilities, releases, deprecations, and documentation.

---

## RFC Lifecycle

```
DRAFT ──→ IN_REVIEW ──→ APPROVED ──→ IN_PROGRESS ──→ COMPLETE
  │           │                                            │
  │           v                                            v
  └──→ WITHDRAWN                                  SUPERSEDED (replaced by newer RFC)
```

### Stages

| Stage | Activities | Artifacts |
|---|---|---|
| **DRAFT** | Author writes problem, approach, alternatives, consequences | RFC document |
| **IN_REVIEW** | Maintainer + stakeholders review; feedback incorporated | Review comments, revised RFC |
| **APPROVED** | Accepted for implementation; architecture review conducted | Architecture Review notes |
| **IN_PROGRESS** | Implementation underway; capability maturity advances | Code, tests, UI, documentation |
| **COMPLETE** | Implementation done; tests pass; capability registered | Release notes, updated ADR |
| **WITHDRAWN** | RFC abandoned before completion | Archived RFC |
| **SUPERSEDED** | Replaced by a newer RFC that covers a superset | Pointer to successor RFC |

### RFC Numbering

```
RFC-NNN: Descriptive Title
  │       │
  │       └─ Hyphenated, capitalised
  └─ Sequential, zero-padded to 3 digits
```

### RFC Requirements

Every RFC MUST include:
- **Problem** — What gap or limitation does this address?
- **Approach** — How will it be solved?
- **Alternatives** — What other approaches were considered and why were they rejected?
- **Consequences** — Positive, negative, and neutral effects
- **Dependencies** — Other RFCs or capabilities required
- **Migration** — How existing code transitions (if breaking)
- **Compatibility** — Backward compatibility guarantees

### Current RFCs

| RFC | Title | Status |
|---|---|---|
| RFC-018 | Capability Platform | COMPLETE |
| RFC-018.5 | GymOS Kernel | IN_PROGRESS |
| RFC-019 | Recovery Intelligence | DRAFT |
| RFC-020 | Prediction Intelligence | COMPLETE |
| RFC-020.5 | Prediction Intelligence Upgrade | COMPLETE |

---

## Milestone Lifecycle

```
DEFINED ──→ IN_PROGRESS ──→ REACHED
```

| Stage | Criteria | Action |
|---|---|---|
| **DEFINED** | Milestone created with version, criteria, target date | Registered in Kernel state |
| **IN_PROGRESS** | Active sprint working toward milestone | Capability health tracked |
| **REACHED** | All criteria met, release tagged | Kernel snapshot taken |

### Milestone Registry

| Milestone | Version | Status | Criteria |
|---|---|---|---|
| Platform Maturity | v0.5 | ✅ REACHED | 688 tests, 6 capabilities COMPLETE |
| Recovery Intelligence | v0.6 | 📋 DEFINED | Recovery module, deload scheduler, nutrition dashboard, 800 tests |
| Prediction Intelligence | v0.7 | ✅ REACHED | 272 prediction tests, 13 engines, 4 analysis engines |
| AI Coach | v0.8 | 📋 DEFINED | NLG, multi-rule synthesis, 1000 tests |
| Adaptive Programming | v0.9 | 📋 DEFINED | Auto-adjustment, dynamic exercises, 1100 tests |
| Full Autopilot | v1.0 | 📋 DEFINED | All pillars, 1200 tests, performance targets |
| Digital Twin | v2.0 | 📋 DEFINED | Athlete models, 2000 tests |

---

## Capability Lifecycle

```
NOT_STARTED ──→ IN_PROGRESS ──→ COMPLETE ──→ DEPRECATED
```

Maturity progression (within each status):

```
CONCEPT → DESIGN → FOUNDATION → IMPLEMENTED → STABLE → ADVANCED → OPTIMIZED → SELF-EVOLVING
```

### Stage Transitions

| Transition | Criteria | Review |
|---|---|---|
| CONCEPT → DESIGN | Approved RFC | Architecture Review |
| DESIGN → FOUNDATION | Core domain entities, skeleton engine | Code Review |
| FOUNDATION → IMPLEMENTED | Engine complete, ≥80% tests, UI working | QA Review |
| IMPLEMENTED → STABLE | ≥200 tests, full docs, production use 1+ minor version | Release Review |
| STABLE → ADVANCED | Exceeds requirements, optimized, self-monitoring | Architecture Review |
| ADVANCED → OPTIMIZED | Performance-tuned, automated health checks | Performance Review |
| OPTIMIZED → SELF-EVOLVING | Auto-improving from usage data | Product Review |
| COMPLETE → DEPRECATED | Successor exists, migration complete | Migration Review |

### Registration

Every capability must be registered in `shared/capabilities/__init__.py` with:
- Unique capability_id
- Name and description
- Category (core, intelligence, platform, meta, future)
- Status and maturity levels
- Health scores (architecture, tests, documentation, platform)
- Completion metrics (current_percent, remaining_tasks)
- Dependencies, blocked_by, used_by
- Risk level and priority
- Documentation links

### Current Capabilities

| ID | Status | Maturity |
|---|---|---|
| training-intelligence | COMPLETE | IMPLEMENTED |
| nutrition-intelligence | COMPLETE | IMPLEMENTED |
| recovery-intelligence | IN_PROGRESS | DESIGN |
| decision-intelligence | IN_PROGRESS | FOUNDATION |
| knowledge-platform | COMPLETE | IMPLEMENTED |
| event-platform | COMPLETE | IMPLEMENTED |
| experience-platform | NOT_STARTED | CONCEPT |
| ai-coach | NOT_STARTED | CONCEPT |
| prediction-engine | COMPLETE | IMPLEMENTED |
| digital-twin | NOT_STARTED | CONCEPT |
| product-intelligence | COMPLETE | IMPLEMENTED |
| capability-platform | COMPLETE | IMPLEMENTED |

---

## Release Lifecycle

```
PLANNED ──→ IN_DEVELOPMENT ──→ CODE_FREEZE ──→ RELEASE_CANDIDATE ──→ RELEASED
```

### Stages

| Stage | Activities | Gate |
|---|---|---|
| **PLANNED** | Version identified, capabilities targeted, RFCs assigned | Milestone definition |
| **IN_DEVELOPMENT** | RFCs implemented, tests written, UI built | Ongoing |
| **CODE_FREEZE** | No new features; only bug fixes and documentation | Feature complete |
| **RELEASE_CANDIDATE** | Full regression suite, performance profiling, capability reports | QA sign-off |
| **RELEASED** | Tagged in git, version published, milestone marked REACHED | Release review |

### Release Criteria

Every release must meet:
1. All targeted capabilities at or above target maturity
2. Full regression suite passes (zero regressions)
3. No blocking issues (critical or high-severity bugs)
4. Documentation up to date (ADRs, READMEs, capability reports)
5. Performance targets met

### Version Schema

```
v<major>.<minor>.<patch>
```

| Component | Scope | Examples |
|---|---|---|
| major | Platform rewrites, architecture overhauls | v1.0, v2.0 |
| minor | Capability milestones, new pillars | v0.6, v0.7, v1.1 |
| patch | Hotfixes, small improvements | v0.5.1, v0.6.2 |

---

## Deprecation Policy

### Deprecation Process

1. **Announce** — Announce deprecation in release notes, mark capability as DEPRECATED in registry
2. **Grace period** — 1 minor version cycle where the deprecated feature still works
3. **Migration path** — Document how to migrate from deprecated to replacement
4. **Removal** — Remove in the next major version

### Criteria for Deprecation

- Replaced by a superior implementation
- Architecture no longer aligns with platform standards
- No longer serves a product pillar
- Maintenance burden exceeds value

### Current Deprecated Items

None.

---

## Backward Compatibility

### Guarantee

GymOS guarantees backward compatibility within the same major version.

### What "Compatible" Means

- All public APIs retain their signatures (parameters, return types)
- All Provider interfaces remain unchanged
- All events retain their schema
- All database schemas are additive only (no column removals)
- All configuration formats remain parseable

### Breaking Changes

Breaking changes are permitted ONLY:
1. In a new major version (v1.0, v2.0, etc.)
2. After a deprecation cycle (1 minor version)
3. With a documented migration path

### What IS NOT Covered

- Private/internal APIs (prefixed with `_`)
- Test-only interfaces
- Internal engine implementations (as long as public API is stable)

---

## Documentation Policy

### Required Documentation by Stage

| Stage | Required Documents |
|---|---|
| **CONCEPT** | RFC document |
| **PROTOTYPE** | Architecture review notes |
| **ALPHA** | Module README |
| **BETA** | Engine documentation, UI documentation, test coverage report |
| **RC** | ADR, capability report, release notes |
| **PRODUCTION** | User guide (if applicable), changelog |
| **LTS** | Maintenance guide |

### Documentation Types

| Document | Location | Maintainer |
|---|---|---|
| RFC | `docs/architecture/ADR-NNN-title.md` | Author |
| Architecture Decision Record | `docs/architecture/ADR-NNN-title.md` | Architect |
| Module README | `modules/<name>/README.md` | Module owner |
| Engine Roadmap | `docs/ENGINE_ROADMAP.md` | Product |
| Product Pillars | `docs/PRODUCT_PILLARS.md` | Product |
| Capability Report | Generated by Capability Platform | Automated |
| Release Notes | `docs/releases/v<version>.md` | Maintainer |
| User Guide | `docs/user/` | Product |
| API Reference | `docs/api/` | Automated |

### Master Document

This Master Plan (GMP-001) is the governing document. All other documents must be consistent with it. The MASTER_INDEX.md provides a single navigation page linking all documents.

### Verification

Documentation health is tracked in the Capability Platform's health scoring. Each capability's `documentation` dimension reflects the completeness of its required documentation artifacts.
