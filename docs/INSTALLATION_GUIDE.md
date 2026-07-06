# GymOS Installation Guide

## System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| OS | Windows 10 / Ubuntu 22.04 / macOS 11 | Windows 11 / Ubuntu 24.04 / macOS 14 |
| CPU | Dual-core 2.0 GHz | Quad-core 2.5 GHz |
| RAM | 2 GB | 4 GB |
| Storage | 500 MB | 1 GB |
| Display | 1280×720 | 1920×1080 |

## Windows

### Option 1: Installer (Recommended)

1. Download `GymOS-{version}-Setup.exe` from the [releases page](https://github.com/gymos/gymos/releases)
2. Double-click the installer
3. Follow the setup wizard (defaults are recommended)
4. Launch GymOS from the Start Menu or desktop shortcut

**Installation directory:** `C:\Program Files\GymOS`  
**User data:** `%APPDATA%\GymOS`

### Option 2: Portable ZIP

1. Download `GymOS-{version}-Windows.zip`
2. Extract to any folder
3. Run `GymOS.exe`

No installation required. User data is stored in the `portable_data/` folder next to the executable.

### Uninstallation

**Via installer:**
1. Open Settings → Apps → Installed Apps
2. Find "GymOS" and click Uninstall
3. Choose whether to keep your personal data

**Via portable ZIP:**
Delete the extracted folder.

## Linux

### Option 1: DEB Package (Debian/Ubuntu)

```bash
sudo dpkg -i gymos_{version}_amd64.deb
sudo apt-get install -f   # install dependencies
gymos                      # launch
```

### Option 2: AppImage (All Distributions)

```bash
chmod +x GymOS-{version}-x86_64.AppImage
./GymOS-{version}-x86_64.AppImage
```

For desktop integration, use [AppImageLauncher](https://github.com/TheAssassin/AppImageLauncher).

### Dependencies

When using the DEB package, these dependencies are installed automatically:
- Python 3.11+
- PySide6
- libqt6svg6

### Uninstallation

**DEB:**
```bash
sudo dpkg -r gymos
sudo dpkg --purge gymos   # also remove config
```

**AppImage:**
Delete the `.AppImage` file.

**User data:** `~/.local/share/gymos`

## macOS

### Option 1: DMG (Recommended)

1. Download `GymOS-{version}.dmg`
2. Double-click to mount
3. Drag GymOS to the Applications folder
4. Launch from Applications or Launchpad

### Code Signing

On first launch, macOS may show a security warning for unsigned builds:
1. Open **System Settings → Privacy & Security**
2. Scroll to the "Security" section
3. Click "Open Anyway" next to GymOS

### Uninstallation

Delete `GymOS.app` from the Applications folder.

**User data:** `~/Library/Application Support/GymOS`

## Data Directory

| Platform | Path |
|----------|------|
| Windows | `%APPDATA%\GymOS` |
| Linux | `~/.local/share/gymos` |
| macOS | `~/Library/Application Support/GymOS` |

The data directory contains:
- `gymos.db` — Main database (workouts, nutrition, recovery)
- `backups/` — Automatic database backups
- `crashes/` — Crash reports

## First Run

On first launch, GymOS will:
1. Show a splash screen with loading progress
2. Initialize the database
3. Display the welcome wizard to set up your profile
4. Offer to load demo data

## Updating

### Automatic Updates
GymOS checks for updates on startup via the release channel manifest.

### Manual Update
1. Download the latest version from the [releases page](https://github.com/gymos/gymos/releases)
2. Install over your existing installation (data is preserved)

### Backup Before Update
GymOS automatically creates a database backup before running schema migrations.

## Troubleshooting

### Application doesn't start
1. Verify system requirements are met
2. Check the crash report in the data directory:
   - Windows: `%APPDATA%\GymOS\crashes\`
   - Linux: `~/.local/share/gymos/crashes/`
   - macOS: `~/Library/Application Support/GymOS/crashes/`
3. Submit the crash report when reporting issues

### Database issues
1. Close GymOS
2. Navigate to the data directory
3. Restore from a backup in the `backups/` folder
4. Delete or rename `gymos.db` to start fresh

### Permission issues (Linux)
```bash
chmod +x GymOS-*.AppImage
./GymOS-*.AppImage --no-sandbox
```

### Permission issues (macOS)
```bash
xattr -d com.apple.quarantine /Applications/GymOS.app
```
