# GymBrain — GymOS Intelligence Engine

## Overview

GymBrain is the evidence-based decision-making engine of GymOS. It answers one question:

> **What should the user do next to maximize hypertrophy?**

Every recommendation is:
- **Deterministic** — same data always produces the same recommendations
- **Reproducible** — recommendations can be traced to specific rules and data points
- **Explainable** — every recommendation includes its rule, evidence, and confidence level

## Architecture

```
modules/gymbrain/
├── __init__.py                  # Public API exports
├── models/
│   ├── recommendations.py       # Recommendation, category, priority, action, evidence types
│   └── analysis.py              # FatigueResult, PlateauResult, MuscleAnalysis, GoalProgress, WeeklyReview
├── rules/
│   ├── base.py                  # BaseRule ABC + RuleResult
│   ├── engine.py                # RuleEngine — evaluates all rules, deduplicates, sorts
│   ├── volume_rules.py          # VolumeRule, VolumeExcessRule, FrequencyRule
│   ├── progression_rules.py     # ProgressionRule, DeloadRule
│   ├── plateau_rules.py         # WeightPlateauRule, StrengthPlateauRule, RepPlateauRule
│   ├── fatigue_rules.py         # FatigueRule, TechniqueRule, RestRule
│   ├── recovery_rules.py        # RecoveryRule, ConsistencyRule
│   └── nutrition_rules.py       # NutritionRule, BodyweightStallRule
├── analysis/
│   ├── plateau.py               # PlateauDetector — 6 plateau types
│   ├── fatigue.py               # FatigueAnalyzer — 5-factor fatigue model
│   ├── muscle.py                # MuscleAnalyzer — per-muscle volume, frequency, recovery
│   └── goals.py                 # GoalTracker — bodyweight goals, bulking progress
├── services/
│   ├── decision_engine.py       # DecisionEngine — central orchestrator + Dashboard API
│   └── weekly_review.py         # WeeklyReviewGenerator — structured weekly summary
├── providers/
│   └── data_provider.py         # DataProvider — decouples GymBrain from infrastructure
├── cache/
│   └── analysis_cache.py        # Time-based analysis result cache
└── tests/                       # 130 tests, all passing
```

## Data Flow

```
User Action → Workout Session → Event Bus → Event Store
                                                  ↓
DataProvider ←──────────────────── reads from ←────┘
     ↓
RuleEngine → evaluates 15 rules against current state
     ↓
DecisionEngine → deduplicates, sorts by priority × confidence
     ↓
Structured Recommendations → consumed by UI/Notifications
```

## Key Principles

1. **No AI, no LLMs** — all decisions are rule-based and deterministic
2. **No direct DB access** — GymBrain consumes only DataProvider interfaces
3. **No UI logic** — Dashboard API returns typed objects, never HTML or strings
4. **No magic heuristics** — every number, threshold, and calculation is documented
5. **Modular rules** — each rule is a single class, independently testable

## Future Integration Paths

- **Nutrition Intelligence** — add `NutritionProvider` subclass, nutrition-specific rules
- **Recovery Intelligence** — add sleep data, HRV, subjective well-being metrics
- **AI Coach** — rule engine outputs feed into LLM-based natural language generation
- **Wearable Data** — additional data sources via DataProvider interface
