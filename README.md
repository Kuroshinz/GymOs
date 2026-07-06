# GymOS — Personal Hypertrophy Operating System

Build your best physique. One intelligent decision at a time.

GymOS is a desktop application that plans, logs, analyzes, and optimizes every aspect of hypertrophy training for ONE user. It replaces spreadsheets, generic fitness apps, and guesswork with a deterministic, evidence-based intelligence layer.

## What GymOS Does

GymOS answers one question every day:

> *"What should I do today to build my best physique?"*

It does this by combining:
- **Workout Intelligence** — PPL-UL programming, double progression, set logging, PR detection
- **Nutrition Intelligence** — macro tracking, lean bulk analysis, hydration management
- **Recovery Intelligence** — fatigue analysis, deload detection, readiness assessment *(in progress)*
- **GymBrain** — deterministic rule engine that evaluates 18+ rules and produces ranked recommendations
- **Knowledge Platform** — 100+ exercises, 50+ muscles, progression science, nutrition protocols

## Current Maturity

| Layer | Status |
|-------|--------|
| Workout tracking | ✅ v0.5 — Production-ready |
| Dashboard | ✅ v0.5 — Production-ready |
| Progress charts | ✅ v0.5 — Production-ready |
| Nutrition Intelligence | ✅ v0.5 — Production-ready (49 tests) |
| GymBrain | ✅ v0.5 — Production-ready (163 tests) |
| Event Platform | ✅ v0.5 — Production-ready |
| Knowledge Platform | ✅ v0.5 — Production-ready |
| Platform Standardization | ✅ v0.5 — ADRs, Protocols, DI Standard |
| Recovery Intelligence | ⏳ v0.6 — Scaffolding, event wired |
| Prediction Engine | 📋 v0.7 — Planned |
| AI Coach | 📋 v0.8 — Planned |
| Adaptive Programming | 📋 v0.9 — Planned |

## Quick Start

```bash
# Install
uv sync

# Run
python main.py

# Test
pytest
```

## Repository Structure

```
.ai/                        # Agent identity, constitution, standards
docs/                       # Product & architecture documentation
├── architecture/           # ADR, DI standard, knowledge platform, module audit
├── archive/               # Outdated docs preserved for reference
├── PRODUCT_STRATEGY.md    # Long-term mission and positioning
├── VERSION_STRATEGY.md    # 0.5 → 1.0 plan
├── ENGINE_ROADMAP.md      # All engine maturity roadmaps
├── EXPERIENCE_ROADMAP.md   # Complete user journey
└── PRODUCT_PILLARS.md      # Training, Nutrition, Recovery, Consistency, Intelligence
knowledge/                  # Single source of truth for fitness data
modules/                    # Domain modules (Clean Architecture)
shared/                     # Events, interfaces, domain models
core/                       # Infrastructure services (DI, EventBus, config)
ui/                         # PySide6 desktop application
tests/                      # Test infrastructure (688+ passing)
```

## Documentation

- [Engineering Constitution](.ai/ENGINEERING_CONSTITUTION.md) — Governing rules for all development
- [Product Strategy](docs/PRODUCT_STRATEGY.md) — Long-term mission, pillars, competitive advantages
- [Version Strategy](docs/VERSION_STRATEGY.md) — 0.5 through 1.0 milestones and criteria
- [Engine Roadmap](docs/ENGINE_ROADMAP.md) — Maturity of every engine
- [Experience Roadmap](docs/EXPERIENCE_ROADMAP.md) — Complete user journey from open to adaptive programming
- [Product Pillars](docs/PRODUCT_PILLARS.md) — Training, Nutrition, Recovery, Consistency, Intelligence, Automation, Knowledge

## Architecture Philosophy

- **Event-Driven** — All module communication through typed Domain Events
- **Clean Architecture** — Domain → Application → Presentation → Infrastructure per module
- **Offline-First** — Zero internet required; SQLite local storage
- **Deterministic** — Same data always produces same recommendations
- **Knowledge-Powered** — All fitness science in `knowledge/`, consumed through validated pipeline

## Who It's For

A 178 cm, 63.4 kg male on a PPL-UL split, lean bulking to 72–75 kg. Focus: shoulders, upper chest, back width, arms. Hypertrophy-first, not powerlifting.

Every feature is built for this user first.

## What GymOS Is NOT

- NOT a generic workout tracker
- NOT a calorie counter
- NOT a social fitness app
- NOT a multi-user platform
- NOT a cloud service
- NOT a powerlifting tracker
