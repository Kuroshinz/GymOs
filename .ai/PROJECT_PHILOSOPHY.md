# Project Philosophy

*Effective: Sprint 3.2.5*

## 1. What GymOS Is

GymOS is a **Personal Hypertrophy Operating System**. It is not a workout tracker. It is not a nutrition logger. It is an intelligent training companion that:

- **Analyzes** training, nutrition, and recovery data
- **Reasons** about user state using deterministic rules
- **Recommends** the best next action for maximum hypertrophy
- **Adapts** to user goals, preferences, and progress
- **Explains** why every recommendation exists

## 2. Core Beliefs

### 2.1 Evidence-Based, Not Trend-Based
Every rule, threshold, and recommendation MUST be grounded in exercise science. If a rule cannot cite a source, it shouldn't exist.

### 2.2 Deterministic, Not Black-Box
The same data always produces the same output. No randomness. No hidden state. Every recommendation is explainable.

### 2.3 Progress Over Perfection
The system MUST work with partial data. No nutrition data? Still recommend workouts. No recovery data? Still detect plateaus. Degrade gracefully.

### 2.4 Offline-First
All features work without internet. Sync is additive, not required.

### 2.5 Modules, Not Monoliths
Every domain is an independent module. Modules communicate through typed events. No module knows the internal structure of another.

## 3. Design Values

### 3.1 Testability
Every component MUST be testable in isolation. If it's hard to test, the design is wrong. Use constructor injection, Protocol interfaces, and dependency inversion.

### 3.2 Simplicity
Favor simple solutions over clever ones. Flat is better than nested. Explicit is better than implicit. Working is better than perfect.

### 3.3 Replaceability
Every external dependency (database, API, file format) MUST be behind an interface. Swapping SQLite for PostgreSQL should require changes in one place.

### 3.4 Traceability
Every event, recommendation, and decision MUST be traceable back to its source. Why did the system recommend a deload week? Because rules X, Y, Z triggered with evidence A, B, C.

## 4. What GymOS Is NOT

- **Not a social network** — no friends, no sharing, no leaderboards
- **Not a coaching platform** — no paid plans, no subscriptions, no trainers
- **Not a mobile app** — Desktop-first (PySide6), CLI second
- **Not a black box** — every decision is explainable and overridable
- **Not a data silo** — export all data in open formats (JSON, CSV)

## 5. The Golden Rule

Never sacrifice determinism for convenience. Never sacrifice testability for speed. Never sacrifice simplicity for generality.

The best code is the code that:
1. Works correctly
2. Is easy to test
3. Is easy to change
4. Is easy to understand

In that order.
