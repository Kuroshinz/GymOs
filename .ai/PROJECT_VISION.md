# GymOS — Project Vision

GymOS is not a workout tracker.  
GymOS is not a spreadsheet replacement.  
GymOS is a **Personal Hypertrophy Operating System**.

Every feature must directly improve the user's ability to build an aesthetic physique. If it doesn't, it doesn't belong in GymOS.

## Governing Document

**GMP-001 (GymOS Master Plan)** at `docs/GMP/MASTER_PLAN.md` defines the permanent mission, vision, philosophy, principles, roadmap, version strategy, and governance for the entire platform.

## The North Star

> **"What should I do today to build my best physique?"**

Every screen, every recommendation, every data point serves this question.

## The Eight Pillars

All features belong to one of these pillars (defined in GMP-001):

| Pillar | Core Principle |
|--------|---------------|
| **Training** | Optimized PPL-UL programming with double progression |
| **Nutrition** | Lean bulk macro tracking with GymBrain integration |
| **Recovery** | Fatigue management, deload timing, readiness assessment |
| **Consistency** | Streak tracking, habit formation, session adherence |
| **Intelligence** | Deterministic rule engine — explainable, rankable recommendations |
| **Prediction** | Forecast athlete states, simulate scenarios, quantify risk |
| **Automation** | Reduce manual decisions — data-driven programming |
| **Knowledge** | Single source of truth for all fitness science |

## Long-Term Vision

| Version | Identity | Capabilities |
|---------|----------|-------------|
| v0.5 | **Platform** | Mature architecture, GymBrain, Nutrition Intelligence, Prediction Intelligence, ADRs, Standards |
| v0.6 | **Coach** | Recovery Intelligence, deload scheduling, nutrition UI, weekly review |
| v0.7 | **Analyst** | Prediction Engine complete (already delivered in v0.5), timeline charts, compound analysis |
| v0.8 | **Coach** | AI Coach — natural language explanations, adaptive guidance |
| v0.9 | **Autopilot** | Adaptive programming — self-tuning program from recovery, nutrition, prediction |
| v1.0 | **Operating System** | Full Autopilot — all pillars operational, 1200+ tests, performance targets met |
| v2.0 | **Digital Twin** | Longitudinal athlete model, adaptation tracking, injury risk, form decay |

## Design Philosophy

1. **One user, perfectly served.** Every feature evaluated against one criterion: "Does this help the user build muscle?"
2. **Data-driven, not hype-driven.** Training decisions from the user's own history, not generic programs.
3. **Minimalist.** Features that don't directly improve a pillar are rejected.
4. **Calm, premium, fast.** No noise, no notifications, polished interactions, instant startup.
5. **Offline-first.** Zero internet required. Sync is convenience, not requirement.
6. **Knowledge-powered.** All science in `knowledge/`. GymBrain consumes through typed interfaces.

## What GymOS is NOT

- NOT a social fitness app
- NOT a powerlifting tracker (hypertrophy-first)
- NOT a calorie counter (Cronometer handles logging)
- NOT a multi-user platform
- NOT a cloud service
- NOT a marketplace or plugin ecosystem

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Weight gain | 63.4 → 72-75 kg | Weekly weigh-in trend |
| Strength progression | Linear 6+ months | Volume/1RM charts |
| Workout consistency | ≥85% sessions | Streak tracking |
| Nutrition compliance | Protein ≥140g, calories ≥2800 daily | Macro tracking |
| Platform stability | 484+ tests passing | CI pipeline |
