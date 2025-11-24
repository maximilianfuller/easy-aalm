"""
Easy AALM - Simplified Web Interface for EPA All-Ages Lead Model
A lightweight wrapper making AALM easy to use for field workers
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import subprocess
import os
import re
from pathlib import Path
import tempfile
import shutil

st.set_page_config(
    page_title="Easy AALM - Lead Exposure Model",
    layout="wide"
)

st.title("Easy AALM - Lead Exposure Calculator")
st.markdown("Simple tool to estimate Blood Lead Levels from environmental measurements")

# Sidebar for inputs
st.sidebar.header("Parameters")

# Age and Sex
age_range = st.sidebar.slider("Age Range (years)", 0, 90, (0, 90), help="Simulation from birth to specified age")
sex = st.sidebar.selectbox("Sex", ["Male", "Female"])

st.sidebar.markdown("---")
st.sidebar.markdown("### Lead Exposure Sources")

# Food/Diet
st.sidebar.markdown("#### Food")
food_input_type = st.sidebar.radio(
    "Food Input Type",
    ["μg/day (constant)", "μg/kg/day", "PPM"],
    help="How you want to specify dietary lead"
)

if food_input_type == "μg/day (constant)":
    food_value = st.sidebar.number_input("Food Lead (μg/day)", 0.0, 100.0, 5.0, 0.1)
    food_ug_day = food_value
elif food_input_type == "μg/kg/day":
    food_value = st.sidebar.number_input("Food Lead (μg/kg/day)", 0.0, 10.0, 0.5, 0.1)
    # Will be converted based on body weight in input file
    food_ug_day = food_value  # Placeholder, actual conversion happens in template
else:  # PPM
    food_value = st.sidebar.number_input("Food Lead (PPM)", 0.0, 10.0, 0.1, 0.01)
    food_ug_day = food_value * 500  # Rough estimate: 500g food/day for child

# Water
st.sidebar.markdown("#### Water")
water_input_type = st.sidebar.radio(
    "Water Input Type",
    ["μg/L (PPB)", "μg/kg/day"],
    help="Lead concentration in drinking water"
)

if water_input_type == "μg/L (PPB)":
    water_ug_l = st.sidebar.number_input("Water Lead (μg/L)", 0.0, 50.0, 1.0, 0.1)
else:
    water_ug_kg_day = st.sidebar.number_input("Water Lead (μg/kg/day)", 0.0, 5.0, 0.1, 0.01)
    water_ug_l = water_ug_kg_day * 20  # Rough conversion

# Soil/Dust (optional)
with st.sidebar.expander("Soil/Dust (Optional)"):
    include_soil = st.checkbox("Include soil exposure")
    if include_soil:
        soil_ppm = st.number_input("Soil Lead (PPM)", 0, 5000, 200, 10)
    else:
        soil_ppm = 0

    include_dust = st.checkbox("Include dust exposure")
    if include_dust:
        dust_ppm = st.number_input("Dust Lead (PPM)", 0, 5000, 150, 10)
    else:
        dust_ppm = 0

# Run button
run_button = st.sidebar.button("Calculate Blood Lead Level", type="primary", use_container_width=True)

# Main content area
if run_button:
    with st.spinner("Running AALM simulation..."):
        try:
            # Find AALM executable - now bundled with the app!
            script_dir = Path(__file__).parent
            aalm_paths = [
                script_dir / "aalm_original" / "AALM_64.exe",  # Bundled version
                Path("aalm_original/AALM_64.exe"),  # Relative path
                Path("AALM_64.exe"),  # Current directory
            ]

            aalm_exe = None
            for path in aalm_paths:
                if path.exists():
                    aalm_exe = path
                    break

            if aalm_exe is None:
                st.error("Could not find AALM_64.exe. Please ensure it's in the correct location.")
                st.stop()

            # Create temporary directory for this simulation
            with tempfile.TemporaryDirectory() as tmpdir:
                tmpdir = Path(tmpdir)

                # Generate input file
                template_path = script_dir / "aalm_original" / "Examples" / "LeggettInput_Ex1a.txt"
                if not template_path.exists():
                    st.error(f"Template file not found at {template_path}. Please ensure aalm_original/Examples directory exists.")
                    st.stop()

                # Read template
                with open(template_path, 'r') as f:
                    template_lines = f.readlines()

                # Modify template with user inputs
                modified_lines = []
                for line_idx, line in enumerate(template_lines):
                    parts = line.rstrip().split(',')

                    # Change simulation name (first line) to WebSim
                    if line_idx == 0 and len(parts) > 0 and parts[0] == 'Name':
                        parts[1] = 'WebSim'
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
                                parts[3 + i] = f"{food_ug_day:.2f}"
                        modified_lines.append(','.join(parts) + '\n')

                    # Modify water concentration
                    elif len(parts) > 1 and parts[0] == 'Water' and parts[1] == 'concs1':
                        parts[3] = f"{water_ug_l:.2f}"
                        modified_lines.append(','.join(parts) + '\n')

                    # Modify soil concentration
                    elif len(parts) > 1 and parts[0] == 'Soil' and parts[1] == 'concs1':
                        parts[3] = f"{soil_ppm}"
                        modified_lines.append(','.join(parts) + '\n')

                    # Modify dust concentration
                    elif len(parts) > 1 and parts[0] == 'Dust' and parts[1] == 'concs1':
                        parts[3] = f"{dust_ppm}"
                        modified_lines.append(','.join(parts) + '\n')

                    else:
                        modified_lines.append(line)

                # Write input file in AALM's directory (it needs to run from there)
                aalm_dir = aalm_exe.parent
                input_file = aalm_dir / "LeggettInput_web.txt"
                with open(input_file, 'w') as f:
                    f.writelines(modified_lines)

                # Create output directory for WebSim (Fortran doesn't create it!)
                output_dir = aalm_dir / "WebSim"
                output_dir.mkdir(exist_ok=True)

                # Run AALM from its own directory (important!)
                result = subprocess.run(
                    [str(aalm_exe), str(input_file.name)],  # Just the filename
                    cwd=str(aalm_dir),  # Run from AALM directory
                    capture_output=True,
                    text=True,
                    timeout=60
                )

                if result.returncode != 0:
                    st.error(f"AALM simulation failed:\n{result.stderr}")
                    st.code(result.stdout)
                    st.stop()

                # Parse output
                stdout = result.stdout

                # Extract average BLL
                avg_bll_match = re.search(r'Average BLL over simulation\s*=\s*([\d.]+)', stdout)
                if avg_bll_match:
                    avg_bll = float(avg_bll_match.group(1))
                else:
                    avg_bll = None

                # Find output CSV files - AALM creates CSVs in SimName/ folder in its directory
                output_csv = None
                # We set the name to WebSim, so look for that
                sim_name = 'WebSim'
                output_csv = aalm_dir / sim_name / f"Out_{sim_name}.csv"

                if not output_csv.exists():
                    # Fallback 1: Check stdout for actual run name
                    sim_name_match = re.search(r'Run name = (\S+)', stdout)
                    if sim_name_match:
                        sim_name = sim_name_match.group(1).strip()
                        output_csv = aalm_dir / sim_name / f"Out_{sim_name}.csv"

                if not output_csv.exists():
                    # Fallback 2: look for any Out_*.csv in AALM dir (most recent)
                    out_csvs = list(aalm_dir.glob("*/Out_*.csv"))
                    if out_csvs:
                        # Get the most recently modified one
                        output_csv = max(out_csvs, key=lambda p: p.stat().st_mtime)

                # Display results
                st.success("Simulation Complete!")

                st.markdown("---")
                st.markdown("### Results Summary")

                col1, col2, col3 = st.columns(3)
                with col1:
                    if avg_bll is not None:
                        st.metric("Average Blood Lead Level", f"{avg_bll:.2f} μg/dL")
                with col2:
                    st.metric("Age Range", f"{age_range[0]}-{age_range[1]} years")
                with col3:
                    threshold = 3.5  # CDC reference level
                    status = "Above" if avg_bll and avg_bll > threshold else "Below"
                    st.metric(f"CDC Threshold ({threshold} μg/dL)", status)

                # Try to parse and plot CSV if available
                if output_csv and output_csv.exists():
                    try:
                        df = pd.read_csv(output_csv)
                        # Strip whitespace from column names
                        df.columns = df.columns.str.strip()

                        st.markdown("---")
                        st.markdown("### Blood Lead Level Over Time")

                        # Create plot - use 'Days' and 'Cblood' columns from Out_*.csv
                        fig = go.Figure()
                        if 'Days' in df.columns and 'Cblood' in df.columns:
                            fig.add_trace(go.Scatter(
                                x=df['Days'] / 365,  # Convert to years
                                y=df['Cblood'],
                                mode='lines',
                                name='Blood Lead Level',
                                line=dict(color='#D32F2F', width=2)
                            ))

                            fig.add_hline(
                                y=3.5,
                                line_dash="dash",
                                line_color="#FF9800",
                                annotation_text="CDC Reference (3.5 μg/dL)",
                                annotation_position="right"
                            )

                            fig.update_layout(
                                xaxis_title="Age (years)",
                                yaxis_title="Blood Lead Level (μg/dL)",
                                template="plotly_white",
                                height=400
                            )

                            st.plotly_chart(fig, use_container_width=True)

                        # Export options
                        st.markdown("---")
                        st.markdown("### Export Data")

                        col1, col2 = st.columns(2)

                        with col1:
                            # CSV download
                            csv_data = df.to_csv(index=False)
                            st.download_button(
                                "Download CSV (Daily)",
                                csv_data,
                                f"aalm_results_{age_range[1]}y.csv",
                                "text/csv"
                            )

                        with col2:
                            # CSV download (weekly averages)
                            # Group by weeks (every 7 rows)
                            df_weekly = df.iloc[::7].copy()  # Take every 7th row
                            csv_weekly_data = df_weekly.to_csv(index=False)
                            st.download_button(
                                "Download CSV (Weekly)",
                                csv_weekly_data,
                                f"aalm_results_{age_range[1]}y_weekly.csv",
                                "text/csv"
                            )

                    except Exception as e:
                        st.warning(f"Could not parse output CSV: {e}")
                        st.text("Raw output:")
                        st.code(stdout)

                else:
                    st.info("Output CSV not found. Showing raw output:")
                    st.code(stdout)

        except subprocess.TimeoutExpired:
            st.error("Simulation timed out. Try reducing the age range.")
        except Exception as e:
            st.error(f"Error: {str(e)}")
            import traceback
            st.code(traceback.format_exc())

else:
    # Initial state - show instructions
    st.info("Enter your exposure parameters in the sidebar and click **Calculate**")

    st.markdown("""
    ### How to Use This Tool

    This tool helps field workers quickly estimate Blood Lead Levels (BLL) from:
    - **XRF measurements** of soil/dust
    - **Lab results** for food and water samples

    #### Steps:
    1. **Set age range** - Typically 0-7 years for children
    2. **Choose sex** - Male or Female (affects body weight parameters)
    3. **Enter lead exposure**:
       - **Food**: Micrograms per day from dietary intake
       - **Water**: Micrograms per liter (PPB) from tap water
       - **Soil/Dust** (optional): PPM from XRF readings

    4. **Click Calculate** to run the simulation
    5. **View results**: BLL graph and summary statistics
    6. **Export**: Download data as CSV or Excel

    #### Example Scenarios:
    - **Low exposure**: 2 μg/day food, 1 μg/L water → BLL ~1-2 μg/dL
    - **Moderate**: 5 μg/day food, 5 μg/L water → BLL ~2-3 μg/dL
    - **High**: 10 μg/day food, 15 μg/L water, 500 PPM soil → BLL >5 μg/dL

    ---
    **Based on EPA All-Ages Lead Model (AALM) v3.1**
    """)

# Footer
st.markdown("---")
st.caption("Easy AALM | Lightweight wrapper for EPA All-Ages Lead Model | For field use")
