import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
from models.database import get_db_connection

conn = get_db_connection()
with conn.cursor() as cur:
    cur.execute("SELECT DISTINCT status FROM academic_resources")
    print("Distinct statuses in academic_resources:", [r['status'] for r in cur.fetchall()])
    cur.execute("SELECT id, title, subject, status, created_by, file_name, file_path FROM academic_resources LIMIT 10")
    for r in cur.fetchall():
        print(r)
conn.close()
