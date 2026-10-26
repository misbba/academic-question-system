import sys, os
sys.path.insert(0, r'C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system')
sys.path.insert(0, r'C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\backend')
from models.database import get_db_connection

conn = get_db_connection()
with conn.cursor() as cur:
    cur.execute("SELECT id, question_text, subject, unit, is_in_bank, created_by, created_at FROM questions WHERE created_by = 25")
    rows = cur.fetchall()
    print(f"Total questions for Kavitha (ID 25): {len(rows)}")
    for r in rows:
        print("  ", r['id'], r['subject'], r['unit'], r['is_in_bank'], r['question_text'][:60])
conn.close()
