# Easy AALM

A simple, user-friendly web interface for the EPA All-Ages Lead Model (AALM).

## Overview

Easy AALM makes the EPA's lead exposure model accessible to field workers and researchers without requiring Windows, Excel, or complex setup. It wraps the original AALM Fortran executable with a clean web interface.

### Features

- **Simple inputs** - Age, sex, food/water lead levels (constant exposure)
- **Cross-platform** - Runs on Mac (with Wine) and Windows
- **Visual output** - Interactive BLL graphs over time
- **CSV export** - Download daily or weekly data
- **Field-ready** - Designed for quick XRF-to-BLL calculations

## Quick Start

### Windows

1. **Download** this repository (click green "Code" button → Download ZIP)
2. **Extract** the ZIP file
3. **Double-click** `run.bat`

That's it! Setup runs automatically on first launch, then the app opens in your browser.

### Mac

1. **Download** this repository (click green "Code" button → Download ZIP)
2. **Extract** the ZIP file
3. **Double-click** `Easy AALM.app`

The app is **fully signed and notarized** by Apple - no security warnings!

On first run, the app will automatically:
- Install Python dependencies (Streamlit, Pandas, Plotly)
- Install Wine (required to run the AALM Windows executable on Mac)
- Install Homebrew if needed

A Terminal window will open showing setup progress (first time only). The app will automatically open in your browser at `http://localhost:8501`.

---

**Based on**: EPA AALM v3.1
**License**: Public domain (U.S. Government work)
