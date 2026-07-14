# RFC-040: Visual Language 3.0

**Status:** IMPLEMENTATION  
**Priority:** CRITICAL  
**Sprint:** REP-007K  

---

## 1. Executive Summary

GymOS has completed all feature pages (Dashboard, Workout, Progress, Recovery, Prediction) and the Motion System. However, the application still exhibits visual inconsistencies that prevent it from feeling like a single product.

This RFC documents the comprehensive visual audit and defines the unified visual language that will make every screenshot immediately identifiable as GymOS.

### Three Words That Define GymOS

| Word | Meaning | Visual Expression |
|------|---------|-------------------|
| **Calm** | Confident, never aggressive | Dark backgrounds, generous spacing, subtle gradients, muted accents |
| **Premium** | Deliberate, not cheap | Consistent border radii, unified card language, glow effects on primary actions |
| **Supportive** | Coaching, not commanding | Narrative-first labels, StatusBadge for feedback, warm accent colors |

---

## 2. Typography Audit

### Current State

| Style | Token | Pages Using Correctly | Pages Using Literals |
|-------|-------|----------------------|---------------------|
| hero | `font_style('hero')` | Dashboard, Workout, Recovery, Prediction, Progress | Settings |
| h1 | `font_style('h1')` | Dashboard | — |
| h2 | `font_style('h2')` | Dashboard, Progress, Recovery, Prediction | Settings |
| h3 | `font_style('h3')` | Workout, Recovery, Prediction, Progress | Settings, Dialogs |
| body | `font_style('body')` | All pages | Settings |
| body_small | `font_style('body_small')` | Recovery, Prediction | Settings |
| caption | `font_style('caption')` | All pages | Settings |
| label | `font_style('label')` | StatusBadge, SectionHeader | Settings |
| metric | `font_style('metric')` | Dashboard, Progress | Settings |

### Issues Found

1. **SettingsView** — Uses hardcoded `font-size: 24px; font-weight: 700;` instead of `font_style('h2')`
2. **Dialogs** — Inconsistent: some use tokens, others use literals
3. **WorkoutView** — `font-size: 16px` literals in several places instead of `font_style('body')`
4. **Sidebar** — Uses `font-size: 14px` literals for nav buttons

### Resolution

- Replace all font-size literals with `font_style()` calls
- Enforce: only one hero size, one h1, one h2, one body, one caption, one label
- No `font-size` CSS property should appear outside token definitions

---

## 3. Color Audit

### Current State

All color values come from `color_from_scheme(ColorScheme.DARK)` except:

| File | Issue | Severity |
|------|-------|----------|
| `ui/settings_view.py` | ALL colors hardcoded (`#1E293B`, `#F1F5F9`, etc.) | **CRITICAL** |
| `ui/workout_view.py` | Some backgrounds use literals | Medium |
| `ui/shell/header.py` | Button backgrounds use literals | Low |

### Resolution

- `settings_view.py`: Complete rewrite with DarkColorTokens
- `workout_view.py`: Replace all remaining color literals
- Enforce: every color value goes through `color_from_scheme()`

---

## 4. Card Language Audit

### Current Card Implementations

| Card Type | Used In | Implementation |
|-----------|---------|---------------|
| Hero card | Dashboard, Recovery, Prediction | Custom QFrame with gradient background |
| Mission card | Dashboard | Custom QFrame |
| Summary cards | Recovery | AppCard |
| Evidence cards | Prediction | Custom _EvidenceCard(AppCard) |
| Coach card | Dashboard | Custom QFrame |
| PR cards | Progress | AppCard |
| Achievement cards | Progress | Custom _AchievementCard(QFrame) |
| Exercise card | Workout | Custom ExerciseCard(QFrame) |
| Set blocks | Workout | Custom _SetBlock(QFrame) |
| Action cards | Dashboard | Custom _CommandCard(QFrame) |
| Counterfactual cards | Recovery, Prediction | Custom _CounterfactualCard(AppCard) |

### Issues

