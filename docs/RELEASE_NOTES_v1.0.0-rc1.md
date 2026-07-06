# GymOS v1.0.0-rc1 — Release Notes

**Date:** 2026-07-06  
**Status:** Release Candidate 1  

---

We are pleased to announce the first Release Candidate of GymOS v1.0.0.

GymOS is a personal hypertrophy operating system — a modular, domain-driven fitness intelligence platform that integrates workout programming, recovery tracking, predictive analytics, and adaptive decision-making.

This release represents the culmination of 11 RFC sprints spanning architecture, interaction wiring, product completion, production hardening, release infrastructure, product finish, packaging, and certification.

---

## Features

**Training**
- Workout tracking with exercises, sets, reps, weight, and RPE
- Program import, activation, and management (PPL, Push/Pull/Legs, etc.)
- Progress view with volume trends and PR tracking

**Nutrition**
- Meal logging with macro tracking (calories, protein, carbs, fat)
- Daily nutrition summary and adherence scoring

**Recovery**
- Sleep logging with quality tracking
- Stress and fatigue monitoring
- Readiness scoring with multi-factor analysis
- Deload scheduling and history

**Predictive Analytics**
- Confidence scoring for training outcomes
- Scenario analysis and forecasting
- Risk assessment for training decisions

**Command Center**
- 9-page executive dashboard (Home, Mission, Planning, Prediction, Recovery, Knowledge, Analytics, Adaptive, System)
- 124 interactive surfaces with real-time data display
- Quick search and command palette
- Breadcrumb navigation with history

**Visualization**
- 30 interactive visualization widgets (rings, curves, timelines, gauges, graphs, heatmaps)
- Training load, recovery, PR, bodyweight, and macro trend curves
- Muscle volume heatmaps and fatigue analysis

---

## Infrastructure

**Crash Safety**
- Global exception handler with detailed crash reports
- Recovery dialog on next startup
- Safe shutdown with service cleanup registry

**Database**
- SQLite with WAL mode, foreign keys, and busy timeout
- Schema version tracking via PRAGMA user_version
- Alembic migration chain (3 migrations)
- Automatic backup before schema migration
- Backup validation with integrity check

**Version System**
- Single canonical version source (`shared/version.py`)
- Version, build, schema, database, protocol, and release channel tracked
- Consistent across all 6 version locations

**Packaging**
- Windows: PyInstaller + NSIS installer (EXE + portable ZIP)
- Linux: AppImage + DEB package
- macOS: DMG with code signing pipeline
- All with SHA256 checksum verification

**Auto-Update**
- Version manifest with release channel support
- Update checker with semver comparison
- Download verification via SHA256

---

## UI/UX

- Animated splash screen with startup progress (8 stages)
- 4-step first-launch onboarding wizard
- Welcome screen with demo data seeding
- Global Qt stylesheet covering 20+ widget types
- Custom scrollbar styling (thin, accent hover)
- Application icon (SVG, 7 resolutions up to 512px, ICO + ICNS)
- About dialog with 4 tabs (About, Credits, License, Build Info)
- Credits, license, and changelog viewer dialogs
- Consistent hover, focus, and selection feedback

---

## Downloads

| Platform | File |
|----------|------|
| Windows (installer) | `GymOS-0.5.0-Setup.exe` |
| Windows (portable) | `GymOS-0.5.0-Windows.zip` |
| Linux (AppImage) | `GymOS-0.5.0-x86_64.AppImage` |
| Linux (DEB) | `gymos_0.5.0_amd64.deb` |
| macOS | `GymOS-0.5.0.dmg` |

---

## Checksums

```
(SHA256 checksums available in dist/SHA256SUMS.txt)
```

---

## Known Limitations

This is a Release Candidate. The following issues are acknowledged but are not blocking:

- 48 test failures (all test bugs — stale assertions, not production bugs)
- 12 silenced exception handlers in dashboard data service
- 28 silenced exception handlers in production provider
- No code signing (Windows/macOS — SmartScreen/Gatekeeper warnings expected)
- Build pipeline not yet verified on a clean machine
- Screen reader support not implemented

See `docs/KNOWN_LIMITATIONS.md` for the full list.

---

## Installation

See `docs/INSTALLATION_GUIDE.md` for platform-specific instructions.

**Quick start:**
1. Download the appropriate package for your platform
2. Install or extract
3. Launch GymOS
4. Complete the 4-step welcome wizard
5. Start training

---

## Feedback

Please report issues at: https://github.com/gymos/gymos/issues

Include crash reports from `data/crashes/` when reporting bugs.
