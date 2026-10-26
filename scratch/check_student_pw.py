import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
from models.database import get_db_connection
from werkzeug.security import check_password_hash

conn = get_db_connection()
with conn.cursor() as cur:
    cur.execute("SELECT id, full_name, email, password_hash, role FROM users WHERE role = 'student'")
    users = cur.fetchall()
    print('Student users count:', len(users))
    test_passwords = ['Password123!', 'Student123!', 'Password123', 'student', 'Student@123', 'nisha', '123456', 'Welcome123!']
    for u in users:
        matches = [pw for pw in test_passwords if check_password_hash(u['password_hash'], pw)]
        print(f"ID {u['id']}, Email: {u['email']}, Hash starts with: {u['password_hash'][:15]}, Matching pw: {matches}")
conn.close()
