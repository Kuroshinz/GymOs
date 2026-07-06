# ADR-008: Product State Engine

**Status:** Accepted

## Context

GymOS has grown into a complex platform with multiple subsystems (Capability Platform, Kernel, Evolution Engine, Product Knowledge Graph). There is no single authoritative answer to "What state is the product in right now?" Understanding the product's current operational state — whether it's bootstrapping, growing, stable, blocked, or ready for release — requires a dedicated runtime layer that continuously evaluates all canonical data sources.

The RFC requires a system capable of answering:
- What state is GymOS in right now?
- How confident are we in this assessment?
- Is the product drifting from its ideal state?
- Is the product ready for release?
- What would a transition cost?

## Decision

Build a Product State Engine as a stateless evaluation layer in `shared/state/`. The engine:

- **Consumes without duplicating**: reads from Capability Platform, Kernel, Evolution Engine, and Product Knowledge Graph. No data is stored in the state engine — it computes everything fresh from source data.
- **9 deterministic states**: Bootstrapping, Growing, Stable, Optimizing, Refactoring, Blocked, ReleaseCandidate, ReadyForRelease, Maintenance. Each state has clear entry criteria derived from indicator thresholds.
- **Multi-dimensional analysis**: 5 drift dimensions (architecture, documentation, capability, knowledge, RFC), composite confidence scoring, release readiness assessment.
- **Legal transition enforcement**: ~40 legal transitions with type classification (natural, promotion, regression, sideways).
- **Clean Architecture compliance**: Lives in `shared/` — any module can query it. No UI, no workout/nutrition/recovery logic.

## Rationale

1. **Self-awareness without duplication**: The engine is pure computation — all data comes from canonical sources. If the capability registry changes, the state evaluation reflects it immediately.

2. **Deterministic state determination**: State is not guessed — it's computed from quantitative indicators (health scores, completion percentages, debt counts, readiness scores).

3. **Composable scoring**: Confidence, drift, and release readiness are independent dimensions that can be analyzed separately or combined.

4. **Transition safety**: The transition engine prevents illegal state changes and provides clear reasoning for every transition.

5. **Testable**: All evaluation logic is pure — indicators in, state out. No I/O, no side effects.

## Consequences

**Positive:**
- Single authority for product state — no more guessing "where are we?"
- Drift detection catches architecture and documentation degradation early
- Release readiness assessment provides clear go/no-go criteria
- 180+ tests verify correctness
- Transition history provides audit trail

**Negative:**
- Depends on the accuracy of underlying canonical sources
- State thresholds are heuristic — may need tuning as product evolves
- No persistence (intentional — state is always computed fresh)

## Technical Details

### State Determination Rules

```
health ≥70, readiness ≥70, completion ≥80% → ReleaseCandidate
health ≥85, readiness ≥90 → ReadyForRelease
blocking_debt ≥3 or blockers ≥2 → Blocked
health ≥60, completion ≥70%, in_progress ≤3 → Stable
health ≥50, in_progress=0, not_started ≤2 → Optimizing
debt ≥10, health ≥30 → Refactoring
complete ≥80%, not_started=0 → Maintenance
in_progress >0, completion ≥30% → Growing
else → Bootstrapping
```

### Drift Dimensions

| Dimension | Calculation | Threshold |
|-----------|------------|-----------|
| Architecture | Variance in architecture scores across capabilities | >30 = elevated |
| Documentation | Average gap between doc score and target (80) | >30 = elevated |
| Capability | Gap between current and target maturity | >30 = elevated |
| Knowledge | % capabilities without documentation links | >30 = elevated |
| RFC | % RFCs stuck in DRAFT | >30 = elevated |

### Confidence Scoring

| Component | Weight |
|-----------|--------|
| State Confidence | 30% |
| Release Confidence | 30% |
| Data Quality | 15% |
| Coverage | 15% |
| Timestamp Freshness | 10% |
