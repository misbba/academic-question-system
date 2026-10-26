import pymysql

conn = pymysql.connect(
    host='localhost',
    user='root',
    password='sqlamzad@123',
    database='academic_question_system',
    cursorclass=pymysql.cursors.DictCursor
)
with conn.cursor() as cur:
    cur.execute("SELECT id, email, password_hash FROM users WHERE id IN (24, 25)")
    for r in cur.fetchall():
        print(r)
conn.close()
