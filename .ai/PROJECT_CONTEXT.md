# GymOS — Project Context

## Identity

**GymOS** is a Personal Hypertrophy Operating System built for exactly ONE user.

The entire application exists to answer one question:  
*"What should I do today to build my best physique?"*

## Governing Document

**GMP-001 (GymOS Master Plan)** is the permanent governing document for all product, architecture, and engineering decisions. Every RFC, milestone, capability, and release must align with GMP-001.

See `docs/GMP/MASTER_PLAN.md` for the full Master Plan.

## Current Phase

**v0.5.0 — Platform Standardization Complete**

The application has matured beyond the original "workout tracker" vision. It is now an intelligence platform with a deterministic rule engine, nutrition intelligence, event-driven architecture, prediction intelligence, and platform-wide engineering standards.

## The User

| Attribute | Value |
|-----------|-------|
| Height | 178 cm |
| Current Weight | 63.4 kg |
| Goal Weight | 72–75 kg |
| Training Style | PPL-UL (5-6 days/week) |
| Goal | Lean Bulk |
| Focus Muscles | Shoulders, Upper Chest, Back Width, Arms |
| Philosophy | Hypertrophy-first, not powerlifting |

## What This Means for Development

Every feature must improve at least one of the eight product pillars (defined in GMP-001):

1. **Training** — better workouts, smarter progression, more effective exercises
2. **Nutrition** — eat enough to grow, track macros, stay on bulk
3. **Recovery** — sleep, deload, fatigue management to maximize gains
4. **Consistency** — show up every session, never miss, streak tracking
5. **Intelligence** — deterministic rule engine that explains every recommendation
6. **Automation** — reduce manual decisions, let data drive programming
7. **Prediction** — forecast athlete states, simulate scenarios, quantify risk
8. **Knowledge** — single source of truth for all fitness science

## Architecture Principle

Event-driven desktop application built with Clean Architecture: Python 3.11+, SQLite, PySide6. The knowledge layer (`knowledge/`) is the single source of truth. GymBrain consumes all module data through typed Provider interfaces and produces deterministic, explainable recommendations.

## What NOT to Build

- No social features (no friends, no sharing, no leaderboards)
- No marketplace or plugin ecosystem
- No multi-user or coach features
- No wearable vendor lock-in (maybe later for HRV/sleep)
- No cloud dependency (offline-first is mandatory)
- No features that don't serve the hypertrophy goal
