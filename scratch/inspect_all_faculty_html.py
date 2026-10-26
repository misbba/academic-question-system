import glob
import os
import re

project_dir = r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system"
faculty_files = glob.glob(os.path.join(project_dir, "faculty-*.html"))

print(f"Found {len(faculty_files)} faculty files:")
for fpath in faculty_files:
    fname = os.path.basename(fpath)
    if fname in ['faculty-login.html', 'faculty-register.html']:
        continue
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    has_name_id = 'id="facultyNameDisplay"' in content
    has_dept_id = 'id="facultyDeptDisplay"' in content
    has_vance = 'Vance' in content or 'Alistair' in content
    has_auth = 'js/auth.js' in content
    has_app = 'js/app.js' in content
    
    # Extract the line containing facultyNameDisplay
    name_line = ""
    for line in content.splitlines():
        if 'facultyNameDisplay' in line:
            name_line = line.strip()
            break
            
    print(f"{fname:35} | name_id: {has_name_id} | dept_id: {has_dept_id} | vance: {has_vance} | auth: {has_auth} | line: {name_line}")
