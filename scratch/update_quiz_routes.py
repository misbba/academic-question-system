import os

file_path = r'C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\backend\routes\quiz_routes.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

target = """@quiz_bp.route('/api/quizzes/<id>/submit', methods=['POST'])
def submit_quiz_api(id):"""

replacement = """@quiz_bp.route('/api/quizzes/<id>/submit', methods=['POST'])
@quiz_bp.route('/api/quizzes/<id>/attempts', methods=['POST'])
def submit_quiz_api(id):"""

target_norm = '\n'.join(line.rstrip() for line in target.splitlines())
content_norm = '\n'.join(line.rstrip() for line in content.splitlines())

if target_norm in content_norm:
    new_content_norm = content_norm.replace(target_norm, '\n'.join(line.rstrip() for line in replacement.splitlines()))
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content_norm)
    print("SUCCESS: Updated quiz_routes.py")
else:
    print("ERROR: Target norm not found")
