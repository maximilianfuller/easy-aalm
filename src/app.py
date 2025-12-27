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
import platform
from pathlib import Path
import tempfile
import shutil

# Windows: flags to hide console windows from subprocesses
if platform.system() == 'Windows':
    SUBPROCESS_FLAGS = subprocess.CREATE_NO_WINDOW
    STARTUPINFO = subprocess.STARTUPINFO()
    STARTUPINFO.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    STARTUPINFO.wShowWindow = subprocess.SW_HIDE
else:
    SUBPROCESS_FLAGS = 0
    STARTUPINFO = None


@st.cache_data
def parse_golden_file_schedules(template_path: str) -> dict:
    """Parse intake schedules from the golden template file."""
    schedules = {}
    with open(template_path, 'r') as f:
        for line in f:
            parts = line.strip().split(',')
            if len(parts) < 4:
                continue
            source = parts[0]  # Water, Soil, Dust, Air
            param = parts[1]   # intake_ages, intake_amt
            count = int(parts[2]) if parts[2].isdigit() else 0

            if param == 'intake_ages':
                values = [float(x) for x in parts[3:3+count] if x]
                schedules[f'{source}_ages'] = values
            elif param == 'intake_amt':
                values = [float(x) for x in parts[3:3+count] if x]
                schedules[f'{source}_amt'] = values
    return schedules


# Get template path and parse schedules
_template_path = Path(__file__).resolve().parent / "templates" / "LeggettInput_Golden.txt"
if _template_path.exists():
    SCHEDULES = parse_golden_file_schedules(str(_template_path))
else:
    # Fallback to empty schedules if template not found
    SCHEDULES = {}

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
    for key in ['water_conc', 'food_amt', 'soil_conc', 'dust_conc', 'air_conc']:
        st.session_state.pop(key, None)
    st.rerun()

col1, col2, col3, col4, col5 = st.columns(5)

# WATER column
with col1:
    st.markdown("**Water**")
    water_input = st.number_input("Concentration (PPB)", min_value=0.0, max_value=50000.0, value=0.9, step=0.1, key="water_conc")
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
        intake_ages_years = [d/365 for d in SCHEDULES.get('Water_ages', [])]
        scaled_intake = [amt * water_scale_factor for amt in SCHEDULES.get('Water_amt', [])]
        intake_df = pd.DataFrame({
            'Age (years)': intake_ages_years,
            'Intake (L/day)': scaled_intake
        })
        st.dataframe(intake_df, width='stretch', hide_index=True)

# FOOD column
with col2:
    st.markdown("**Food**")
    food_ug_day = st.number_input("Amount (μg/day)", min_value=0.0, max_value=1000.0, value=10.0, step=0.1, key="food_amt")

# SOIL column
with col3:
    st.markdown("**Soil**")
    soil_ppm = st.number_input("Concentration (PPM)", min_value=0, max_value=10000, value=652, step=10, key="soil_conc")

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
        intake_ages_years = [d/365 for d in SCHEDULES.get('Soil_ages', [])]
        scaled_intake = [amt * soil_scale_factor for amt in SCHEDULES.get('Soil_amt', [])]
        intake_df = pd.DataFrame({
            'Age (years)': intake_ages_years,
            'Intake (g/day)': scaled_intake
        })
        st.dataframe(intake_df, width='stretch', hide_index=True)

# DUST column
with col4:
    st.markdown("**Dust**")
    dust_ppm = st.number_input("Concentration (PPM)", min_value=0, max_value=10000, value=10, step=10, key="dust_conc")

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
        intake_ages_years = [d/365 for d in SCHEDULES.get('Dust_ages', [])]
        scaled_intake = [amt * dust_scale_factor for amt in SCHEDULES.get('Dust_amt', [])]
        intake_df = pd.DataFrame({
            'Age (years)': intake_ages_years,
            'Intake (g/day)': scaled_intake
        })
        st.dataframe(intake_df, width='stretch', hide_index=True)

# AIR column
with col5:
    st.markdown("**Air**")
    air_ug_m3 = st.number_input("Concentration (μg/m³)", min_value=0.0, max_value=1000.0, value=0.01, step=0.01, key="air_conc")

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
        intake_ages_years = [d/365 for d in SCHEDULES.get('Air_ages', [])]
        scaled_intake = [amt * air_scale_factor for amt in SCHEDULES.get('Air_amt', [])]
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

# Initialize session state for results
if 'simulation_results' not in st.session_state:
    st.session_state.simulation_results = None

