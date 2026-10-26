import sys, os
sys.path.insert(0, r'C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system')
sys.path.insert(0, r'C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\backend')
from models.database import get_db_connection

conn = get_db_connection()
with conn.cursor() as cur:
    for fid, name in [(24, 'Murugan'), (25, 'Mrs V Kavitha')]:
        print(f"\n==================== DATA FOR {name} (ID: {fid}) ====================")
        # Academic resources
        cur.execute("SELECT id, title, subject, unit, topic, resource_type, file_name, created_by FROM academic_resources WHERE created_by = %s", (fid,))
        res = cur.fetchall()
        print(f"Academic Resources ({len(res)}):")
        for r in res[:5]:
            print("  ", r)
            
        # Questions
        cur.execute("SELECT COUNT(*) as cnt, subject, is_in_bank FROM questions WHERE created_by = %s GROUP BY subject, is_in_bank", (fid,))
        q_stats = cur.fetchall()
        print("Questions breakdown:")
        for q in q_stats:
            print("  ", q)
            
        # Question papers
        cur.execute("SELECT id, title, subject, exam_type, status, created_by FROM question_papers WHERE created_by = %s", (fid,))
        papers = cur.fetchall()
        print(f"Question Papers ({len(papers)}):")
        for p in papers:
            print("  ", p)
            
        # Quizzes
        cur.execute("SELECT id, title, subject, status, created_by FROM quizzes WHERE created_by = %s", (fid,))
        quizzes = cur.fetchall()
        print(f"Quizzes ({len(quizzes)}):")
        for q in quizzes:
            print("  ", q)
            
        # Assignments
        cur.execute("SELECT id, title, subject, status, created_by FROM assignments WHERE created_by = %s", (fid,))
        asns = cur.fetchall()
        print(f"Assignments ({len(asns)}):")
        for a in asns:
            print("  ", a)
            
        # Lesson Plans
        cur.execute("SELECT id, title, subject, created_by FROM lesson_plans WHERE created_by = %s", (fid,))
        lps = cur.fetchall()
        print(f"Lesson Plans ({len(lps)}):")
        for lp in lps:
            print("  ", lp)
            
        # Presentations
        cur.execute("SELECT id, title, subject, created_by FROM presentations WHERE created_by = %s", (fid,))
        ppts = cur.fetchall()
        print(f"Presentations ({len(ppts)}):")
        for ppt in ppts:
            print("  ", ppt)

        # Activity History
        cur.execute("SELECT id, activity_type, title, subject, created_at FROM activity_history WHERE user_id = %s ORDER BY created_at DESC LIMIT 5", (fid,))
        acts = cur.fetchall()
        print(f"Activity History ({len(acts)}):")
        for act in acts:
            print("  ", act)

conn.close()
