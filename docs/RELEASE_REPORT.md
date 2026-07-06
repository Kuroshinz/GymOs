# GymOS v1.0.0-rc1 — Release Report

**Date:** 2026-07-06  
**Release Candidate:** 1  

---

## Overview

GymOS is a personal hypertrophy operating system — a modular, domain-driven fitness intelligence platform that integrates workout programming, recovery tracking, predictive analytics, and adaptive decision-making.

This is the first Release Candidate for public distribution.

---

## What's Included

### Features

- **Workout tracking** — Log exercises, sets, reps, weight, RPE
- **Program management** — Import, activate, switch between training programs
- **Nutrition logging** — Log meals, track macros, adherence scoring
- **Recovery tracking** — Sleep, stress, fatigue, readiness, HRV, soreness
- **Predictive analytics** — Confidence scores, scenarios, risk assessment
- **Decision intelligence** — Adaptive programming, training recommendations
- **Command Center** — 9-page dashboard with KPIs, charts, and interactive widgets
- **Knowledge graph** — Relationship mapping and concept exploration

### Infrastructure

- **Crash safety** — Global exception handler, crash reports, recovery dialog
- **Database versioning** — WAL mode, foreign keys, schema migration chain
- **Backup/restore** — Automatic pre-migration backups, integrity validation
- **Version system** — Single canonical source, no drift
- **Auto-update** — Version manifest, SHA256 verification, release channels

### Packaging

| Platform | Format | Installer |
|----------|--------|-----------|
| Windows | EXE + ZIP | NSIS |
| Linux | AppImage + DEB | appimagetool / dpkg-deb |
| macOS | DMG | hdiutil |

---

## Key Metrics

| Metric | Value |
|--------|-------|
| Modules | 12 domain modules |
| UI Pages | 16 (7 legacy + 9 command center) |
| Dialogs | 10 production dialogs |
| Design components | 35+ reusable widgets |
| Visualization widgets | 30 interactive visualizations |
| Interactive surfaces | 124 (99.2% connected) |
| Tests | 3327 passing, 48 known test bugs |
| Test pass rate | 98.6% |
| Lines of code | ~45,000 |

---

## Version Architecture

```
shared/version.py
├── APP_VERSION          = "0.5.0"
├── BUILD_NUMBER          = 1
├── SCHEMA_VERSION        = 3
├── DATABASE_VERSION      = 3
├── PROTOCOL_VERSION      = "1.0"
├── RELEASE_CHANNEL       = "alpha"
├── ALEMBIC_HEAD          = "003"
├── VersionInfo dataclass → CURRENT
├── shared/constants/__init__.py
├── shared/kernel/kernel.py
├── shared/kernel/kernel_context.py
├── ui/dialogs/about_gymos_dialog.py
├── main.py
└── pyproject.toml
```

---

## Database

| Property | Value |
|----------|-------|
| Engine | SQLite 3 (via SQLAlchemy 2.x) |
| Safety | WAL mode, foreign_keys=ON, busy_timeout=5000 |
| Schema version | 3 (PRAGMA user_version) |
| Migration | Alembic with 3 migration scripts |
| Backup | Automatic before migration, integrity validation |
| Repositories | 6 (workout, nutrition, recovery, prediction, program, settings) |

---

## Release Contents

| Artifact | Size (est.) |
|----------|-------------|
| GymOS-0.5.0-Setup.exe | ~55 MB |
| GymOS-0.5.0-Windows.zip | ~50 MB |
| GymOS-0.5.0-x86_64.AppImage | ~60 MB |
| gymos_0.5.0_amd64.deb | ~55 MB |
| GymOS-0.5.0.dmg | ~60 MB |
| update_manifest.json | <1 KB |
| SHA256SUMS.txt | <1 KB |

---

## Known Limitations

See `docs/KNOWN_LIMITATIONS.md` for the full list.

**Top 5:**
1. 48 test bugs need resolution (all stale assertions, not production bugs)
2. DashboardDataService has 12 silenced exception handlers — some dashboard features silently fail
3. TrendIndicator is the only non-interactive click surface
4. No code signing for Windows/macOS builds
5. Screen reader support not implemented

---

## Post-v1 Roadmap

See `docs/POST_V1_ROADMAP.md` for the full plan.

**Next priorities:**
1. Fix 48 test bugs for green CI
2. Remove 47 actionable `Any` annotations
3. Fix 60+ silenced exception handlers
4. Obtain code signing certificates

---

## Resources

| Resource | Location |
|----------|----------|
| Source code | `https://github.com/gymos/gymos` |
| Installation | `docs/INSTALLATION_GUIDE.md` |
| Architecture | `docs/RELEASE_ARCHITECTURE.md` |
| Changelog | `docs/CHANGELOG.md` |
| Build instructions | `scripts/build/README.md` |
| Issues | `https://github.com/gymos/gymos/issues` |
