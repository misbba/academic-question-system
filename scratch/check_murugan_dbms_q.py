import pymysql

conn = pymysql.connect(
    host='localhost',
    user='root',
    password='sqlamzad@123',
    database='academic_question_system',
    cursorclass=pymysql.cursors.DictCursor
)
with conn.cursor() as cur:
    cur.execute("SELECT id, question_text, marks, unit, topic, bloom_level FROM questions WHERE created_by = 24 AND subject = 'Database Management Systems'")
    rows = cur.fetchall()
    print(f"Total DBMS questions for Faculty 24: {len(rows)}")
    for r in rows:
        print(f"  ID {r['id']:3d} | {r['marks']:2d}M | {r['unit']} | {r['bloom_level']} | {r['question_text'][:50]}")

conn.close()
