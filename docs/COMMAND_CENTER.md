# GymOS Command Center — RFC-022

## Overview

The Command Center is a premium desktop experience that exposes existing GymOS platform intelligence through a unified, modern dashboard UI. It consumes canonical business logic from 6 registered capabilities without duplicating any domain logic.

## Architecture

```
ui/command_center/
├── command_center.py          # Main container widget
├── controller.py               # Aggregated controller (event-driven)
├── models.py                   # Data models (frozen dataclasses)
├── theme.py                    # Design system constants
├── navigation/                 # Sidebar, breadcrumb, search, palette
├── layout/                     # Grid, dockable, resizable panels
├── pages/                      # 9 page views
├── widgets/                    # 16 widget cards
├── services/                   # 9 data services (pull-based)
└── visualization/              # 7 reusable viz components
```

## Pages (9)

| Page | ID | Description |
|------|-----|-------------|
| Home | `home` | Overview dashboard with top intelligence cards |
| Today's Mission | `mission` | Intent, readiness, adaptive/decision timelines |
| Planning | `planning` | Mesocycle progress, weekly review, volume chart |
| Prediction Center | `prediction` | Forecast cards, strength/volume trend charts |
| Recovery Center | `recovery` | Score, readiness, sleep/stress, trends, heatmap |
| Knowledge Center | `knowledge` | Insights, knowledge updates, relationship graph |
| Adaptive Center | `adaptive` | Adaptation & decision timelines, strategy charts |
| Analytics Center | `analytics` | Volume, compliance, nutrition, PR trends, heatmap |
| System Center | `system` | Health, capabilities, release, kernel, product state |

## Widgets (16)

| Widget | Card Title | Data Source |
|--------|-----------|-------------|
| AdaptiveTimelineWidget | Adaptive Timeline | AdaptiveService |
| DecisionTimelineWidget | Decision Timeline | AdaptiveService |
| KnowledgeUpdatesWidget | Knowledge Updates | KnowledgeService |
| PredictionSummaryWidget | Prediction Summary | PredictionService |
| IntentCardWidget | Current Intent | MissionService |
| OptimizationInsightsWidget | Optimization Insights | KnowledgeService |
| RecoveryOverviewWidget | Recovery Overview | RecoveryService |
| TrainingReadinessWidget | Training Readiness | RecoveryService |
| CurrentMesocycleWidget | Current Mesocycle | PlanningService |
| WeeklyReviewWidget | Weekly Review | PlanningService |
| SystemHealthWidget | System Health | SystemService |
| CapabilityProgressWidget | Capability Progress | SystemService |
| ReleaseReadinessWidget | Release Readiness | SystemService |
| KernelRuntimeWidget | Kernel Runtime | SystemService |
| ProductStateWidget | Product State | SystemService |
| KnowledgeGraphWidget | Knowledge Graph | KnowledgeService |

## Data Flow

```
Domain Events (EventBus)
    ↓ subscribe
CommandCenterController
    ↓ data_updated signal
Pages (9)
    ↓ update_data
Widgets (16) ← set_data(models)
```

## Design Principles

- **No duplicated business logic** — all services consume canonical engines via composition
- **No AI/LLM** — all data is deterministic and reproducible
- **Event-driven** — widgets update reactively via controller signals
- **Frozen models** — all data models are frozen dataclasses with defaults
- **Safe failures** — every service wraps calls in try/except with sensible defaults

## File Count

- 50 source files across 7 subpackages
- 366+ tests across 20 test files
