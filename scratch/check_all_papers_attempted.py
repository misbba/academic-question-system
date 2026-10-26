import pymysql, json, sys, os
sys.path.insert(0, r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\backend")

from services.question_paper_service import calculate_attempted_marks, validate_question_paper_structure

conn = pymysql.connect(
    host='localhost',
    user='root',
    password='sqlamzad@123',
    database='academic_question_system',
    cursorclass=pymysql.cursors.DictCursor
)
with conn.cursor() as cur:
    cur.execute("SELECT id, title, exam_type, total_marks, status, sections, created_by FROM question_papers")
    rows = cur.fetchall()
    for r in rows:
        sec = json.loads(r['sections']) if isinstance(r['sections'], str) else (r['sections'] or [])
        calc_att = calculate_attempted_marks(sec)
        valid, msg = validate_question_paper_structure(r, calc_att)
        print(f"Paper {r['id']:2d} | Faculty: {r['created_by']} | {r['status']:9s} | {r['exam_type']:25s} | DB Total: {r['total_marks']:3d} | Calc Att: {calc_att:3d} | Valid: {str(valid):5s} | Msg: {msg}")
conn.close()
