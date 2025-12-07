#!/usr/bin/env python3
"""
Test the shared fortran_input_generator module.

This test validates that the shared module (used by both app.py and generate_default_input.py)
produces output that matches the golden reference when given default parameters.
"""

import difflib
from pathlib import Path
from fortran_input_generator import generate_fortran_input


def compare_lines(expected_lines, actual_lines):
    """Compare two lists of lines and return diff."""
    diff = list(difflib.unified_diff(
        expected_lines,
        actual_lines,
        fromfile='expected',
        tofile='actual',
        lineterm=''
    ))
    return diff, expected_lines == actual_lines


def main():
    print("Testing shared fortran_input_generator module...")
    print()

    # Default parameters (matching golden reference)
    age_range = (0, 90)
    sex = "Male"
    water_ppb = 0.9
    water_scale_factor = 1.0
    food_ug_day = 10.0
    soil_ppm = 25
    soil_scale_factor = 1.0
    dust_ppm = 175
    dust_scale_factor = 1.0
    air_ug_m3 = 0.01
    air_scale_factor = 1.0

    water_ug_l = water_ppb  # PPB = μg/L

    # Use golden reference as template
    template_path = Path("fortran_input_golden.txt")
    if not template_path.exists():
        print(f"❌ FAILURE: Template file not found: {template_path}")
        return 1

    # Generate input using shared module
    print("Generating Fortran input with default parameters...")
    try:
        modified_lines = generate_fortran_input(
            template_path=template_path,
            age_range=age_range,
            sex=sex,
            food_ug_day=food_ug_day,
            water_ug_l=water_ug_l,
            water_scale_factor=water_scale_factor,
            soil_ppm=soil_ppm,
            soil_scale_factor=soil_scale_factor,
            dust_ppm=dust_ppm,
            dust_scale_factor=dust_scale_factor,
            air_ug_m3=air_ug_m3,
            air_scale_factor=air_scale_factor,
            sim_name=None  # Keep template name (SimName)
        )
    except Exception as e:
        print(f"❌ FAILURE: Error generating input: {e}")
        return 1

    # Read golden reference
    with open(template_path, 'r') as f:
        golden_lines = f.readlines()

    # Compare
    print("Comparing against golden reference...")
    diff, matches = compare_lines(golden_lines, modified_lines)

    if matches:
        print("✅ SUCCESS: Shared module produces golden reference output!")
        print()
        print("This validates that both app.py and generate_default_input.py")
        print("will produce correct output when using default parameters.")
        return 0
    else:
        print("❌ FAILURE: Output does NOT match golden reference!")
        print()
        print("Differences:")
        print("-" * 80)
        for line in diff:
            print(line)
        print("-" * 80)
        return 1


if __name__ == "__main__":
    exit(main())
