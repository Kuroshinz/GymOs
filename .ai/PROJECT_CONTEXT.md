# GymOS — Project Context

## Identity

**GymOS** (formerly NEXUS) is a personal operating system built for exactly ONE user.

The entire application exists to answer one question:  
*"What should I do today to build my best physique?"*

## The User

| Attribute | Value |
|-----------|-------|
| Height | 178 cm |
| Current Weight | 63.4 kg |
| Goal Weight | 72–75 kg |
| Training Style | PPL-UL (Push/Pull/Legs — Upper/Lower) |
| Goal | Lean Bulk |
| Focus Muscles | Shoulders, Upper Chest, Back Width, Arms |
| Philosophy | Hypertrophy-first, not powerlifting |

## What This Means for Development

Every feature must improve at least one of:
- **Training** — better workouts, smarter progression, more effective exercises
- **Nutrition** — eat enough to grow, track macros, stay on bulk
- **Recovery** — sleep, deload, fatigue management to maximise gains
- **Consistency** — show up every session, never miss, streak tracking
- **Progressive Overload** — always be adding weight, reps, or volume

## What NOT to Build

- No social features (no friends, no sharing, no leaderboards)
- No marketplace or plugin ecosystem (this is personal software)
- No multi-user or coach features
- No wearable vendor lock-in (maybe later for HRV/sleep)
- No cloud dependency (offline-first is mandatory)
- No features that don't serve the hypertrophy goal

## Architecture Principle

The platform is an event-driven desktop application built with Clean Architecture, Python 3.11+, SQLite, and PySide6. The knowledge layer (`knowledge/`) is the single source of truth for all fitness domain data. The AI Engine references this data to provide coaching recommendations.

## Current Phase

**MVP (v0.1.0):** Workout tracking, dashboard, progress charts, nutrition import, settings. Replace the Excel tracker used daily in the gym.
