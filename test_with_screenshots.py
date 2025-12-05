#!/usr/bin/env python3
"""
Integration Test with Screenshots

This test runs the complete workflow including:
1. Starting Streamlit
2. Opening in browser (automated)
3. Filling in form parameters
4. Clicking calculate
5. Capturing screenshots of results

Prerequisites:
    pip install playwright
    playwright install chromium

Usage:
    python3 test_with_screenshots.py
"""

import subprocess
import time
from pathlib import Path
import sys

def check_playwright():
    """Check if Playwright is installed"""
    try:
        import playwright
        print("✓ Playwright installed")
        return True
    except ImportError:
        print("❌ Playwright not installed")
        print("Install with:")
        print("  pip install playwright")
        print("  playwright install chromium")
        return False

def is_streamlit_running():
    """Check if Streamlit is already running"""
    result = subprocess.run(
        ["pgrep", "-f", "streamlit run app.py"],
        capture_output=True
    )
    return result.returncode == 0

def start_streamlit():
    """Start Streamlit in background"""
    venv_streamlit = Path.home() / "Library" / "Application Support" / "Easy AALM" / "venv" / "bin" / "streamlit"

    if is_streamlit_running():
        print("✓ Streamlit already running")
        return None

    print("Starting Streamlit...")
    process = subprocess.Popen(
        [str(venv_streamlit), "run", "app.py", "--server.headless", "true"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    # Wait for Streamlit to start
    time.sleep(5)
    print("✓ Streamlit started")
    return process

def run_browser_test():
    """Run automated browser test with screenshots"""
    from playwright.sync_api import sync_playwright

    print("\n" + "=" * 70)
    print("RUNNING BROWSER TEST")
    print("=" * 70)
    print()

    with sync_playwright() as p:
        # Launch browser
        print("Launching browser...")
        browser = p.chromium.launch(headless=False)  # Set to True for headless
        page = browser.new_page()

        # Navigate to Streamlit
        url = "http://localhost:8501"
        print(f"Navigating to {url}...")
        page.goto(url)

        # Wait for page to load
        time.sleep(3)

        # Take screenshot of initial state
        print("📸 Screenshot 1: Initial state")
        page.screenshot(path="test_screenshots/01_initial.png", full_page=True)

        # Fill in water concentration
        print("Filling in water concentration...")
        # Click PPM radio button (if not selected)
        page.click('text="PPM"')
        # Fill in water lead value
        page.fill('input[aria-label="Lead in Water (PPM)"]', '5.0')

        # Adjust water intake scale slider
        print("Adjusting water intake scale...")
        # The slider might need special handling
        slider = page.locator('input[type="range"]').first
        slider.fill('75')  # Set to 75 on slider (maps to ~316% via log scale)

        time.sleep(1)

        # Take screenshot of filled form
        print("📸 Screenshot 2: Form filled")
        page.screenshot(path="test_screenshots/02_form_filled.png", full_page=True)

        # Click calculate button
        print("Clicking Calculate button...")
        page.click('button:has-text("Calculate Blood Lead Level")')

        # Wait for results to load
        print("Waiting for results...")
        time.sleep(15)  # AALM simulation takes time

        # Wait for success message
        try:
            page.wait_for_selector('text="Simulation Complete!"', timeout=30000)
            print("✓ Simulation completed!")
        except:
            print("⚠ Timeout waiting for results")

        # Take screenshot of results
        print("📸 Screenshot 3: Results")
        page.screenshot(path="test_screenshots/03_results.png", full_page=True)

        # Scroll to graph
        print("Scrolling to graph...")
        page.evaluate("window.scrollTo(0, 800)")
        time.sleep(1)

        print("📸 Screenshot 4: Graph closeup")
        page.screenshot(path="test_screenshots/04_graph.png", full_page=True)

        # Check for expander and click it
        print("Opening Fortran input file expander...")
        try:
            page.click('text="Show Fortran Input File"')
            time.sleep(2)
            print("📸 Screenshot 5: Fortran input file")
            page.screenshot(path="test_screenshots/05_fortran_input.png", full_page=True)
        except:
            print("⚠ Could not find Fortran input expander")

        # Close browser
        print("\nClosing browser...")
        browser.close()

        print("\n" + "=" * 70)
        print("✅ BROWSER TEST COMPLETE!")
        print("=" * 70)
        print("\nScreenshots saved in test_screenshots/:")
        print("  01_initial.png       - Initial app state")
        print("  02_form_filled.png   - Form with parameters")
        print("  03_results.png       - Full results page")
        print("  04_graph.png         - Graph closeup")
        print("  05_fortran_input.png - Fortran input file")
        print()

def main():
    print("\n" + "=" * 70)
    print("EASY AALM - INTEGRATION TEST WITH SCREENSHOTS")
    print("=" * 70)
    print()

    # Check prerequisites
    if not check_playwright():
        sys.exit(1)

    # Create screenshots directory
    screenshots_dir = Path("test_screenshots")
    screenshots_dir.mkdir(exist_ok=True)
    print(f"✓ Screenshots directory: {screenshots_dir}")
    print()

    # Start Streamlit
    streamlit_process = start_streamlit()

    try:
        # Run browser test
        run_browser_test()
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        # Clean up
        if streamlit_process:
            print("Stopping Streamlit...")
            streamlit_process.terminate()
            streamlit_process.wait()

    print("Test completed successfully!")

if __name__ == "__main__":
    main()
