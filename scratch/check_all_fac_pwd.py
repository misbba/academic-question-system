import pymysql
from werkzeug.security import check_password_hash

conn = pymysql.connect(host='localhost', user='root', password='sqlamzad@123', database='academic_question_system', cursorclass=pymysql.cursors.DictCursor)
with conn.cursor() as cur:
    cur.execute("SELECT id, email, full_name, password_hash FROM users WHERE role = 'faculty'")
    for u in cur.fetchall():
        for p in ["Password123!", "password", "Password123", "Admin123!", "faculty123"]:
            if check_password_hash(u['password_hash'], p):
                print(f"ID {u['id']} ({u['email']}) -> {p}")
                break
conn.close()
