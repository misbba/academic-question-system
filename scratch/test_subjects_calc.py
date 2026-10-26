import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
from models.database import get_db_connection

conn = get_db_connection()
with conn.cursor() as cur:
    subjects = [
        {"code": "CS301", "name": "Database Management Systems", "credits": 4, "desc": "Relational database design, relational algebra, SQL optimization, transactions, ACID properties, and concurrency control."},
        {"code": "23CST504", "name": "Distributed Computing", "credits": 4, "desc": "Distributed system architectures, RPC, clock synchronization, Lamport logical timestamps, mutual exclusion, and consensus."},
        {"code": "AI401", "name": "Machine Learning", "credits": 4, "desc": "Supervised and unsupervised learning, classification, neural networks, deep architectures, and model performance metrics."},
        {"code": "IT302", "name": "Cloud Computing", "credits": 3, "desc": "Cloud virtualization, IaaS, PaaS, SaaS delivery models, distributed storage, and cloud microservices orchestration."}
    ]
    for s in subjects:
        cur.execute("SELECT count(*) as c FROM academic_resources WHERE subject = %s AND status != 'Deleted'", (s['name'],))
        s['materials_count'] = cur.fetchone()['c']
        cur.execute("SELECT count(*) as c FROM quizzes WHERE subject = %s AND status = 'Published'", (s['name'],))
        s['quizzes_count'] = cur.fetchone()['c']
        cur.execute("SELECT count(*) as c FROM assignments WHERE subject = %s AND status = 'Published'", (s['name'],))
        s['assignments_count'] = cur.fetchone()['c']
        cur.execute("SELECT count(*) as c FROM question_papers WHERE subject = %s AND status = 'Published'", (s['name'],))
        s['papers_count'] = cur.fetchone()['c']
        print(s)

conn.close()
