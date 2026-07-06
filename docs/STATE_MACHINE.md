# Product State Machine

The Product State Machine defines 9 canonical states and the legal transitions between them. The state machine is deterministic — state transitions are governed by rules derived from canonical data sources.

## State Diagram

```
                   ┌──────────────┐
                   │ Bootstrapping │
                   └──────┬───────┘
                          │
                     ┌────▼────┐
          ┌──────────│ Growing  │◄──────────┐
          │          └────┬────┘           │
          │               │                │
     ┌────▼────┐    ┌─────▼──────┐   ┌────┴─────┐
     │ Blocked │    │   Stable   │   │Refactoring│
     └────┬────┘    └─────┬──────┘   └────┬─────┘
          │               │                │
          │          ┌────▼────────┐       │
          │          │  Optimizing │       │
          │          └────┬────────┘       │
          │               │                │
          │          ┌────▼──────────┐     │
          │          │Release        │     │
          └──────────│Candidate      │─────┘
                     └────┬──────────┘
                          │
                     ┌────▼──────────┐
                     │Ready For      │
                     │Release        │
                     └────┬──────────┘
                          │
                     ┌────▼──────────┐
                     │  Maintenance  │
                     └───────────────┘
```

## State Definitions

### Bootstrapping
- **Description**: Initial product development phase
- **Entry**: Default state when product is first evaluated
- **Exit criteria**: At least 30% completion, at least 1 capability in progress

### Growing
- **Description**: Active capability development and feature expansion
- **Entry**: ≥30% completion, ≥1 capability in progress
- **Exit criteria**: Health ≥60, completion ≥70%, ≤3 capabilities in progress

### Stable
- **Description**: Core capabilities are complete and reliable
- **Entry**: Health ≥60, completion ≥70%, ≤3 in progress
- **Exit criteria**: Transition to optimizing, refactoring, release candidate, maintenance, growing (new features), or blocked

### Optimizing
- **Description**: Quality improvements, performance tuning, test coverage
- **Entry**: Health ≥50, no active development, ≤2 not started
- **Exit criteria**: Back to stable or toward release candidate

### Refactoring
- **Description**: Technical debt reduction, architecture improvements
- **Entry**: Debt ≥10 items, health ≥30
- **Exit criteria**: Back to stable, optimizing, or growing

### Blocked
- **Description**: Development paused due to blockers
- **Entry**: Blocking debt ≥3 or capability blockers ≥2
- **Exit criteria**: Blockers resolved → growing, refactoring, or stable

### Release Candidate
- **Description**: Feature-complete, undergoing validation
- **Entry**: Health ≥70, readiness ≥70, completion ≥80%
- **Exit criteria**: ✅ Ready for Release or ⏳ back to stable/optimizing

### Ready for Release
- **Description**: All release criteria met
- **Entry**: Health ≥85, readiness ≥90
- **Exit criteria**: → Maintenance or back to release candidate/stable

### Maintenance
- **Description**: Bug fixes and minor improvements
- **Entry**: ≥80% complete, nothing not started
- **Exit criteria**: → Growing, optimizing, refactoring, or blocked

## Legal Transitions

The transition engine defines ~40 legal transitions between states. All transitions are enforced at runtime — the engine will reject illegal transitions with a clear error message.
