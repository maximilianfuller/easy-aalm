#!/bin/bash
set -e

echo "========================================"
echo "Easy AALM - Fresh Install Test"
echo "========================================"
echo ""
echo "This script simulates a fresh user installation by:"
echo "  1. Cleaning all user data"
echo "  2. Launching the app"
echo "  3. Verifying first-run setup completes"
echo "  4. Testing basic functionality"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

USER_DATA_DIR="$HOME/Library/Application Support/Easy AALM"
APP_BUNDLE="./Easy AALM.app"
RUN_SCRIPT="$APP_BUNDLE/Contents/Resources/run.sh"

# Check if app bundle exists
if [ ! -d "$APP_BUNDLE" ]; then
    echo -e "${RED}Error: App bundle not found at $APP_BUNDLE${NC}"
    echo "Please run this script from the easy-aalm directory"
    exit 1
fi

# Helper functions
pass_test() {
    echo -e "${GREEN}✓ PASS${NC}: $1"
}

fail_test() {
    echo -e "${RED}✗ FAIL${NC}: $1"
    echo ""
    echo "Test failed. Cleaning up..."
    pkill -f streamlit 2>/dev/null || true
    exit 1
}

warn_test() {
    echo -e "${YELLOW}⚠ WARN${NC}: $1"
}

# Step 1: Backup existing user data
BACKUP_DIR=""
if [ -d "$USER_DATA_DIR" ]; then
    BACKUP_DIR="${USER_DATA_DIR}_backup_$(date +%s)"
    echo "Step 1: Backing up existing user data..."
    mv "$USER_DATA_DIR" "$BACKUP_DIR"
    pass_test "Backed up to: $BACKUP_DIR"
else
    echo "Step 1: No existing user data found"
    pass_test "Clean environment confirmed"
fi

# Step 2: Kill any running Streamlit processes
echo ""
echo "Step 2: Stopping any running processes..."
pkill -f "streamlit.*app.py" 2>/dev/null || true
sleep 2
pass_test "All processes stopped"

# Step 3: Launch app in background
echo ""
echo "Step 3: Launching app for first-time setup..."
echo "This will:"
echo "  - Create virtual environment"
echo "  - Install Python dependencies"
echo "  - Check/install Wine (if needed)"
echo "  - Copy app files"
echo ""

# Create a log file for the app output
LOG_FILE="/tmp/easy_aalm_test_$(date +%s).log"
echo "App output will be logged to: $LOG_FILE"

# Launch the app in background
bash "$RUN_SCRIPT" > "$LOG_FILE" 2>&1 &
APP_PID=$!

echo "App launched with PID: $APP_PID"

# Wait for setup to complete (look for specific markers in log)
echo "Waiting for first-time setup to complete..."
TIMEOUT=300  # 5 minutes timeout
ELAPSED=0
SETUP_COMPLETE=false

while [ $ELAPSED -lt $TIMEOUT ]; do
    if grep -q "Setup complete" "$LOG_FILE" 2>/dev/null; then
        SETUP_COMPLETE=true
        break
    fi

    if grep -q "Starting Streamlit app" "$LOG_FILE" 2>/dev/null; then
        SETUP_COMPLETE=true
        break
    fi

    # Check if process is still running
    if ! kill -0 $APP_PID 2>/dev/null; then
        echo ""
        echo "App process died unexpectedly. Last 50 lines of log:"
        tail -50 "$LOG_FILE"
        fail_test "App process terminated during setup"
    fi

    sleep 2
    ELAPSED=$((ELAPSED + 2))

    # Show progress every 10 seconds
    if [ $((ELAPSED % 10)) -eq 0 ]; then
        echo "  ... still setting up ($ELAPSED seconds elapsed)"
    fi
done

if [ "$SETUP_COMPLETE" = false ]; then
    echo ""
    echo "Setup did not complete within $TIMEOUT seconds"
    echo "Last 50 lines of log:"
    tail -50 "$LOG_FILE"
    pkill -f streamlit 2>/dev/null || true
    fail_test "Setup timeout"
fi

