# Easy AALM - Testing Guide

This guide explains how to test Easy AALM to ensure it works reliably for end users.

## Testing Scripts

We provide three testing scripts to help catch issues before distribution:

### 1. Quick Validation Test (`test_app.sh`)

Validates the app bundle structure and basic setup without running a full install.

**Usage:**
```bash
./test_app.sh quick    # Fast checks without first-run setup
./test_app.sh full     # Complete test including first-run setup
```

**What it tests:**
- App bundle exists and has required files
- Python 3 is installed
- Wine is installed (on macOS)
- Virtual environment can be created
- Dependencies can be installed
- Files are copied to user directory correctly
- Wine is in PATH

**When to use:** Quick smoke test after making changes to the app bundle structure.

### 2. Fresh Install Test (`test_fresh_install.sh`)

Simulates a complete first-time user installation from scratch.

**Usage:**
```bash
./test_fresh_install.sh
```

**What it tests:**
- Cleans user environment completely
- Runs first-time setup
- Verifies virtual environment creation
- Verifies dependency installation
- Verifies file copying
- Tests Streamlit server startup
- Checks Wine PATH configuration
- Validates UI accessibility
- Restores your original environment

**When to use:** Before releasing a new version to ensure the first-run experience works.

**Important:** This script will temporarily remove your user data but backs it up first and restores it after the test.

### 3. Clean User Environment (`clean_user_env.sh`)

Removes all Easy AALM user data to reset to a fresh state.

**Usage:**
```bash
./clean_user_env.sh
```

**What it does:**
- Removes `~/Library/Application Support/Easy AALM/`
- Stops any running Streamlit processes
- Provides confirmation before deleting

**When to use:** When you want to manually test a fresh installation without the automated test.

## Recommended Testing Workflow

### Before Every Release:

1. **Run the fresh install test:**
   ```bash
   ./test_fresh_install.sh
   ```

2. **Manual verification:**
   - After the test completes, manually launch the app
   - Test each major feature:
     - Load a preset
     - Fill in custom parameters
     - Generate input file
     - Run AALM simulation
     - View results

3. **Test on a clean environment:**
   - Use `./clean_user_env.sh` to reset
   - Double-click the app to launch it normally
   - Verify the first-run experience is smooth

### After Making Changes:

1. **Quick validation:**
   ```bash
   ./test_app.sh quick
   ```

2. **Full validation if needed:**
   ```bash
   ./test_app.sh full
   ```

## Common Issues and Solutions

### Wine Not Found Error

**Symptom:** `FileNotFoundError: [Errno 2] No such file or directory: 'wine'`

**Check:**
- Wine is installed: `which wine`
- Homebrew PATH is correct in `run.sh` (lines 164-169)
- Wine is executable: `wine --version`

**Test:** The fresh install test specifically validates Wine PATH configuration.

### Template File Not Found

**Symptom:** `Template file not found at ...`

**Check:**
- Template file exists in app bundle: `ls "Easy AALM.app/Contents/Resources/templates/"`
- Template is copied during setup: Check user directory after first run

**Test:** Both test scripts validate template file presence.

### Streamlit Won't Start

**Symptom:** App hangs or browser doesn't open

**Check:**
- Virtual environment was created: `ls "$HOME/Library/Application Support/Easy AALM/venv"`
- Dependencies were installed: Check pip list in venv
- Port 8501 is not in use: `lsof -i :8501`

**Test:** The fresh install test monitors Streamlit startup and checks HTTP response.

## Debugging Failed Tests

If a test fails, check the following:

1. **Review test output** - Failed tests show which step failed
2. **Check log files** - Fresh install test creates logs in `/tmp/easy_aalm_test_*.log`
3. **Manual inspection** - Use `clean_user_env.sh` and run the app manually
4. **Check app bundle** - Verify all required files are in the app bundle

## Continuous Testing

For ongoing development, consider:

1. Run `./test_app.sh quick` before every commit
2. Run `./test_fresh_install.sh` before every release
3. Test on different machines (Intel vs Apple Silicon)
4. Test with/without Wine pre-installed
5. Test with/without Homebrew pre-installed

## Test Coverage

What we test:
- ✓ First-time setup flow
- ✓ Virtual environment creation
- ✓ Dependency installation
- ✓ File copying and structure
- ✓ Wine installation (if needed)
- ✓ Wine PATH configuration
- ✓ Streamlit server startup
- ✓ UI accessibility

What we don't test (manual testing required):
- ✗ Actual AALM simulation execution
- ✗ Result plotting and visualization
- ✗ Excel file parsing
- ✗ Input file generation accuracy
- ✗ Multi-user scenarios
- ✗ Update/upgrade scenarios

## Notes

- All tests backup your existing user data before making changes
- Tests are designed to be non-destructive
- If a test fails, your environment will be restored
- Log files are saved for debugging even if tests pass
