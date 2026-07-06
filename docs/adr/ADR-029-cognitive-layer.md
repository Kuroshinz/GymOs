# ADR-029: Cognitive Layer & Attention Engine

**Status:** Accepted

## Context

GymOS has 16 registered capabilities, 30+ engines, a command center with 10 pages, and a narrative engine producing coach-like briefings. There is no single system that determines:

- what deserves the user's attention right now,
- what should be hidden or deferred,
- what should be promoted to the primary focus,
- and how the interface should adapt to the user's current context.

Without a cognitive layer, every engine and UI component makes independent visibility decisions, leading to noise, competing priorities, and a fragmented experience.

## Decision

Build a **Cognitive Layer** in `shared/cognitive/` as a deterministic, stateless evaluation platform above all existing engines.

The Cognitive Layer:

- **Consumes canonical outputs only**: reads from Recovery, Prediction, Planning, Knowledge, Explainability, and Runtime. No data is stored — every output is computed fresh from source data.
- **Six components**:
  - `AttentionEngine` — rank signals by urgency, confidence, impact, and context
  - `PriorityEngine` — compute deterministic priority scores for recommendations
  - `ContextEngine` — build a runtime context from cross-engine data
  - `FocusEngine` — determine the single primary action for the current session
  - `NotificationPolicy` — suppress low-value, surface high-value notifications
  - `WorkspaceState` — describe the current cognitive state of the application
- **Deterministic weighted rules only**: no AI, no LLM, no probabilistic generation.
- **No duplicated business logic**: all scores are computed from existing engine outputs. No engine calculations are re-implemented.
- **Clean Architecture**: lives in `shared/` — any module can query it. No UI dependency.

## Outputs

- Today's Primary Focus
- Critical Alerts
- Secondary Recommendations
- Deferred Items
- Achievements
- Milestones
- Upcoming Risks

## Integration Points

- **Dashboard Hero**: reflects the primary focus from `FocusEngine`
- **Narrative cards**: reordered by `PriorityEngine` score
- **Visualization emphasis**: follows `AttentionEngine` ranking
- **Notification center**: consumes `NotificationPolicy`
- **Command Center**: highlights current context from `ContextEngine`

## Rationale

1. **Single source of attention truth**: One platform answers "what matters now?" consistently across all UI surfaces.

2. **Deterministic and testable**: Weighted rules produce identical outputs for identical inputs. All components have unit tests.

3. **No lock-in**: The layer can be extended with new signals (user preferences, historical behavior) without changing any engine.

4. **Minimal coupling**: The Cognitive Layer imports dataclasses only — no engine classes, no service instances, no mutable state.

## Consequences

- All UI components that surface attention/priority must route through `CognitiveLayer` rather than making independent decisions.
- New signals (e.g., user feedback on focus accuracy) can be added as weighted rule inputs without architectural changes.
- The layer adds ~600 lines of Python across 6 components + tests + integration glue.
