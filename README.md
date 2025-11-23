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

### Mac

1. **Download** this repository (click green "Code" button → Download ZIP)
2. **Extract** the ZIP file
3. **Double-click** `setup.sh`
   - First time: Right-click → "Open" → Click "Open" again
   - Setup automatically installs Python and Wine if needed
4. **Download AALM** from the [EPA website](https://www.epa.gov/land-research/all-ages-lead-model-aalm) and note where you save it
5. **Edit** `app.py` (line 91) to point to your AALM_64.exe location
6. **Double-click** `run.sh` to launch

The app opens automatically in your browser at `http://localhost:8501`

**Want a clickable app icon?** See [MAC_SETUP.md](MAC_SETUP.md).

### Windows

1. **Download** this repository (click green "Code" button → Download ZIP)
2. **Extract** the ZIP file
3. **Double-click** `setup.bat`
4. **Download AALM** from the [EPA website](https://www.epa.gov/land-research/all-ages-lead-model-aalm) and note where you save it
5. **Edit** `app.py` (line 91) to point to your AALM_64.exe location
6. **Double-click** `run.bat` to launch

The app opens automatically in your browser at `http://localhost:8501`

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
aalm-app/
├── app.py                          # Streamlit web interface
├── requirements.txt                # Python dependencies
├── setup.bat                       # Windows setup script
├── run.bat                         # Windows run script
├── setup.sh                        # Mac/Linux setup script
├── run.sh                          # Mac/Linux run script
├── .gitignore                      # Git ignore file
├── README.md                       # This file
└── aalm_original/                  # Original AALM files (for template)
    └── Examples/
        └── LeggettInput_Ex1.txt    # Template input file
```

**Note**: You must download AALM_64.exe separately from the EPA website.

## Requirements

- Python 3.8+
- Streamlit, Pandas, Plotly (installed via requirements.txt)
- AALM v3.1 executable (download from EPA)
- Wine (Mac/Linux only)

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
- Mac/Linux need Wine installed
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