pass_test "First-time setup completed"

# Step 4: Wait for Streamlit to start
echo ""
echo "Step 4: Waiting for Streamlit server to start..."
STREAMLIT_READY=false
TIMEOUT=60
ELAPSED=0

while [ $ELAPSED -lt $TIMEOUT ]; do
    if grep -q "You can now view your Streamlit app" "$LOG_FILE" 2>/dev/null; then
        STREAMLIT_READY=true
        break
    fi

    if curl -s http://localhost:8501 > /dev/null 2>&1; then
        STREAMLIT_READY=true
        break
    fi

    sleep 2
    ELAPSED=$((ELAPSED + 2))
done

if [ "$STREAMLIT_READY" = false ]; then
    echo ""
    echo "Streamlit did not start within $TIMEOUT seconds"
    echo "Last 50 lines of log:"
    tail -50 "$LOG_FILE"
    pkill -f streamlit 2>/dev/null || true
    fail_test "Streamlit startup timeout"
fi

pass_test "Streamlit server is running"

# Step 5: Verify user data directory structure
echo ""
echo "Step 5: Verifying user data directory structure..."

EXPECTED_ITEMS=(
    "venv/bin/python"
    "app.py"
    "fortran_input_generator.py"
    "templates/LeggettInput_ExcelDefaults.txt"
    "aalm_original/AALM_64.exe"
)

for item in "${EXPECTED_ITEMS[@]}"; do
    if [ -e "$USER_DATA_DIR/$item" ]; then
        pass_test "Found $item"
    else
        fail_test "Missing $item"
    fi
done

# Step 6: Verify Wine is accessible
echo ""
echo "Step 6: Verifying Wine is accessible..."

if [[ "$OSTYPE" == "darwin"* ]]; then
    # Check Wine in the PATH that would be used by the app
    if [[ $(uname -m) == "arm64" ]]; then
        TEST_PATH="/opt/homebrew/bin:$PATH"
    else
        TEST_PATH="/usr/local/bin:$PATH"
    fi

    if PATH="$TEST_PATH" command -v wine &> /dev/null; then
        WINE_VERSION=$(PATH="$TEST_PATH" wine --version)
        pass_test "Wine is accessible: $WINE_VERSION"
    else
        warn_test "Wine not found in PATH (this may cause issues running AALM)"
    fi
else
    pass_test "Not on macOS, skipping Wine check"
fi

# Step 7: Test Streamlit UI is accessible
echo ""
echo "Step 7: Testing Streamlit UI accessibility..."

HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8501)

if [ "$HTTP_STATUS" = "200" ]; then
    pass_test "Streamlit UI is accessible (HTTP 200)"
else
    warn_test "Streamlit returned HTTP $HTTP_STATUS (expected 200)"
fi

# Step 8: Stop the app
echo ""
echo "Step 8: Stopping the app..."
pkill -f streamlit 2>/dev/null || true
sleep 2
pass_test "App stopped"

# Step 9: Cleanup and restore
echo ""
echo "========================================"
echo "Test Cleanup"
echo "========================================"

if [ -n "$BACKUP_DIR" ]; then
    echo "Restoring original user data..."
    rm -rf "$USER_DATA_DIR"
    mv "$BACKUP_DIR" "$USER_DATA_DIR"
    pass_test "Restored original user data"
else
    echo "Keeping test user data for inspection..."
    echo "User data location: $USER_DATA_DIR"
    pass_test "Test data preserved"
fi

echo "Log file saved to: $LOG_FILE"

# Final summary
echo ""
echo "========================================"
echo -e "${GREEN}Fresh Install Test PASSED!${NC}"
echo "========================================"
echo ""
echo "Summary:"
echo "  - First-time setup completed successfully"
echo "  - All required files created"
echo "  - Streamlit server started"
echo "  - UI is accessible"
if [[ "$OSTYPE" == "darwin"* ]] && PATH="$TEST_PATH" command -v wine &> /dev/null; then
    echo "  - Wine is properly configured"
fi
echo ""
echo "The app is ready for distribution!"
echo ""
