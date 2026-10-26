import pymysql

conn = pymysql.connect(host='localhost', user='root', password='sqlamzad@123', database='academic_question_system', cursorclass=pymysql.cursors.DictCursor)
with conn.cursor() as cur:
    cur.execute("SELECT * FROM academic_resources WHERE id IN (2, 3, 4)")
    for r in cur.fetchall():
        print(r)
conn.close()
