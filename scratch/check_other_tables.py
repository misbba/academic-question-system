import pymysql

conn = pymysql.connect(
    host='localhost',
    user='root',
    password='sqlamzad@123',
    database='academic_question_system',
    cursorclass=pymysql.cursors.DictCursor
)

with conn.cursor() as cur:
    for tbl in ['assignments', 'presentations', 'lesson_plans', 'activity_history', 'quiz_attempts']:
        cur.execute(f"DESCRIBE {tbl}")
        cols = cur.fetchall()
        cur.execute(f"SELECT count(*) as cnt FROM {tbl}")
        cnt = cur.fetchone()['cnt']
        print(f"\nTable '{tbl}' (count={cnt}):")
        for col in cols:
            print(f"  {col['Field']} ({col['Type']})")
