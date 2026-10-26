# -*- coding: utf-8 -*-
import os

faculty_pages = [
    'faculty-dashboard.html',
    'faculty-resources.html',
    'faculty-generate-questions.html',
    'faculty-question-paper.html',
    'faculty-history.html',
    'faculty-profile.html',
    'faculty-image-question.html',
    'faculty-language-converter.html',
    'faculty-voice-question.html',
    'faculty-generate-quiz.html',
    'faculty-generate-assignment.html',
    'faculty-generate-ppt.html',
    'faculty-generate-lesson-plan.html',
    'faculty-results.html',
    'faculty-performance.html'
]

base_dir = r'C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system'

for p in faculty_pages:
    fp = os.path.join(base_dir, p)
    if not os.path.exists(fp):
        print("MISSING:", p)
        continue
    with open(fp, 'r', encoding='utf-8') as f:
        html = f.read()
    has_name = 'facultyNameDisplay' in html
    has_dept = 'facultyDeptDisplay' in html
    has_auth = 'auth.js' in html
    has_app = 'app.js' in html
    has_logout = 'handleLogout()' in html
    has_fingerprint = 'fingerprint' in html.lower()
    has_alistair = 'alistair' in html.lower()
    
    status = []
    if not has_name: status.append('NO_NAME_ELEM')
    if not has_dept: status.append('NO_DEPT_ELEM')
    if not has_auth: status.append('NO_AUTH_JS')
    if not has_app: status.append('NO_APP_JS')
    if not has_logout: status.append('NO_LOGOUT')
    if has_fingerprint: status.append('HAS_FINGERPRINT')
    if has_alistair: status.append('HAS_ALISTAIR')
    
    status_str = "OK" if not status else ", ".join(status)
    print(f"{p:<35} : {status_str}")
