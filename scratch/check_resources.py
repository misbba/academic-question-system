import pymysql

conn = pymysql.connect(
    host='localhost',
    user='root',
    password='sqlamzad@123',
    database='academic_question_system',
    cursorclass=pymysql.cursors.DictCursor
)
with conn.cursor() as cur:
    cur.execute("SELECT id, title, subject, resource_type, file_name, file_path, created_by FROM academic_resources")
    rows = cur.fetchall()
    print(f"Total resources: {len(rows)}")
    for r in rows:
        print(f"ID {r['id']} | Faculty {r['created_by']} | Subj: '{r['subject']}' | Type: {r['resource_type']} | Title: '{r['title']}' | File: '{r['file_path']}'")
conn.close()
