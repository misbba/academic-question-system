import pymysql

conn = pymysql.connect(host='localhost', user='root', password='sqlamzad@123', database='academic_question_system', cursorclass=pymysql.cursors.DictCursor)
with conn.cursor() as cur:
    cur.execute("SELECT COUNT(*) as cnt, subject, is_in_bank FROM questions WHERE created_by = 24 GROUP BY subject, is_in_bank")
    for r in cur.fetchall():
        print(r)
conn.close()
