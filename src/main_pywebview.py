"""
Easy AALM - PyWebview Desktop Application
Bundles Python, Streamlit, and Wine for a fully self-contained app.
"""

import webview
import subprocess
import sys
import os
import time
import socket
import platform
from pathlib import Path
from multiprocessing import freeze_support

_streamlit_process = None


def get_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]


def get_app_dir():
    if getattr(sys, 'frozen', False):
        if platform.system() == 'Darwin':
            bundle_dir = Path(sys.executable).parent.parent / 'Resources'
            if bundle_dir.exists():
                return bundle_dir
        # On Windows, PyInstaller 6.x puts files in _internal subdirectory
        exe_dir = Path(sys.executable).parent
        internal_dir = exe_dir / '_internal'
        if internal_dir.exists() and (internal_dir / 'app.py').exists():
            return internal_dir
        # Fallback: check if app.py is next to executable
        if (exe_dir / 'app.py').exists():
            return exe_dir
        # Last resort: return _internal if it exists
        if internal_dir.exists():
            return internal_dir
        return exe_dir
    return Path(__file__).parent


def get_bundled_wine():
    """Get path to bundled Wine."""
    app_dir = get_app_dir()
    bundled = app_dir / 'Wine Crossover.app' / 'Contents' / 'Resources' / 'wine' / 'bin' / 'wine'
    if bundled.exists():
        return str(bundled)
    return None


def wait_for_server(port, timeout=60):
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.socket() as s:
                s.settimeout(1)
                if s.connect_ex(('127.0.0.1', port)) == 0:
                    return True
        except:
            pass
        time.sleep(0.5)
    return False


def find_venv_python(app_dir):
    """Find Python in bundled venv."""
    if platform.system() == 'Windows':
        # On Windows with standalone Python, python.exe is directly in venv/
        # Try standalone Python first (python.exe in root)
        venv_python = app_dir / 'venv' / 'python.exe'
        if not venv_python.exists():
            venv_python = app_dir.parent / 'venv' / 'python.exe'
        # Fallback to traditional venv layout (Scripts/python.exe)
        if not venv_python.exists():
            venv_python = app_dir / 'venv' / 'Scripts' / 'python.exe'
        if not venv_python.exists():
            venv_python = app_dir.parent / 'venv' / 'Scripts' / 'python.exe'
    else:
        venv_python = app_dir / 'venv' / 'bin' / 'python'
    if venv_python.exists():
        return str(venv_python)
    # Fallback to system Python
    if platform.system() == 'Windows':
        return 'python'
    for p in ['/opt/homebrew/bin/python3', '/usr/local/bin/python3', '/usr/bin/python3']:
        if os.path.isfile(p):
            return p
    return 'python3'


