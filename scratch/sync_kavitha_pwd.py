import pymysql
from werkzeug.security import generate_password_hash

conn = pymysql.connect(host='localhost', user='root', password='sqlamzad@123', database='academic_question_system')
with conn.cursor() as cur:
    new_hash = generate_password_hash("Password123!")
    cur.execute("UPDATE users SET password_hash = %s WHERE id = 25", (new_hash,))
    conn.commit()
    print("Updated Kavitha (ID 25) password hash to Password123!")
conn.close()
