# Easy AALM Architecture

## Overview

Easy AALM is a desktop application that wraps the EPA's All-Ages Lead Model (AALM) Fortran executable with a modern web UI. It uses PyWebView to create a native window that displays a Streamlit web application.

## Directory Structure

```
easy-aalm/
├── src/                    # Application source code
│   ├── app.py              # Main Streamlit web UI
│   ├── main_pywebview.py   # Desktop app entry point (PyWebView + Streamlit)
│   ├── fortran_input_generator.py  # Generates AALM input files
│   └── templates/          # AALM input file templates
├── aalm_original/          # EPA AALM Fortran executables
│   ├── AALM_64.exe         # 64-bit Windows executable
│   ├── AALM_32.exe         # 32-bit Windows executable
│   ├── Examples/           # Example input files
│   └── RespMod/            # Respiratory model files
├── build/                  # Build infrastructure
│   ├── easy_aalm.spec      # PyInstaller spec for macOS
│   ├── easy_aalm_windows.spec  # PyInstaller spec for Windows
│   ├── installer.iss       # Inno Setup script for Windows installer
│   ├── wine-entitlements.plist  # macOS entitlements for Wine
│   ├── build_desktop.sh    # Local build script
│   └── requirements-desktop.txt  # Build dependencies
├── .github/workflows/      # CI/CD
│   └── release.yml         # Build and release workflow
├── .streamlit/             # Streamlit configuration
├── assets/                 # App icons
├── test/                   # Test files
├── dev.sh                  # Local development script
└── README.md
```

## Application Architecture

### Runtime Flow

1. **main_pywebview.py** creates a native window using PyWebView
2. It launches Streamlit as a subprocess running **app.py**
3. The window displays the Streamlit UI at `http://127.0.0.1:<port>`
4. User inputs are processed by app.py, which generates AALM input files
5. Wine (macOS) or native (Windows) runs the AALM executable
6. Results are parsed and displayed in the Streamlit UI

### Key Components

- **PyWebView**: Creates native desktop window (WebKit on macOS, Edge/Chromium on Windows)
- **Streamlit**: Web framework for the UI
- **Wine Crossover**: Runs Windows AALM executable on macOS
- **AALM Fortran**: EPA's lead exposure model

## Build Process

### GitHub Actions (`release.yml`)

Triggered by pushing a tag like `v1.0.0` or manual workflow dispatch.

#### macOS Build

1. Checkout code
2. Install Python 3.11, PyInstaller, PyWebView
3. Download Wine Crossover
4. Run PyInstaller with `build/easy_aalm.spec`
5. Download standalone Python (ARM64 for Apple Silicon)
6. Create venv with Streamlit/Pandas/Plotly in app bundle
7. Bundle Wine Crossover into app
8. Sign all binaries with Developer ID certificate
9. Notarize with Apple (required for distribution outside App Store)
10. Staple notarization ticket
11. Create DMG with Applications shortcut

#### Windows Build

1. Checkout code
2. Install Python 3.11, PyInstaller, PyWebView, pythonnet
3. Run PyInstaller with `build/easy_aalm_windows.spec`
4. Bundle pythonnet/clr_loader (for WebView2)
5. Download standalone Python
6. Create venv with dependencies
7. Create installer with Inno Setup

### Local Build

```bash
./build/build_desktop.sh
```

Requires PyInstaller, PyWebView, and dependencies installed.

## Local Development

```bash
./dev.sh
```

This:
1. Sources Homebrew (for Wine on macOS)
2. Creates/activates a Python venv
3. Installs Streamlit, Pandas, Plotly, openpyxl
4. Runs `streamlit run src/app.py`

The app opens at `http://localhost:8501`. Wine must be installed separately for local development on macOS.

## Environment Variables

Used by `main_pywebview.py` for Wine configuration:

- `WINEPREFIX`: Temporary directory for Wine data (avoids modifying app bundle)
- `WINEDLLOVERRIDES`: Disables Wine menu builder and .NET
- `WINEDEBUG`: Suppresses Wine debug output
- `DISPLAY`: Empty to prevent X11 dialogs

## Signing and Notarization (macOS)

The app requires:
1. **Developer ID Application** certificate
2. **Hardened runtime** enabled
3. **JIT entitlement** for Wine (in `wine-entitlements.plist`)
4. **Notarization** via Apple's notary service
5. **Stapling** the ticket to the app

Secrets stored in GitHub:
- `APPLE_CERTIFICATE_BASE64`: Base64-encoded .p12 certificate
- `APPLE_CERTIFICATE_PASSWORD`: Certificate password
- `APPLE_ID`: Apple Developer account email
- `APPLE_ID_PASSWORD`: App-specific password
- `APPLE_TEAM_ID`: Developer team ID
