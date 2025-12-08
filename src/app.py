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
from aalm_constants import (
    WATER_INTAKE_AGES_DAYS,
    WATER_INTAKE_AMOUNTS,
    SOIL_INTAKE_AGES_DAYS,
    SOIL_INTAKE_AMOUNTS,
    DUST_INTAKE_AGES_DAYS,
    DUST_INTAKE_AMOUNTS,
)

st.set_page_config(
    page_title="Easy AALM - Lead Exposure Model",
    layout="wide"
)


st.title("Easy AALM - Lead Exposure Calculator")
st.markdown("Simple tool to estimate Blood Lead Levels from environmental measurements | Uses code from the [EPA AALM Model](https://www.epa.gov/superfund/lead-all-ages-lead-model-aalm)")

st.markdown("---")

# Demographics section at top
st.markdown("### Demographics")
col1, spacer, col2 = st.columns([1, 0.2, 1])
with col1:
    age_range = st.slider("Age Range (years)", 0, 90, (0, 90), help="Simulation from birth to specified age")
with col2:
    sex = st.radio("Sex", ["Female", "Male"], horizontal=True)

st.markdown("---")

# All 5 exposure pathways in columns
st.markdown("### Lead Exposure Sources")
if st.button("Clear All Sources", help="Set all lead concentrations to zero"):
    st.session_state.water_conc = 0.0
    st.session_state.food_amt = 0.0
    st.session_state.soil_conc = 0
    st.session_state.dust_conc = 0
    st.session_state.air_conc = 0.0
    st.rerun()

col1, col2, col3, col4, col5 = st.columns(5)

# WATER column
with col1:
    st.markdown("**Water**")
    water_input = st.number_input("Concentration (PPB)", 0.0, 50000.0, 0.9, 0.1, key="water_conc")
    water_ug_l = water_input  # 1 PPB = 1 μg/L

    water_scale_pct = st.number_input(
        "Intake Scale (%)",
        min_value=1.0,
        max_value=10000.0,
        value=100.0,
        step=10.0,
        key="water_scale"
    )
    water_scale_factor = water_scale_pct / 100.0

    with st.expander("Schedule"):
        # Excel defaults
        intake_ages_days = [0, 91.25, 365, 3650, 5475, 9125, 18250]
        intake_ages_years = [d/365 for d in intake_ages_days]
        intake_amt_liters = [0.2, 0.3, 0.35, 0.45, 0.55, 0.7, 1.04]
        scaled_intake = [amt * water_scale_factor for amt in intake_amt_liters]
        intake_df = pd.DataFrame({
            'Age (years)': intake_ages_years,
            'Intake (L/day)': scaled_intake
        })
        st.dataframe(intake_df, width='stretch', hide_index=True)

# FOOD column
with col2:
    st.markdown("**Food**")
    food_ug_day = st.number_input("Amount (μg/day)", 0.0, 1000.0, 10.0, 0.1, key="food_amt")

# SOIL column
with col3:
    st.markdown("**Soil**")
    soil_ppm = st.number_input("Concentration (PPM)", 0, 10000, 652, 10, key="soil_conc")

    soil_scale_pct = st.number_input(
        "Intake Scale (%)",
        min_value=1.0,
        max_value=10000.0,
        value=100.0,
        step=10.0,
        key="soil_scale"
    )
    soil_scale_factor = soil_scale_pct / 100.0

    with st.expander("Schedule"):
        intake_ages_years = [d/365 for d in SOIL_INTAKE_AGES_DAYS]
        scaled_intake = [amt * soil_scale_factor for amt in SOIL_INTAKE_AMOUNTS]
        intake_df = pd.DataFrame({
            'Age (years)': intake_ages_years,
            'Intake (g/day)': scaled_intake
        })
        st.dataframe(intake_df, width='stretch', hide_index=True)

# DUST column
with col4:
    st.markdown("**Dust**")
    dust_ppm = st.number_input("Concentration (PPM)", 0, 10000, 10, 10, key="dust_conc")

    dust_scale_pct = st.number_input(
        "Intake Scale (%)",
        min_value=1.0,
        max_value=10000.0,
        value=100.0,
        step=10.0,
        key="dust_scale"
    )
    dust_scale_factor = dust_scale_pct / 100.0

    with st.expander("Schedule"):
        # Excel defaults (g/day)
        intake_ages_days = [0, 91.25, 365, 1825, 3650, 5475]
        intake_ages_years = [d/365 for d in intake_ages_days]
        intake_amt_grams = [0.022, 0.039, 0.05, 0.044, 0.033, 0.017]
        scaled_intake = [amt * dust_scale_factor for amt in intake_amt_grams]
        intake_df = pd.DataFrame({
            'Age (years)': intake_ages_years,
            'Intake (g/day)': scaled_intake
        })
        st.dataframe(intake_df, width='stretch', hide_index=True)

