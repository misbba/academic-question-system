import pymysql

conn = pymysql.connect(
    host='localhost',
    user='root',
    password='sqlamzad@123',
    database='academic_question_system',
    cursorclass=pymysql.cursors.DictCursor
)

with conn.cursor() as cur:
    cur.execute("SELECT id, subject, is_in_bank, status, question_text, created_at FROM questions WHERE created_by = 25")
    rows = cur.fetchall()
    print(f"Total questions for Kavitha (25): {len(rows)}")
    for r in rows:
        print(f"ID={r['id']} | Subj={r['subject']} | Bank={r['is_in_bank']} | Status={r['status']} | Text={r['question_text'][:50]}")
