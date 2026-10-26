import sys
import os
from werkzeug.security import check_password_hash

sys.path.insert(0, os.path.abspath(r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\backend"))

from models.database import get_db_connection

conn = get_db_connection()
with conn.cursor() as cur:
    cur.execute("SELECT id, full_name, email, password_hash FROM users")
    users = cur.fetchall()
    common_passwords = ["Password123!", "password123", "Faculty@123", "Password@123", "admin123", "password", "Faculty123!"]
    for u in users:
        matched = []
        for pwd in common_passwords:
            if check_password_hash(u['password_hash'], pwd):
                matched.append(pwd)
        if matched:
            print(f"ID: {u['id']}, Email: {u['email']}, Password: {matched}")
conn.close()
