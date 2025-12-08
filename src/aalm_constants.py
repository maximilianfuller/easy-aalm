"""
Shared constants for AALM model.
These values match the golden template (LeggettInput_Golden.txt).
"""

# Water intake schedule (L/day)
WATER_INTAKE_AGES_DAYS = [0, 91.25, 365, 3650, 5475, 9125, 18250]
WATER_INTAKE_AMOUNTS = [0.2, 0.3, 0.35, 0.45, 0.55, 0.7, 1.04]

# Soil intake schedule (g/day)
SOIL_INTAKE_AGES_DAYS = [0, 365, 730, 1095, 1460, 1825, 2190]
SOIL_INTAKE_AMOUNTS = [0.0387, 0.0423, 0.03015, 0.02835, 0.03015, 0.0234, 0.02475]

# Dust intake schedule (g/day)
DUST_INTAKE_AGES_DAYS = [0, 365, 730, 1095, 1460, 1825, 2190]
DUST_INTAKE_AMOUNTS = [0.0473, 0.0517, 0.03685, 0.03465, 0.03685, 0.0286, 0.03025]

# Air intake schedule (m³/day)
AIR_INTAKE_AGES_DAYS = [0, 365, 1825, 3650, 5475, 9125]
AIR_INTAKE_AMOUNTS = [2.9, 5.2, 8.8, 15.3, 17.9, 19.9]

# Relative Bioavailability (RBA) values
RBA_WATER = 1.0
RBA_AIR = 1.0
RBA_FOOD = 1.0
RBA_SOIL = 0.6
RBA_DUST = 0.001
