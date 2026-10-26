import pymysql

conn = pymysql.connect(host='localhost', user='root', password='sqlamzad@123', database='academic_question_system', cursorclass=pymysql.cursors.DictCursor)
with conn.cursor() as cur:
    cur.execute('SELECT COUNT(*) as cnt FROM questions')
    print('Total questions in DB:', cur.fetchone()['cnt'])
    cur.execute('SELECT COUNT(*) as cnt FROM questions WHERE created_by = 24')
    print('Murugan questions:', cur.fetchone()['cnt'])
    cur.execute('SELECT DISTINCT subject FROM questions')
    print('Distinct subjects in questions:', cur.fetchall())
    cur.execute('SELECT DISTINCT subject FROM academic_resources')
    print('Distinct subjects in resources:', cur.fetchall())
    cur.execute("SELECT COUNT(*) as cnt FROM question_papers WHERE created_by = 24 AND status = 'Draft'")
    print('Murugan draft papers:', cur.fetchone()['cnt'])
    cur.execute("SELECT COUNT(*) as cnt FROM question_papers WHERE created_by = 24 AND status = 'Published'")
    print('Murugan published papers:', cur.fetchone()['cnt'])
conn.close()
