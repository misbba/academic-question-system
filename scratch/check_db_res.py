import sys, os
sys.path.insert(0, r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system")
from backend.db import get_db_connection
import pymysql.cursors

conn = get_db_connection()
with conn.cursor() as cur:
    cur.execute("SELECT id, title, subject, file_name, file_path, file_size FROM resources")
    rows = cur.fetchall()
    for r in rows:
        print(r)
conn.close()
