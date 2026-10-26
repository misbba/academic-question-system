import sys
sys.path.insert(0, r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\backend")
from services.question_paper_service import generate_template_paper

ok, res, status = generate_template_paper(24, {
    "template_type": "internal_test",
    "subject": "Database Management Systems",
    "department": "Artificial Intelligence & Data Science"
})
print("Status:", status, "ok:", ok)
if ok:
    p = res["paper"]
    print("Exam Type:", p.get("exam_type"))
    print("Total Marks:", p.get("total_marks"))
    print("Sections:", len(p.get("sections", [])))
    for s in p.get("sections", []):
        print("  Sec:", s.get("name"), "Attempted:", s.get("attempted_marks"))
else:
    print("Error:", res)
