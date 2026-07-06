# Product Runtime

## Overview

The Product Runtime is the part of the Kernel that tracks **what GymOS is right now** — version, phase, active RFCs, and roadmap position.

## State Model

```
ProductRuntime
    ├── identity (ProductIdentity)
    │   ├── name: "GymOS"
    │   ├── version: "0.5.0"
    │   ├── phase: ALPHA
    │   ├── roadmap_stage: FOUNDATION
    │   └── current_milestone: "Platform Maturity"
    ├── rfcs (dict[str, RfcRecord])
    │   ├── RFC-018: Capability Platform (COMPLETE)
    │   ├── RFC-018.5: GymOS Kernel (IN_PROGRESS)
    │   └── RFC-019: Recovery Intelligence (DRAFT)
    ├── releases (dict[str, Release])
    │   ├── 0.5.0: Platform Maturity
    │   └── 0.6.0: Recovery Intelligence
    ├── current_rfc: "RFC-018.5"
    └── next_rfc: "RFC-019"
```

## Default State

`create_default_state()` in `kernel_state.py` pre-populates:

**RFCs:**
- RFC-018 (Capability Platform) — COMPLETE, completed 2026-07-03
- RFC-018.5 (GymOS Kernel) — IN_PROGRESS, depends on RFC-018
- RFC-019 (Recovery Intelligence) — DRAFT, depends on RFC-018.5

**Releases:**
- v0.5.0 — Platform Maturity (RFC-018, RFC-018.5, 6 capabilities)
- v0.6.0 — Recovery Intelligence (RFC-019, 1 capability)

**Current:** RFC-018.5 → Next: RFC-019

## Lifecycle

### Product Phase
```
ALPHA (current) → BETA → STABLE → MATURE
```

### Roadmap Stage
```
FOUNDATION (current) → GROWTH → OPTIMIZATION → EXPANSION
```

### RFC Status
```
DRAFT → IN_REVIEW → APPROVED → IN_PROGRESS → COMPLETE
                                                ↓
                                           SUPERSEDED
```

## Key Files

- `shared/kernel/kernel.py` — `ProductIdentity`, `RfcRecord`, `Release` dataclasses
- `shared/kernel/kernel_state.py` — `KernelState` (mutable), `create_default_state()`
