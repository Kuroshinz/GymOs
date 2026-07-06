# Product Lifecycle

Defines the stages every GymOS capability, feature, and release passes through.

---

## Stages

```
CONCEPT → PROTOTYPE → ALPHA → BETA → RELEASE CANDIDATE → PRODUCTION → LTS
```

---

### 1. CONCEPT

**Entry criteria:** Identified user need aligned with at least one product pillar.

**Activities:**
- Define problem statement and success criteria
- Identify pillar alignment and cross-pillar dependencies
- Draft RFC with motivation, approach, alternatives
- Initial capability registration at CONCEPT maturity
- No code written

**Exit criteria:**
- RFC submitted and accepted by maintainer
- Capability registered in Capability Platform
- Dependencies identified and assessed

**Artifacts:** RFC document, Capability registration

---

### 2. PROTOTYPE

**Entry criteria:** Accepted RFC.

**Activities:**
- Exploratory implementation in a sandbox branch
- Core domain entities defined
- Basic engine/service skeleton
- Proof-of-concept tests (10-20%)
- No UI, no infrastructure, no integration

**Exit criteria:**
- Core domain entities compile and pass basic tests
- Architecture reviewed and approved
- Decision to proceed (or reject) documented

**Artifacts:** Domain entities, skeleton engine, proof-of-concept tests, Architecture Review notes

---

### 3. ALPHA

**Entry criteria:** Approved architecture.

**Activities:**
- Engine(s) fully implemented
- Deterministic tests covering normal cases
- Provider interfaces defined
- Basic integration with PredictionService/GymBrain
- Capability maturity advanced to DESIGN or FOUNDATION

**Exit criteria:**
- Engine logic complete with tests (≥60%)
- Provider interface defined and implemented
- Integration point wired (even if stubbed)
- Backend-only — no UI required

**Artifacts:** Engine implementation, provider interface, integration wiring, test suite

---

### 4. BETA

**Entry criteria:** Engine complete, provider wired.

**Activities:**
- Full test coverage (≥80%)
- Edge cases, error handling, boundary conditions
- UI widgets implemented
- Dashboard integration
- Events published and consumed correctly
- Capability maturity advanced to IMPLEMENTED

**Exit criteria:**
- All tests pass (≥80% coverage)
- UI widgets render all data states
- Events fire correctly
- Manual QA passes for happy path and edge cases

**Artifacts:** Full test suite, UI widgets, dashboard integration, QA sign-off

---

### 5. RELEASE CANDIDATE

**Entry criteria:** Beta complete.

**Activities:**
- Documentation complete (ADRs, README, capability report)
- Performance profiling and optimization
- Cross-platform testing (Windows primary)
- Full regression suite passes (no regressions)
- Capability report generated

**Exit criteria:**
- All 9 types of documentation artifacts exist
- Performance targets met
- Zero regressions in full test suite
- Release readiness assessed as READY or ALMOST_READY

**Artifacts:** Capability report, release notes, performance benchmark, release readiness assessment

---

### 6. PRODUCTION

**Entry criteria:** Release candidate approved.

**Activities:**
- Merge to main branch
- Tag release version
- Capability marked COMPLETE
- Milestone updated
- Kernel snapshot taken

**Exit criteria:**
- Release tagged and published
- Capability status = COMPLETE

**Artifacts:** Release tag, changelog entry, kernel snapshot

---

### 7. LTS (Long-Term Support)

**Entry criteria:** Entered when a capability reaches STABLE maturity and has been in production for ≥1 minor version cycle.

**Activities:**
- Bug fixes only — no new features
- Security patches as needed
- Dependency updates for compatibility
- Superseded capabilities enter DEPRECATED status

**Exit criteria:** Capability enters DEPRECATED status when a successor is available and migration is complete.

**Artifacts:** LTS branch, maintenance log

---

## Lifecycle State Machine

```
                    ┌─────────────────────────────────────────────┐
                    │                                             │
                    v                                             │
CONCEPT → PROTOTYPE → ALPHA → BETA → RC → PRODUCTION → LTS ──────┤
                    │                    │                         │
                    │                    v                         │
                    │              (rollback) ───→ CONCEPT         │
                    │                                             │
                    v                                             │
              (rejected) ─────→ ARCHIVE                            │
                                                                   │
              DEPRECATED ←─────────────────────────────────────────┘
```

## Phase-to-Maturity Mapping

| Product Phase | Typical Capability Maturity | Risk Level |
|---|---|---|
| CONCEPT | CONCEPT | HIGH |
| PROTOTYPE | DESIGN | HIGH |
| ALPHA | FOUNDATION | MEDIUM |
| BETA | IMPLEMENTED | MEDIUM |
| RC | IMPLEMENTED | LOW |
| PRODUCTION | IMPLEMENTED → STABLE | LOW |
| LTS | STABLE+ | VERY LOW |
