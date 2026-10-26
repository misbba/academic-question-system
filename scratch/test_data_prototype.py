# -*- coding: utf-8 -*-
"""
Prototype and verify updated question paper service logic.
"""
import sys
sys.path.insert(0, r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\backend")

from models.database import get_db_connection
from services.question_service import format_question_dict

def test_data():
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM questions WHERE subject = 'Machine Learning'")
        ml_rows = cur.fetchall()
        cur.execute("SELECT * FROM questions WHERE subject = 'Database Management Systems'")
        dbms_rows = cur.fetchall()
    conn.close()

    ml_questions = [format_question_dict(r) for r in ml_rows]
    dbms_questions = [format_question_dict(r) for r in dbms_rows]

    print(f"ML Questions: {len(ml_questions)}, DBMS Questions: {len(dbms_questions)}")
    return ml_questions, dbms_questions

if __name__ == '__main__':
    test_data()
