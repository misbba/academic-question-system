import os
import re

print("Starting backend updates...")

# 1. Update backend/routes/question_routes.py
routes_path = r"backend/routes/question_routes.py"
with open(routes_path, "r", encoding="utf-8") as f:
    r_code = f.read()

# Replace line 224 and 250 in routes
r_code = r_code.replace(
    "uploaded_file = request.files.get('image') or request.files.get('file')",
    "uploaded_file = (\n        request.files.get('image') or \n        request.files.get('file') or \n        request.files.get('diagram') or \n        request.files.get('resourceFile')\n    )"
)

with open(routes_path, "w", encoding="utf-8") as f:
    f.write(r_code)
print("[OK] Updated backend/routes/question_routes.py")

