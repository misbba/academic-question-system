import sys
import os

sys.path.insert(0, os.path.abspath(r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\backend"))

from models.database import get_db_connection
from werkzeug.security import check_password_hash

conn = get_db_connection()
with conn.cursor() as cur:
    cur.execute("SELECT id, full_name, email, password_hash FROM users WHERE id = 25")
    u = cur.fetchone()
    print("User 25:", u['full_name'], u['email'])
    for pwd in ["Password123!", "kavitha123", "password", "Admin123!", "kavitha@123", "Password@123"]:
        if check_password_hash(u['password_hash'], pwd):
            print("Found password:", pwd)
            break
conn.close()
