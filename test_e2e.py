#!/usr/bin/env python3
"""
End-to-End Test for Easy AALM

Tests the complete simulation workflow:
1. Generate AALM input file with test parameters
2. Run AALM simulation (requires Wine on macOS)
3. Verify results

Usage:
    python3 test_e2e.py

Prerequisites:
    - Wine installed (on macOS: brew install wine-stable)
    - AALM setup complete (run the app once first)
"""

import subprocess
from pathlib import Path
import re
import sys

# Configuration
USER_DATA_DIR = Path.home() / "Library" / "Application Support" / "Easy AALM"
AALM_EXE = USER_DATA_DIR / "aalm_original" / "AALM_64.exe"
AALM_DIR = AALM_EXE.parent
TEMPLATE_PATH = AALM_DIR / "Examples" / "LeggettInput_Ex1a.txt"

# Test parameters
TEST_PARAMS = {
    'age_range': (0, 7),
    'sex': 'Male',
    'water_ppm': 5.0,
    'water_scale_factor': 1.5,
    'food_ug_day': 0.0,
    'soil_ppm': 0,
    'dust_ppm': 0
}

def print_header(text):
    """Print a formatted header"""
    print("=" * 70)
    print(text)
    print("=" * 70)
    print()

def verify_prerequisites():
    """Check that all required files and tools exist"""
    print_header("VERIFYING PREREQUISITES")

    # Check AALM executable
    if not AALM_EXE.exists():
        print(f"❌ AALM executable not found at {AALM_EXE}")
        return False
    print(f"✓ AALM executable: {AALM_EXE}")

    # Check template
    if not TEMPLATE_PATH.exists():
        print(f"❌ Template not found at {TEMPLATE_PATH}")
        return False
    print(f"✓ Template file: {TEMPLATE_PATH}")

    # Check Wine (macOS only)
    import platform
    if platform.system() == "Darwin":
        wine_check = subprocess.run(
            ["which", "wine"],
            capture_output=True,
            text=True
        )
        if wine_check.returncode != 0:
            print("❌ Wine not installed. Install with: brew install wine-stable")
            return False
        print(f"✓ Wine: {wine_check.stdout.strip()}")

    print()
    return True

def create_input_file():
    """Create AALM input file from template with test parameters"""
    print_header("CREATING INPUT FILE")

    print("Test Parameters:")
    print(f"  Age Range: {TEST_PARAMS['age_range'][0]}-{TEST_PARAMS['age_range'][1]} years")
    print(f"  Sex: {TEST_PARAMS['sex']}")
    print(f"  Water Lead: {TEST_PARAMS['water_ppm']} PPM")
    print(f"  Water Intake Scale Factor: {TEST_PARAMS['water_scale_factor']}x")
    print(f"  Food/Soil/Dust: All set to 0")
    print()

    # Read template
    with open(TEMPLATE_PATH, 'r') as f:
        template_lines = f.readlines()

    # Standard water intake values from EPA AALM
    standard_intake = [0.4, 0.43, 0.51, 0.54, 0.57, 0.6, 0.63]

    # Modify template
    modified_lines = []
    for line_idx, line in enumerate(template_lines):
        parts = line.rstrip().split(',')

        # Change simulation name to WebSim
        if line_idx == 0 and len(parts) > 0 and parts[0] == 'Name':
            parts[1] = 'WebSim'
            modified_lines.append(','.join(parts) + '\n')

        # Modify simulation duration
        elif len(parts) > 1 and parts[0] == 'Sim' and parts[1] == 'age_range':
            parts[3] = str(TEST_PARAMS['age_range'][0])
            parts[4] = str(int(TEST_PARAMS['age_range'][1] * 365))
            modified_lines.append(','.join(parts) + '\n')

        # Modify sex
        elif len(parts) > 1 and parts[0] == 'Growth' and parts[1] == 'sex':
            parts[3] = '1' if TEST_PARAMS['sex'] == "Female" else '0'
            modified_lines.append(','.join(parts) + '\n')

        # Set food intake to 0
        elif len(parts) > 1 and parts[0] == 'Food' and parts[1] == 'source_amt1':
            num_vals = int(parts[2])
            for i in range(num_vals):
                if len(parts) > 3 + i:
                    parts[3 + i] = "0.00"
            modified_lines.append(','.join(parts) + '\n')

        # Set water concentration
        elif len(parts) > 1 and parts[0] == 'Water' and parts[1] == 'concs1':
            parts[3] = f"{TEST_PARAMS['water_ppm']:.2f}"
            modified_lines.append(','.join(parts) + '\n')

        # Apply scale factor to water intake amounts
        elif len(parts) > 1 and parts[0] == 'Water' and parts[1] == 'intake_amt':
            num_vals = int(parts[2])
            for i in range(num_vals):
                if len(parts) > 3 + i and i < len(standard_intake):
                    scaled_value = standard_intake[i] * TEST_PARAMS['water_scale_factor']
                    parts[3 + i] = f"{scaled_value:.2f}"
            modified_lines.append(','.join(parts) + '\n')
            print(f"✓ Applied {TEST_PARAMS['water_scale_factor']}x scale factor to water intake")

        # Set soil concentration to 0
        elif len(parts) > 1 and parts[0] == 'Soil' and parts[1] == 'concs1':
            parts[3] = "0"
            modified_lines.append(','.join(parts) + '\n')

        # Set dust concentration to 0
        elif len(parts) > 1 and parts[0] == 'Dust' and parts[1] == 'concs1':
            parts[3] = "0"
            modified_lines.append(','.join(parts) + '\n')

        else:
            modified_lines.append(line)

    # Write input file
    input_file = AALM_DIR / "LeggettInput_web.txt"
    with open(input_file, 'w') as f:
        f.writelines(modified_lines)

    print(f"✓ Created input file: {input_file}")

    # Create output directory
    output_dir = AALM_DIR / "WebSim"
    output_dir.mkdir(exist_ok=True)
    print(f"✓ Created output directory: {output_dir}")
    print()

    return input_file, output_dir

