import os
import sys
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
from models.database import get_db_connection

conn = get_db_connection()
with conn.cursor() as cur:
    cur.execute("SELECT id, paper_code, title, sections FROM question_papers WHERE id IN (26, 28, 29)")
    for r in cur.fetchall():
        print(f"=== Paper ID {r['id']} ({r['paper_code']}): {r['title']} ===")
        sec_data = json.loads(r['sections']) if r['sections'] else []
        for i, s in enumerate(sec_data):
            print(f" Section {i}: title='{s.get('title')}', questions count={len(s.get('questions', []))}, either_or_groups count={len(s.get('either_or_groups', []))}")
            if s.get('either_or_groups'):
                first_grp = s['either_or_groups'][0]
                print(f"   Sample group keys: {list(first_grp.keys())}")
                if 'option_a' in first_grp:
                    print(f"   option_a: {first_grp['option_a'].get('question_text', '')[:60]}...")
                if 'option_b' in first_grp:
                    print(f"   option_b: {first_grp['option_b'].get('question_text', '')[:60]}...")
conn.close()
