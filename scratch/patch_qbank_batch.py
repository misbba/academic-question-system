service_file = r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\backend\services\question_service.py"
with open(service_file, "r", encoding="utf-8") as f:
    code = f.read()

target = "raw_questions = data.get('questions') or []"
replacement = "raw_questions = data.get('questions') or data.get('batch') or []"

if target in code:
    code = code.replace(target, replacement, 1)
    with open(service_file, "w", encoding="utf-8") as f:
        f.write(code)
    print("Updated save_to_question_bank to also support 'batch'")
else:
    print("Target not found or already updated")
