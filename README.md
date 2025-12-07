# Easy AALM

A simple, user-friendly desktop application for the EPA All-Ages Lead Model (AALM).

**[Download Latest Release](https://github.com/maximilianfuller/easy-aalm/releases/latest)**

## Overview

Easy AALM makes the EPA's lead exposure model accessible to field workers and researchers without requiring Windows, Excel, or complex setup. It wraps the original AALM Fortran executable with a clean web interface.

### Features

- **Simple inputs** - Age, sex, food/water lead levels (constant exposure)
- **Cross-platform** - Runs on Mac and Windows
- **Visual output** - Interactive BLL graphs over time
- **CSV export** - Download daily or weekly data
- **Field-ready** - Designed for quick XRF-to-BLL calculations

## Quick Start

### Download

Get the latest release from the [Releases page](https://github.com/maximilianfuller/easy-aalm/releases/latest):

- **macOS**: Download `Easy-AALM-macOS.dmg`, open it, drag to Applications
- **Windows**: Download `Easy-AALM-Windows-Setup.exe`, run the installer

The apps are fully self-contained with bundled Python and dependencies.

### Development

To run from source:

```bash
git clone https://github.com/maximilianfuller/easy-aalm.git
cd easy-aalm
./dev.sh
```

This creates a Python virtual environment, installs dependencies (Streamlit, Pandas, Plotly), and opens the app at `http://localhost:8501`.

**Requirements:**
- Python 3.9+
- macOS: Wine (`brew install --cask wine-crossover`) to run the AALM Windows executable

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for build and architecture details.

---

**Based on**: EPA AALM v3.1
**License**: Public domain (U.S. Government work)
