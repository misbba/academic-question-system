import pymysql

conn = pymysql.connect(
    host='localhost',
    user='root',
    password='sqlamzad@123',
    database='academic_question_system',
    cursorclass=pymysql.cursors.DictCursor
)

with conn.cursor() as cur:
    cur.execute("SELECT id, full_name, email, role FROM users WHERE role='faculty'")
    faculties = cur.fetchall()
    print("Faculties found:", len(faculties))
    for f in faculties:
        fid = f['id']
        name = f['full_name']
        cur.execute("SELECT count(*) as total, sum(is_in_bank=1) as bank_count, sum(is_in_bank=0) as draft_count FROM questions WHERE created_by=%s", (fid,))
        q = cur.fetchone()
        cur.execute("SELECT DISTINCT subject FROM questions WHERE created_by=%s", (fid,))
        q_subj = [r['subject'] for r in cur.fetchall()]
        cur.execute("SELECT count(*) as res_count FROM academic_resources WHERE created_by=%s", (fid,))
        res = cur.fetchone()
        cur.execute("SELECT DISTINCT subject FROM academic_resources WHERE created_by=%s", (fid,))
        res_subj = [r['subject'] for r in cur.fetchall()]
        cur.execute("SELECT count(*) as p_count FROM question_papers WHERE created_by=%s", (fid,))
        p = cur.fetchone()
        cur.execute("SELECT DISTINCT subject FROM question_papers WHERE created_by=%s", (fid,))
        p_subj = [r['subject'] for r in cur.fetchall()]
        cur.execute("SELECT count(*) as qz_count FROM quizzes WHERE created_by=%s", (fid,))
        qz = cur.fetchone()
        cur.execute("SELECT DISTINCT subject FROM quizzes WHERE created_by=%s", (fid,))
        qz_subj = [r['subject'] for r in cur.fetchall()]
        print(f"\n--- Faculty ID {fid}: {name} ({f['email']}) ---")
        print(f"Questions: total={q['total']}, bank={q['bank_count']}, draft={q['draft_count']}, subjects={q_subj}")
        print(f"Resources: count={res['res_count']}, subjects={res_subj}")
        print(f"Question Papers: count={p['p_count']}, subjects={p_subj}")
        print(f"Quizzes: count={qz['qz_count']}, subjects={qz_subj}")
