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
        return Path(sys.executable).parent
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
        venv_python = app_dir / 'venv' / 'Scripts' / 'python.exe'
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
body { font-family: -apple-system, sans-serif; background: linear-gradient(135deg, #667eea, #764ba2);
       height: 100vh; margin: 0; display: flex; align-items: center; justify-content: center; color: white; }
.spinner { width: 50px; height: 50px; border: 4px solid rgba(255,255,255,0.3); border-top-color: white;
           border-radius: 50%; animation: spin 1s linear infinite; margin: 30px auto; }
@keyframes spin { to { transform: rotate(360deg); } }
h1 { font-size: 2.5em; margin-bottom: 10px; }
</style></head>
<body><div style="text-align:center">
<h1>Easy AALM</h1><p>Lead Exposure Calculator</p><div class="spinner"></div><p>Starting...</p>
</div></body></html>
"""


def main():
    freeze_support()

    app_dir = get_app_dir()
    port = get_free_port()

    win = webview.create_window('Easy AALM', html=LOADING_HTML, width=1400, height=900, min_size=(1000, 700))

    def enable_text_selection():
        """Enable text selection in the webview."""
        css = """
        * { -webkit-user-select: text !important; user-select: text !important; }
        """
        win.evaluate_js(f"var style = document.createElement('style'); style.textContent = `{css}`; document.head.appendChild(style);")

    def start_backend():
        err = start_streamlit(port, app_dir)
        if err:
            win.load_html(f"<html><body style='padding:40px;font-family:sans-serif;'><h1>Error</h1><p>{err}</p></body></html>")
            return
        if wait_for_server(port):
            time.sleep(0.5)
            win.load_url(f'http://127.0.0.1:{port}')
            time.sleep(1)
            enable_text_selection()
        else:
            win.load_html("<html><body style='padding:40px;font-family:sans-serif;'><h1>Timeout</h1><p>Could not start.</p></body></html>")

    import threading
    threading.Thread(target=start_backend, daemon=True).start()

    win.events.closing += lambda: cleanup() or True

    webview.start()
    cleanup()


if __name__ == '__main__':
    main()
