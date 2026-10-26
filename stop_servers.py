"""
Academic Question Generation and Difficulty Balancing System
Safe Server Cleaner (stop_servers.py)

Safely finds and stops any leftover background Python processes on:
- Port 5000 (Flask Backend)
- Port 8080 (Frontend HTTP Server)

Leaves all unrelated processes (MySQL, IntelliJ IDEA, Chrome, etc.) completely untouched.
"""

import os
import sys
import time
import socket
import subprocess


def is_port_in_use(port: int) -> bool:
    """Check if a TCP port is currently in use on localhost."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex(('127.0.0.1', port)) == 0


def get_pid_on_port(port: int):
    """Find the Process ID (PID) listening on the specified port on Windows."""
    try:
        res = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
        for line in res.stdout.splitlines():
            line = line.strip()
            if f":{port}" in line and "LISTENING" in line:
                parts = line.split()
                if len(parts) >= 5:
                    return int(parts[-1])
    except Exception:
        pass
    return None


def get_process_name(pid: int) -> str:
    """Get the executable name for a given PID."""
    try:
        res = subprocess.run(['tasklist', '/FI', f'PID eq {pid}', '/FO', 'CSV', '/NH'], capture_output=True, text=True)
        if res.stdout:
            parts = [p.strip('"\n\r ') for p in res.stdout.strip().split('","')]
            if parts and parts[0]:
                return parts[0]
    except Exception:
        pass
    return "Unknown"


def stop_service_on_port(port: int, label: str):
    """Stop only Python processes listening on the given port."""
    if not is_port_in_use(port):
        print(f"  [OK] Port {port} ({label}): Already FREE.")
        return True

    pid = get_pid_on_port(port)
    if not pid:
        print(f"  [NOTICE] Port {port} ({label}) is in use, but could not determine PID.")
        return False

    proc_name = get_process_name(pid)
    print(f"  [DETECTED] Port {port} ({label}) is occupied by: {proc_name} (PID: {pid})")

    # Safety check: Only kill if it is a python executable
    if "python" in proc_name.lower():
        print(f"  [STOPPING] Terminating Python process tree (PID: {pid})...")
        try:
            subprocess.run(['taskkill', '/F', '/T', '/PID', str(pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            print(f"  [WARN] Failed to terminate PID {pid}: {e}")

        # Wait and verify
        time.sleep(1)
        if not is_port_in_use(port):
            print(f"  [RELEASED] Port {port} ({label}) is now FREE.")
            return True
        else:
            print(f"  [WARNING] Port {port} ({label}) still in use after termination attempt.")
            return False
    else:
        print(f"  [SKIPPED] Process '{proc_name}' is not a Python process. Leaving untouched for safety.")
        return False


def main():
    print("=" * 70)
    print("  Academic Question System — Safe Server Cleaner")
    print("=" * 70)

    p5000_ok = stop_service_on_port(5000, "Flask Backend")
    p8080_ok = stop_service_on_port(8080, "Frontend Server")

    print("-" * 70)
    if not is_port_in_use(5000) and not is_port_in_use(8080):
        print("  [SUCCESS] All project ports (5000 & 8080) are CLEAN and FREE!")
        print("  You can now start the application via IntelliJ IDEA:")
        print("    >> Select 'Academic Question System — Run All' and click the green Run button.")
    else:
        print("  [INFO] Status summary:")
        print(f"    - Port 5000 (Backend):  {'FREE' if not is_port_in_use(5000) else 'OCCUPIED'}")
        print(f"    - Port 8080 (Frontend): {'FREE' if not is_port_in_use(8080) else 'OCCUPIED'}")
    print("=" * 70)


if __name__ == '__main__':
    main()
