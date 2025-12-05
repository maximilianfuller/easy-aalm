# Easy AALM - Lightweight Web Wrapper

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

**Option 1: Pre-built App (Recommended)**
1. **Download** this repository (click green "Code" button → Download ZIP)
2. **Extract** the ZIP file
3. **Double-click** `Easy AALM.app`

The app is **fully signed and notarized** by Apple - no security warnings!

On first run, the app will automatically:
- Install Python dependencies (Streamlit, Pandas, Plotly)
- Install Wine (required to run the AALM Windows executable on Mac)
- Install Homebrew if needed

A Terminal window will open showing setup progress (first time only) and server status. The app will automatically open in your browser at `http://localhost:8501`.

**Option 2: Alternative Launcher**
1. **Download** this repository (click green "Code" button → Download ZIP)
2. **Extract** the ZIP file
3. **Double-click** `run.command`

Both options will open the app in your browser at `http://localhost:8501`

## Usage

1. **Set Parameters** (left sidebar):
   - Age range (e.g., 0-7 years)
   - Sex (Male/Female)
   - Food lead intake (μg/day, μg/kg/day, or PPM)
   - Water lead concentration (μg/L or μg/kg/day)
   - Optional: Soil and dust exposure

2. **Click "Calculate Blood Lead Level"**

3. **View Results**:
   - Average BLL
   - BLL vs. age graph
   - Comparison to CDC threshold

4. **Export**: Download CSV (daily or weekly data)

## Project Structure

```
easy-aalm/
├── Easy AALM.app/                  # Mac app bundle (signed & notarized)
├── app.py                          # Streamlit web interface
├── requirements.txt                # Python dependencies
├── setup.bat                       # Windows setup script
├── run.bat                         # Windows run script
├── setup.sh                        # Mac/Linux setup script
├── run.sh                          # Mac/Linux run script
├── run.command                     # Mac launcher script
├── sign-and-notarize.sh            # Developer script for code signing
├── .gitignore                      # Git ignore file
├── README.md                       # This file
└── aalm_original/                  # Original AALM files (for template)
    └── Examples/
        └── LeggettInput_Ex1.txt    # Template input file
```

**Note**: You must download AALM_64.exe separately from the EPA website.

## Requirements

- Python 3.8+
- Streamlit, Pandas, Plotly (installed automatically)
- AALM v3.1 executable (download from EPA)
- Wine (Mac/Linux only - installed automatically on Mac)

## Design Philosophy

This wrapper follows the "Easy AALM" requirements:
- **NOT a rewrite** - Uses original AALM Fortran executable
- **Simplified inputs** - Common use cases only (constant exposure)
- **Field-focused** - Quick XRF/lab results → BLL conversion
- **Cross-platform** - Works on Mac and Windows

### Non-Goals
- Full AALM functionality (use original Excel interface for advanced features)
- Time-varying exposure scenarios
- Solve/optimization features

## How It Works

1. **Input Generation**: Modifies AALM template file with user parameters
2. **Execution**: Calls AALM_64.exe with generated input
3. **Parsing**: Extracts BLL from output CSV
4. **Visualization**: Displays interactive graphs
5. **Export**: Packages results for download

## Limitations

- Simplified input model (constant exposure only)
- Requires AALM executable (Windows binary)
- Mac/Linux need Wine (installed automatically on Mac)
- Single scenario at a time (no batch processing)

## Original AALM

This tool wraps the EPA All-Ages Lead Model (AALM) Version 3.1:
- **Developer**: U.S. Environmental Protection Agency
- **Version**: 3.1 (August 2024)
- **Reference**: [EPA AALM Page](https://www.epa.gov/land-research/all-ages-lead-model-aalm)

The original Fortran code and documentation remain unchanged.

## License

This wrapper code is provided as-is for research and educational purposes.

The AALM Fortran executable is public domain (U.S. Government work).

## Testing

### Automated Test (Unix/macOS)

Run the end-to-end test to verify the simulation works:

```bash
python3 test_e2e.py
```

This test:
- Generates an AALM input file with test parameters (5.0 PPM water, 1.5x scale factor)
- Runs the AALM simulation via Wine
- Verifies output generation and calculates Blood Lead Level
- Reports success/failure

**Prerequisites:**
- Wine installed (`brew install wine-stable` on macOS)
- AALM app run at least once (to set up files)

### Fortran Input Validation Tests

Verify that the application generates correct Fortran input matching EPA Excel defaults:

```bash
# Test the shared input generation module (recommended)
python3 test_shared_module.py

# Or test via the standalone generator script
python3 generate_default_input.py
python3 test_fortran_input_defaults.py
```

**Architecture**: Both `app.py` (the actual UI) and `generate_default_input.py` (test script) use a shared module `fortran_input_generator.py` for input generation. This ensures consistency and allows the test to validate the same code used by the app.

These tests:
- Validate the shared `fortran_input_generator` module
- Compare generated Fortran input against golden reference file
- Ensure default parameters match EPA Excel defaults (AALM_Inputs_v3-1.xlsm)
- Validate intake schedules, concentrations, and RBA values
- Report any differences with detailed diff output

**Default parameters tested:**
- Age Range: 0-90 years
- Sex: Male
- Water: 0.9 PPB (7-point intake schedule)
- Food: 10.0 μg/day (7-point schedule)
- Soil: 25 PPM (6-point intake schedule, RBA=0.6)
- Dust: 175 PPM (6-point intake schedule, RBA=0.6)
- Air: 0.01 μg/m³ (13-point intake schedule)

### Integration Test with Screenshots

Automated browser test that captures screenshots:

```bash
# Install Playwright first (one-time setup)
pip install playwright
playwright install chromium

# Run the test
python3 test_with_screenshots.py
```

This test:
- Starts Streamlit in the background
- Opens automated browser (Chromium)
- Fills in test parameters (5.0 PPM water, log-scaled intake)
- Clicks Calculate button
- Waits for AALM simulation to complete
- Captures screenshots at each step
- Saves screenshots to `test_screenshots/` directory

Screenshots captured:
1. `01_initial.png` - Initial app state
2. `02_form_filled.png` - Form with parameters entered
3. `03_results.png` - Complete results page
4. `04_graph.png` - Blood lead level graph closeup
5. `05_fortran_input.png` - Fortran input file view

Use this test for visual regression testing and creating feedback loop for UI iterations.

## Support

For issues with the wrapper: [GitHub Issues]
For AALM model questions: brown.james@epa.gov, PbHelp@epa.gov

## Future Enhancements

- [ ] Docker container with Wine pre-installed
- [ ] Batch processing (multiple scenarios)
- [ ] Time-varying exposure support
- [ ] Mobile-friendly interface
- [ ] Cloud deployment option

---

**Created**: November 2024
**Status**: Functional prototype
**Based on**: EPA AALM v3.1
