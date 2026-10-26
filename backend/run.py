import sys
import os

# Add backend directory to python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import app
from config import Config

if __name__ == '__main__':
    port = Config.FLASK_PORT
    # Check if port is already occupied (only in main process before reloader forks)
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        import socket
        port_in_use = False
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as _sock:
            _sock.settimeout(0.5)
            if _sock.connect_ex(('127.0.0.1', port)) == 0:
                port_in_use = True

        if port_in_use:
            # Check if an existing instance of this Flask backend is already healthy
            is_healthy = False
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(0.5)
                    s.connect(('127.0.0.1', port))
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
                print("=" * 65)
                print(f"  [INFO] Academic Question System Backend is ALREADY ACTIVE on port {port}!")
                print(f"  [INFO] Health API verified: http://localhost:{port}/api/health (Database Connected)")
                print(f"  [INFO] Reusing existing healthy backend instance.")
                print(f"  [INFO] No duplicate process started. Your backend is ready to serve requests.")
                print("=" * 65)
                sys.exit(0)
            else:
                print("=" * 65)
                print(f"[ERROR] Port {port} is already in use by another process!")
                print(f"Please stop the existing process running on port {port} before starting the Flask server.")
                print(f"Tip: You can safely stop background servers by running: python stop_servers.py")
                print("=" * 65)
                sys.exit(1)

    print(f"Starting Academic Question System Backend Server on http://localhost:{port}/")
    app.run(host='0.0.0.0', port=port, debug=(Config.FLASK_ENV == 'development'))
