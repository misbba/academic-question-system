import pymysql

conn = pymysql.connect(
    host='localhost',
    user='root',
    password='sqlamzad@123',
    database='academic_question_system',
    cursorclass=pymysql.cursors.DictCursor
)

with conn.cursor() as cursor:
    for uid in [24, 25]:
        cursor.execute("""
            SELECT subject, 
                   MAX(department) as department, 
                   MAX(academic_year) as academic_year, 
                   MAX(semester) as semester, 
                   COUNT(*) as item_count
            FROM (
                SELECT subject, department, academic_year, semester FROM questions WHERE created_by = %s AND is_in_bank = 1 AND subject IS NOT NULL AND subject != ''
                UNION ALL
                SELECT subject, department, academic_year, semester FROM academic_resources WHERE created_by = %s AND subject IS NOT NULL AND subject != ''
                UNION ALL
                SELECT subject, department, academic_year, semester FROM question_papers WHERE created_by = %s AND subject IS NOT NULL AND subject != ''
                UNION ALL
                SELECT subject, department, academic_year, semester FROM quizzes WHERE created_by = %s AND subject IS NOT NULL AND subject != ''
            ) AS s
            GROUP BY subject
            ORDER BY subject ASC
        """, (uid, uid, uid, uid))
        courses = cursor.fetchall()
        print(f"User {uid} active courses ({len(courses)}):")
        for c in courses:
            print("  ", c)
