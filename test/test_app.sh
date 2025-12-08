#!/bin/bash
set -e

echo "========================================"
echo "Easy AALM - Automated Test Suite"
echo "========================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test configuration
USER_DATA_DIR="$HOME/Library/Application Support/Easy AALM"
APP_BUNDLE="./Easy AALM.app"
TEST_MODE="${1:-quick}"  # quick or full

# Helper functions
pass_test() {
    echo -e "${GREEN}✓ PASS${NC}: $1"
}

fail_test() {
    echo -e "${RED}✗ FAIL${NC}: $1"
    exit 1
}

warn_test() {
    echo -e "${YELLOW}⚠ WARN${NC}: $1"
}

# Test 1: Check app bundle exists
echo "Test 1: Checking app bundle exists..."
if [ -d "$APP_BUNDLE" ]; then
    pass_test "App bundle found at $APP_BUNDLE"
else
    fail_test "App bundle not found at $APP_BUNDLE"
fi

# Test 2: Check required files in app bundle
echo ""
echo "Test 2: Checking required files in app bundle..."
REQUIRED_FILES=(
    "Contents/Resources/run.sh"
    "Contents/Resources/app.py"
    "Contents/Resources/fortran_input_generator.py"
    "Contents/Resources/templates/LeggettInput_Golden.txt"
    "Contents/Resources/aalm_original/AALM_64.exe"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$APP_BUNDLE/$file" ]; then
        pass_test "Found $file"
    else
        fail_test "Missing $file"
    fi
done

# Test 3: Backup existing user data if it exists
echo ""
echo "Test 3: Setting up test environment..."
BACKUP_DIR=""
if [ -d "$USER_DATA_DIR" ]; then
    BACKUP_DIR="${USER_DATA_DIR}_backup_$(date +%s)"
    echo "Backing up existing user data to $BACKUP_DIR"
    mv "$USER_DATA_DIR" "$BACKUP_DIR"
    pass_test "Backed up existing user data"
else
    pass_test "No existing user data to backup"
fi

# Test 4: Check if Python 3 is installed
echo ""
echo "Test 4: Checking Python 3 installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    pass_test "Python 3 is installed: $PYTHON_VERSION"
else
    fail_test "Python 3 is not installed"
fi

# Test 5: Check if Wine is installed (for macOS)
echo ""
echo "Test 5: Checking Wine installation..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    if command -v wine &> /dev/null; then
        WINE_VERSION=$(wine --version)
        pass_test "Wine is installed: $WINE_VERSION"
    else
        warn_test "Wine is not installed - app will attempt to install it on first run"
        if [ "$TEST_MODE" == "quick" ]; then
            echo "Skipping first-run test in quick mode (would install Wine)"
        fi
    fi
else
    pass_test "Not on macOS, skipping Wine check"
fi

# Test 6: Launch app in background (only in full mode or if Wine already installed)
if [ "$TEST_MODE" == "full" ] || command -v wine &> /dev/null; then
    echo ""
    echo "Test 6: Testing first-run setup..."

    # Run the app's setup script directly
    cd "$APP_BUNDLE/Contents/Resources"
    APP_RESOURCES="$(pwd)"

    # Export environment for run.sh
    export USER_DATA_DIR

    # Run just the setup portion of run.sh
    if [ ! -f "$USER_DATA_DIR/venv/bin/python" ]; then
        echo "Running first-time setup..."

        # Create virtual environment
        python3 -m venv "$USER_DATA_DIR/venv"
        if [ $? -ne 0 ]; then
            fail_test "Failed to create virtual environment"
        fi
        pass_test "Created virtual environment"

        # Install dependencies
        "$USER_DATA_DIR/venv/bin/python" -m pip install -q streamlit pandas plotly
        if [ $? -ne 0 ]; then
            fail_test "Failed to install dependencies"
        fi
        pass_test "Installed dependencies"

        # Copy app files
        cp -r "$APP_RESOURCES/aalm_original" "$USER_DATA_DIR/"
        cp -r "$APP_RESOURCES/.streamlit" "$USER_DATA_DIR/"
        cp -r "$APP_RESOURCES/templates" "$USER_DATA_DIR/"
        cp "$APP_RESOURCES/app.py" "$USER_DATA_DIR/"
        cp "$APP_RESOURCES/fortran_input_generator.py" "$USER_DATA_DIR/"
        pass_test "Copied app files to user directory"
    fi
else
    echo ""
    echo "Test 6: Skipping first-run setup test (use './test_app.sh full' for full test)"
fi

# Test 7: Check user data directory structure
echo ""
echo "Test 7: Checking user data directory structure..."
if [ -d "$USER_DATA_DIR" ]; then
    EXPECTED_ITEMS=(
        "venv"
        "app.py"
        "fortran_input_generator.py"
        "templates/LeggettInput_Golden.txt"
        "aalm_original/AALM_64.exe"
    )

    for item in "${EXPECTED_ITEMS[@]}"; do
        if [ -e "$USER_DATA_DIR/$item" ]; then
            pass_test "Found $item in user directory"
        else
            if [ "$TEST_MODE" == "full" ]; then
                fail_test "Missing $item in user directory"
            else
                warn_test "Missing $item (expected in quick mode without first-run)"
            fi
        fi
    done
fi

# Test 8: Verify Wine is in PATH
if [ "$TEST_MODE" == "full" ] || [ -d "$USER_DATA_DIR" ]; then
    echo ""
    echo "Test 8: Checking Wine PATH configuration..."

    # Simulate the PATH setup from run.sh
    if [[ $(uname -m) == "arm64" ]]; then
        TEST_PATH="/opt/homebrew/bin:$PATH"
    else
        TEST_PATH="/usr/local/bin:$PATH"
    fi

    if PATH="$TEST_PATH" command -v wine &> /dev/null; then
        pass_test "Wine is accessible in configured PATH"
    else
        if [ "$TEST_MODE" == "full" ]; then
            fail_test "Wine is not accessible in configured PATH"
        else
            warn_test "Wine check skipped in quick mode"
        fi
    fi
fi

# Test 9: Check AALM executable permissions
if [ -f "$USER_DATA_DIR/aalm_original/AALM_64.exe" ]; then
    echo ""
    echo "Test 9: Checking AALM executable permissions..."

    if [ -x "$USER_DATA_DIR/aalm_original/AALM_64.exe" ]; then
        pass_test "AALM_64.exe has execute permissions"
    else
        warn_test "AALM_64.exe does not have execute permissions (will be set on app run)"
    fi
fi

# Cleanup: Restore backup if it exists
echo ""
echo "========================================"
echo "Test Cleanup"
echo "========================================"

if [ -n "$BACKUP_DIR" ]; then
    echo "Restoring original user data..."
    rm -rf "$USER_DATA_DIR"
    mv "$BACKUP_DIR" "$USER_DATA_DIR"
    pass_test "Restored original user data"
elif [ "$TEST_MODE" == "full" ] && [ -d "$USER_DATA_DIR" ]; then
    echo "Cleaning up test user data..."
    rm -rf "$USER_DATA_DIR"
    pass_test "Removed test user data"
fi

echo ""
echo "========================================"
echo -e "${GREEN}All tests completed!${NC}"
echo "========================================"
echo ""
echo "Test modes:"
echo "  ./test_app.sh quick  - Fast checks without first-run setup"
echo "  ./test_app.sh full   - Complete test including first-run setup"
echo ""
