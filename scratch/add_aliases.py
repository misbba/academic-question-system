filepath = r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\backend\routes\question_routes.py"
with open(filepath, "r", encoding="utf-8") as f:
    c = f.read()

c = c.replace("@question_bp.route('/api/question-bank', methods=['POST'])", "@question_bp.route('/api/question-bank', methods=['POST'])\n@question_bp.route('/api/questions/bank', methods=['POST'])")
c = c.replace("@question_bp.route('/api/question-bank', methods=['GET'])", "@question_bp.route('/api/question-bank', methods=['GET'])\n@question_bp.route('/api/questions/bank', methods=['GET'])")

with open(filepath, "w", encoding="utf-8") as f:
    f.write(c)
print("Done adding route aliases")
