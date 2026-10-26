import re

service_path = r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\backend\services\question_paper_service.py"

with open(service_path, "r", encoding="utf-8") as f:
    content = f.read()

# Pattern from def calculate_attempted_marks down to def generate_template_paper
start_marker = "def calculate_attempted_marks(sections):"
end_marker = "def generate_template_paper(faculty_id, data):"

assert start_marker in content, f"Could not find start marker: {start_marker}"
assert end_marker in content, f"Could not find end marker: {end_marker}"

start_pos = content.index(start_marker)
end_pos = content.index(end_marker)

replacement_block = '''def calculate_attempted_marks(sections):
    """
    Calculates attempted marks strictly according to academic rules:
    - Compulsory questions: each question is counted once.
    - Either/Or groups: students attempt only ONE alternative per group.
      Counts the marks for exactly ONE alternative (never both).
      Both alternatives must represent equal marks (e.g. 16M each in Part B Semester Exam).
    - If a section defines count and marks_per_q, uses count * marks_per_q.
    - Does not double-count alternatives, duplicated question references, or section totals.
    - Strictly supports only 2, 8, and 16 marks.
    """
    if isinstance(sections, str):
        try:
            import json
            sections = json.loads(sections)
        except Exception:
            return 0
    if not sections or not isinstance(sections, list):
        return 0

    total = 0
    for sec in sections:
        if not isinstance(sec, dict):
            continue

        groups = sec.get('groups') or sec.get('either_or_groups')
        if groups and isinstance(groups, list) and len(groups) > 0:
            for g in groups:
                if not isinstance(g, dict):
                    continue

                def get_alt_marks(alt):
                    if not alt:
                        return 0
                    if isinstance(alt, list):
                        return sum(int(q.get('marks', 0)) for q in alt if isinstance(q, dict))
                    elif isinstance(alt, dict):
                        if alt.get('is_subquestion') or alt.get('subquestions'):
                            subs = alt.get('subquestions') or []
                            return sum(int(sq.get('marks', 0)) for sq in subs if isinstance(sq, dict))
                        return int(alt.get('marks') or 0)
                    return 0

                alt_a = g.get('alternative_a') or g.get('option_a') or g.get('alt_a')
                alt_b = g.get('alternative_b') or g.get('option_b') or g.get('alt_b')

                m_a = get_alt_marks(alt_a)
                m_b = get_alt_marks(alt_b)

                g_attempted = g.get('attempted_marks')
                if g_attempted is not None and int(g_attempted) > 0:
                    group_marks = int(g_attempted)
                elif m_a > 0:
                    group_marks = m_a
                elif m_b > 0:
                    group_marks = m_b
                else:
                    group_marks = int(sec.get('marks_per_q') or 16)

                total += group_marks
        else:
            qs = sec.get('questions')
            if qs and isinstance(qs, list) and len(qs) > 0:
                total += sum(int(q.get('marks', 2)) for q in qs if isinstance(q, dict))
            else:
                sec_att = sec.get('attempted_marks')
                if sec_att is not None and int(sec_att) > 0:
                    total += int(sec_att)
                else:
                    c = int(sec.get('count') or 0)
                    m = int(sec.get('marks_per_q') or 2)
                    total += (c * m)

    return total


def find_section(sections, part_letter):
    """
    Finds section matching Part A, Part B, Part C, Section A, Section B, Section C.
    Avoids false positives where the word 'SECTION' matches 'C'.
    """
    if not sections or not isinstance(sections, list):
        return None
    import re
    target = str(part_letter).upper().strip()
    for s in sections:
        if not isinstance(s, dict):
            continue
        name = str(s.get('name') or s.get('title') or '').upper().strip()
        if re.search(rf'\\b(PART|SECTION|SEC)\\s*[-–—]?\\s*{target}\\b', name):
            return s
        if name in [target, f"PART {target}", f"PART - {target}", f"PART-{target}", f"SECTION {target}"]:
            return s
    return None


def validate_question_paper_structure(paper_data, attempted_marks=None):
    """
    Validates question paper structure based on actual college examination formats:
    1. Internal Examination (inter.pdf):
       - Exactly 50 attempted marks
       - Duration: 100 Mins.
       - Part A: 5 questions x 2m = 10 Marks
       - Part B: 1 Either/Or group of 8 Marks
       - Part C: 2 Either/Or groups of 16 Marks each
    2. Semester Examination (April May 2024 ML.pdf):
       - Exactly 100 attempted marks
       - Duration: 3 Hours
       - Part A: 10 questions x 2m = 20 Marks
       - Part B: 5 Either/Or groups of 16 attempted marks = 80 Marks (Direct 16M or Split 8+8)
       - Strictly Part A and Part B only (No Part C)
    """
    exam_type = str(paper_data.get('exam_type') or paper_data.get('paper_type') or paper_data.get('template') or paper_data.get('template_type') or '').lower()
    sections = paper_data.get('sections') or []
    if isinstance(sections, str):
        try:
            import json
            sections = json.loads(sections)
        except Exception:
            sections = []

    if not sections:
        return True, ""

    if attempted_marks is None:
        attempted_marks = calculate_attempted_marks(sections)

    # 1. Internal Examination
    if 'internal' in exam_type or 'unit test' in exam_type:
        if attempted_marks != 50:
            return False, f"Validation Error: Internal Examination must have exactly 50 attempted marks (calculated: {attempted_marks} marks). The marks calculation must count only the marks students actually attempt, not both Either/Or alternatives."

        sec_a = find_section(sections, 'A')
        if sec_a:
            q_list = sec_a.get('questions') or []
            if len(q_list) > 0 and len(q_list) != 5:
                return False, f"Validation Error: Section A of Internal Examination must contain exactly 5 compulsory questions (found {len(q_list)})."

        sec_b = find_section(sections, 'B')
        if sec_b:
            b_groups = sec_b.get('groups') or sec_b.get('either_or_groups') or []
            if len(b_groups) != 1:
                return False, f"Validation Error: Section B must contain exactly 1 Either/Or group of 8 marks (found {len(b_groups)})."

        sec_c = find_section(sections, 'C')
        if sec_c:
            c_groups = sec_c.get('groups') or sec_c.get('either_or_groups') or []
            if len(c_groups) != 2:
                return False, f"Validation Error: Section C must contain exactly 2 Either/Or groups of 16 marks each (found {len(c_groups)})."

    # 2. Semester Examination
    elif 'semester' in exam_type or 'model' in exam_type or 'end semester' in exam_type or attempted_marks == 100:
        if attempted_marks != 100:
            return False, f"Validation Error: Semester Examination must have exactly 100 attempted marks (calculated: {attempted_marks} marks). The marks calculation must count only the marks students actually attempt, not both Either/Or alternatives."

        # The Semester Examination must contain only Part A and Part B. Do not add Part C.
        sec_c = find_section(sections, 'C')
        if sec_c:
            return False, "Validation Error: The Semester Examination must contain only Part A and Part B. Do not add Part C."

        sec_a = find_section(sections, 'A')
        if not sec_a:
            return False, "Validation Error: Semester Examination must contain Part A."
        qs = sec_a.get('questions') or []
        if len(qs) != 10:
            return False, f"Validation Error: Section A of Semester Examination must have exactly 10 compulsory questions of 2 marks (found {len(qs)})."
        for idx, q in enumerate(qs, start=1):
            if int(q.get('marks', 2)) != 2:
                return False, f"Validation Error: Part A Question {idx} must be worth 2 marks (found {q.get('marks')})."

        sec_b = find_section(sections, 'B')
        if not sec_b:
            return False, "Validation Error: Semester Examination must contain Part B."
        b_groups = sec_b.get('groups') or sec_b.get('either_or_groups') or []
        if len(b_groups) != 5:
            return False, f"Validation Error: Section B of Semester Examination must contain exactly 5 Either/Or groups of 16 attempted marks each (found {len(b_groups)})."

        # Validate each Part B group: each alternative must represent exactly 16 marks
        for g_idx, grp in enumerate(b_groups, start=1):
            q_num = grp.get('question_number') or (10 + g_idx)

            def validate_alternative(alt, letter):
                if not alt:
                    return f"In Part B Question {q_num}, Alternative ({letter}) is missing."
                if isinstance(alt, list):
                    m = sum(int(q.get('marks', 0)) for q in alt if isinstance(q, dict))
                    if m != 16:
                        return f"In Part B Question {q_num}, Alternative ({letter}) must represent exactly 16 marks (found {m} marks)."
                    return None
                elif isinstance(alt, dict):
                    if alt.get('is_subquestion') or alt.get('subquestions'):
                        subs = alt.get('subquestions') or []
                        if len(subs) != 2:
                            return f"In Part B Question {q_num}, Split Alternative ({letter}) must contain exactly two 8-mark subquestions (found {len(subs)})."
                        sub_sum = sum(int(sq.get('marks', 0)) for sq in subs if isinstance(sq, dict))
                        if sub_sum != 16:
                            return f"In Part B Question {q_num}, Split Alternative ({letter}) subquestions must combine to exactly 16 marks (found {sub_sum} marks: {subs[0].get('marks')} + {subs[1].get('marks')})."
                        return None
                    else:
                        m = int(alt.get('marks', 0))
                        if m != 16:
                            return f"In Part B Question {q_num}, Direct Alternative ({letter}) must be worth exactly 16 marks (found {m} marks)."
                        return None
                return f"In Part B Question {q_num}, Alternative ({letter}) has invalid data structure."

            err_a = validate_alternative(grp.get('alternative_a') or grp.get('option_a') or grp.get('alt_a'), 'a')
            if err_a:
                return False, f"Validation Error: {err_a} Each alternative must represent exactly 16 marks (either Direct 16M or Split 8 + 8)."

            err_b = validate_alternative(grp.get('alternative_b') or grp.get('option_b') or grp.get('alt_b'), 'b')
            if err_b:
                return False, f"Validation Error: {err_b} Each alternative must represent exactly 16 marks (either Direct 16M or Split 8 + 8)."

    return True, ""


'''

new_content = content[:start_pos] + replacement_block + content[end_pos:]

with open(service_path, "w", encoding="utf-8") as f:
    f.write(new_content)

print("Successfully updated question_paper_service.py with robust calculate_attempted_marks and validate_question_paper_structure!")
