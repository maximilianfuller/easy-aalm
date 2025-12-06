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

# Make Python fully portable by copying the binary and its dependencies
echo "Making Python portable..."
# Get the real executable path (follows all symlinks)
PYTHON_REAL=$(python3 -c "import sys, os; print(os.path.realpath(sys.executable))")
# Get the framework path (parent of bin directory)
PYTHON_FRAMEWORK=$(dirname "$(dirname "$PYTHON_REAL")")

echo "  Python binary: $PYTHON_REAL"
echo "  Framework: $PYTHON_FRAMEWORK"

# Copy the actual Python binary (replacing symlink)
rm -f "$BUNDLE_VENV/bin/python3"
cp "$PYTHON_REAL" "$BUNDLE_VENV/bin/python3"

# Copy the Python3 dylib that the binary needs (expects @executable_path/../Python3)
if [ -f "$PYTHON_FRAMEWORK/Python3" ]; then
    echo "  Copying Python3 dylib..."
    cp "$PYTHON_FRAMEWORK/Python3" "$BUNDLE_VENV/"
fi

# Copy the Resources folder (contains Python.app needed by macOS Python)
if [ -d "$PYTHON_FRAMEWORK/Resources" ]; then
    echo "  Copying Resources..."
    cp -R "$PYTHON_FRAMEWORK/Resources" "$BUNDLE_VENV/"
fi

# Update pyvenv.cfg to not reference external paths
echo "home = bin" > "$BUNDLE_VENV/pyvenv.cfg"
echo "include-system-site-packages = false" >> "$BUNDLE_VENV/pyvenv.cfg"

# Create relative symlinks
cd "$BUNDLE_VENV/bin"
rm -f python python3.9 2>/dev/null || true
ln -s python3 python
ln -s python3 python3.9
cd - > /dev/null

# Copy Wine into the bundle
echo "Bundling Wine..."
cp -R "bundled_wine/Wine Crossover.app" "dist/Easy AALM.app/Contents/Resources/"

echo ""
echo "=== Build complete ==="
echo "App: dist/Easy AALM.app"
du -sh "dist/Easy AALM.app"
