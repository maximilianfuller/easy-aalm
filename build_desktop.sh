#!/bin/bash
set -e

cd "$(dirname "$0")"

echo "=== Building Easy AALM Desktop App (fully bundled) ==="

# Create build venv if needed
if [ ! -d ".build-venv" ]; then
    echo "Creating build environment..."
    python3 -m venv .build-venv
fi

source .build-venv/bin/activate
pip install -q pyinstaller pywebview

# Download Wine if not already downloaded
if [ ! -d "bundled_wine/Wine Crossover.app" ]; then
    echo "Downloading Wine Crossover..."
    curl -L -o wine-crossover.tar.xz "https://github.com/Gcenx/winecx/releases/download/crossover-wine-23.7.1-1/wine-crossover-23.7.1-1-osx64.tar.xz"
    mkdir -p bundled_wine
    tar -xf wine-crossover.tar.xz -C bundled_wine
    rm wine-crossover.tar.xz
fi

# Build with PyInstaller
echo "Building app..."
pyinstaller easy_aalm.spec --clean --noconfirm 2>&1 | grep -E "(INFO: Build|ERROR|WARNING.*not found)" || true

# Create bundled Python venv
echo "Creating bundled Python environment..."
BUNDLE_VENV="dist/Easy AALM.app/Contents/Resources/venv"
rm -rf "$BUNDLE_VENV"
python3 -m venv "$BUNDLE_VENV"

echo "Installing Streamlit in bundled environment..."
"$BUNDLE_VENV/bin/pip" install -q streamlit pandas plotly openpyxl

# Copy Wine into the bundle
echo "Bundling Wine..."
cp -R "bundled_wine/Wine Crossover.app" "dist/Easy AALM.app/Contents/Resources/"

echo ""
echo "=== Build complete ==="
echo "App: dist/Easy AALM.app"
du -sh "dist/Easy AALM.app"
