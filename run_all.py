"""
Academic Question Generation and Difficulty Balancing System
Unified One-Click Process Launcher

Starts both:
1. Flask Backend REST API (http://localhost:5000)
2. Frontend HTTP Server   (http://localhost:8080)

Maintains both processes, streams logs with prefixes, verifies startup health,
and cleanly terminates both child processes upon exit.
"""

import sys
import os
import time
import socket
import signal
import subprocess
import threading
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
BACKEND_SCRIPT = PROJECT_ROOT / "backend" / "app.py"

BACKEND_PORT = 5000
FRONTEND_PORT = 8080

backend_proc = None
frontend_proc = None
is_shutting_down = False


def is_port_in_use(port: int) -> bool:
    """Check if a TCP port is currently in use on localhost."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex(('127.0.0.1', port)) == 0


def terminate_process(proc, name="Process"):
    """Safely terminate a subprocess and its child process tree."""
    if proc is None:
        return
    if proc.poll() is not None:
        return

    try:
        if os.name == 'nt':
            # On Windows, taskkill /F /T ensures the entire process tree is terminated
            subprocess.run(
                ['taskkill', '/F', '/T', '/PID', str(proc.pid)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False
            )
        else:
            proc.terminate()
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                proc.kill()
    except Exception:
        try:
            proc.kill()
        except Exception:
            pass


def shutdown(signum=None, frame=None):
    """Graceful shutdown handler for both processes."""
    global is_shutting_down, backend_proc, frontend_proc
    if is_shutting_down:
        return
    is_shutting_down = True

    print("\n" + "=" * 70)
    print("Academic Question System — Stopping all servers...")
    print("=" * 70)

    terminate_process(frontend_proc, "Frontend")
    terminate_process(backend_proc, "Backend")

    print("[SHUTDOWN] Both Frontend and Backend servers have been stopped cleanly.")
    sys.exit(0)


def stream_logs(proc, prefix: str):
    """Read lines from process stdout and print with prefix."""
    try:
        for line in iter(proc.stdout.readline, ''):
            if not line:
                break
            line_str = line.rstrip()
            if line_str:
                print(f"[{prefix}] {line_str}", flush=True)
    except Exception:
        pass


def verify_services(timeout_sec=12):
    """Probe both backend and frontend ports to verify readiness."""
    start_time = time.time()
    backend_ready = False
    frontend_ready = False

    while time.time() - start_time < timeout_sec:
        if not backend_ready:
            try:
                req = urllib.request.Request("http://127.0.0.1:5000/api/health")
                with urllib.request.urlopen(req, timeout=1) as resp:
                    if resp.status == 200:
                        backend_ready = True
            except Exception:
                pass

        if not frontend_ready:
            try:
                req = urllib.request.Request("http://127.0.0.1:8080/index.html")
                with urllib.request.urlopen(req, timeout=1) as resp:
                    if resp.status in (200, 304):
                        frontend_ready = True
            except Exception:
                pass

        if backend_ready and frontend_ready:
            return True, True

        time.sleep(0.4)

    return backend_ready, frontend_ready


def main():
    global backend_proc, frontend_proc

    # Register termination signals
    signal.signal(signal.SIGINT, shutdown)
    if hasattr(signal, 'SIGTERM'):
        signal.signal(signal.SIGTERM, shutdown)

    print("=" * 70)
    print("  Academic Question Generation & Difficulty Balancing System")
    print("  Starting Full Stack Application (Backend + Frontend)")
    print("=" * 70)

    # 1. Check if ports are already occupied
    port_conflict = False
    start_backend = True
    start_frontend = True

    if is_port_in_use(BACKEND_PORT):
        # Check if it's already a healthy instance of our backend
        is_healthy = False
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.5)
                s.connect(('127.0.0.1', BACKEND_PORT))
                s.sendall(b"GET /api/health HTTP/1.1\r\nHost: 127.0.0.1\r\nConnection: close\r\n\r\n")
                raw_resp = b""
                while True:
                    chunk = s.recv(1024)
                    if not chunk:
                        break
                    raw_resp += chunk
                    if len(raw_resp) > 4096:
                        break
                if b"Academic Question System" in raw_resp:
                    is_healthy = True
        except Exception:
            pass

        if is_healthy:
            print(f"[INFO] Backend on port {BACKEND_PORT} is ALREADY ACTIVE and healthy. Reusing existing instance.")
            start_backend = False
        else:
            print(f"[ERROR] Port {BACKEND_PORT} is already in use by another process!")
            print(f"        Please stop the application using port {BACKEND_PORT} before starting.")
            print(f"        Tip: Run 'python stop_servers.py' to release occupied ports.")
            port_conflict = True

    if is_port_in_use(FRONTEND_PORT):
        # Check if frontend is already responding
        is_frontend_up = False
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.5)
                s.connect(('127.0.0.1', FRONTEND_PORT))
                s.sendall(b"GET /index.html HTTP/1.1\r\nHost: 127.0.0.1\r\nConnection: close\r\n\r\n")
                raw_resp = b""
                while True:
                    chunk = s.recv(1024)
                    if not chunk:
                        break
                    raw_resp += chunk
                    if len(raw_resp) > 4096:
                        break
                if (b"200 OK" in raw_resp or b"304" in raw_resp) and (b"Academic" in raw_resp or b"<!DOCTYPE" in raw_resp):
                    is_frontend_up = True
        except Exception:
            pass

        if is_frontend_up:
            print(f"[INFO] Frontend on port {FRONTEND_PORT} is ALREADY ACTIVE. Reusing existing instance.")
            start_frontend = False
        else:
            print(f"[ERROR] Port {FRONTEND_PORT} is already in use by another process!")
            print(f"        Please stop the application using port {FRONTEND_PORT} before starting.")
            print(f"        Tip: Run 'python stop_servers.py' to release occupied ports.")
            port_conflict = True

    if port_conflict:
        print("=" * 70)
        sys.exit(1)

    # 2. Environment for unbuffered output
    child_env = os.environ.copy()
    child_env["PYTHONUNBUFFERED"] = "1"

    # 3. Start Flask Backend if not already running
    if start_backend:
        print("[LAUNCH] Starting Flask Backend on http://localhost:5000 ...")
        backend_proc = subprocess.Popen(
            [sys.executable, str(BACKEND_SCRIPT)],
            cwd=str(PROJECT_ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            env=child_env
        )
        t_backend = threading.Thread(target=stream_logs, args=(backend_proc, "BACKEND"), daemon=True)
        t_backend.start()
    else:
        print("[LAUNCH] Backend port 5000 is already running; skipping launch to avoid duplicate process.")

    # 4. Start Frontend Server if not already running
    if start_frontend:
        print("[LAUNCH] Starting Frontend HTTP Server with API Proxy on http://localhost:8080 ...")
        frontend_proc = subprocess.Popen(
            [sys.executable, str(PROJECT_ROOT / "run_frontend.py")],
            cwd=str(PROJECT_ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            env=child_env
        )
        t_frontend = threading.Thread(target=stream_logs, args=(frontend_proc, "FRONTEND"), daemon=True)
        t_frontend.start()
    else:
        print("[LAUNCH] Frontend port 8080 is already running; skipping launch to avoid duplicate process.")

    # 5. Verify readiness
    b_ok, f_ok = verify_services(timeout_sec=10)

    print("=" * 70)
    if b_ok and f_ok:
        print(" [SUCCESS] Academic Question System is LIVE and READY!")
        print(" --------------------------------------------------------------------")
        print("   >> Main Application URL: http://localhost:8080/")
        print("   >> Landing Page:        http://localhost:8080/index.html")
        print("   >> Faculty Login:       http://localhost:8080/faculty-login.html")
        print("   >> Student Login:       http://localhost:8080/student-login.html")
        print("   >> Backend Health API:  http://localhost:5000/api/health")
        print(" --------------------------------------------------------------------")
        print("  Press IntelliJ's Red Stop button (or Ctrl+C) to terminate both servers.")
    else:
        print(" [NOTICE] Services launched. Checking status:")
        print(f"   Backend  (Port 5000): {'ONLINE' if b_ok else 'INITIALIZING / CHECK LOGS'}")
        print(f"   Frontend (Port 8080): {'ONLINE' if f_ok else 'INITIALIZING / CHECK LOGS'}")
    print("=" * 70)

    # 6. Keep launcher process alive while monitoring children
    try:
        while True:
            time.sleep(1)
            b_code = backend_proc.poll() if backend_proc else None
            f_code = frontend_proc.poll() if frontend_proc else None

            if backend_proc and b_code is not None:
                print(f"\n[ALERT] Backend process terminated unexpectedly (exit code: {b_code}).")
                shutdown()
            if frontend_proc and f_code is not None:
                print(f"\n[ALERT] Frontend process terminated unexpectedly (exit code: {f_code}).")
                shutdown()
    except KeyboardInterrupt:
        shutdown()


if __name__ == '__main__':
    main()
