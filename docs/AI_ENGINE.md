# NEXUS — AI Engine Architecture

## Overview

The AI Engine (`nexus/engines/AIEngine/`) powers the AI Coach, recommendations,
predictions, and intelligent automation in NEXUS. It is designed to run fully
offline with local LLMs or connect to cloud APIs when available.

## Architecture

```
┌───────────────────────────────────────────┐
│              AI Engine                     │
│                                           │
│  ┌─────────┐  ┌──────────┐  ┌─────────┐  │
│  │ Coach   │  │ Reasoner │  │ Predict │  │
│  └────┬────┘  └────┬─────┘  └────┬────┘  │
│       │            │             │        │
│  ┌────┴────────────┴─────────────┴────┐   │
│  │          Context Builder            │   │
│  │  (loads knowledge/ + user data)     │   │
│  └────────────────┬───────────────────┘   │
│                   │                       │
│  ┌────────────────┴───────────────────┐   │
│  │          LLM Interface              │   │
│  │  (Local: llama.cpp / Ollama)        │   │
│  │  (Cloud: OpenAI, Anthropic API)     │   │
│  └─────────────────────────────────────┘   │
└───────────────────────────────────────────┘
```

## Components

### 1. Coach Module (`modules/brain/coach/`)
- Reads user's training history
- Loads exercise data from `knowledge/exercises/`
- Loads progression rules from `knowledge/progression/`
- Generates workout recommendations, deload suggestions, progression advice

### 2. Reasoner Module (`modules/brain/reasoner/`)
- Answers user questions about form, technique, programming
- Uses knowledge/ as authoritative reference
- Provides citations to knowledge source

### 3. Prediction Engine (`nexus/engines/PredictionEngine/`)
- Predicts 1RM progression based on historical data
- Forecasts recovery time based on training load
- Suggests optimal deload timing

## Knowledge Sources

The AI Engine reads from:

| Source | Purpose |
|--------|---------|
| `knowledge/exercises/*.json` | Exercise data, targets, cues, mistakes |
| `knowledge/progression/*.md` | Progression rules (double progression, RIR, etc.) |
| `knowledge/nutrition/*.md` | Nutrition guidelines, macros, timing |
| `knowledge/recovery/*.md` | Recovery protocols, sleep, HRV |
| `knowledge/research/*.md` | Scientific references for recommendations |

## Prompt Architecture

```
System Prompt:
  - Role: Expert strength coach and nutritionist
  - Identity from .ai/AGENT.md
  - Instructions to reference knowledge/ data
  - Citation requirement

Context:
  - User's training history (last 30 days)
  - Current goals from settings
  - Today's scheduled workout
  - Relevant knowledge/ entries

User Query:
  - Natural language question or request

Response:
  - Specific, actionable recommendation
  - Citations to knowledge/ and scientific research
  - Structured format (exercise, sets, reps, RPE where applicable)
```

## Offline-First Strategy

| Scenario | Strategy |
|----------|----------|
| No Internet | Use local LLM (Ollama with Llama/Mistral) |
| Internet available | Use cloud API (OpenAI, Anthropic) |
| No GPU | Use smaller quantised model or cloud-only |
| API rate limited | Fall back to rule-based recommendations |

## Integration Points

- **EventBus**: Listens to `workout.completed`, `nutrition.meal_logged`,
  `recovery.sleep_logged` to trigger analysis
- **Settings**: Reads user preferences (goals, experience level, equipment)
- **Knowledge Layer**: Reads domain data via file system
- **Progress Module**: Reads historical data for trend analysis