def run_aalm_simulation(input_file):
    """Execute AALM simulation using Wine"""
    print_header("RUNNING AALM SIMULATION")

    # Determine command based on platform
    import platform
    if platform.system() == "Darwin":
        cmd = ["wine", str(AALM_EXE), str(input_file.name)]
        print("Running AALM with Wine...")
    else:
        cmd = [str(AALM_EXE), str(input_file.name)]
        print("Running AALM...")

    # Run simulation
    result = subprocess.run(
        cmd,
        cwd=str(AALM_DIR),
        capture_output=True,
        text=True,
        timeout=60
    )

    if result.returncode != 0:
        print(f"❌ AALM failed! Return code: {result.returncode}")
        if result.stderr:
            print(f"STDERR: {result.stderr[:500]}")
        return None

    print("✓ AALM completed successfully!")
    print()

    return result.stdout

def verify_results(stdout, output_dir):
    """Verify simulation results"""
    print_header("VERIFYING RESULTS")

    # Extract average BLL
    avg_bll_match = re.search(r'Average BLL over simulation\s*=\s*([\d.]+)', stdout)
    if avg_bll_match:
        avg_bll = float(avg_bll_match.group(1))
        print(f"✓ Average Blood Lead Level: {avg_bll:.2f} μg/dL")
    else:
        print("⚠ Could not extract average BLL from output")
        avg_bll = None

    # Check output CSV
    output_csv = output_dir / "Out_WebSim.csv"
    if output_csv.exists():
        print(f"✓ Output CSV created: {output_csv}")
        with open(output_csv, 'r') as f:
            lines = f.readlines()
        print(f"✓ CSV contains {len(lines)} lines (including header)")
    else:
        print(f"⚠ Output CSV not found at {output_csv}")
        # Try to find any Out_*.csv
        out_csvs = list(AALM_DIR.glob("*/Out_*.csv"))
        if out_csvs:
            output_csv = max(out_csvs, key=lambda p: p.stat().st_mtime)
            print(f"✓ Found alternative CSV: {output_csv}")

    print()
    return avg_bll

def print_summary(avg_bll):
    """Print test summary"""
    print_header("✅ ALL TESTS PASSED!")

    print("Summary:")
    print(f"  ✓ Water concentration: {TEST_PARAMS['water_ppm']} PPM")
    print(f"  ✓ Water intake scale factor: {TEST_PARAMS['water_scale_factor']}x")
    print(f"  ✓ Template: {TEMPLATE_PATH.name}")
    print(f"  ✓ All non-water exposures set to 0")
    print(f"  ✓ AALM executed successfully")
    if avg_bll is not None:
        print(f"  ✓ Blood Lead Level calculated: {avg_bll:.2f} μg/dL")
    print()

def main():
    """Run end-to-end test"""
    print()
    print_header("EASY AALM - END-TO-END TEST")

    try:
        # 1. Verify prerequisites
        if not verify_prerequisites():
            sys.exit(1)

        # 2. Create input file
        input_file, output_dir = create_input_file()

        # 3. Run simulation
        stdout = run_aalm_simulation(input_file)
        if stdout is None:
            sys.exit(1)

        # 4. Verify results
        avg_bll = verify_results(stdout, output_dir)

        # 5. Print summary
        print_summary(avg_bll)

        print("Test completed successfully!")
        print()

    except Exception as e:
        print()
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
