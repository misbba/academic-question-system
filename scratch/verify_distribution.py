import sys
sys.path.insert(0, r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\backend")
from models.database import get_db_connection

conn = get_db_connection()
with conn.cursor() as cur:
    cur.execute("SELECT unit, marks, count(*) as count FROM questions WHERE is_in_bank = 1 GROUP BY unit, marks ORDER BY unit, marks")
    for r in cur.fetchall():
        print(f"Unit: {r['unit']} | Marks: {r['marks']}M | Count: {r['count']}")
conn.close()
