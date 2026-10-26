import pymysql, json

conn = pymysql.connect(
    host='localhost',
    user='root',
    password='sqlamzad@123',
    database='academic_question_system',
    cursorclass=pymysql.cursors.DictCursor
)
with conn.cursor() as cur:
    cur.execute("SELECT id, title, exam_type, total_marks, sections FROM question_papers WHERE id IN (3, 12, 13, 17, 19, 26)")
    rows = cur.fetchall()
    for r in rows:
        print(f"\n=================== Paper {r['id']} ({r['exam_type']}) - Total Marks: {r['total_marks']} ===================")
        sec = json.loads(r['sections']) if isinstance(r['sections'], str) else (r['sections'] or [])
        print(f"Num sections: {len(sec)}")
        for idx, s in enumerate(sec):
            print(f"  Section {idx+1}: name='{s.get('name')}' count={s.get('count')} marks_per_q={s.get('marks_per_q')} attempted_marks={s.get('attempted_marks')} total_marks={s.get('total_marks')}")
            qs = s.get('questions') or []
            grps = s.get('groups') or s.get('either_or_groups') or []
            print(f"    questions count: {len(qs)}, groups count: {len(grps)}")
            if grps:
                for g_i, g in enumerate(grps):
                    print(f"      Group {g_i+1}: attempted_marks={g.get('attempted_marks')} alt_a={type(g.get('alternative_a'))} alt_b={type(g.get('alternative_b'))}")

conn.close()
