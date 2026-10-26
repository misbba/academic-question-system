"""
Automated Verification Suite for One-Click Startup & Dual-Server Lifecycle
Tests:
1. Syntax & Configuration XML Validation
2. Process Launch (Backend Port 5000 + Frontend Port 8080)
3. HTTP Health Check (Backend /api/health + MySQL DB Status)
4. Frontend HTTP Server (Port 8080 / index.html)
5. CORS Header Validation (Origin: http://localhost:8080)
6. Faculty & Student Authentication via Session Cookies
7. Frontend -> Backend API Communication
8. Port Conflict Detection
9. Graceful Shutdown & Port De-allocation
"""

import sys
import os
import time
import socket
import subprocess
import xml.etree.ElementTree as ET
import urllib.request
import urllib.parse
import json
import http.cookiejar

PYTHON_EXE = r"C:\Program Files\Python313\python.exe"
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
RUN_ALL_SCRIPT = os.path.join(PROJECT_ROOT, "run_all.py")


def log(msg, success=True):
    mark = "[PASS]" if success else "[FAIL]"
    print(f" {mark} {msg}")


def is_port_listening(port, timeout=0.5):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(timeout)
        return s.connect_ex(('127.0.0.1', port)) == 0


def test_xml_configs():
    print("\n--- TEST 1: IntelliJ Run Configurations & XML Integrity ---")
    run_all_xml = os.path.join(PROJECT_ROOT, ".idea", "runConfigurations", "Academic_Question_System____Run_All.xml")
    backend_xml = os.path.join(PROJECT_ROOT, ".idea", "runConfigurations", "Academic_Question_System___Flask_Backend.xml")
    frontend_xml = os.path.join(PROJECT_ROOT, ".idea", "runConfigurations", "Academic_Question_System___Frontend.xml")

    for path in [run_all_xml, backend_xml, frontend_xml]:
        assert os.path.exists(path), f"Missing run configuration: {path}"
        tree = ET.parse(path)
        root = tree.getroot()
        assert root.tag == "component", f"Root tag must be component in {path}"

    # Verify compound configuration matches child configuration names
    tree_all = ET.parse(run_all_xml)
    cfg = tree_all.getroot().find("configuration")
    assert cfg.get("name") == "Academic Question System — Run All", f"Invalid compound name: {cfg.get('name')}"
    assert cfg.get("type") == "CompoundRunConfigurationType", "Must be CompoundRunConfigurationType"
    
    sub_tasks = [to_run.get("name") for to_run in cfg.findall("toRun")]
    assert "Academic Question System - Flask Backend" in sub_tasks, "Missing backend in compound config"
    assert "Academic Question System - Frontend" in sub_tasks, "Missing frontend in compound config"
    log("IntelliJ Run Configuration XMLs verified and structurally valid.")


def test_syntax_checks():
    print("\n--- TEST 2: Python Code Syntax Checks ---")
    files_to_check = [
        os.path.join(PROJECT_ROOT, "run_all.py"),
        os.path.join(PROJECT_ROOT, "run_frontend.py"),
        os.path.join(PROJECT_ROOT, "stop_servers.py"),
        os.path.join(PROJECT_ROOT, "backend", "app.py"),
        os.path.join(PROJECT_ROOT, "backend", "run.py"),
        os.path.join(PROJECT_ROOT, "backend", "config.py"),
    ]
    for f in files_to_check:
        res = subprocess.run([PYTHON_EXE, "-m", "py_compile", f], capture_output=True, text=True)
        assert res.returncode == 0, f"Syntax error in {f}: {res.stderr}"
    log("All Python files passed py_compile syntax verification.")


