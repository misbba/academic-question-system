"""
Academic Question Generation and Difficulty Balancing System
Frontend HTTP Server Launcher (run_frontend.py)

Serves the frontend static files on http://localhost:8080.
Proxies all /api/* requests directly to the Flask backend on http://127.0.0.1:5000.
Checks if port 8080 is already active and healthy before starting to avoid socket collisions.
"""

import sys
import os
import json
import socket
import urllib.request
import urllib.error
from http.server import HTTPServer, SimpleHTTPRequestHandler

PORT = 8080
BACKEND_URL = "http://127.0.0.1:5000"
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))


class FrontendProxyHandler(SimpleHTTPRequestHandler):
    """
    Serves static frontend files (HTML, JS, CSS, images) and transparently
    proxies /api/* requests to the Flask backend running on port 5000.
    """

    def proxy_to_backend(self):
        backend_target = f"{BACKEND_URL}{self.path}"
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length) if content_length > 0 else None

        req = urllib.request.Request(backend_target, data=body, method=self.command)
        for header, value in self.headers.items():
            if header.lower() not in ('host', 'content-length'):
                req.add_header(header, value)

        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                self.send_response(resp.status)
                resp_body = resp.read()
                for header, value in resp.headers.raw_items():
                    if header.lower() not in ('transfer-encoding', 'connection', 'content-length'):
                        self.send_header(header, value)
                self.send_header('Content-Length', str(len(resp_body)))
                self.end_headers()
                self.wfile.write(resp_body)
        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            err_body = e.read()
            for header, value in e.headers.raw_items():
                if header.lower() not in ('transfer-encoding', 'connection', 'content-length'):
                    self.send_header(header, value)
            self.send_header('Content-Length', str(len(err_body)))
            self.end_headers()
            self.wfile.write(err_body)
        except Exception as e:
            self.send_response(502)
            self.send_header('Content-Type', 'application/json')
            err_json = json.dumps({
                "status": "error",
                "message": f"Proxy communication error to backend: {str(e)}"
            }).encode('utf-8')
            self.send_header('Content-Length', str(len(err_json)))
            self.end_headers()
            self.wfile.write(err_json)

    def do_GET(self):
        if self.path.startswith('/api/'):
            self.proxy_to_backend()
        else:
            super().do_GET()

    def do_HEAD(self):
        if self.path.startswith('/api/'):
            self.proxy_to_backend()
        else:
            super().do_HEAD()

    def do_POST(self):
        if self.path.startswith('/api/'):
            self.proxy_to_backend()
        else:
            self.send_error(501, f"Unsupported method ({self.command})")

    def do_PUT(self):
        if self.path.startswith('/api/'):
            self.proxy_to_backend()
        else:
            self.send_error(501, f"Unsupported method ({self.command})")

    def do_DELETE(self):
        if self.path.startswith('/api/'):
            self.proxy_to_backend()
        else:
            self.send_error(501, f"Unsupported method ({self.command})")

    def do_OPTIONS(self):
        if self.path.startswith('/api/'):
            self.proxy_to_backend()
        else:
            self.send_response(200)
            self.send_header('Allow', 'GET, HEAD, POST, PUT, DELETE, OPTIONS')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With')
            self.send_header('Content-Length', '0')
            self.end_headers()


def is_port_in_use(port: int) -> bool:
    """Check if TCP port is already open."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex(('127.0.0.1', port)) == 0


def is_frontend_healthy(port: int) -> bool:
    """Check if existing server on port serves valid project HTML."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            s.connect(('127.0.0.1', port))
            s.sendall(b"GET /index.html HTTP/1.1\r\nHost: 127.0.0.1\r\nConnection: close\r\n\r\n")
            raw_resp = b""
            while True:
                chunk = s.recv(1024)
                if not chunk:
                    break
                raw_resp += chunk
                if len(raw_resp) > 4096:
                    break
            return (b"200 OK" in raw_resp or b"304" in raw_resp) and (b"Academic" in raw_resp or b"<!DOCTYPE" in raw_resp)
    except Exception:
        return False


def main():
    os.chdir(PROJECT_ROOT)

    if is_port_in_use(PORT):
        if is_frontend_healthy(PORT):
            print("=" * 65)
            print(f"  [INFO] Academic Question System Frontend is ALREADY ACTIVE on port {PORT}!")
            print(f"  [INFO] Application URL: http://localhost:{PORT}/")
            print(f"  [INFO] Landing Page:    http://localhost:{PORT}/index.html")
            print(f"  [INFO] Reusing existing frontend instance (no duplicate process needed).")
            print("=" * 65)
            sys.exit(0)
        else:
            print("=" * 65)
            print(f"[ERROR] Port {PORT} is already in use by another process!")
            print(f"Please stop the existing process running on port {PORT} before starting.")
            print(f"Tip: You can safely stop background servers by running: python stop_servers.py")
            print("=" * 65)
            sys.exit(1)

    print("=" * 65)
    print("  Academic Question System Frontend — Starting HTTP Server with Backend Proxy")
    print(f"  Server URL:    http://localhost:{PORT}/")
    print(f"  API Proxy:     http://localhost:{PORT}/api/* -> {BACKEND_URL}/api/*")
    print(f"  Landing Page:  http://localhost:{PORT}/index.html")
    print("=" * 65)

    server_address = ('0.0.0.0', PORT)
    httpd = HTTPServer(server_address, FrontendProxyHandler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping frontend server...")
        httpd.server_close()


if __name__ == '__main__':
    main()
