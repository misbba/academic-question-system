import sys
import os
from flask import Flask, jsonify
from flask_cors import CORS

# Ensure backend folder is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from config import Config
from models.database import DatabaseError
from werkzeug.middleware.proxy_fix import ProxyFix
from routes.health_routes import health_bp
from routes.auth_routes import auth_bp
from routes.resource_routes import resource_bp
from routes.question_routes import question_bp
from routes.question_paper_routes import question_paper_bp
from routes.quiz_routes import quiz_bp
from routes.academic_material_routes import material_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Enable proxy fix so that Flask correctly detects HTTPS scheme when behind Render/Nginx reverse proxy
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

    # Ensure upload directories exist inside configured persistent storage
    upload_res_dir = os.path.join(Config.UPLOAD_FOLDER, 'resources')
    upload_asn_dir = os.path.join(Config.UPLOAD_FOLDER, 'assignments')
    os.makedirs(upload_res_dir, exist_ok=True)
    os.makedirs(upload_asn_dir, exist_ok=True)

    # Build allowed origins for CORS (supports comma-separated values from FRONTEND_ORIGIN env var)
    allowed_origins = [
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost:5000",
        "http://127.0.0.1:5000",
        "http://localhost:63342",
        "http://127.0.0.1:63342"
    ]
    if Config.FRONTEND_ORIGIN:
        for orig in Config.FRONTEND_ORIGIN.split(','):
            cleaned = orig.strip().rstrip('/')
            if cleaned and cleaned not in allowed_origins:
                allowed_origins.append(cleaned)

    # Enable CORS for frontend origins with credentials support
    CORS(app, supports_credentials=True, resources={r"/api/*": {"origins": allowed_origins}})

    # Register Route Blueprints
    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(resource_bp)
    app.register_blueprint(question_bp)
    app.register_blueprint(question_paper_bp)
    app.register_blueprint(quiz_bp)
    app.register_blueprint(material_bp)

    # Global Error Handlers
    @app.errorhandler(404)
    def handle_not_found(e):
        return jsonify({
            "status": "error",
            "message": "Resource or API endpoint not found",
            "code": 404
        }), 404

    @app.errorhandler(500)
    def handle_server_error(e):
        return jsonify({
            "status": "error",
            "message": "Internal server error occurred",
            "code": 500
        }), 500

    @app.errorhandler(DatabaseError)
    def handle_database_error(e):
        return jsonify({
            "status": "error",
            "message": str(e),
            "code": 500
        }), 500

    return app

app = create_app()

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

    print("=" * 60)
    print(f"Academic Question System API — Starting Flask Server")
    print(f"Server URL: http://localhost:{port}/")
    print(f"Health API: http://localhost:{port}/api/health")
    print("=" * 60)
    app.run(host='0.0.0.0', port=port, debug=(Config.FLASK_ENV == 'development'))
