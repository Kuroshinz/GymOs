# GymOS Distribution Guide

## Release Process

### 1. Prepare Release

```bash
# Update version
# Edit shared/version.py — bump MAJOR.MINOR.PATCH and BUILD_NUMBER

# Update changelog
# Edit docs/CHANGELOG.md — add release entry

# Verify version consistency
python -c "
from shared.version import APP_VERSION, BUILD_NUMBER, SCHEMA_VERSION
print(f'Version: {APP_VERSION}')
print(f'Build:   {BUILD_NUMBER}')
print(f'Schema:  {SCHEMA_VERSION}')
"
```

### 2. Build

```bash
# Full release build (runs PyInstaller + platform packaging)
./scripts/build/release.sh

# Generate icons and banners
python scripts/build/render_icons.py --banners --screenshots

# Generate update manifest
python scripts/build/generate_manifest.py
```

### 3. Verify

```bash
# Check all artifacts exist
ls -lh dist/

# Verify checksums
cd dist
sha256sum -c SHA256SUMS.txt
```

### 4. Publish

```bash
# Tag the release
git tag -a v0.5.0 -m "GymOS 0.5.0"
git push origin v0.5.0

# CI/CD will automatically:
#   1. Verify tag matches APP_VERSION
#   2. Run lint + test + typecheck
#   3. Create release artifacts
#   4. Create GitHub Release with changelog
```

## Distribution Channels

### GitHub Releases (Primary)

All build artifacts are published to GitHub Releases:
- `GymOS-{version}-Setup.exe` — Windows installer
- `GymOS-{version}-Windows.zip` — Windows portable
- `GymOS-{version}-x86_64.AppImage` — Linux AppImage
- `gymos_{version}_amd64.deb` — Linux DEB
- `GymOS-{version}.dmg` — macOS DMG
- `update_manifest.json` — Auto-update manifest
- `SHA256SUMS.txt` — File checksums

### Update Manifests

Channel-specific manifests are generated at build time:
- `dist/update_manifest.json` — Full manifest
- `dist/stable.json` — Stable channel
- `dist/alpha.json` — Alpha channel (if configured)

These should be hosted at `https://gymos.app/updates/` or on the GitHub Pages site.

### Release Notes Template

```markdown
## GymOS {version}

### What's New
- {feature 1}
- {feature 2}

### Bug Fixes
- {fix 1}

### Infrastructure
- {infra change}

### Downloads
| Platform | File | Size |
|----------|------|------|
| Windows | GymOS-{version}-Setup.exe | {size} |
| Windows (portable) | GymOS-{version}-Windows.zip | {size} |
| Linux | GymOS-{version}-x86_64.AppImage | {size} |
| Linux (DEB) | gymos_{version}_amd64.deb | {size} |
| macOS | GymOS-{version}.dmg | {size} |

### Checksums
```
{SHA256 hashes}
```
```

## Repository Structure

```
gymos/
├── .github/workflows/release.yml    # Automated release CI
├── scripts/build/                   # Build scripts
│   ├── gymos.spec                   # PyInstaller spec
│   ├── installer.nsi                # Windows installer
│   ├── build_windows.py             # Windows build
│   ├── build_linux.py               # Linux build
│   ├── build_macos.py               # macOS build
│   ├── render_icons.py              # Icon generation
│   └── generate_manifest.py         # Update manifest
├── shared/update/                   # Auto-update module
├── docs/
│   ├── CHANGELOG.md                 # Release changelog
│   ├── INSTALLATION_GUIDE.md        # User installation docs
│   └── DISTRIBUTION.md              # This file
└── dist/                            # Build output
```

## Platform-Specific Notes

### Windows
- **Code signing:** Recommended but not required. Sign with `signtool.exe` before distributing:
  ```bash
  signtool sign /a /fd SHA256 /td SHA256 /tr http://timestamp.digicert.com GymOS-{version}-Setup.exe
  ```
- **Windows Defender:** First releases may trigger SmartScreen. Submit to Microsoft for reputation.
- **Portable mode:** Create an empty `portable_data/` folder next to the EXE to store data locally.

### Linux
- **AppImage:** Built with `appimagetool`. Must run on FUSE-capable system.
- **DEB:** Tested on Ubuntu 22.04+ and Debian 12+.
- **Flatpak/Snap:** Not yet available. Community contributions welcome.

### macOS
- **Code signing:** Required for Gatekeeper. Must have Apple Developer account.
- **Notarization:** Submit DMG to Apple for notarization:
  ```bash
  xcrun notarytool submit dist/GymOS-{version}.dmg --keychain-profile gymos --wait
  xcrun stapler staple dist/GymOS-{version}.dmg
  ```
- **Universal binary:** x86_64 only. ARM64 support requires CI on Apple Silicon.

## Security

### Checksum Verification
All releases include `SHA256SUMS.txt` with checksums for every artifact. Users should verify before installing:

```bash
# Windows (PowerShell)
Get-FileHash GymOS-{version}-Setup.exe

# Linux / macOS
sha256sum GymOS-{version}-x86_64.AppImage
```

### Update Channel Security
The update manifest URL should be served over HTTPS. SHA256 verification is performed client-side before applying updates.

## Post-Release

1. Verify GitHub Release is published with all assets
2. Update `latest` tag if needed
3. Announce release on communication channels
4. Monitor for crash reports in `data/crashes/`
5. Monitor update manifest fetch success rates

## CI/CD Integration

The `release` job in `.github/workflows/ci.yml` is triggered by version tags:
- Tag format: `v{MAJOR}.{MINOR}.{PATCH}`  (e.g., `v0.5.0`)
- Automatically verifies tag matches `shared.version.APP_VERSION`
- Runs test suite before releasing
- Creates GitHub Release with changelog
- Uploads build artifacts