# AIR column
with col5:
    st.markdown("**Air**")
    air_ug_m3 = st.number_input("Concentration (μg/m³)", 0.0, 1000.0, 0.01, 0.01, key="air_conc")

    air_scale_pct = st.number_input(
        "Intake Scale (%)",
        min_value=1.0,
        max_value=10000.0,
        value=100.0,
        step=10.0,
        key="air_scale"
    )
    air_scale_factor = air_scale_pct / 100.0

    with st.expander("Schedule"):
        intake_ages_years = [0, 1, 2, 3, 6, 11, 16, 21, 31, 51, 61, 71, 81]
        intake_amt_m3 = [5.4, 8, 8.9, 10.1, 12, 15.2, 16.3, 15.7, 16, 15.7, 14.2, 12.9, 12.2]
        scaled_intake = [amt * air_scale_factor for amt in intake_amt_m3]
        intake_df = pd.DataFrame({
            'Age (years)': intake_ages_years,
            'Intake (m³/day)': scaled_intake
        })
        st.dataframe(intake_df, width='stretch', hide_index=True)

# Run button - centered and prominent
st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    run_button = st.button("Calculate Blood Lead Level", type="primary", width='stretch')

st.markdown("---")

# Main content area
if run_button:
    with st.spinner("Running AALM simulation..."):
        try:
            # Find AALM executable - check bundled locations only
            script_dir = Path(__file__).parent

            # If running from src/ subdirectory, use parent directory
            if script_dir.name == "src":
                repo_dir = script_dir.parent
            else:
                repo_dir = script_dir

            aalm_paths = [
                script_dir / "aalm_original" / "AALM_64.exe",  # Same directory as script (bundled app)
                repo_dir / "aalm_original" / "AALM_64.exe",  # Repository root (development)
                Path("aalm_original/AALM_64.exe"),  # Relative path
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

                # Generate input file using shared module
                from fortran_input_generator import generate_fortran_input

                # Template file is in the same directory as this script
                template_path = Path(__file__).parent / "templates" / "LeggettInput_Golden.txt"
                if not template_path.exists():
                    st.error(f"Template file not found at {template_path}")
                    st.stop()

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
                    sim_name='WebSim'
                )

                # Copy AALM and required files to temp directory (app bundle is read-only on macOS)
                import shutil
                work_dir = tmpdir / "aalm_work"
                work_dir.mkdir(exist_ok=True)

                # Copy AALM executable
                shutil.copy(aalm_exe, work_dir)
                work_aalm_exe = work_dir / aalm_exe.name

                # Set execute permissions on Linux/Unix systems (needed after copy)
                # Platform and stat are imported below - we'll move them up
                import platform
                import stat
                if platform.system() != "Windows":
                    os.chmod(work_aalm_exe, os.stat(work_aalm_exe).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

                # Copy RespMod directory (required by AALM)
                respmod_src = aalm_exe.parent / "RespMod"
                if respmod_src.exists():
                    shutil.copytree(respmod_src, work_dir / "RespMod")

                # Write input file in working directory
                input_file = work_dir / "LeggettInput_web.txt"
                with open(input_file, 'w') as f:
                    f.writelines(modified_lines)

                # Create output directory for WebSim (Fortran doesn't create it!)
                output_dir = work_dir / "WebSim"
                output_dir.mkdir(exist_ok=True)

                # Run AALM from working directory
                # On macOS, use Wine to run the Windows executable
                script_dir = Path(__file__).parent
                if platform.system() == "Darwin":
                    # Find Wine - check bundled location first
                    wine_path = "wine"
                    bundled_wine = script_dir / "Wine Crossover.app" / "Contents" / "Resources" / "wine" / "bin" / "wine"
                    if bundled_wine.exists():
                        wine_path = str(bundled_wine)
                    cmd = [wine_path, str(work_aalm_exe), str(input_file.name)]
                else:
                    cmd = [str(work_aalm_exe), str(input_file.name)]

                # Set up environment to prevent Wine from accessing user folders and showing GUI
                # Use a persistent temp location so Wine doesn't re-initialize every simulation
                wine_env = os.environ.copy()
                wine_prefix = Path(tempfile.gettempdir()) / 'easy-aalm-wine'
                wine_prefix.mkdir(exist_ok=True)
                wine_env['WINEPREFIX'] = str(wine_prefix)
                wine_env['WINEDLLOVERRIDES'] = 'winemenubuilder.exe=d;mscoree=d;mshtml=d'
                wine_env['WINEDEBUG'] = '-all'  # Suppress Wine debug output
                wine_env['DISPLAY'] = ''  # Disable X11 to prevent GUI dialogs

                # Pre-initialize Wine prefix silently (avoids "Wine configuration" popup)
                # and remove symlinks to user folders to prevent permission dialogs
                wine_prefix_initialized = (wine_prefix / 'drive_c').exists()
                if platform.system() == "Darwin" and not wine_prefix_initialized:
                    wineboot_path = Path(wine_path).parent / 'wineboot' if wine_path != "wine" else "wineboot"
                    try:
                        subprocess.run(
                            [str(wineboot_path), '--init'],
                            env=wine_env,
                            capture_output=True,
                            timeout=60
                        )
                        # Remove symlinks to user folders that trigger permission dialogs
                        users_dir = wine_prefix / 'drive_c' / 'users'
                        if users_dir.exists():
                            for user_dir in users_dir.iterdir():
                                if user_dir.is_dir():
                                    for folder in ['Desktop', 'Documents', 'Downloads', 'Music', 'Pictures', 'Videos']:
                                        folder_path = user_dir / folder
                                        if folder_path.is_symlink():
                                            folder_path.unlink()
                                            folder_path.mkdir(exist_ok=True)
                    except Exception:
                        pass  # Continue even if wineboot fails

                result = subprocess.run(
                    cmd,
                    cwd=str(work_dir),  # Run from working directory
                    capture_output=True,
                    text=True,
                    timeout=60,
                    env=wine_env
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

                # Find output CSV files - AALM creates CSVs in SimName/ folder in working directory
                output_csv = None
                # We set the name to WebSim, so look for that
                sim_name = 'WebSim'
                output_csv = work_dir / sim_name / f"Out_{sim_name}.csv"

                if not output_csv.exists():
                    # Fallback 1: Check stdout for actual run name
                    sim_name_match = re.search(r'Run name = (\S+)', stdout)
                    if sim_name_match:
                        sim_name = sim_name_match.group(1).strip()
                        output_csv = work_dir / sim_name / f"Out_{sim_name}.csv"

                if not output_csv.exists():
                    # Fallback 2: look for any Out_*.csv in working dir (most recent)
                    out_csvs = list(work_dir.glob("*/Out_*.csv"))
                    if out_csvs:
                        # Get the most recently modified one
                        output_csv = max(out_csvs, key=lambda p: p.stat().st_mtime)

                # Display results
                st.markdown("## Results")
                st.success("Simulation Complete!")

                st.markdown("### Summary")

                col1, col2 = st.columns(2)
                with col1:
                    if avg_bll is not None:
                        # Convert from µg/dL to µg/L (multiply by 10)
                        avg_bll_per_L = avg_bll * 10
                        st.metric("Average Blood Lead Level", f"{avg_bll_per_L:.1f} μg/L")
                with col2:
                    st.metric("Age Range", f"{age_range[0]}-{age_range[1]} years")

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
                            # Convert Cblood from µg/dL to µg/L (multiply by 10)
                            fig.add_trace(go.Scatter(
                                x=df['Days'] / 365,  # Convert to years
                                y=df['Cblood'] * 10,  # Convert to µg/L
                                mode='lines',
                                name='Blood Lead Level',
                                line=dict(color='#D32F2F', width=2)
                            ))

                            fig.update_layout(
                                xaxis_title="Age (years)",
                                yaxis_title="Blood Lead Level (μg/L)",
                                template="plotly_white",
                                height=400
                            )

                            st.plotly_chart(fig, width='stretch')

                        # Fortran input file as hidden expander
                        with st.expander("Show Fortran Input File"):
                            st.caption("This shows the parameters sent to the AALM Fortran model")

                            # Read and display the input file
                            if input_file.exists():
                                # Parse input file into a table
                                input_data = []
                                with open(input_file, 'r') as f:
                                    for line in f:
                                        line = line.strip()
                                        if line:
                                            parts = line.split(',')
                                            input_data.append(parts)

                                # Create DataFrame with appropriate columns
                                max_cols = max(len(row) for row in input_data) if input_data else 0
                                col_names = ['Parameter', 'Variable', 'Count'] + [f'Value{i}' for i in range(1, max_cols - 2)]

                                # Pad rows to have same length
                                padded_data = []
                                for row in input_data:
                                    padded_row = row + [''] * (max_cols - len(row))
                                    padded_data.append(padded_row)

                                input_df = pd.DataFrame(padded_data, columns=col_names[:max_cols])

                                # Display as table
                                st.dataframe(
                                    input_df,
                                    width='stretch',
                                    height=400
                                )

                                # Also provide download button for input file
                                with open(input_file, 'r') as f:
                                    input_file_content = f.read()
                                st.download_button(
                                    "Download Input File",
                                    input_file_content,
                                    "LeggettInput_web.txt",
                                    "text/plain",
                                    key="download_input_file"
                                )
                            else:
                                st.warning("Input file not found")

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
                                "text/csv",
                                key="download_csv_daily"
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
                                "text/csv",
                                key="download_csv_weekly"
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
    # Initial state
    st.info("Enter your exposure parameters above and click **Calculate Blood Lead Level**")

# Footer
st.markdown("---")
st.caption("Easy AALM | Lightweight wrapper for EPA All-Ages Lead Model | For field use")