# Main content area
if run_button:
    with st.spinner("Running AALM simulation..."):
        try:
            # Find AALM executable - check bundled locations only
            script_dir = Path(__file__).resolve().parent

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

                # Initialize profiling
                import time
                profiling_times = {}
                overall_start = time.time()

                # Generate input file using shared module
                start_time = time.time()
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
                profiling_times['input_generation'] = time.time() - start_time

                # Copy AALM and required files to temp directory (app bundle is read-only on macOS)
                start_time = time.time()
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
                profiling_times['file_setup'] = time.time() - start_time

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
                start_time = time.time()
                wine_prefix_initialized = (wine_prefix / 'drive_c').exists()
                if platform.system() == "Darwin" and not wine_prefix_initialized:
                    wineboot_path = Path(wine_path).parent / 'wineboot' if wine_path != "wine" else "wineboot"
                    try:
                        subprocess.run(
                            [str(wineboot_path), '--init'],
                            env=wine_env,
                            capture_output=True,
                            timeout=60,
                            creationflags=SUBPROCESS_FLAGS,
                            startupinfo=STARTUPINFO
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
                profiling_times['wine_init'] = time.time() - start_time

                # Run AALM simulation
                start_time = time.time()
                result = subprocess.run(
                    cmd,
                    cwd=str(work_dir),  # Run from working directory
                    capture_output=True,
                    text=True,
                    timeout=60,
                    env=wine_env,
                    creationflags=SUBPROCESS_FLAGS,
                    startupinfo=STARTUPINFO
                )
                profiling_times['aalm_execution'] = time.time() - start_time

                if result.returncode != 0:
                    st.error(f"AALM simulation failed:\n{result.stderr}")
                    st.code(result.stdout)
                    st.stop()

                # Parse output
                start_time = time.time()
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
                profiling_times['output_parsing'] = time.time() - start_time

                # Calculate total time
                profiling_times['total'] = time.time() - overall_start

                # Read CSV and input file contents before temp dir is cleaned up
                csv_content = None
                input_content = None
                if output_csv and output_csv.exists():
                    csv_content = output_csv.read_text()
                if input_file.exists():
                    input_content = input_file.read_text()

                # Store results in session state (with file contents, not paths)
                st.session_state.simulation_results = {
                    'avg_bll': avg_bll,
                    'age_range': age_range,
                    'sex': sex,
                    'csv_content': csv_content,
                    'input_content': input_content,
                    'stdout': stdout,
                    'profiling': profiling_times
                }

        except subprocess.TimeoutExpired:
            st.error("Simulation timed out. Try reducing the age range.")
        except Exception as e:
            st.error(f"Error: {str(e)}")
            import traceback
            st.code(traceback.format_exc())

# Display results from session state (persists across reruns)
if st.session_state.simulation_results:
    results = st.session_state.simulation_results

    st.markdown("## Results")
    st.success("Simulation Complete!")

    st.markdown("### Summary")

    col1, col2 = st.columns(2)
    with col1:
        if results['avg_bll'] is not None:
            # Convert from µg/dL to µg/L (multiply by 10)
            avg_bll_per_L = results['avg_bll'] * 10
            st.metric("Average Blood Lead Level", f"{avg_bll_per_L:.1f} μg/L")
    with col2:
        st.metric("Age Range", f"{results['age_range'][0]}-{results['age_range'][1]} years")

    # Display profiling data in a collapsible expander
    if 'profiling' in results and results['profiling']:
        with st.expander("⏱️ Performance Profiling"):
            prof = results['profiling']
            st.caption("Time spent in each stage of the simulation:")

            # Create a bar chart of profiling data
            prof_df = pd.DataFrame([
                {"Stage": "Input Generation", "Time (ms)": prof.get('input_generation', 0) * 1000},
                {"Stage": "File Setup", "Time (ms)": prof.get('file_setup', 0) * 1000},
                {"Stage": "Wine Init", "Time (ms)": prof.get('wine_init', 0) * 1000},
                {"Stage": "AALM Execution", "Time (ms)": prof.get('aalm_execution', 0) * 1000},
                {"Stage": "Output Parsing", "Time (ms)": prof.get('output_parsing', 0) * 1000},
            ])

            # Display as metrics in columns
            cols = st.columns(5)
            for idx, row in prof_df.iterrows():
                with cols[idx]:
                    st.metric(row['Stage'], f"{row['Time (ms)']:.1f} ms")

            # Show total time
            st.markdown(f"**Total Time:** {prof.get('total', 0)*1000:.1f} ms")

    # Try to parse and plot CSV if available
    if results.get('csv_content'):
        try:
            from io import StringIO
            df = pd.read_csv(StringIO(results['csv_content']))
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

                # Display the input file content
                if results.get('input_content'):
                    # Parse input file into a table
                    input_data = []
                    for line in results['input_content'].splitlines():
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
                    st.download_button(
                        "Download Input File",
                        results['input_content'],
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
                    f"aalm_results_{results['age_range'][1]}y.csv",
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
                    f"aalm_results_{results['age_range'][1]}y_weekly.csv",
                    "text/csv",
                    key="download_csv_weekly"
                )

        except Exception as e:
            st.warning(f"Could not parse output CSV: {e}")
            st.text("Raw output:")
            st.code(results['stdout'])

    else:
        st.info("Output CSV not found. Showing raw output:")
        st.code(results['stdout'])

else:
    # Initial state
    st.info("Enter your exposure parameters above and click **Calculate Blood Lead Level**")

# Footer
st.markdown("---")
st.caption("Easy AALM | Lightweight wrapper for EPA All-Ages Lead Model | For field use")