def test_lifecycle_and_api():
    print("\n--- TEST 3: Full Server Lifecycle, Health & Authentication ---")

    # Ensure ports are free before test
    assert not is_port_listening(5000), "Port 5000 is already in use before testing!"
    assert not is_port_listening(8080), "Port 8080 is already in use before testing!"

    # Launch run_all.py
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    proc = subprocess.Popen(
        [PYTHON_EXE, RUN_ALL_SCRIPT],
        cwd=PROJECT_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        env=env
    )

    try:
        # Wait for both ports to open
        backend_up = False
        frontend_up = False
        start_t = time.time()
        while time.time() - start_t < 15:
            if not backend_up and is_port_listening(5000):
                backend_up = True
            if not frontend_up and is_port_listening(8080):
                frontend_up = True
            if backend_up and frontend_up:
                break
            time.sleep(0.5)

        assert backend_up, "Backend (Port 5000) failed to start within timeout"
        assert frontend_up, "Frontend (Port 8080) failed to start within timeout"
        log("Both Port 5000 (Backend) and Port 8080 (Frontend) are actively listening.")

        # Test Backend /api/health
        time.sleep(1)
        health_req = urllib.request.Request("http://127.0.0.1:5000/api/health")
        with urllib.request.urlopen(health_req, timeout=3) as resp:
            assert resp.status == 200, f"Health check returned status {resp.status}"
            data = json.loads(resp.read().decode('utf-8'))
            assert data.get("status") == "success"
            db_status = data.get("database", {}).get("status")
            assert db_status == "connected", f"Database is not connected: {data}"
            log("Backend /api/health responded 200 OK and MySQL is CONNECTED.")

        # Test Frontend index.html
        front_req = urllib.request.Request("http://127.0.0.1:8080/index.html")
        with urllib.request.urlopen(front_req, timeout=3) as resp:
            assert resp.status == 200, f"Frontend returned status {resp.status}"
            body = resp.read().decode('utf-8', errors='ignore')
            assert "Academic" in body, "Frontend response body missing expected title content"
            log("Frontend port 8080 returned 200 OK with valid HTML content.")

        # Test CORS headers for http://localhost:8080
        cors_req = urllib.request.Request(
            "http://127.0.0.1:5000/api/auth/status",
            headers={"Origin": "http://localhost:8080"}
        )
        with urllib.request.urlopen(cors_req, timeout=3) as resp:
            allow_origin = resp.headers.get("Access-Control-Allow-Origin")
            allow_cred = resp.headers.get("Access-Control-Allow-Credentials")
            assert allow_origin in ("http://localhost:8080", "http://127.0.0.1:8080"), f"CORS origin mismatch: {allow_origin}"
            assert allow_cred == "true", f"CORS credentials not allowed: {allow_cred}"
            log("CORS configuration properly configured for frontend origin http://localhost:8080.")

        # Test Authentication with CookieJar (Session-based)
        cookie_jar = http.cookiejar.CookieJar()
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))

        # Register a test faculty account
        ts = int(time.time())
        fac_email = f"startup.fac.{ts}@university.edu"
        reg_payload = json.dumps({
            "full_name": "Dr. Startup Verifier",
            "email": fac_email,
            "password": "Password123!",
            "role": "faculty",
            "department": "Artificial Intelligence & Data Science",
            "academic_year": "2025-2026"
        }).encode('utf-8')

        reg_req = urllib.request.Request(
            "http://127.0.0.1:5000/api/auth/register",
            data=reg_payload,
            headers={"Content-Type": "application/json"}
        )
        with opener.open(reg_req, timeout=3) as resp:
            assert resp.status in (200, 201), f"Faculty registration failed: {resp.status}"

        # Faculty Login
        login_payload = json.dumps({
            "email": fac_email,
            "password": "Password123!",
            "role": "faculty"
        }).encode('utf-8')
        login_req = urllib.request.Request(
            "http://127.0.0.1:5000/api/auth/login",
            data=login_payload,
            headers={"Content-Type": "application/json"}
        )
        with opener.open(login_req, timeout=3) as resp:
            assert resp.status == 200, f"Faculty login failed: {resp.status}"
            user_data = json.loads(resp.read().decode('utf-8'))
            assert user_data.get("status") == "success"
            log(f"Faculty login succeeded with session cookie for {fac_email}.")

        # Check /api/auth/me using authenticated session
        me_req = urllib.request.Request("http://127.0.0.1:5000/api/auth/me")
        with opener.open(me_req, timeout=3) as resp:
            assert resp.status == 200
            me_data = json.loads(resp.read().decode('utf-8'))
            assert me_data.get("user", {}).get("email") == fac_email
            log("Session-based authentication verified via /api/auth/me.")

    finally:
        print("\n--- TEST 4: Clean Termination & Port Release ---")
        # Terminate launcher
        if proc.poll() is None:
            if os.name == 'nt':
                subprocess.run(['taskkill', '/F', '/T', '/PID', str(proc.pid)],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except Exception:
                proc.kill()

        time.sleep(2)
        # Verify both ports are freed
        p5000_free = not is_port_listening(5000)
        p8080_free = not is_port_listening(8080)
        assert p5000_free, "Port 5000 remained locked after launcher termination!"
        assert p8080_free, "Port 8080 remained locked after launcher termination!"
        log("Both Port 5000 and Port 8080 were cleanly released upon stopping.")


def test_port_conflict():
    print("\n--- TEST 5: Port Conflict Detection ---")
    # Occupy port 5000 temporarily
    dummy_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    dummy_sock.bind(('127.0.0.1', 5000))
    dummy_sock.listen(1)

    try:
        # Run run_all.py - it should detect port 5000 is occupied and exit with code 1
        res = subprocess.run([PYTHON_EXE, RUN_ALL_SCRIPT], capture_output=True, text=True, timeout=5)
        assert res.returncode == 1, f"Expected returncode 1 on port conflict, got {res.returncode}"
        assert "Port 5000 is already in use" in res.stdout, f"Unexpected output: {res.stdout}"
        log("Port conflict detected cleanly; clear user notification printed without unhandled crash.")
    finally:
        dummy_sock.close()


def main():
    print("=" * 70)
    print("  ONE-CLICK RUN VERIFICATION SUITE")
    print("  Academic Question Generation and Difficulty Balancing System")
    print("=" * 70)

    test_xml_configs()
    test_syntax_checks()
    test_lifecycle_and_api()
    test_port_conflict()

    print("\n" + "=" * 70)
    print("  ALL VERIFICATION TESTS COMPLETED SUCCESSFULLY! (5/5 PASSED)")
    print("=" * 70)


if __name__ == '__main__':
    main()
