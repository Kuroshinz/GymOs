# Cognitive Layer — RFC-029

## Overview

The Cognitive Layer is a deterministic platform above all existing engines that determines what deserves attention, what should be hidden or promoted, and how GymOS should adapt its interface to the user's current context.

**No AI. No LLM. No probabilistic generation.** Every output is computed from weighted deterministic rules consuming canonical engine outputs only.

## Architecture

```
shared/cognitive/
├── __init__.py           # Public API — exports all components
├── models.py             # CognitiveInput / CognitiveOutput dataclasses
├── attention.py          # AttentionEngine — rank signals by urgency/confidence/impact
├── priority.py           # PriorityEngine — deterministic priority scores
├── context.py            # ContextEngine — build runtime context from engine outputs
├── focus.py              # FocusEngine — determine single primary action
├── policy.py             # NotificationPolicy — suppress low-value, surface high-value
├── state.py              # WorkspaceState — describe current cognitive state
└── orchestrator.py       # CognitiveOrchestrator — run full pipeline in one call
```

## Components

### AttentionEngine

Ranks signals by a composite score: `urgency × 0.4 + confidence × 0.3 + impact × 0.3`.

| Signal | Trigger | Score | Narrative Key |
|--------|---------|-------|---------------|
| `CRITICAL_ALERT` | recovery flags present | 100 | `risk_alerts` |
| `RECOVERY_DROP` | recovery_score < 40 | 85 | `recovery_summary` |
| `FATIGUE_SPIKE` | fatigue_score > 80 | 80 | `recovery_summary` |
| `READINESS_LOW` | readiness_score < 40 | 75 | `morning_brief` |
| `PR_ACHIEVED` | weekly_prs > 0 | 70 | (achievement) |
| `ADHERENCE_DROP` | adherence < 50% | 60 | `planning_summary` |
| `DECISION_PENDING` | decision_count > 0 | 40 | `decision_feed` |
| `PREDICTION_CONFIDENCE` | accuracy ≥ 80% | 55 | (info) |

Output: `list[AttentionItem]` sorted by score descending.

### PriorityEngine

Categorizes items into three tiers:

- **Primary** (score ≥ 70): critical health signals, PRs, high fatigue
- **Secondary** (40 ≤ score < 70): moderate signals, pending decisions, system health
- **Deferred** (score < 40): insights, routine updates

Also provides `narrative_order(data) -> list[str]` — template names sorted by priority for narrative rendering.

### ContextEngine

Builds a `CognitiveContext` from raw engine data:

| Field | Source | Values |
|-------|--------|--------|
| `health_summary` | avg(recovery, system, readiness) | good / fair / poor |
| `recovery_status` | recovery_score | optimal / adequate / low / critical |
| `readiness_status` | readiness_score | high / moderate / low |
| `fatigue_level` | fatigue_score | normal / elevated / high |
| `adherence_status` | adherence rate | good / moderate / low |
| `prediction_confidence` | accuracy | high / moderate / low |
| `system_health_status` | system_health | healthy / degraded / critical |
| `to_tags()` | context state | has-alerts, recovery-critical, fatigue-high, etc. |

### FocusEngine

Determines the single primary action using a priority-ordered rule table:

```
1. address critical alerts          → risk_alerts
2. prioritise recovery              → recovery_summary
3. reduce training load             → recovery_summary
4. focus on recovery and mobility   → morning_brief
5. improve sleep quality            → recovery_summary
6. improve workout adherence        → planning_summary
7. review pending decisions         → decision_feed
8. check system health              → risk_alerts
9. review latest insights           → knowledge_summary
10. continue with planned training  → today_focus
```

Returns `FocusRecommendation` with `action`, `reason`, `narrative_key`, and `severity`.

### NotificationPolicy

Deterministic suppression/promotion rules:

- **Score ≥ 80**: always show
- **Score < 30**: always suppress
- **Recovery-critical context**: suppresses score < 60 (except achievements)
- **High fatigue context**: suppresses prediction confidence signals
- **Achievements**: always shown (score ≥ 70 bypasses suppression)

### WorkspaceState

9 deterministic states computed from `CognitiveContext`:

| State | Condition |
|-------|-----------|
| `ALERT` | has_critical_alerts |
| `SYSTEM_DEGRADED` | system_health_status in (critical, degraded) |
| `RECOVERY_FOCUSED` | recovery_status == critical |
| `HIGH_FATIGUE` | fatigue_level == high |
| `LOW_READINESS` | readiness_status == low |
| `ACHIEVEMENT` | pr_count > 0 |
| `DECISION_PENDING` | pending_decision_count > 0 |
| `OFF_SEASON` | no active mesocycle |
| `NOMINAL` | everything nominal |

### CognitiveOrchestrator

Runs the full pipeline in one call:

```python
result = CognitiveOrchestrator.run(data)
# result.attention    — ranked AttentionItems
# result.context      — CognitiveContext
# result.focus        — FocusRecommendation
# result.workspace    — WorkspaceState
# result.output       — CognitiveOutput (all outputs aggregated)
# result.policy_results — NotificationPolicy results per item
```

## CognitiveInput / CognitiveOutput

```python
@dataclass
class CognitiveInput:
    recovery_score: float        # 0-100
    fatigue_score: float         # 0-100
    readiness_score: float       # 0-100
    sleep_score: float           # 0-100
    weekly_adherence: float      # 0-100
    prediction_accuracy: float   # 0-100
    system_health: float         # 0-100
    mission_confidence: float    # 0-100
    weekly_prs: int
    recovery_flags: list[str]
    # ... plus planning, knowledge, decision fields

@dataclass  
class CognitiveOutput:
    workspace_state: str
    primary_focus: str
    primary_focus_reason: str
    critical_alerts: list[str]
    secondary_recommendations: list[str]
    deferred_items: list[str]
    achievements: list[str]
    milestones: list[str]
    upcoming_risks: list[str]
    attention_items: list[dict]
    suppressed_notifications: int
```

## Integration Points

| Integration | What it does |
|------------|-------------|
| **Dashboard Hero** | Reflects `FocusEngine` primary focus |
| **Narrative cards** | Reordered by `PriorityEngine` score via `narrative_order()` |
| **Visualization emphasis** | Follows `AttentionEngine` ranking |
| **Notification center** | Consumes `NotificationPolicy` |
| **Command Center** | Highlights current `CognitiveContext` |
| **Kernel Runtime** | Registered as capability `cognitive-layer` |

## Design Principles

1. **No business logic**: Every score is computed from existing engine outputs. No engine calculations are re-implemented.
2. **Fully deterministic**: Same inputs → same outputs. Tests verify this explicitly.
3. **No AI/LLM**: Weighted rules only. Extensible with new rules, never with models.
4. **Stateless**: All outputs are computed fresh from source data. No stored state.
5. **Consumes canonical outputs only**: Reads from `CognitiveInput` which aggregates Recovery, Prediction, Planning, Knowledge, and Runtime data.
6. **No UI dependency**: Lives in `shared/` — any module can query it.

## Capability

Registered as `cognitive-layer` in the Capability Platform (status: COMPLETE, maturity: IMPLEMENTED).
