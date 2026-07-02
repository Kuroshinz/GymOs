# NEXUS — Architectural Decision Log

## Format

```
## ADR-NNN: Title

Status: [Proposed | Accepted | Deprecated | Superseded]

Context:
<why we need to decide>

Decision:
<what we chose>

Rationale:
<why we chose it over alternatives>

Consequences:
<positive and negative effects>
```

---

## ADR-001: EventBus as Central Communication

Status: Accepted

Context:
NEXUS needs decoupled module communication. Direct imports between modules
create tight coupling and make testing difficult.

Decision:
All inter-module communication passes through an EventBus with middleware
support. Events are typed, immutable value objects.

Rationale:
- Modules become independently testable
- New modules can hook existing events without changing producers
- Middleware enables cross-cutting concerns (logging, metrics, tracing)

Consequences:
+ Loose coupling between modules
+ Easy to add new integrations
- Slightly more boilerplate than direct calls
- Need clear event naming conventions

---

## ADR-002: Clean Architecture per Module

Status: Accepted

Context:
Each module contains business logic that must be testable independently
of frameworks and infrastructure.

Decision:
Every module follows Domain → Application → Infrastructure → Presentation.
Dependency flows inward. Infrastructure implements application ports.

Rationale:
- Business logic is framework-agnostic
- Swap database/UI without touching domain
- Proven at scale (DDD community)

Consequences:
+ Highly testable business logic
+ Infrastructure can be replaced
- More files per module
- Team must understand the pattern

---

## ADR-003: Custom DI Container (No Framework)

Status: Accepted

Context:
NEXUS needs dependency injection without pulling in a heavy framework
(DependencyInjector, inject, etc.).

Decision:
A lightweight custom Container with register/resolve, factory support,
and lifecycle management.

Rationale:
- Zero external dependency for core infrastructure
- Easy to debug (no magic)
- Full control over lifecycle

Consequences:
+ Minimal dependency footprint
+ Easy to understand and debug
- Won't have advanced features (auto-wiring, scopes)
- Must maintain ourselves

---

## ADR-004: SDK Wrapper Over Core

Status: Accepted

Context:
Plugins should not depend on internal core APIs that may change.

Decision:
An SDK layer (`sdk/`) re-exports stable core APIs. Plugins import only from
`nexus.sdk.*`. Core can refactor without breaking plugins.

Rationale:
- Backward compatibility guarantee for plugin authors
- Core can evolve independently
- SDK version can differ from core version

Consequences:
+ Stable plugin API
+ Core refactoring freedom
- Extra abstraction layer to maintain
- SDK must be kept in sync

---

## ADR-005: Async Throughout

Status: Accepted

Context:
NEXUS handles I/O-bound operations (database, HTTP, file I/O) and needs
concurrent event handling.

Decision:
All I/O-bound functions are `async def`. Uses `asyncio` primitives.
Event handlers run concurrently.

Rationale:
- Efficient concurrency for I/O
- Single-threaded simplifies state management
- Ecosystem maturity (SQLAlchemy async, aiohttp)

Consequences:
+ Efficient resource usage
+ Natural concurrent event handling
- Slight learning curve for sync-only developers
- Must be careful with blocking calls

---

## ADR-006: SQLite + SQLAlchemy Async

Status: Accepted

Context:
MVP needs a zero-configuration database that works offline-first.

Decision:
SQLite with SQLAlchemy async ORM and Alembic for migrations.

Rationale:
- Zero setup — file-based database
- SQLAlchemy provides rich ORM with async support
- Alembic handles schema evolution
- Easy to migrate to PostgreSQL later

Consequences:
+ Simple deployment
+ Rich ORM features
- Concurrency limits (WAL mode mitigates)
- SQLite-specific SQL must be isolated

---

## ADR-007: Domain Knowledge as Structured Data

Status: Accepted

Context:
AI Coach and workout features need authoritative exercise, nutrition,
and progression data. Hardcoding in Python or relying on AI to guess
leads to inconsistency.

Decision:
Domain knowledge stored as structured files (JSON/YAML) in `knowledge/`.
Each domain has its own directory. AI reads this data before generating
coaching advice or workout logic.

Rationale:
- Single source of truth for domain data
- Easy to update by domain experts (non-developers)
- AI can reliably reference known-correct data
- Foundation for future knowledge graph

Consequences:
+ Higher quality AI outputs
+ Domain experts can contribute without writing code
+ Audit trail for fitness knowledge
- Must keep knowledge/ in sync with code
- File management overhead at scale

---

## ADR-008: Single-User Focus (Rebrand to GymOS)

Status: Accepted

Context:
The original NEXUS vision targeted a broad "Personal Performance OS" with
multi-user, marketplace, plugin ecosystem, and general wellness features.
This generic scope added complexity without serving the user's actual goal.

Decision:
Rebrand to GymOS. Narrow the focus to ONE user's hypertrophy goal.
Remove all multi-user, social, marketplace, and platform features from scope.

Rationale:
- Every feature that doesn't serve the single user's goal is wasted effort
- Single-user design dramatically simplifies architecture (no auth, no sharing)
- Focused scope delivers working product faster
- The user's actual need is hypertrophy training, not a generic OS

Consequences:
+ Massively simplified product scope
+ All features directly serve the user's goal
+ Faster MVP delivery
- Renaming effort (code, docs, config)
- Must reject feature requests outside scope

---

## ADR-009: Double Progression as Primary Hypertrophy Method

Status: Accepted

Context:
GymOS is optimised for hypertrophy (not powerlifting). Need a progression
method that maximises volume accumulation, is sustainable long-term, and
provides clear weekly progress signals.

Decision:
Double Progression (reps first, weight second) is the primary progression
method for all hypertrophy training.

Rationale:
- Higher volume accumulation than 5x5 / linear progression
- Clear, measurable progress every session (more reps)
- Built-in deload mechanism (weight jumps naturally reduce reps)
- Better hypertrophy stimulus from higher rep ranges
- The user can see progress even when weight hasn't increased

Consequences:
+ Every session has a clear goal (beat last session's reps)
+ Sustainable for 6+ months without linear progression burnout
+ Naturally fits 8-12 and 10-15 rep ranges
- Must educate the user on the method
- Requires consistent tracking (which GymOS provides)

---

## ADR-010: Prioritised Muscle Focus in Programming

Status: Accepted

Context:
GymOS must reflect the user's specific aesthetic goals, not generic
programming advice. The user prioritises shoulders, upper chest, back
width, and arms.

Decision:
All workout planning and exercise selection must prioritise:
1. Side + Rear Delts (lateral raises, face pulls)
2. Upper Chest (incline press, low-to-high fly)
3. Back Width (lat pulldowns, pull-ups, wide rows)
4. Arms (curls, extensions, hammer curls)

Lower body volume is maintained for proportion but not prioritised.

Consequences:
+ Program is personalised to the user's aesthetic goals
+ Volume distribution reflects priorities
+ Exercise suggestions bias toward focus muscles
- Must document the priority system clearly
- Lower body may progress slower (acceptable trade-off)
