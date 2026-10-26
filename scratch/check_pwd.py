import sys
import os
from werkzeug.security import check_password_hash

sys.path.insert(0, os.path.abspath(r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\backend"))

from models.database import get_db_connection

conn = get_db_connection()
with conn.cursor() as cur:
    cur.execute("SELECT id, full_name, email, password_hash FROM users WHERE email = 'kavitha@vsb.com'")
    u = cur.fetchone()
    print("User:", u)
    for pwd in ["Password123!", "password", "Password123", "admin123", "vsb123", "kavitha123"]:
        print(f"Testing '{pwd}':", check_password_hash(u['password_hash'], pwd))
conn.close()
