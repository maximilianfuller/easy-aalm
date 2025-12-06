#!/bin/bash
set -e

cd "/Users/maxf/easy-aalm/dist"

SIGNING_IDENTITY="Developer ID Application: Maximilian Fuller (FC52693UCD)"

echo "Signing all Mach-O binaries in Wine..."
find "Easy AALM.app/Contents/Resources/Wine Crossover.app" -type f | while read file; do
  if file "$file" | grep -q "Mach-O"; then
    echo "Signing: $file"
    codesign --force --options runtime --timestamp --sign "$SIGNING_IDENTITY" "$file" 2>/dev/null || true
  fi
done

echo ""
echo "Signing Wine Crossover.app bundle..."
codesign --force --deep --options runtime --timestamp --sign "$SIGNING_IDENTITY" "Easy AALM.app/Contents/Resources/Wine Crossover.app"

echo ""
echo "Signing Easy AALM.app..."
codesign --force --deep --options runtime --timestamp --sign "$SIGNING_IDENTITY" "Easy AALM.app"

echo ""
echo "Verifying..."
codesign --verify --deep --strict "Easy AALM.app" && echo "SUCCESS" || echo "FAILED"
