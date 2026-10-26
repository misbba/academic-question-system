import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
from models.database import get_db_connection

conn = get_db_connection()
with conn.cursor() as cur:
    print('=== Academic Resources ===')
    cur.execute("SELECT id, title, subject, department, file_name, file_path, status FROM academic_resources")
    for r in cur.fetchall():
        fp = r.get('file_path') or ''
        full_p = os.path.join(os.path.dirname(__file__), '..', 'backend', fp) if fp else ''
        exists = os.path.exists(full_p) if fp else False
        print(f"ID: {r['id']}, Title: {r['title']}, Subject: {r['subject']}, file_name: {r['file_name']}, file_path: {r['file_path']}, Exists on disk: {exists}")

    print('\n=== Question Papers ===')
    cur.execute("SELECT id, paper_code, title, subject, exam_type, total_marks, status, sections FROM question_papers")
    for r in cur.fetchall():
        has_sec = bool(r['sections'])
        sec_len = len(r['sections']) if r['sections'] else 0
        print(f"ID: {r['id']}, Code: {r['paper_code']}, Title: {r['title']}, Subject: {r['subject']}, Type: {r['exam_type']}, Total: {r['total_marks']}, Status: {r['status']}, SecLen: {sec_len}")

    print('\n=== Quizzes ===')
    cur.execute("SELECT id, quiz_code, title, subject, status, duration_minutes, total_questions FROM quizzes")
    for r in cur.fetchall():
        print(f"ID: {r['id']}, Code: {r['quiz_code']}, Title: {r['title']}, Subject: {r['subject']}, Status: {r['status']}")

conn.close()
