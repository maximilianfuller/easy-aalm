#!/usr/bin/env python3
"""
Generate Fortran input file with default parameters to compare with Excel macro output
"""

from pathlib import Path
from fortran_input_generator import generate_fortran_input

# Default parameters (matching golden result)
age_range = (0, 90)
sex = "Male"
water_ppb = 0.9  # PPB
soil_ppm = 25
dust_ppm = 175
air_ug_m3 = 0.01

# Scale factors (1.0 = 100% = default)
water_scale_factor = 1.0
soil_scale_factor = 1.0
dust_scale_factor = 1.0
air_scale_factor = 1.0
food_scale_factor = 1.0

# Convert water PPB to μg/L (they're the same)
water_ug_l = water_ppb

# Use golden reference as template (matches Excel defaults exactly)
template_path = Path("fortran_input_golden.txt")

# Generate input using shared module (no custom schedules = use template defaults)
modified_lines = generate_fortran_input(
    template_path=template_path,
    age_range=age_range,
    sex=sex,
    water_ug_l=water_ug_l,
    water_scale_factor=water_scale_factor,
    soil_ppm=soil_ppm,
    soil_scale_factor=soil_scale_factor,
    dust_ppm=dust_ppm,
    dust_scale_factor=dust_scale_factor,
    air_ug_m3=air_ug_m3,
    air_scale_factor=air_scale_factor,
    food_scale_factor=food_scale_factor,
    sim_name=None  # Keep template name (SimName)
)

# Write output
output_file = Path("fortran_input_streamlit_defaults.txt")
with open(output_file, 'w') as f:
    f.writelines(modified_lines)

print(f"Generated Fortran input file: {output_file}")
print("\nDefault parameters used:")
print(f"  Age Range: {age_range[0]}-{age_range[1]} years")
print(f"  Sex: {sex}")
print(f"  Water: {water_ppb} PPB (= {water_ug_l} μg/L)")
print(f"  Soil: {soil_ppm} PPM")
print(f"  Dust: {dust_ppm} PPM")
print(f"  Air: {air_ug_m3} μg/m³")