1. **Dashboard builds all cards as QFrame** instead of using AppCard — inconsistent with other pages
2. **Multiple card patterns** — no single card "language" is enforced
3. **Padding inconsistency** — varies from 12px to 24px

### Card Family Definition

| Card Family | Radius | Padding | Border | Elevation | Use |
|-------------|--------|---------|--------|-----------|-----|
| Hero | `R.xl` (20px) | 24px | `1px solid border` | Level 3 | Page heroes |
| SectionCard | `R.lg` (16px) | 20px | `1px solid border` | Level 2 | Section content |
| MetricCard | `R.lg` (16px) | 16px | `1px solid border` | Level 1 | Metric values |
| InsightCard | `R.md` (10px) | 12px | `1px solid border` | Level 1 | Coach insights |
| TimelineCard | `R.md` (10px) | 12px | `1px solid border` | Level 0 | Timeline items |

### Resolution

- Dashboard hero frames remain as gradient QFrames (they're structural, not cards)
- All other cards should use AppCard or conform to the card family
- Standardize card padding to token values

---

## 5. Spacing Audit

### Current Inconsistencies

| Locale | Space | Token | Issue |
|--------|-------|-------|-------|
| Dashboard section gap | `_px32` / `_px24` | `S.s8` / `S.s6` | Mixed |
| Progress section gap | `_px24` / `_px20` | `S.s6` / `S.s5` | Minor |
| Recovery section gap | `_px24` | `S.s6` | ✅ |
| Prediction section gap | `_px24` | `S.s6` | ✅ |
| Workout section gap | `_px12` | `S.s3` | Different page type |

### Resolution

- Standardize section gaps to `S.s6` (24px)
- Standardize card padding to `S.s4` (16px)
- Standardize content margins to `S.s8` (32px)

---

## 6. Visual Density Audit

### Issues

1. **Dashboard action cards** — 88px height is too tall for 5 cards
2. **Workout set blocks** — 52px height makes the timeline feel dense
3. **Recovery summary cards** — Well balanced
4. **Prediction evidence cards** — Well balanced

### Resolution

- Reduce unnecessary spacing between related items
- Remove redundant labels
- Increase white space between sections

---

## 7. Emotional Design Audit

### Current Tone

| Page | Tone | Issue |
|------|------|-------|
| Dashboard | Supportive, energetic | ✅ |
| Workout | Coaching, focused | ✅ |
| Progress | Motivating, narrative | ✅ |
| Recovery | Calm, analytical | Could be warmer |
| Prediction | Analytical, informative | Could be more supportive |

### Resolution

- Add narrative warmth to Recovery coach messages
- Make Prediction language more supportive, less clinical

---

## 8. Accessibility Audit

### Issues

1. SettingsView lacks accessible names on several interactive elements
2. Some dialog buttons missing `setAccessibleName`
3. Focus rings not always visible (some custom widgets override styles)

### Resolution

- Add `setAccessibleName()` to all interactive elements
- Ensure all custom QFrame subclasses have visible focus rings
- Add keyboard navigation hints to empty states

---

## 9. Implementation Checklist

- [x] Generate RFC-040 document
- [x] Fix `settings_view.py` — replace all hardcoded colors with DarkColorTokens
- [x] Fix `workout_view.py` — replace font-size literals with tokens
- [x] Fix `settings_view.py` — use `font_style()` for all typography
- [x] Add accessible names to all interactive elements
- [x] Standardize card styling across pages
- [x] All pages compile without errors

---

## 10. Before/After Comparison

### Settings View

**Before:** Hardcoded `#1E293B` backgrounds, `#F1F5F9` text, `#818CF8` buttons — no token usage at all.  
**After:** Uses `colors.surface`, `colors.text_primary`, `colors.primary` — every value from tokens.

### Workout View

**Before:** Mixed `font-size: 12px`, `font-size: 16px`, `font-size: 48px` literals alongside `font_style()` calls.  
**After:** All typography uses `font_style()` — no font-size literals.

### Accessibility

**Before:** Missing `setAccessibleName()` on command cards, dialog CTAs, and some buttons.  
**After:** Every interactive element has an accessible name.
