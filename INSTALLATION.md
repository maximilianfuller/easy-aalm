# Installation Guide

## Prerequisites

### All Platforms
- Python 3.8 or higher
- Git (optional, for cloning)

### Mac/Linux Only
- Wine (to run Windows AALM executable)

## Step-by-Step Installation

### 1. Download the Repository

**Option A: Using Git**
```bash
git clone https://github.com/[your-username]/easy-aalm.git
cd easy-aalm
```

**Option B: Download ZIP**
1. Click the green "Code" button on GitHub
2. Select "Download ZIP"
3. Extract the files to a folder
4. Open terminal/command prompt in that folder

### 2. Download AALM

Download the AALM v3.1 executable from the EPA:
https://www.epa.gov/land-research/all-ages-lead-model-aalm

Extract the downloaded files. You'll need to note the location of `AALM_64.exe`.

### 3. Configure AALM Path

Edit `app.py` and update lines 90-94 with the path to your `AALM_64.exe`:

```python
aalm_paths = [
    Path("/path/to/your/AALM_64.exe"),  # Update this
    Path("AALM_64.exe"),
]
```

**Windows Example:**
```python
aalm_paths = [
    Path("C:/Users/YourName/Downloads/aalm_v3-1-1/AALM_64.exe"),
    Path("AALM_64.exe"),
]
```

**Mac/Linux Example (with Wine):**
```python
aalm_paths = [
    Path("/Users/YourName/Downloads/aalm_v3-1-1/AALM_64.exe"),
    Path("AALM_64.exe"),
]
```

### 4. Run Setup

**Windows:**
```
Double-click setup.bat
```

**Mac/Linux:**
```bash
chmod +x setup.sh run.sh
./setup.sh
```

The setup script will:
- Create a Python virtual environment
- Install all required dependencies
- Verify Python is installed

### 5. Install Wine (Mac/Linux Only)

**Mac:**
```bash
brew install --cask wine-stable
```

**Ubuntu/Debian:**
```bash
sudo apt install wine
```

**Other Linux:**
Check your distribution's package manager for Wine installation.

## Running the Application

**Windows:**
```
Double-click run.bat
```

**Mac/Linux:**
```bash
./run.sh
```

The application will start and automatically open in your browser at `http://localhost:8501`

## Troubleshooting

### "Python not found"
- Install Python 3.8+ from python.org
- Ensure Python is added to your PATH

### "AALM_64.exe not found"
- Verify the path in app.py points to the correct location
- Ensure you downloaded AALM from the EPA website

### "Wine not found" (Mac/Linux)
- Install Wine as described in step 5
- Verify installation: `wine --version`

### "Module not found" errors
- Re-run the setup script
- Manually install: `pip install -r requirements.txt`

### Port already in use
- Close other applications using port 8501
- Or specify a different port: `streamlit run app.py --server.port 8502`

## Next Steps

Once installed, see [README.md](README.md) for usage instructions.
