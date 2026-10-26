import os

app_path = r'C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\js\app.js'
with open(app_path, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Add API_RESOURCES_BASE to global constants
old_constants = "const API_QUESTION_BANK_BASE = 'http://localhost:5000/api/question-bank';"
new_constants = """const API_QUESTION_BANK_BASE = 'http://localhost:5000/api/question-bank';
const API_RESOURCES_BASE = 'http://localhost:5000/api/resources';"""

if old_constants in text and "const API_RESOURCES_BASE = 'http://localhost:5000/api/resources';" not in text:
    text = text.replace(old_constants, new_constants, 1)
    print("Added API_RESOURCES_BASE to global constants")
else:
    print("Global constants check: already present or not found")

# 2. In renderStudentMaterialsTable, make apiUrl resilient
old_fetch = """    const response = await fetch(API_RESOURCES_BASE, {
      method: 'GET',
      credentials: 'include'
    });"""

new_fetch = """    const apiUrl = (typeof API_RESOURCES_BASE !== 'undefined' && API_RESOURCES_BASE) ? API_RESOURCES_BASE : 'http://localhost:5000/api/resources';
    const response = await fetch(apiUrl, {
      method: 'GET',
      credentials: 'include'
    });"""

if old_fetch in text:
    text = text.replace(old_fetch, new_fetch, 1)
    print("Made renderStudentMaterialsTable fetch resilient with apiUrl")
else:
    print("renderStudentMaterialsTable fetch pattern not found or already updated")

# 3. In viewStudentMaterial, make fetch resilient
old_view_fetch = """      const res = await fetch(`${API_RESOURCES_BASE}/${resourceId}`, { credentials: 'include' });"""
new_view_fetch = """      const apiUrl = (typeof API_RESOURCES_BASE !== 'undefined' && API_RESOURCES_BASE) ? API_RESOURCES_BASE : 'http://localhost:5000/api/resources';
      const res = await fetch(`${apiUrl}/${resourceId}`, { credentials: 'include' });"""

if old_view_fetch in text:
    text = text.replace(old_view_fetch, new_view_fetch, 1)
    print("Made viewStudentMaterial fetch resilient with apiUrl")
else:
    print("viewStudentMaterial fetch pattern not found or already updated")

with open(app_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("Finished applying fix_study_materials.py")
