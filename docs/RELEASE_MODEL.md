# Release Model

## Overview

The Release Model assesses whether GymOS is ready to ship a version. It is the Kernel's release gating system — combining blockers, capability completion, documentation, tests, health, and debt into a single readiness score.

## Release Score

**Formula:** `cap_completion * 0.30 + doc_score * 0.15 + test_score * 0.20 + health_score * 0.20 + debt_score * 0.15 - (blockers * 10)`

### Component Weights

| Component | Weight | Source |
|-----------|--------|--------|
| Capability Completion | 30% | Status distribution across 12 capabilities |
| Documentation | 15% | Average documentation health from Capability Platform |
| Test Coverage | 20% | Average test coverage from Capability Platform |
| Overall Health | 20% | Average health across all capabilities |
| Technical Debt | 15% | Blocking debt ratio (blocking / total) |
| Blocker Penalty | -10 per blocker | Blocked capabilities + blocked_by references |

## Readiness Tiers

| Tier | Score | Requirements |
|------|-------|-------------|
| **NOT_READY** | < 40 | Blockers exist, significant gaps remain |
| **ALMOST_READY** | 40-74 | Some blockers or gaps, but core is functional |
| **READY** | >= 75 | No blockers, high completion, good health |

## Current Assessment

For v0.5.0:
- **Readiness:** NOT_READY (score: 0)
- **Blockers:** 6+ (Recovery Intelligence blocked by settings, Decision Intelligence blocked by Recovery, Experience Platform blocked by Recovery, AI Coach blocked by Decision + Recovery, Prediction Engine blocked by AI Coach, Digital Twin blocked by Prediction + AI Coach)
- **Gaps:** 4 capabilities not started (Experience Platform, AI Coach, Prediction Engine, Digital Twin)

This is expected for Alpha — the model will graduate more releases as capabilities complete.

## Blockers

A blocker is any capability that:
1. Has status = BLOCKED, OR
2. Has non-empty `blocked_by` references

Blocking is transitive: if A blocks B and B blocks C, all three count.

## Release Record

```python
Release(
    version="0.5.0",
    name="Platform Maturity",
    rfc_ids=("RFC-018", "RFC-018.5"),
    capabilities=("training-intelligence", "nutrition-intelligence", ...),
    is_released=False,
)
```

## Key Files

- `shared/kernel/kernel.py` — `Release`, `ReleaseReadinessResult`, `ReleaseReadiness` enum
- `shared/kernel/kernel_context.py` — `assess_release_readiness()`
