import os
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
    """Application Configuration Class"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'academic_question_system_default_secret_key')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
    FRONTEND_ORIGIN = os.getenv('FRONTEND_ORIGIN', 'http://localhost:8080')

    # Session & Cookie Configuration for Local Development
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = False  # Set to True in HTTPS production environments


    # MySQL Configuration
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    DB_NAME = os.getenv('DB_NAME', 'academic_question_system')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'root')

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
        return config
