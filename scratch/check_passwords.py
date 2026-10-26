import pymysql
from werkzeug.security import check_password_hash

conn = pymysql.connect(host='localhost', user='root', password='sqlamzad@123', database='academic_question_system', cursorclass=pymysql.cursors.DictCursor)
with conn.cursor() as cur:
    cur.execute("SELECT id, email, full_name, password_hash FROM users WHERE role = 'faculty'")
    for u in cur.fetchall():
        is_pass123 = check_password_hash(u['password_hash'], 'Password123!')
        print(u['id'], u['email'], u['full_name'], 'Password123! valid?', is_pass123)
conn.close()
