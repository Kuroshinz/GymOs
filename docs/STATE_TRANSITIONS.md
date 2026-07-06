# Product State Transitions

The transition engine determines legal transitions between product states,
generates transition reasons, and maintains a transition history.

## Transition Types

| Type | Description | Example |
|------|-------------|---------|
| **NATURAL** | Normal forward progression | Bootstrapping → Growing |
| **PROMOTION** | Moving toward release | Stable → Release Candidate |
| **REGRESSION** | Moving backward | Growing → Blocked |
| **SIDEWAYS** | Moving laterally | Optimizing → Refactoring |

## Complete Transition Table

| From | → | To | Type | Condition |
|------|---|----|------|-----------|
| Bootstrapping | → | Growing | Natural | Core infrastructure complete |
| Bootstrapping | → | Refactoring | Natural | Early architecture cleanup |
| Bootstrapping | → | Blocked | Regression | Critical blockers |
| Growing | → | Stable | Promotion | Active dev complete |
| Growing | → | Optimizing | Sideways | Quality focus needed |
| Growing | → | Refactoring | Sideways | Debt accumulated during growth |
| Growing | → | Blocked | Regression | Critical blockers detected |
| Stable | → | Optimizing | Natural | Optimization opportunity |
| Stable | → | Refactoring | Natural | Tech debt reduction |
| Stable | → | Release Candidate | Promotion | Release criteria met |
| Stable | → | Maintenance | Natural | All features complete |
| Stable | → | Growing | Natural | New feature development |
| Stable | → | Blocked | Regression | Regressions detected |
| Optimizing | → | Stable | Natural | Optimization complete |
| Optimizing | → | Refactoring | Sideways | Debt prioritized over optimization |
| Optimizing | → | Release Candidate | Promotion | Ready for release |
| Optimizing | → | Growing | Natural | New feature development |
| Refactoring | → | Stable | Promotion | Refactoring complete |
| Refactoring | → | Optimizing | Natural | Quality focus after refactor |
| Refactoring | → | Growing | Natural | New feature development |
| Refactoring | → | Blocked | Regression | Refactoring revealed blockers |
| Blocked | → | Growing | Promotion | Blockers resolved |
| Blocked | → | Refactoring | Natural | Use blocked time for cleanup |
| Blocked | → | Stable | Promotion | Blockers resolved |
| Release Candidate | → | Ready for Release | Promotion | Validation passed |
| Release Candidate | → | Blocked | Regression | Validation failed |
| Release Candidate | → | Stable | Regression | Criteria not met |
| Release Candidate | → | Optimizing | Sideways | More optimization needed |
| Ready for Release | → | Maintenance | Natural | Released |
| Ready for Release | → | Release Candidate | Regression | Issues found |
| Ready for Release | → | Stable | Regression | Release postponed |
| Maintenance | → | Growing | Natural | New feature development |
| Maintenance | → | Optimizing | Natural | Quality improvements |
| Maintenance | → | Refactoring | Natural | Tech debt reduction |
| Maintenance | → | Blocked | Regression | Issues found |

## Transition History

The transition engine maintains an ordered history of all state transitions.
Each record includes:

- `from_state`: The previous product state
- `to_state`: The new product state
- `transition_type`: Natural, Promotion, Regression, or Sideways
- `timestamp`: When the transition occurred
- `reason`: Human-readable explanation
- `confidence`: Confidence score at transition time

## Usage

```python
from shared.state.transitions import TransitionEngine, ProductStateType

engine = TransitionEngine()

# Check if a transition is legal
is_legal = engine.is_legal(
    ProductStateType.GROWING,
    ProductStateType.STABLE,
)

# Get all legal targets from a state
targets = engine.get_legal_transitions(ProductStateType.STABLE)
# → [Optimizing, Refactoring, ReleaseCandidate, Maintenance, Growing, Blocked]

# Record a transition
record = engine.record_transition(
    from_state=ProductStateType.GROWING,
    to_state=ProductStateType.STABLE,
    reason="Active development complete.",
    confidence=85.0,
)

# Get transition history
history = engine.get_history()
```
