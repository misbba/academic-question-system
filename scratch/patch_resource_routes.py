import os

file_path = r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\backend\routes\resource_routes.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

target = "if not owned:\n            return jsonify({\"status\": \"error\", \"message\": \"Forbidden. You are not authorized to access this file.\"}), 403"
replacement = "if not owned and not safe_name.startswith('diagram_'):\n            return jsonify({\"status\": \"error\", \"message\": \"Forbidden. You are not authorized to access this file.\"}), 403"

if "not safe_name.startswith('diagram_')" not in content:
    content = content.replace(target, replacement)
    content = content.replace(target.replace("\n", "\r\n"), replacement.replace("\n", "\r\n"))
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Updated resource_routes.py for diagram files")
else:
    print("Already updated resource_routes.py")
