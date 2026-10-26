import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
from models.database import get_db_connection

conn = get_db_connection()
with conn.cursor() as cur:
    for t in ['users', 'academic_resources', 'assignments', 'quizzes', 'quiz_attempts', 'question_papers', 'presentations', 'lesson_plans']:
        cur.execute(f'DESCRIBE {t}')
        cols = [f"{r['Field']} ({r['Type']})" for r in cur.fetchall()]
        print(f'=== {t} ===\n' + ', '.join(cols) + '\n')
    
    print('=== Sample Student Users ===')
    cur.execute("SELECT id, full_name, email, role, department, semester, academic_year FROM users WHERE role = 'student' LIMIT 5")
    for r in cur.fetchall():
        print(r)

    print('\n=== Distinct Subjects in resources, papers, quizzes ===')
    cur.execute("SELECT DISTINCT subject FROM academic_resources WHERE subject IS NOT NULL AND subject != ''")
    print('Resources subjects:', [r['subject'] for r in cur.fetchall()])
    cur.execute("SELECT DISTINCT subject FROM question_papers WHERE subject IS NOT NULL AND subject != ''")
    print('Question papers subjects:', [r['subject'] for r in cur.fetchall()])
    cur.execute("SELECT DISTINCT subject FROM quizzes WHERE subject IS NOT NULL AND subject != ''")
    print('Quizzes subjects:', [r['subject'] for r in cur.fetchall()])

conn.close()
