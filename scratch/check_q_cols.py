import sys
import os

sys.path.insert(0, os.path.abspath(r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\backend"))

from models.database import get_db_connection

conn = get_db_connection()
with conn.cursor() as cur:
    cur.execute("DESCRIBE questions")
    cols = cur.fetchall()
    for c in cols:
        print(c['Field'], c['Type'])
conn.close()
