import pymysql

conn = pymysql.connect(
    host='localhost',
    user='root',
    password='sqlamzad@123',
    database='academic_question_system',
    cursorclass=pymysql.cursors.DictCursor
)
with conn.cursor() as cur:
    cur.execute("SELECT created_by, subject, marks, count(*) as cnt FROM questions GROUP BY created_by, subject, marks ORDER BY created_by, subject, marks")
    rows = cur.fetchall()
    for r in rows:
        print(f"Faculty: {r['created_by']:2d} | Subject: {r['subject']:30s} | Marks: {r['marks']:2d} | Count: {r['cnt']:3d}")

    print("\n--- Question Papers ---")
    cur.execute("SELECT id, title, exam_type, total_marks, status, created_by FROM question_papers")
    papers = cur.fetchall()
    for p in papers:
        print(f"Paper {p['id']:2d} | Faculty: {p['created_by']:2d} | Status: {p['status']:9s} | Exam: {p['exam_type']:25s} | Marks: {p['total_marks']:3d} | Title: {p['title']}")

conn.close()
