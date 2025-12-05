#!/usr/bin/env python3
"""
Shared module for generating AALM Fortran input files.

This module provides the core input generation logic used by both:
- app.py (Streamlit web interface)
- generate_default_input.py (standalone test script)
"""

from pathlib import Path
from typing import List, Tuple, Optional


def format_number(value: float) -> str:
    """
    Format a number without trailing zeros to match Excel defaults.

    Examples:
        0.9 -> "0.9" (not "0.90")
        0.018 -> "0.018" (not "0.0180")
        10.0 -> "10" (not "10.00")
    """
    # Format with enough precision
    formatted = f"{value:.10f}"
    # Strip trailing zeros and decimal point if needed
    formatted = formatted.rstrip('0').rstrip('.')
    return formatted


def generate_fortran_input(
    template_path: Path,
    age_range: Tuple[int, int],
    sex: str,
    food_ug_day: float,
    water_ug_l: float,
    water_scale_factor: float,
    soil_ppm: float,
    soil_scale_factor: float,
    dust_ppm: float,
    dust_scale_factor: float,
    air_ug_m3: float,
    air_scale_factor: float,
    sim_name: Optional[str] = None
) -> List[str]:
    """
    Generate AALM Fortran input file content from template and parameters.

    Args:
        template_path: Path to template file (should be LeggettInput_ExcelDefaults.txt)
        age_range: (start_age, end_age) in years
        sex: "Male" or "Female"
        food_ug_day: Food lead intake (μg/day)
        water_ug_l: Water lead concentration (μg/L)
        water_scale_factor: Scale factor for water intake (1.0 = 100%)
        soil_ppm: Soil lead concentration (PPM)
        soil_scale_factor: Scale factor for soil intake (1.0 = 100%)
        dust_ppm: Dust lead concentration (PPM)
        dust_scale_factor: Scale factor for dust intake (1.0 = 100%)
        air_ug_m3: Air lead concentration (μg/m³)
        air_scale_factor: Scale factor for air intake (1.0 = 100%)
        sim_name: Optional simulation name (if None, keeps template name)

    Returns:
        List of lines to write to Fortran input file

    Raises:
        FileNotFoundError: If template file doesn't exist
    """
    if not template_path.exists():
        raise FileNotFoundError(f"Template file not found: {template_path}")

    # Read template
    with open(template_path, 'r') as f:
        template_lines = f.readlines()

    # Modify template with parameters
    modified_lines = []
    for line_idx, line in enumerate(template_lines):
        parts = line.rstrip().split(',')

        # Change simulation name (first line) if specified
        if line_idx == 0 and len(parts) > 0 and parts[0] == 'Name':
            if sim_name is not None:
                parts[1] = sim_name
            modified_lines.append(','.join(parts) + '\n')

        # Modify simulation duration
        elif len(parts) > 1 and parts[0] == 'Sim' and parts[1] == 'age_range':
            parts[3] = str(age_range[0])
            parts[4] = str(int(age_range[1] * 365))
            modified_lines.append(','.join(parts) + '\n')

        # Modify sex
        elif len(parts) > 1 and parts[0] == 'Growth' and parts[1] == 'sex':
            parts[3] = '1' if sex == "Female" else '0'
            modified_lines.append(','.join(parts) + '\n')

        # Modify food intake
        elif len(parts) > 1 and parts[0] == 'Food' and parts[1] == 'source_amt1':
            num_vals = int(parts[2])
            # Set all values to constant food intake
            for i in range(num_vals):
                if len(parts) > 3 + i:
                    parts[3 + i] = format_number(food_ug_day)
            modified_lines.append(','.join(parts) + '\n')

        # Modify water concentration
        elif len(parts) > 1 and parts[0] == 'Water' and parts[1] == 'concs1':
            parts[3] = format_number(water_ug_l)
            modified_lines.append(','.join(parts) + '\n')

        # Modify water intake amounts (apply scale factor)
        elif len(parts) > 1 and parts[0] == 'Water' and parts[1] == 'intake_amt':
            num_vals = int(parts[2])
            # Excel defaults (L/day)
            standard_intake = [0.2, 0.3, 0.35, 0.45, 0.55, 0.7, 1.04]
            for i in range(num_vals):
                if len(parts) > 3 + i and i < len(standard_intake):
                    parts[3 + i] = format_number(standard_intake[i] * water_scale_factor)
            modified_lines.append(','.join(parts) + '\n')

        # Modify soil concentration
        elif len(parts) > 1 and parts[0] == 'Soil' and parts[1] == 'concs1':
            parts[3] = format_number(soil_ppm)
            modified_lines.append(','.join(parts) + '\n')

        # Modify soil intake amounts (apply scale factor)
        elif len(parts) > 1 and parts[0] == 'Soil' and parts[1] == 'intake_amt':
            num_vals = int(parts[2])
            # Excel defaults (g/day)
            standard_intake = [0.018, 0.032, 0.041, 0.036, 0.027, 0.014]
            for i in range(num_vals):
                if len(parts) > 3 + i and i < len(standard_intake):
                    parts[3 + i] = format_number(standard_intake[i] * soil_scale_factor)
            modified_lines.append(','.join(parts) + '\n')

        # Modify soil RBA (Relative Bioavailability)
        elif len(parts) > 1 and parts[0] == 'Soil' and parts[1] == 'RBA':
            parts[3] = "0.6"  # Soil has 60% bioavailability
            modified_lines.append(','.join(parts) + '\n')

        # Modify dust concentration
        elif len(parts) > 1 and parts[0] == 'Dust' and parts[1] == 'concs1':
            parts[3] = format_number(dust_ppm)
            modified_lines.append(','.join(parts) + '\n')

        # Modify dust intake amounts (apply scale factor)
        elif len(parts) > 1 and parts[0] == 'Dust' and parts[1] == 'intake_amt':
            num_vals = int(parts[2])
            # Excel defaults (g/day)
            standard_intake = [0.022, 0.039, 0.05, 0.044, 0.033, 0.017]
            for i in range(num_vals):
                if len(parts) > 3 + i and i < len(standard_intake):
                    parts[3 + i] = format_number(standard_intake[i] * dust_scale_factor)
            modified_lines.append(','.join(parts) + '\n')

        # Modify air concentration
        elif len(parts) > 1 and parts[0] == 'Air' and parts[1] == 'concs1':
            parts[3] = format_number(air_ug_m3)
            modified_lines.append(','.join(parts) + '\n')

        # Modify air intake amounts (apply scale factor)
        elif len(parts) > 1 and parts[0] == 'Air' and parts[1] == 'intake_amt':
            num_vals = int(parts[2])
            # Excel defaults (m³/day)
            standard_intake = [5.4, 8, 8.9, 10.1, 12, 15.2, 16.3, 15.7, 16, 15.7, 14.2, 12.9, 12.2]
            for i in range(num_vals):
                if len(parts) > 3 + i and i < len(standard_intake):
                    parts[3 + i] = format_number(standard_intake[i] * air_scale_factor)
            modified_lines.append(','.join(parts) + '\n')

        # Set RBA values for all sources
        elif len(parts) > 1 and parts[1] == 'RBA':
            if parts[0] == 'Water':
                parts[3] = "1"  # Water has 100% bioavailability
            elif parts[0] == 'Air':
                parts[3] = "1"  # Air has 100% bioavailability
            elif parts[0] == 'Food':
                parts[3] = "1"  # Food has 100% bioavailability
            elif parts[0] == 'Dust':
                parts[3] = "0.6"  # Dust has 60% bioavailability
            modified_lines.append(','.join(parts) + '\n')

        else:
            modified_lines.append(line)

    return modified_lines
