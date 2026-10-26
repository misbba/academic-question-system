import os
import sys
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
from models.database import get_db_connection

conn = get_db_connection()
with conn.cursor() as cur:
    cur.execute("SELECT sections FROM question_papers WHERE id = 28")
    sec_data = json.loads(cur.fetchone()['sections'])
    print(json.dumps(sec_data[1]['either_or_groups'][0], indent=2))
conn.close()
