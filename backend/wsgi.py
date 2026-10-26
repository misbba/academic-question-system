import os
import sys

# Ensure backend directory is in python module search path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import app

if __name__ == "__main__":
    from config import Config
    port = Config.FLASK_PORT
    app.run(host="0.0.0.0", port=port)
