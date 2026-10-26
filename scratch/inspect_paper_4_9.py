import pymysql, json

conn = pymysql.connect(
    host='localhost',
    user='root',
    password='sqlamzad@123',
    database='academic_question_system',
    cursorclass=pymysql.cursors.DictCursor
)
with conn.cursor() as cur:
    cur.execute("SELECT id, title, exam_type, total_marks, sections, question_ids FROM question_papers WHERE id IN (4, 9)")
    rows = cur.fetchall()
    for r in rows:
        print(f"\n=================== Paper {r['id']} ({r['exam_type']}) - Total Marks: {r['total_marks']} ===================")
        print("question_ids:", r['question_ids'])
        print("sections:", r['sections'])

conn.close()
