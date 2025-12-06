#!/bin/bash
set -e

APP_NAME="Easy AALM.app"
BUNDLE_ID="com.easyaalm.app"
DEVELOPER_ID="Developer ID Application: Maximilian Fuller (FC52693UCD)"

echo "======================================"
echo "Signing and Notarizing Easy AALM"
echo "======================================"
echo ""

# Check for required environment variables
if [ -z "$APPLE_ID" ]; then
    echo "Error: APPLE_ID environment variable not set"
    exit 1
fi

if [ -z "$APP_PASSWORD" ]; then
    echo "Error: APP_PASSWORD environment variable not set"
    exit 1
fi

# Remove existing signatures
echo "Removing existing signatures..."
codesign --remove-signature "$APP_NAME" 2>/dev/null || true

# Sign all executables and scripts inside the app
echo "Signing contents..."
find "$APP_NAME/Contents" -type f \( -name "*.sh" -o -name "*.py" -o -perm +111 \) -exec codesign --force --sign "$DEVELOPER_ID" --timestamp --options runtime {} \; 2>/dev/null || true

# Sign the app bundle
echo "Signing app bundle..."
codesign --force --sign "$DEVELOPER_ID" \
    --timestamp \
    --options runtime \
    --identifier "$BUNDLE_ID" \
    --deep \
    "$APP_NAME"

# Verify signature
echo "Verifying signature..."
codesign --verify --deep --strict --verbose=2 "$APP_NAME"

# Create ZIP for notarization
echo "Creating ZIP for notarization..."
ZIP_FILE="Easy_AALM.zip"
rm -f "$ZIP_FILE"
ditto -c -k --keepParent "$APP_NAME" "$ZIP_FILE"

# Submit for notarization
echo "Submitting for notarization..."
xcrun notarytool submit "$ZIP_FILE" \
    --apple-id "$APPLE_ID" \
    --password "$APP_PASSWORD" \
    --team-id FC52693UCD \
    --wait

# Staple the notarization ticket
echo "Stapling notarization ticket..."
xcrun stapler staple "$APP_NAME"

# Verify stapling
echo "Verifying stapling..."
xcrun stapler validate "$APP_NAME"

# Clean up
rm -f "$ZIP_FILE"

echo ""
echo "======================================"
echo "Success! App is signed and notarized"
echo "======================================"
