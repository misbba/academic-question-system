import sys, os
sys.path.insert(0, r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\backend")

from services.question_paper_service import update_question_paper

# Try to publish Paper 26
ok, result, status_code = update_question_paper(26, 24, {"status": "Published"})
print(f"Status Code: {status_code}")
print(f"Success: {ok}")
print(f"Result: {result}")
