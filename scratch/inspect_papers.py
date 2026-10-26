import pymysql, json

conn = pymysql.connect(
    host='localhost',
    user='root',
    password='sqlamzad@123',
    database='academic_question_system',
    cursorclass=pymysql.cursors.DictCursor
)
with conn.cursor() as cur:
    cur.execute("SELECT id, title, exam_type, total_marks, status, sections, created_by FROM question_papers WHERE exam_type LIKE '%Semester%' ORDER BY id DESC")
    rows = cur.fetchall()
    for r in rows:
        print(f"=== Paper ID: {r['id']}, Faculty: {r['created_by']}, Title: {r['title']}, Status: {r['status']}, Total Marks: {r['total_marks']} ===")
        sec = json.loads(r['sections']) if isinstance(r['sections'], str) else r['sections']
        print('Number of sections:', len(sec) if sec else 0)
        if sec:
            for s in sec:
                print(' Section name:', s.get('name') or s.get('title'),
                      '| count:', s.get('count'),
                      '| marks_per_q:', s.get('marks_per_q'),
                      '| attempted_marks:', s.get('attempted_marks'),
                      '| groups:', len(s.get('groups') or s.get('either_or_groups') or []),
                      '| questions:', len(s.get('questions') or []))
                groups = s.get('groups') or s.get('either_or_groups') or []
                for g in groups:
                    print('   Group attempted_marks:', g.get('attempted_marks'),
                          'alt_a keys:', list(g.get('alternative_a', {}).keys()) if isinstance(g.get('alternative_a'), dict) else type(g.get('alternative_a')),
                          'alt_b keys:', list(g.get('alternative_b', {}).keys()) if isinstance(g.get('alternative_b'), dict) else type(g.get('alternative_b')))
conn.close()
