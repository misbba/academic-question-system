import pymysql, json

conn = pymysql.connect(
    host='localhost',
    user='root',
    password='sqlamzad@123',
    database='academic_question_system',
    cursorclass=pymysql.cursors.DictCursor
)
with conn.cursor() as cur:
    cur.execute("SELECT * FROM question_papers WHERE id = 26")
    r = cur.fetchone()
    print("=== Paper 26 ===")
    for k, v in r.items():
        if k == 'sections':
            sec = json.loads(v) if isinstance(v, str) else v
            print("sections count:", len(sec))
            for i, s in enumerate(sec):
                print(f" Section {i}:", s.get('name'), "| groups:", len(s.get('groups') or []), "| questions:", len(s.get('questions') or []))
        else:
            print(f" {k}: {v}")
conn.close()
