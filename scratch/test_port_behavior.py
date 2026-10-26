"""
Test Suite for Resilient Port Handling & Backend Single-Instance Workflow
"""

import sys
import os
import socket
import subprocess
import time
import urllib.request
import json

PROJECT_ROOT = r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system"
PYTHON_EXE = sys.executable


def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex(('127.0.0.1', port)) == 0


def test_conflict_detection():
    print("\n--- Test A: Foreign/Raw Socket Conflict Detection ---")
    dummy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    dummy.bind(('127.0.0.1', 5000))
    dummy.listen(1)

    try:
        res = subprocess.run(
            [PYTHON_EXE, os.path.join(PROJECT_ROOT, "backend", "app.py")],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=5
        )
        assert res.returncode == 1, f"Expected returncode 1, got {res.returncode}"
        assert "Port 5000 is already in use by another process" in res.stdout, f"Unexpected: {res.stdout}"
        print("  [PASS] Successfully detected raw socket conflict on port 5000 and exited with code 1.")
    finally:
        dummy.close()


def test_frontend_conflict_detection():
    print("\n--- Test B: Foreign/Raw Socket Conflict Detection for Frontend ---")
    dummy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    dummy.bind(('127.0.0.1', 8080))
    dummy.listen(1)

    try:
        res = subprocess.run(
            [PYTHON_EXE, os.path.join(PROJECT_ROOT, "run_frontend.py")],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=5
        )
        assert res.returncode == 1, f"Expected returncode 1, got {res.returncode}"
        assert "Port 8080 is already in use by another process" in res.stdout, f"Unexpected: {res.stdout}"
        print("  [PASS] Successfully detected raw socket conflict on port 8080 and exited with code 1.")
    finally:
        dummy.close()


def test_healthy_backend_reuse():
    print("\n--- Test C: Healthy Backend Instance Reuse ---")
    # Start real Flask backend in subprocess
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    server_proc = subprocess.Popen(
        [PYTHON_EXE, os.path.join(PROJECT_ROOT, "backend", "app.py")],
        cwd=PROJECT_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        env=env
    )

    try:
        # Wait for port 5000 to become active
        started = False
        for _ in range(20):
            if is_port_in_use(5000):
                started = True
                break
            time.sleep(0.5)
        assert started, "Backend failed to start on port 5000"

        # Now run app.py a SECOND time while the first one is healthy
        second_run = subprocess.run(
            [PYTHON_EXE, os.path.join(PROJECT_ROOT, "backend", "app.py")],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=5
        )
        print("  Second run output:\n", second_run.stdout)
        assert second_run.returncode == 0, f"Expected returncode 0 for healthy reuse, got {second_run.returncode}"
        assert "ALREADY ACTIVE" in second_run.stdout or "already active" in second_run.stdout.lower(), "Expected ALREADY ACTIVE notice"
        assert "Reusing existing healthy backend instance" in second_run.stdout, "Expected reuse notice"
        print("  [PASS] Successfully reused existing healthy backend instance without port 5000 error!")
    finally:
        # Stop first server
        subprocess.run(['taskkill', '/F', '/T', '/PID', str(server_proc.pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        server_proc.terminate()
        server_proc.wait()
        time.sleep(1)


def main():
    print("=" * 60)
    print("RUNNING PORT BEHAVIOR TESTS")
    print("=" * 60)

    test_conflict_detection()
    test_frontend_conflict_detection()
    test_healthy_backend_reuse()

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)


if __name__ == '__main__':
    main()