def start_streamlit(port, app_dir):
    global _streamlit_process

    app_py = app_dir / 'app.py'
    if not app_py.exists():
        return f"app.py not found"

    python_exe = find_venv_python(app_dir)

    env = os.environ.copy()
    env['STREAMLIT_SERVER_PORT'] = str(port)
    env['STREAMLIT_SERVER_HEADLESS'] = 'true'
    env['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'

    # Use a temp directory for Wine prefix (app bundle is read-only on macOS)
    import tempfile
    wine_temp = Path(tempfile.gettempdir()) / 'easy-aalm-wine'
    wine_temp.mkdir(exist_ok=True)

    # Wine-specific settings to prevent user folder access and GUI dialogs
    env['WINEPREFIX'] = str(wine_temp)
    env['WINEDLLOVERRIDES'] = 'winemenubuilder.exe=d;mscoree=d;mshtml=d'
    env['WINEDEBUG'] = '-all'
    env['DISPLAY'] = ''  # Disable X11 GUI dialogs

    # Add bundled Wine to PATH if available
    bundled_wine = get_bundled_wine()
    if bundled_wine:
        wine_bin_dir = str(Path(bundled_wine).parent)
        env['PATH'] = wine_bin_dir + ':' + env.get('PATH', '')

    try:
        _streamlit_process = subprocess.Popen(
            [python_exe, '-m', 'streamlit', 'run', str(app_py),
             '--server.port', str(port),
             '--server.headless', 'true',
             '--server.address', '127.0.0.1'],
            cwd=str(app_dir),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return None
    except Exception as e:
        return str(e)


def cleanup():
    global _streamlit_process
    if _streamlit_process:
        _streamlit_process.terminate()
        try:
            _streamlit_process.wait(timeout=3)
        except:
            _streamlit_process.kill()
        _streamlit_process = None


LOADING_HTML = """
<!DOCTYPE html>
<html>
<head><style>
body { font-family: -apple-system, SF Pro Text, sans-serif; background: linear-gradient(135deg, #667eea, #764ba2);
       height: 100vh; margin: 0; display: flex; align-items: center; justify-content: center; color: white; }
h1 { font-size: 2.5em; margin-bottom: 10px; }
#status { font-size: 14px; opacity: 0.9; margin-top: 20px; }
#log { font-family: SF Mono, monospace; font-size: 12px; text-align: left; background: rgba(0,0,0,0.2);
       padding: 15px; border-radius: 8px; margin-top: 20px; max-width: 500px; min-height: 60px; }
</style></head>
<body><div style="text-align:center">
<h1>Easy AALM</h1>
<p>Lead Exposure Calculator</p>
<div id="status">Initializing...</div>
<div id="log"></div>
</div></body></html>
"""


def main():
    freeze_support()

    app_dir = get_app_dir()
    port = get_free_port()

    win = webview.create_window('Easy AALM', html=LOADING_HTML, width=1400, height=900, min_size=(1000, 700), text_select=True)

    def log(msg):
        """Update the loading screen with a log message."""
        escaped = msg.replace("'", "\\'").replace("\n", "\\n")
        win.evaluate_js(f"document.getElementById('log').innerHTML += '{escaped}<br>';")

    def status(msg):
        """Update the status message."""
        escaped = msg.replace("'", "\\'")
        win.evaluate_js(f"document.getElementById('status').innerText = '{escaped}';")

    def start_backend():
        time.sleep(0.5)  # Wait for window to be ready

        log(f"App directory: {app_dir}")

        # Check if app.py exists
        app_py = app_dir / 'app.py'
        log(f"app.py exists: {app_py.exists()}")

        status("Finding Python environment...")
        python_exe = find_venv_python(app_dir)
        log(f"Python: {python_exe}")
        log(f"Python exists: {Path(python_exe).exists()}")

        # Test if Python can run
        try:
            test_result = subprocess.run(
                [python_exe, '-c', 'import sys; print(sys.version)'],
                capture_output=True, text=True, timeout=10
            )
            if test_result.returncode == 0:
                log(f"Python version: {test_result.stdout.strip()[:50]}")
            else:
                log(f"Python error: {test_result.stderr[:100]}")
        except Exception as e:
            log(f"Python test failed: {str(e)[:50]}")

        status("Starting Streamlit server...")
        err = start_streamlit(port, app_dir)
        if err:
            status("Error starting Streamlit")
            log(f"Error: {err}")
            return

        log(f"Streamlit starting on port {port}")
        status("Waiting for server to be ready...")

        start_time = time.time()
        last_check = 0
        while time.time() - start_time < 60:
            try:
                with socket.socket() as s:
                    s.settimeout(1)
                    if s.connect_ex(('127.0.0.1', port)) == 0:
                        log("Server is ready!")
                        status("Loading application...")
                        time.sleep(0.3)
                        win.load_url(f'http://127.0.0.1:{port}')
                        return
            except:
                pass

            elapsed = int(time.time() - start_time)
            status(f"Waiting for server... ({elapsed}s)")

            # Check process status every 5 seconds
            if elapsed - last_check >= 5:
                last_check = elapsed
                if _streamlit_process:
                    poll = _streamlit_process.poll()
                    if poll is not None:
                        log(f"Process exited with code {poll}")
                        # Try to get error output
                        try:
                            stderr = _streamlit_process.stderr.read()
                            if stderr:
                                log(f"Error: {stderr[:200]}")
                        except:
                            pass
                        return

            time.sleep(0.5)

        status("Timeout waiting for server")
        log("Server did not start within 60 seconds")

    import threading
    threading.Thread(target=start_backend, daemon=True).start()

    win.events.closing += lambda: cleanup() or True

    webview.start()
    cleanup()


if __name__ == '__main__':
    main()
