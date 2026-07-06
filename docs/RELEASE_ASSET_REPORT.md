# Release Asset Report — REP-001H Phase 5

**Date:** 2026-07-06  

---

## Found/Missing Matrix

| # | Asset | Status | Details |
|---|-------|--------|---------|
| 1a | `.ico` icon | **MISSING** | No `.ico` files |
| 1b | `.icns` icon | **MISSING** | No `.icns` files |
| 1c | `.png` icon | **MISSING** | No app icon PNGs |
| 1d | `setWindowIcon()` call | **MISSING** | Not in `main.py` or `main_window.py` |
| 2a | About dialog source | **FOUND** | `ui/dialogs/about_gymos_dialog.py` |
| 2b | About dialog wired in UI | **MISSING** | Exists but not connected |
| 3a | Version in `pyproject.toml` | **FOUND** | `"0.1.0"` |
| 3b | Version in `shared/constants/__init__.py` | **FOUND** | `APP_VERSION = "0.1.0"` |
| 3c | Version in `shared/kernel/kernel.py` | **FOUND** | `ProductIdentity.version = "0.5.0"` |
| 3d | Version in about dialog | **FOUND** | `VERSION = "0.5.0"` |
| 3e | Version consistency | **BROKEN** | 3 conflicting versions |
| 4a | `CHANGELOG.md` | **FOUND** | Well-maintained, 108 lines |
| 4b | Release notes | **MISSING** | No dedicated release notes file |
| 4c | Splash screen | **MISSING** | No splash implementation |
| 4d | Startup banner/welcome | **MISSING** | No onboarding |
| 4e | `pyproject.toml` authors | **MISSING** | Not declared |
| 4f | `pyproject.toml` license | **MISSING** | Not declared |
| 4g | `pyproject.toml` classifiers | **MISSING** | Not declared |
| 4h | `pyproject.toml` entry points | **MISSING** | No console_scripts or gui_scripts |

---

## Version Inconsistency

Three distinct version claims exist:

| Location | Version |
|----------|---------|
| `pyproject.toml` | `0.1.0` |
| `main.py` docstring | `0.1.0` |
| `shared/constants/__init__.py` | `0.1.0` |
| `ui/dialogs/about_gymos_dialog.py` | `0.5.0` |
| `shared/kernel/kernel.py` | `0.5.0` |
| `shared/kernel/kernel_context.py` | `0.5.0` |
| `docs/CHANGELOG.md` | `0.5.0` |

**Recommendation:** Unify to `0.5.0` across all locations. This is a 30-second fix: update `pyproject.toml`, `shared/constants/`, and `main.py`.

---

## Asset Readiness Score: 2/10

The only complete assets are `CHANGELOG.md` and the About dialog source (unwired). Everything else is missing or inconsistent.
