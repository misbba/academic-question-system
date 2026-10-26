import glob
import os

project_dir = r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system"
student_files = glob.glob(os.path.join(project_dir, "student-*.html"))

print(f"Found {len(student_files)} student files:")
for fpath in student_files:
    fname = os.path.basename(fpath)
    if fname in ['student-login.html', 'student-register.html']:
        continue
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    has_name_id = 'id="studentNameDisplay"' in content
    has_roll_id = 'id="studentRollDisplay"' in content
    has_vance = 'Vance' in content or 'Alistair' in content
    has_auth = 'js/auth.js' in content
    has_app = 'js/app.js' in content
    
    print(f"{fname:35} | name_id: {has_name_id} | roll_id: {has_roll_id} | vance: {has_vance} | auth: {has_auth}")
