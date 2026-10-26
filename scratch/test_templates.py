import sys
sys.path.insert(0, r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\backend")
from models.database import get_db_connection

def normalize_unit(unit_str):
    if not unit_str:
        return "Unit I"
    u = str(unit_str).upper().strip()
    if "UNIT 1" in u or "UNIT I " in u or u == "UNIT I" or "UNIT I—" in u or "UNIT I -" in u or "UNIT I –" in u or "UNIT-I" in u:
        return "Unit I"
    if "UNIT 2" in u or "UNIT II " in u or u == "UNIT II" or "UNIT II—" in u or "UNIT II -" in u or "UNIT II –" in u or "UNIT-II" in u:
        return "Unit II"
    if "UNIT 3" in u or "UNIT III " in u or u == "UNIT III" or "UNIT III—" in u or "UNIT III -" in u or "UNIT III –" in u or "UNIT-III" in u:
        return "Unit III"
    if "UNIT 4" in u or "UNIT IV " in u or u == "UNIT IV" or "UNIT IV—" in u or "UNIT IV -" in u or "UNIT IV –" in u or "UNIT-IV" in u:
        return "Unit IV"
    if "UNIT 5" in u or "UNIT V " in u or u == "UNIT V" or "UNIT V—" in u or "UNIT V -" in u or "UNIT V –" in u or "UNIT-V" in u:
        return "Unit V"
    return unit_str

def calculate_attempted_marks(sections):
    if not sections or not isinstance(sections, list):
        return 0
    total = 0
    for sec in sections:
        if not isinstance(sec, dict):
            continue
        groups = sec.get('groups')
        if groups and isinstance(groups, list):
            for g in groups:
                if not isinstance(g, dict):
                    continue
                g_attempted = g.get('attempted_marks')
                if g_attempted is not None:
                    total += int(g_attempted)
                else:
                    alt_a = g.get('alternative_a') or {}
                    total += int(alt_a.get('marks') or sec.get('marks_per_q') or 16)
        else:
            qs = sec.get('questions')
            if qs and isinstance(qs, list):
                total += sum(int(q.get('marks', 2)) for q in qs if isinstance(q, dict))
            else:
                c = int(sec.get('count') or 0)
                m = int(sec.get('marks_per_q') or 2)
                total += (c * m)
    return total

print("Test calculate_attempted_marks:")
# Test Internal Test
mock_internal_sections = [
    {"name": "SECTION A", "type": "compulsory", "count": 5, "marks_per_q": 2, "questions": [{"marks": 2}] * 5},
    {"name": "SECTION B", "type": "either_or", "groups": [{"attempted_marks": 8, "alternative_a": {"marks": 8}, "alternative_b": {"marks": 8}}]},
    {"name": "SECTION C", "type": "either_or", "groups": [
        {"attempted_marks": 16, "alternative_a": {"marks": 16}, "alternative_b": {"marks": 16}},
        {"attempted_marks": 16, "alternative_a": {"marks": 16}, "alternative_b": {"marks": 16}}
    ]}
]
int_attempted = calculate_attempted_marks(mock_internal_sections)
print("Internal Test Attempted Marks:", int_attempted)
assert int_attempted == 50, f"Expected 50, got {int_attempted}"

# Test Semester Exam
mock_sem_sections = [
    {"name": "SECTION A", "type": "compulsory", "count": 10, "marks_per_q": 2, "questions": [{"marks": 2}] * 10},
    {"name": "SECTION B", "type": "either_or", "groups": [
        {"attempted_marks": 16, "alternative_a": {"marks": 16}, "alternative_b": {"marks": 16}} for _ in range(5)
    ]}
]
sem_attempted = calculate_attempted_marks(mock_sem_sections)
print("Semester Exam Attempted Marks:", sem_attempted)
assert sem_attempted == 100, f"Expected 100, got {sem_attempted}"
print("All assertions passed!")
