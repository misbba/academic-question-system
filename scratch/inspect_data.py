import sys
sys.path.insert(0, 'C:/Users/Nisha/.gemini/antigravity/scratch/academic-question-system/backend')
from models.database import get_db_connection

conn = get_db_connection()
with conn.cursor() as cur:
    for uid, name in [(24, 'Murugan'), (25, 'Mrs V Kavitha')]:
        cur.execute('SELECT COUNT(*) AS c FROM questions WHERE created_by = %s', (uid,))
        q_count = cur.fetchone()['c']
        cur.execute("SELECT COUNT(*) AS c FROM question_papers WHERE created_by = %s AND status = 'Draft'", (uid,))
        d_count = cur.fetchone()['c']
        cur.execute("SELECT COUNT(*) AS c FROM question_papers WHERE created_by = %s AND status = 'Published'", (uid,))
        p_count = cur.fetchone()['c']
        cur.execute('SELECT COUNT(*) AS c FROM academic_resources WHERE created_by = %s', (uid,))
        r_count = cur.fetchone()['c']
        
        # Also distinct subjects for active courses
        cur.execute("""
            SELECT COUNT(DISTINCT subject) AS c FROM (
                SELECT subject FROM questions WHERE created_by = %s AND subject IS NOT NULL AND subject != ''
                UNION
                SELECT subject FROM academic_resources WHERE created_by = %s AND subject IS NOT NULL AND subject != ''
                UNION
                SELECT subject FROM question_papers WHERE created_by = %s AND subject IS NOT NULL AND subject != ''
            ) AS s
        """, (uid, uid, uid))
        c_count = cur.fetchone()['c']
        
        print(f'{name} (id {uid}): Questions={q_count}, Drafts={d_count}, Published={p_count}, Resources={r_count}, Courses={c_count}')
conn.close()
