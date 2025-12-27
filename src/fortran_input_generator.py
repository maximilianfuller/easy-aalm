#!/usr/bin/env python3
"""
Shared module for generating AALM Fortran input files.

This module provides the core input generation logic used by both:
- app.py (Streamlit web interface)
- generate_default_input.py (standalone test script)

All intake schedules and RBA values are read directly from the golden template file.
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
    food_scale_factor: float,
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
        template_path: Path to template file (should be LeggettInput_Golden.txt)
        age_range: (start_age, end_age) in years
        sex: "Male" or "Female"
        food_scale_factor: Scale factor for food intake (1.0 = 100%)
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
        # EPA model convention: sex=0 is Female, sex=1 is Male
        elif len(parts) > 1 and parts[0] == 'Growth' and parts[1] == 'sex':
            parts[3] = '0' if sex == "Female" else '1'
            modified_lines.append(','.join(parts) + '\n')

        # Modify sex-specific growth parameters
        # Golden template (Female sex=0): wbirth=3.3, wadult=34, lambda=0.017, HCTA=0.41
        # Male (sex=1): wbirth=3.5, wadult=50, lambda=0.0095, HCTA=0.46
        elif len(parts) > 1 and parts[0] == 'Growth' and parts[1] == 'wbirth':
            parts[3] = '3.5' if sex == "Male" else '3.3'
            modified_lines.append(','.join(parts) + '\n')

        elif len(parts) > 1 and parts[0] == 'Growth' and parts[1] == 'wchild':
            parts[3] = '23' if sex == "Male" else '22'
            modified_lines.append(','.join(parts) + '\n')

        elif len(parts) > 1 and parts[0] == 'Growth' and parts[1] == 'wadult':
            parts[3] = '50' if sex == "Male" else '34'
            modified_lines.append(','.join(parts) + '\n')

        elif len(parts) > 1 and parts[0] == 'Growth' and parts[1] == 'lambda':
            parts[3] = '0.0095' if sex == "Male" else '0.017'
            modified_lines.append(','.join(parts) + '\n')

        elif len(parts) > 1 and parts[0] == 'Growth' and parts[1] == 'LB':
            parts[3] = '0.88' if sex == "Male" else '0.85'
            modified_lines.append(','.join(parts) + '\n')

        # Modify sex-specific physiological parameters
        elif len(parts) > 1 and parts[0] == 'Phys' and parts[1] == 'HCTA':
            parts[3] = '0.46' if sex == "Male" else '0.41'
            modified_lines.append(','.join(parts) + '\n')

        # Modify food intake amounts (apply scale factor to template values)
        elif len(parts) > 1 and parts[0] == 'Food' and parts[1] == 'source_amt1':
            num_vals = int(parts[2])
            for i in range(num_vals):
                if len(parts) > 3 + i and parts[3 + i]:
                    original_value = float(parts[3 + i])
                    parts[3 + i] = format_number(original_value * food_scale_factor)
            modified_lines.append(','.join(parts) + '\n')

        # Modify water concentration
        elif len(parts) > 1 and parts[0] == 'Water' and parts[1] == 'concs1':
            parts[3] = format_number(water_ug_l)
            modified_lines.append(','.join(parts) + '\n')

        # Modify water intake amounts (apply scale factor to template values)
        elif len(parts) > 1 and parts[0] == 'Water' and parts[1] == 'intake_amt':
            num_vals = int(parts[2])
            for i in range(num_vals):
                if len(parts) > 3 + i and parts[3 + i]:
                    original_value = float(parts[3 + i])
                    parts[3 + i] = format_number(original_value * water_scale_factor)
            modified_lines.append(','.join(parts) + '\n')

        # Modify soil concentration
        elif len(parts) > 1 and parts[0] == 'Soil' and parts[1] == 'concs1':
            parts[3] = format_number(soil_ppm)
            modified_lines.append(','.join(parts) + '\n')

        # Modify soil intake amounts (apply scale factor to template values)
        elif len(parts) > 1 and parts[0] == 'Soil' and parts[1] == 'intake_amt':
            num_vals = int(parts[2])
            for i in range(num_vals):
                if len(parts) > 3 + i and parts[3 + i]:
                    original_value = float(parts[3 + i])
                    parts[3 + i] = format_number(original_value * soil_scale_factor)
            modified_lines.append(','.join(parts) + '\n')

        # Modify dust concentration
        elif len(parts) > 1 and parts[0] == 'Dust' and parts[1] == 'concs1':
            parts[3] = format_number(dust_ppm)
            modified_lines.append(','.join(parts) + '\n')

        # Modify dust intake amounts (apply scale factor to template values)
        elif len(parts) > 1 and parts[0] == 'Dust' and parts[1] == 'intake_amt':
            num_vals = int(parts[2])
            for i in range(num_vals):
                if len(parts) > 3 + i and parts[3 + i]:
                    original_value = float(parts[3 + i])
                    parts[3 + i] = format_number(original_value * dust_scale_factor)
            modified_lines.append(','.join(parts) + '\n')

        # Modify air concentration
        elif len(parts) > 1 and parts[0] == 'Air' and parts[1] == 'concs1':
            parts[3] = format_number(air_ug_m3)
            modified_lines.append(','.join(parts) + '\n')

        # Modify air intake amounts (apply scale factor to template values)
        elif len(parts) > 1 and parts[0] == 'Air' and parts[1] == 'intake_amt':
            num_vals = int(parts[2])
            for i in range(num_vals):
                if len(parts) > 3 + i and parts[3 + i]:
                    original_value = float(parts[3 + i])
                    parts[3 + i] = format_number(original_value * air_scale_factor)
            modified_lines.append(','.join(parts) + '\n')

        # All other lines (including RBA) - keep as-is from template
        else:
            modified_lines.append(line)

    return modified_lines
