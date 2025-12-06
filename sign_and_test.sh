#!/bin/bash
set -e

cd /Users/maxf/easy-aalm/dist

SIGNING_IDENTITY="Developer ID Application: Maximilian Fuller (FC52693UCD)"

echo "Removing extended attributes..."
xattr -cr "Easy AALM.app"

echo "Signing all Mach-O binaries..."
find "Easy AALM.app" -type f | while read file; do
  if file "$file" 2>/dev/null | grep -q "Mach-O"; then
    echo "  $file"
    codesign --force --options runtime --timestamp --sign "$SIGNING_IDENTITY" "$file" 2>/dev/null || true
  fi
done

echo ""
echo "Signing Wine Crossover.app..."
codesign --force --deep --options runtime --timestamp --sign "$SIGNING_IDENTITY" "Easy AALM.app/Contents/Resources/Wine Crossover.app" 2>/dev/null || true

echo ""
echo "Signing Easy AALM.app..."
codesign --force --deep --options runtime --timestamp --sign "$SIGNING_IDENTITY" "Easy AALM.app"

echo ""
echo "Verifying..."
if codesign --verify --deep --strict "Easy AALM.app" 2>&1; then
  echo "SUCCESS - App is properly signed!"
  echo ""
  echo "Opening app..."
  open "Easy AALM.app"
else
  echo "FAILED - Signature verification failed"
  codesign --verify --deep --strict -vvv "Easy AALM.app" 2>&1 | tail -20
fi
