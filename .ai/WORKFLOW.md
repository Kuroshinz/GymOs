# GymOS Development Workflow

Every AI agent MUST follow this workflow in order when implementing any feature or fix.

---

## Step 1 — Read Constitution

Read `.ai/CONSTITUTION.md`.

Understand the project's permanent governing principles.

If a request conflicts with the constitution, the constitution wins.

---

## Step 2 — Read Product Identity

Read `.ai/PRODUCT_IDENTITY.md`.

Understand what GymOS is, why it exists, and what it is not.

This ensures every decision aligns with the product vision, not just technical requirements.

---

## Step 3 — Read Current Sprint

Read `.ai/CURRENT_MILESTONE.md`.

Understand what is in scope for the current milestone.

Do not implement anything outside the current sprint scope unless explicitly asked.

---

## Step 4 — Read Architecture Rules

Read `.ai/ARCHITECTURE_RULES.md`.

Internalise the inviolable architectural constraints.

Never violate layer rules, dependency rules, or module rules.

---

## Step 5 — Review Existing Implementation

Before writing new code:

- Search the repository for existing implementations of similar features
- Read the relevant module's domain, application, and infrastructure layers
- Understand what already exists before adding anything new
- Use file-picker, code-searcher, and glob tools to explore the codebase

---

## Step 6 — Create Implementation Plan

Write a clear plan (use `write_todos`) covering:

- Which files to create or modify
- What each file will contain
- Dependencies between changes
- Testing strategy

Present the plan to the user for confirmation before implementing.

---

## Step 7 — Implement

Write code following:

- `.ai/CODING_STANDARD.md`
- `.ai/IMPLEMENTATION_RULES.md`
- `.ai/ARCHITECTURE_RULES.md`

Make focused, minimal changes. Reuse existing code. Do not over-engineer.

---

## Step 8 — Run Tests

- Typecheck: `mypy .`
- Lint: `ruff check .`
- Unit tests: `pytest`
- Fix all errors before proceeding

---

## Step 9 — Review

Self-check:

1. Does this serve the hypertrophy goal?
2. Does this reduce friction for daily gym use?
3. Are there any architecture violations?
4. Is there any duplicate code?
5. Are all type hints correct?
6. Are imports clean?

Spawn `code-reviewer-deepseek-flash` for a second opinion on significant changes.

---

## Step 10 — Update Documentation

If the implementation changes:

- Architecture — update `.ai/ARCHITECTURE_RULES.md` or `docs/`
- Data models — update `docs/database/schema.md`
- Product — update `docs/CHANGELOG.md`
- Knowledge — update relevant files in `knowledge/`

---

## Step 11 — Generate Summary

Write a concise summary of:

- What was implemented
- Why it was implemented
- What files were changed
- What the user should know next

---

## Quick Reference (Cheat Sheet)

```
CONSTITUTION → PRODUCT_IDENTITY → CURRENT_MILESTONE
       ↓
ARCHITECTURE_RULES → Review Existing → Plan
       ↓
Implement → Test → Review → Document → Summarise
```
