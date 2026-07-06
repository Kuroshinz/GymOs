# GymOS — Personal Hypertrophy Operating System

A desktop application that plans, logs, analyses, and optimises every training session for ONE user.

**Goal:** Help the owner build the best aesthetic physique possible using data-driven hypertrophy training.

## User

| Attribute | Value |
|-----------|-------|
| Height | 178 cm |
| Current Weight | 63.4 kg |
| Goal Weight | 72–75 kg |
| Split | PPL-UL (5-6 days/week) |
| Goal | Lean Bulk |
| Focus | Shoulders, Upper Chest, Back Width, Arms |

## Architecture

```
Event-driven · Clean Architecture · Python 3.11+ · SQLite · PySide6
```

- `core/` — Infrastructure services (EventBus, DI, Theme, Database)
- `nexus/` — Platform engines (Workout, Nutrition, Recovery, AI)
- `modules/` — Domain modules (Clean Architecture per module)
- `sdk/` — Plugin SDK (future)
- `knowledge/` — Single source of truth for fitness domain data
- `.ai/` — Agent identity and process documentation

## Current Phase

**v0.1.0 MVP** — Replace the Excel tracker with:
- Workout plan management (PPL-UL templates)
- Set logging (weight, reps, RPE) with previous session comparison
- Personal Record detection
- Dashboard (daily view, nutrition, weight, streak)
- Progress charts (weight, volume, strength, frequency)
- Nutrition import from Cronometer CSV
- Dark-themed, keyboard-navigable, offline-first

## Quick Start

```bash
# Install dependencies
uv sync

# Run database migrations
alembic upgrade head

# Start the application
python main.py
```

## Knowledge Base

The `knowledge/` directory is the authoritative source for all fitness domain data:
- `exercises/` — 100+ exercise definitions with setup, cues, mistakes, alternatives
- `nutrition/` — Macronutrient, calorie, and hydration guidelines
- `progression/` — Double progression, deload, RPE/RIR, volume landmarks
- `recovery/` — Sleep, stress, fatigue, recovery protocols
- `research/` — Evidence summaries of hypertrophy science
- `user/` — Current user profile, goals, training data
