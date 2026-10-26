import pymysql

conn = pymysql.connect(
    host='localhost',
    user='root',
    password='sqlamzad@123',
    database='academic_question_system',
    cursorclass=pymysql.cursors.DictCursor
)
with conn.cursor() as cur:
    cur.execute("SELECT * FROM users WHERE role = 'faculty'")
    faculties = cur.fetchall()
    for f in faculties:
        print(f"Faculty ID {f['id']}: {f.get('email')} - Keys: {list(f.keys())}")
        cur.execute("SELECT DISTINCT subject FROM questions WHERE created_by = %s", (f['id'],))
        subjs = [s['subject'] for s in cur.fetchall()]
        print(f"  Subjects in questions: {subjs}")

conn.close()
