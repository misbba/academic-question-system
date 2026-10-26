import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
from models.database import get_db_connection
from werkzeug.security import check_password_hash

conn = get_db_connection()
with conn.cursor() as cur:
    cur.execute("SELECT id, email, password_hash FROM users WHERE id IN (2, 4, 5, 7)")
    rows = cur.fetchall()
    common = ['Password123!', 'password123!', 'Password@123', 'password@123', 'Password123', 'password123',
              'Nisha123!', 'Nisha@123', 'nisha123', 'nisha@123', 'nisha', '12345678', '123456789',
              'Student123!', 'Student@123', 'student123', 'student', 'vsb@123', 'Vsb@123', 'Vsb123!']
    for r in rows:
        for p in common:
            if check_password_hash(r['password_hash'], p):
                print(f"FOUND MATCH for ID {r['id']} ({r['email']}): {p}")
                break
conn.close()
