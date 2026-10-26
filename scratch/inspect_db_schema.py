import sys, os
sys.path.insert(0, r'C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system')
sys.path.insert(0, r'C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\backend')
from models.database import get_db_connection

conn = get_db_connection()
with conn.cursor() as cur:
    cur.execute("SHOW TABLES")
    tables = [list(r.values())[0] if isinstance(r, dict) else r[0] for r in cur.fetchall()]
    for t in tables:
        print(f"\n=== Table: {t} ===")
        cur.execute(f"DESCRIBE {t}")
        cols = cur.fetchall()
        for c in cols:
            print("  ", c)

    print("\n=== USERS ===")
    cur.execute("SELECT * FROM users")
    users = cur.fetchall()
    for u in users:
        # Don't print full password hash for security, just preview
        if 'password_hash' in u:
            u['password_hash'] = u['password_hash'][:15] + '...'
        print(u)

conn.close()
