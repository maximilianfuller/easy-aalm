#!/usr/bin/env python3
"""
Test that verifies the generated Fortran input file matches the golden reference.
This ensures the default parameters from the UI produce the expected output.
"""

import sys
from pathlib import Path
import difflib

def compare_files(file1_path, file2_path):
    """Compare two files line by line and report differences."""
    with open(file1_path, 'r') as f1, open(file2_path, 'r') as f2:
        file1_lines = f1.readlines()
        file2_lines = f2.readlines()

    # Generate unified diff
    diff = list(difflib.unified_diff(
        file1_lines,
        file2_lines,
        fromfile=str(file1_path),
        tofile=str(file2_path),
        lineterm=''
    ))

    return diff, file1_lines == file2_lines

def main():
    # Paths
    golden_file = Path("fortran_input_golden.txt")
    generated_file = Path("fortran_input_streamlit_defaults.txt")

    # Check golden file exists
    if not golden_file.exists():
        print(f"❌ ERROR: Golden reference file not found: {golden_file}")
        print("Run generate_default_input.py first to create it.")
        return 1

    # Check generated file exists
    if not generated_file.exists():
        print(f"❌ ERROR: Generated file not found: {generated_file}")
        print("Run generate_default_input.py first to create it.")
        return 1

    # Compare files
    print(f"Comparing:")
    print(f"  Golden:    {golden_file}")
    print(f"  Generated: {generated_file}")
    print()

    diff, files_match = compare_files(golden_file, generated_file)

    if files_match:
        print("✅ SUCCESS: Generated file matches golden reference!")
        print()
        print("The default parameters produce the expected Fortran input format.")
        return 0
    else:
        print("❌ FAILURE: Generated file does NOT match golden reference!")
        print()
        print("Differences found:")
        print("-" * 80)
        for line in diff:
            print(line)
        print("-" * 80)
        print()
        print("The generated file differs from the expected output.")
        print("Review the differences above to identify the issue.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
