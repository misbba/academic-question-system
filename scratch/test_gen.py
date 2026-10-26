import sys
import json
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

def test_fetch_and_build():
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM questions WHERE subject = 'Database Management Systems' ORDER BY is_in_bank DESC, id ASC")
        rows = cur.fetchall()
    conn.close()
    print("Found total questions:", len(rows))

    # Test Section A for Semester: 2 from each unit
    units = ["Unit I", "Unit II", "Unit III", "Unit IV", "Unit V"]
    sec_a = []
    for u in units:
        u_2m = [r for r in rows if normalize_unit(r['unit']) == u and r['marks'] == 2]
        print(f"2M questions in {u}:", len(u_2m))
        assert len(u_2m) >= 2, f"Expected at least 2 questions in {u}"
        sec_a.extend(u_2m[:2])

    print("Semester Sec A count:", len(sec_a))
    assert len(sec_a) == 10

    # Test Section B for Semester: 5 units with Alt A and Alt B
    sec_b_groups = []
    for idx, u in enumerate(units, 1):
        u_16m = [r for r in rows if normalize_unit(r['unit']) == u and r['marks'] == 16]
        u_8m = [r for r in rows if normalize_unit(r['unit']) == u and r['marks'] == 8]
        print(f"In {u}: 16M count: {len(u_16m)}, 8M count: {len(u_8m)}")
        assert len(u_16m) >= 2 or (len(u_16m) >= 1 and len(u_8m) >= 2) or len(u_8m) >= 4, f"Insufficient 16M/8M in {u}"

    print("All checks passed successfully!")

if __name__ == '__main__':
    test_fetch_and_build()
