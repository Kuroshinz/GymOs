# GymOS AI Constitution

**Version:** 1.0
**Status:** Permanent — supersedes all feature requests

This document defines the permanent operating principles of every AI agent working on GymOS (NEXUS).

This file has **higher priority than all feature requests**.

If a request conflicts with this constitution, the constitution always wins.

---

## PROJECT PURPOSE

GymOS is **NOT** a demo project.

GymOS is **NOT** a portfolio project.

GymOS is a **real software product** that will be used every day by its owner.

The primary mission is:

**Help the user build the best possible aesthetic physique through structured hypertrophy training.**

Everything developed must move the user closer to this goal.

---

## PRIMARY USER

The current application is built for **ONE** person.

| Attribute | Value |
|-----------|-------|
| Height | 178 cm |
| Current Weight | 63.4 kg |
| Goal | Lean Bulk |
| Target Weight | 72–75 kg |
| Training Split | PPL-UL |
| Primary Objective | Hypertrophy |
| Priority Muscles | Side Delts, Upper Chest, Back Width, Arms |

The AI must optimise every feature for this user.

---

## PRODUCT PHILOSOPHY

GymOS is an **Operating System**.

Not a workout tracker.

Not a calorie tracker.

Not an AI chatbot.

Every feature must support one of:

- **Training**
- **Nutrition**
- **Recovery**
- **Consistency**
- **Progressive Overload**

If it does not improve one of these, reject it.

---

## DEVELOPMENT PHILOSOPHY

1. Documentation first.
2. Architecture second.
3. Implementation third.
4. Optimisation fourth.

**Never reverse this order.**

---

## SOURCE OF TRUTH

Never invent data.

Never invent training schedules.

Never invent nutrition values.

Never invent scientific evidence.

Always use `knowledge/` as the primary source.

If information is missing, create placeholders — never hallucinate.

---

## ARCHITECTURE

Always preserve:

- Clean Architecture
- SOLID Principles
- Repository Pattern
- Dependency Injection
- Feature Modules

Never bypass layers.

Never place business logic inside UI.

Never place SQL inside UI.

Never create circular dependencies.

---

## FITNESS RULES

Assume hypertrophy is always the default objective.

| Aspect | Rule |
|--------|------|
| Default Progression | Double Progression |
| Compound Rep Range | 6–12 |
| Isolation Rep Range | 10–15 |
| Core Rep Range | 12–20 |

Always prefer **technique → ROM → consistency** before increasing load.

---

## AI BEHAVIOUR

Before implementing any feature, read in order:

1. `.ai/CONSTITUTION.md`
2. `.ai/PRODUCT_IDENTITY.md`
3. `.ai/WORKFLOW.md`
4. `.ai/IMPLEMENTATION_RULES.md`
5. `.ai/`
6. `docs/`
7. `knowledge/`
8. Current module
9. Current sprint

Then analyse. Then plan. Only then implement.

**Never immediately generate code.**

---

## IMPLEMENTATION ORDER

Always follow:

Understand → Review existing implementation → Reuse existing code → Design → Implement → Test → Review → Update documentation

---

## CODE QUALITY

- Never duplicate code.
- Never over-engineer.
- Never create abstractions without multiple use cases.
- Prefer readability over cleverness.
- Keep functions small.
- Keep modules independent.

---

## USER EXPERIENCE

The owner will use GymOS inside the gym.

Every interaction must be:

- **Fast** — no loading delays
- **Simple** — one tap to log a set
- **Touch-friendly** — large buttons, swipeable
- **Minimal** — show only what's needed

Logging a set should require only a few seconds.

---

## AI COACH

The AI Coach is **NOT** a chatbot.

It is a **performance coach**.

Recommendations must be based on:

- Workout history
- Recovery
- Volume
- Nutrition
- Progression

Never generate random advice.

---

## PERFORMANCE

- GymOS should work offline.
- Startup should be fast.
- Every screen should feel responsive.
- Avoid unnecessary dependencies.

---

## DOCUMENTATION

Every significant implementation must update:

- README
- Architecture docs
- Knowledge files
- Changelog

when appropriate.

---

## REVIEW

Before completing any task, ask yourself:

1. Does this improve GymOS?
2. Does this help the user reach their physique goal?
3. Does this reduce friction?
4. Would the user use this tomorrow?

If the answer is **no**, do not implement.
