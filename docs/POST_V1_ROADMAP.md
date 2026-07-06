# GymOS — Post-v1 Roadmap

**Date:** 2026-07-06  
**Target:** v1.1.0, v1.2.0, v2.0.0  

---

## v1.1.0 — Stability & Polish

**Target:** 2 weeks after v1.0.0-stable

### Required

| # | Task | Area | Effort |
|---|------|------|--------|
| 1 | Fix 48 test bugs for green CI | Testing | 1 day |
| 2 | Fix 12 silenced handlers in dashboard_data_service.py | Exception safety | 0.5 day |
| 3 | Fix 28 silenced handlers in production_provider.py | Exception safety | 1 day |
| 4 | Fix TrendIndicator interactivity | Micro UX | 0.5 day |
| 5 | Reduce 47 actionable `Any` annotations | Typing | 2 days |
| 6 | Implement goal persistence path | Features | 1 day |

### Desired

| # | Task | Area | Effort |
|---|------|------|--------|
| 7 | Wire AdaptiveService to real provider | Features | 2 days |
| 8 | Add tab order to all pages | Accessibility | 1 day |
| 9 | Add accessible names to interactive widgets | Accessibility | 1 day |
| 10 | Code signing (Windows + macOS) | Distribution | 1 day |
| 11 | Verify build pipeline on clean machine | Distribution | 1 day |
| 12 | Add `--cov-fail-under` to CI (currently 70) | CI/CD | 0.5 day |

---

## v1.2.0 — Developer Experience

**Target:** 6 weeks after v1.1.0

| # | Task | Area | Effort |
|---|------|------|--------|
| 1 | Fix remaining 200+ `Any` annotations | Typing | 3 days |
| 2 | Enable mypy strict mode | Typing | 2 days |
| 3 | Add pre-commit hooks (ruff, mypy, trailing whitespace) | CI/CD | 0.5 day |
| 4 | Add Dependabot for dependency updates | CI/CD | 0.5 day |
| 5 | Pytest --strict-markers | Testing | 0.5 day |
| 6 | Add API documentation (pdoc or sphinx) | Documentation | 2 days |
| 7 | Add screenshots to README | Documentation | 1 day |
| 8 | Add CII Best Practices badge | Community | 0.5 day |

---

## v2.0.0 — Platform Expansion

**Target:** 12 weeks after v1.0.0-stable

### Major Features

| # | Feature | Rationale |
|---|---------|-----------|
| 1 | **AI Coach integration** | Wire DecisionEngine to LLM for natural-language coaching |
| 2 | **Training program marketplace** | Community-shared programs with ratings |
| 3 | **Advanced analytics** | Deeper trend analysis, periodization planning |
| 4 | **Multi-user support** | Family/team accounts with shared programs |
| 5 | **Cloud sync** | Optional encrypted sync across devices |
| 6 | **Mobile companion** | Lightweight workout tracking on iOS/Android |

### Infrastructure

| # | Task | Rationale |
|---|------|-----------|
| 7 | ARM64 builds (macOS + Linux) | Apple Silicon, Raspberry Pi |
| 8 | Flatpak + Snap packaging | Broader Linux distribution |
| 9 | Database encryption | User data protection |
| 10 | Internationalization (i18n) | Multi-language support |
| 11 | Performance profiling and optimization | Startup <1s, memory <80MB |

### Architecture

| # | Task | Rationale |
|---|------|-----------|
| 12 | Deprecate legacy dashboard views | Single UI surface |
| 13 | Remove design system visualization shadow | Single visualization source |
| 14 | Service layer push notifications | Real-time UI updates instead of pull polling |
| 15 | Plugin system for third-party extensions | Community contributions |

---

## Feature Requests (Candidates)

These are not committed but are under consideration:

- **Wearable integration** — Import HRV, sleep data from Apple Watch / Garmin / Oura
- **Exercise library** — Video demonstrations, form tips, alternative exercises
- **Meal planning** — AI-generated meal plans based on macro targets
- **Training partners** — Social features, group challenges
- **Export / Import** — CSV, JSON, FIT, TCX
- **Dark / Light theme toggle** — User-selectable theme
- **Custom dashboards** — Drag-and-drop widget arrangement
- **Progressive Web App** — Browser-based workout tracking

---

## Maintenance Cadence

| Cycle | Frequency | Activities |
|-------|-----------|------------|
| Patch | As needed | Critical bug fixes, security updates |
| Minor | 6-8 weeks | Features, improvements, dependency updates |
| Major | 6-12 months | Architecture changes, platform expansion |

---

## Deprecation Policy

- Deprecated features receive **one minor version** of continued support
- Removal is announced one full version cycle in advance
- Migration guides are provided for breaking changes

---

*End of Post-v1 Roadmap*
