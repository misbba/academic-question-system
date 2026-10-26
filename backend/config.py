import os
import urllib.parse
from pathlib import Path
from dotenv import load_dotenv

# Locate project root and load .env file
BASE_DIR = Path(__file__).resolve().parent.parent
env_path = BASE_DIR / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

class Config:
    """Application Configuration Class with Production & Cloud Database Support"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'academic_question_system_default_secret_key')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    IS_PRODUCTION = (FLASK_ENV == 'production') or bool(os.getenv('RENDER'))

    # Port binding: Render dynamically assigns PORT, fallback to FLASK_PORT or 5000
    FLASK_PORT = int(os.getenv('PORT', os.getenv('FLASK_PORT', 5000)))

    # Frontend Origin: Supports comma-separated list of origins (e.g. 'https://my-app.onrender.com,http://localhost:8080')
    FRONTEND_ORIGIN = os.getenv('FRONTEND_ORIGIN', 'http://localhost:8080')

    # Session & Cookie Configuration:
    # In production with cross-origin frontend & backend (e.g. Render Static Site -> Render Web Service),
    # modern browsers strictly require SameSite='None' and Secure=True for credentialed cookies.
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'true' if IS_PRODUCTION else 'false').lower() in ('true', '1')
    SESSION_COOKIE_SAMESITE = os.getenv('SESSION_COOKIE_SAMESITE', 'None' if IS_PRODUCTION else 'Lax')

    # Persistent File Upload Directory (Supports Render Persistent Disks mounted at /var/data or /data)
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', os.path.abspath(os.path.join(BASE_DIR, 'backend', 'uploads')))

    # MySQL Database Configuration:
    # Supports single DATABASE_URL / MYSQL_URL (common on Render / Railway / Aiven) or individual DB_* variables
    _database_url = os.getenv('DATABASE_URL') or os.getenv('MYSQL_URL')
    if _database_url:
        _parsed = urllib.parse.urlparse(_database_url)
        DB_USER = urllib.parse.unquote(_parsed.username or 'root')
        DB_PASSWORD = urllib.parse.unquote(_parsed.password or '')
        DB_HOST = _parsed.hostname or 'localhost'
        DB_PORT = _parsed.port or 3306
        DB_NAME = _parsed.path.lstrip('/') or 'academic_question_system'
    else:
        DB_HOST = os.getenv('DB_HOST', 'localhost')
        DB_PORT = int(os.getenv('DB_PORT', 3306))
        DB_NAME = os.getenv('DB_NAME', 'academic_question_system')
        DB_USER = os.getenv('DB_USER', 'root')
        DB_PASSWORD = os.getenv('DB_PASSWORD', 'root')

    # SSL Configuration for Cloud Hosted MySQL (e.g. Aiven, AWS RDS, TiDB Cloud)
    DB_SSL = os.getenv('DB_SSL', 'false').lower() in ('true', '1', 'required')
    DB_SSL_CA = os.getenv('DB_SSL_CA', None)

    @classmethod
    def get_db_config(cls, include_db_name=True):
        config = {
            'host': cls.DB_HOST,
            'port': cls.DB_PORT,
            'user': cls.DB_USER,
            'password': cls.DB_PASSWORD,
            'charset': 'utf8mb4',
            'autocommit': True
        }
        if include_db_name:
            config['database'] = cls.DB_NAME

        if cls.DB_SSL or cls.DB_SSL_CA:
            ssl_dict = {}
            if cls.DB_SSL_CA and os.path.exists(cls.DB_SSL_CA):
                ssl_dict['ca'] = cls.DB_SSL_CA
            elif cls.DB_SSL_CA:
                ssl_dict['ca'] = cls.DB_SSL_CA
            else:
                ssl_dict['check_hostname'] = False
            config['ssl'] = ssl_dict

        return config
