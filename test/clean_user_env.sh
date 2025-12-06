#!/bin/bash

echo "========================================"
echo "Easy AALM - Clean User Environment"
echo "========================================"
echo ""
echo "This script will remove ALL Easy AALM user data to"
echo "simulate a completely fresh installation by a new user."
echo ""
echo "This will delete:"
echo "  - ~/Library/Application Support/Easy AALM/"
echo "  - All virtual environments, installed dependencies, etc."
echo ""
echo "The app bundle itself will NOT be modified."
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

USER_DATA_DIR="$HOME/Library/Application Support/Easy AALM"

# Check if user data exists
if [ ! -d "$USER_DATA_DIR" ]; then
    echo -e "${YELLOW}No user data found at:${NC}"
    echo "  $USER_DATA_DIR"
    echo ""
    echo "Nothing to clean!"
    exit 0
fi

# Show what will be deleted
echo "The following will be deleted:"
echo "  $USER_DATA_DIR/"
if [ -d "$USER_DATA_DIR" ]; then
    echo ""
    echo "Contents:"
    ls -lh "$USER_DATA_DIR" | tail -n +2
fi
echo ""

# Confirm deletion
read -p "Are you sure you want to delete all user data? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo ""
    echo "Cancelled. No changes made."
    exit 0
fi

# Kill any running Streamlit processes
echo ""
echo "Stopping any running Easy AALM processes..."
pkill -f "streamlit.*app.py" 2>/dev/null || true
sleep 1

# Remove user data directory
echo "Removing user data directory..."
rm -rf "$USER_DATA_DIR"

if [ ! -d "$USER_DATA_DIR" ]; then
    echo ""
    echo -e "${GREEN}✓ Successfully cleaned user environment!${NC}"
    echo ""
    echo "Your environment is now clean."
    echo "Next time you launch Easy AALM, it will:"
    echo "  1. Create a fresh virtual environment"
    echo "  2. Install all dependencies"
    echo "  3. Install Wine (if not already installed)"
    echo "  4. Copy all app files"
    echo ""
    echo "This simulates a first-time user installation."
else
    echo ""
    echo -e "${RED}✗ Failed to remove user data directory${NC}"
    echo "You may need to remove it manually:"
    echo "  rm -rf \"$USER_DATA_DIR\""
    exit 1
fi
