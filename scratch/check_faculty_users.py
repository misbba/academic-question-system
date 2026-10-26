import sys
import os

sys.path.insert(0, os.path.abspath(r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\backend"))

from models.database import get_db_connection

conn = get_db_connection()
with conn.cursor() as cur:
    cur.execute("SELECT * FROM users WHERE role = 'faculty'")
    users = cur.fetchall()
    for u in users:
        print(f"ID: {u.get('id')}, Name: {u.get('full_name') or u.get('username')}, Email: {u.get('email')}")
conn.close()
