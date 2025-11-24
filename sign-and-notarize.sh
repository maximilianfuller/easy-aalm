#!/bin/bash

# Script to sign and notarize Easy AALM for macOS
# Run this on a Mac with Xcode and an Apple Developer account
#
# Usage:
#   Interactive mode:
#     ./sign-and-notarize.sh
#
#   Non-interactive mode (set environment variables):
#     export APPLE_ID="your@email.com"
#     export TEAM_ID="YOUR_TEAM_ID"
#     export APP_PASSWORD="xxxx-xxxx-xxxx-xxxx"
#     ./sign-and-notarize.sh
#
#   Or as one-liner:
#     APPLE_ID="your@email.com" TEAM_ID="YOUR_TEAM_ID" APP_PASSWORD="xxxx-xxxx-xxxx-xxxx" ./sign-and-notarize.sh

set -e

echo "========================================"
echo "Easy AALM - Code Signing & Notarization"
echo "========================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo -e "${RED}ERROR: This script must be run on macOS${NC}"
    exit 1
fi

# Check if app bundle exists
if [ ! -d "Easy AALM.app" ]; then
    echo -e "${RED}ERROR: Easy AALM.app not found in current directory${NC}"
    exit 1
fi

echo "Step 1: Finding code signing identities..."
echo ""
security find-identity -v -p codesigning
echo ""

# Auto-detect or prompt for signing identity
if [ -z "$SIGNING_IDENTITY" ]; then
    # Try to auto-detect Developer ID Application certificate
    SIGNING_IDENTITY=$(security find-identity -v -p codesigning | grep "Developer ID Application" | head -1 | sed -n 's/.*"\(.*\)"/\1/p')

    if [ -z "$SIGNING_IDENTITY" ]; then
        echo -e "${RED}ERROR: No Developer ID Application certificate found${NC}"
        echo "Please create one at https://developer.apple.com/account/resources/certificates/add"
        exit 1
    fi

    echo -e "${GREEN}Auto-detected signing identity: $SIGNING_IDENTITY${NC}"
else
    echo -e "${GREEN}Using provided signing identity: $SIGNING_IDENTITY${NC}"
fi

echo ""
echo "Step 2: Signing the app bundle..."
echo ""

# Remove extended attributes that might cause issues
xattr -cr "Easy AALM.app"

# Sign the app
codesign --deep --force --verify --verbose --sign "$SIGNING_IDENTITY" "Easy AALM.app"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ App signed successfully${NC}"
else
    echo -e "${RED}✗ Signing failed${NC}"
    exit 1
fi

# Verify signature
echo ""
echo "Verifying signature..."
codesign --verify --deep --strict --verbose=2 "Easy AALM.app"
spctl -a -t exec -vv "Easy AALM.app"

echo ""
echo "Step 3: Creating zip for notarization..."
echo ""

# Remove old zip if exists
rm -f "Easy-AALM.zip"

# Create zip
ditto -c -k --keepParent "Easy AALM.app" "Easy-AALM.zip"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Zip created successfully${NC}"
else
    echo -e "${RED}✗ Zip creation failed${NC}"
    exit 1
fi

echo ""
echo "Step 4: Submitting for notarization..."
echo ""

# Check for environment variables or prompt
if [ -z "$APPLE_ID" ] || [ -z "$TEAM_ID" ] || [ -z "$APP_PASSWORD" ]; then
    echo -e "${YELLOW}You need:${NC}"
    echo "  - Apple ID (email)"
    echo "  - App-specific password (create at appleid.apple.com)"
    echo "  - Team ID (found in your Apple Developer account)"
    echo ""
    echo -e "${YELLOW}Tip: Set environment variables to skip prompts:${NC}"
    echo "  export APPLE_ID='your@email.com'"
    echo "  export TEAM_ID='YOUR_TEAM_ID'"
    echo "  export APP_PASSWORD='xxxx-xxxx-xxxx-xxxx'"
    echo ""

    if [ -z "$APPLE_ID" ]; then
        read -p "Enter your Apple ID (email): " APPLE_ID
    fi

    if [ -z "$TEAM_ID" ]; then
        # Try to extract Team ID from signing identity
        TEAM_ID=$(echo "$SIGNING_IDENTITY" | sed -n 's/.*(\(.*\)).*/\1/p')
        if [ -z "$TEAM_ID" ]; then
            read -p "Enter your Team ID: " TEAM_ID
        else
            echo "Auto-detected Team ID from certificate: $TEAM_ID"
        fi
    fi

    if [ -z "$APP_PASSWORD" ]; then
        read -sp "Enter your app-specific password: " APP_PASSWORD
        echo ""
    fi
fi

if [ -z "$APPLE_ID" ] || [ -z "$TEAM_ID" ] || [ -z "$APP_PASSWORD" ]; then
    echo -e "${RED}ERROR: Missing required credentials${NC}"
    exit 1
fi

echo ""
echo "Using Apple ID: $APPLE_ID"
echo "Using Team ID: $TEAM_ID"

echo ""
echo "Submitting to Apple (this may take a few minutes)..."
echo ""

# Submit for notarization
xcrun notarytool submit "Easy-AALM.zip" \
    --apple-id "$APPLE_ID" \
    --password "$APP_PASSWORD" \
    --team-id "$TEAM_ID" \
    --wait

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Notarization successful${NC}"
else
    echo -e "${RED}✗ Notarization failed${NC}"
    echo "Check the logs with: xcrun notarytool log <submission-id> --apple-id $APPLE_ID --password <password> --team-id $TEAM_ID"
    exit 1
fi

echo ""
echo "Step 5: Stapling notarization ticket..."
echo ""

xcrun stapler staple "Easy AALM.app"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Notarization ticket stapled${NC}"
else
    echo -e "${RED}✗ Stapling failed${NC}"
    exit 1
fi

echo ""
echo "Step 6: Final verification..."
echo ""

spctl -a -t exec -vv "Easy AALM.app"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}SUCCESS! App is signed and notarized${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "The app can now be distributed without security warnings."
echo ""
echo "Next steps:"
echo "1. Test the app by double-clicking it"
echo "2. Commit and push to GitHub: git add 'Easy AALM.app' && git commit -m 'Add notarized Mac app' && git push"
echo ""
