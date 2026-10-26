# -*- coding: utf-8 -*-
import sys

SERVICE_PATH = r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\backend\services\question_paper_service.py"

NEW_FUNCTIONS = '''

def get_bloom_tag(bloom_level):
    """Returns official bloom tag code as seen in college examination papers."""
    b = str(bloom_level).lower().strip()
    if 'rem' in b: return '[RE]'
    if 'und' in b: return '[UN]'
    if 'app' in b: return '[AP]'
    if 'ana' in b: return '[AN]'
    if 'eva' in b: return '[EV]'
    if 'cre' in b: return '[CR]'
    return '[UN]'


def get_co_tag(unit_str):
    """Returns course outcome tag as seen in college internal examination papers."""
    norm = normalize_unit(unit_str)
    if 'I' == norm.replace('Unit ', ''): return '(CO1)'
    if 'II' == norm.replace('Unit ', ''): return '(CO2)'
    if 'III' == norm.replace('Unit ', ''): return '(CO3)'
    if 'IV' == norm.replace('Unit ', ''): return '(CO4)'
    if 'V' == norm.replace('Unit ', ''): return '(CO5)'
    return '(CO3)'


def calculate_attempted_marks(sections):
    """
    Calculates the attempted marks for a question paper.
    Strict Rule: Only ONE alternative in Either/Or questions counts toward attempted marks.
    Never sums both alternatives.
    """
    if not sections or not isinstance(sections, list):
        return 0
    total = 0
    for sec in sections:
        if not isinstance(sec, dict):
            continue
        groups = sec.get('groups') or sec.get('either_or_groups')
        if groups and isinstance(groups, list):
            for g in groups:
                if not isinstance(g, dict):
                    continue
                g_attempted = g.get('attempted_marks')
                if g_attempted is not None:
                    total += int(g_attempted)
                else:
                    alt_a = g.get('alternative_a') or {}
                    if isinstance(alt_a, list):
                        total += sum(int(q.get('marks', 0)) for q in alt_a)
                    elif isinstance(alt_a, dict):
                        if alt_a.get('subquestions'):
                            total += sum(int(sq.get('marks', 0)) for sq in alt_a['subquestions'])
                        else:
                            total += int(alt_a.get('marks') or sec.get('marks_per_q') or 0)
        else:
            qs = sec.get('questions')
            if qs and isinstance(qs, list):
                total += sum(int(q.get('marks', 2)) for q in qs if isinstance(q, dict))
            else:
                c = int(sec.get('count') or 0)
                m = int(sec.get('marks_per_q') or 2)
                total += (c * m)
    return total


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
       - Part B: 5 Either/Or groups of 13 Marks each = 65 Marks (supporting 8+5 subquestions)
       - Part C: 1 Either/Or group of 15 Marks = 15 Marks
       - Unit and lesson coverage configurable according to syllabus/faculty requirements.
    """
    exam_type = str(paper_data.get('exam_type') or '').lower()
    sections = paper_data.get('sections') or []
    if isinstance(sections, str):
        try:
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

        sec_a = next((s for s in sections if 'A' in str(s.get('name', '')).upper()), None)
        if sec_a:
            q_list = sec_a.get('questions') or []
            if len(q_list) > 0 and len(q_list) != 5:
                return False, f"Validation Error: Section A of Internal Examination must contain exactly 5 compulsory questions (found {len(q_list)})."

        sec_b = next((s for s in sections if 'B' in str(s.get('name', '')).upper()), None)
        if sec_b:
            b_groups = sec_b.get('groups') or sec_b.get('either_or_groups') or []
            if len(b_groups) != 1:
                return False, f"Validation Error: Section B must contain exactly 1 Either/Or group of 8 marks (found {len(b_groups)})."

        sec_c = next((s for s in sections if 'C' in str(s.get('name', '')).upper()), None)
        if sec_c:
            c_groups = sec_c.get('groups') or sec_c.get('either_or_groups') or []
            if len(c_groups) != 2:
                return False, f"Validation Error: Section C must contain exactly 2 Either/Or groups of 16 marks each (found {len(c_groups)})."

    # 2. Semester Examination
    elif 'semester' in exam_type or 'model' in exam_type or 'end semester' in exam_type:
        if attempted_marks != 100:
            return False, f"Validation Error: Semester Examination must have exactly 100 attempted marks (calculated: {attempted_marks} marks). The marks calculation must count only the marks students actually attempt, not both Either/Or alternatives."

        sec_a = next((s for s in sections if 'A' in str(s.get('name', '')).upper()), None)
        if sec_a and sec_a.get('questions'):
            qs = sec_a['questions']
            if len(qs) != 10:
                return False, f"Validation Error: Section A of Semester Examination must have exactly 10 questions of 2 marks (found {len(qs)})."

        sec_b = next((s for s in sections if 'B' in str(s.get('name', '')).upper()), None)
        if sec_b:
            b_groups = sec_b.get('groups') or sec_b.get('either_or_groups') or []
            if len(b_groups) != 5:
                return False, f"Validation Error: Section B of Semester Examination must contain exactly 5 Either/Or groups of 13 marks each (found {len(b_groups)})."

        sec_c = next((s for s in sections if 'C' in str(s.get('name', '')).upper()), None)
        if sec_c:
            c_groups = sec_c.get('groups') or sec_c.get('either_or_groups') or []
            if len(c_groups) != 1:
                return False, f"Validation Error: Section C of Semester Examination must contain exactly 1 Either/Or group of 15 marks (found {len(c_groups)})."

    return True, ""


def generate_template_paper(faculty_id, data):
    """
    Automated Generator matching the college's actual examination question paper formats:
    1. Semester Examination (April May 2024 ML.pdf):
       - PART - A: 10 questions x 2 marks = 20 Marks
       - PART - B: 5 questions x 13 marks = 65 Marks (supporting 8+5 subquestions)
       - PART - C: 1 question x 15 marks = 15 Marks
       - Duration: Three Hours, Total Attempted: 100 Marks.
    2. Internal Examination (inter.pdf):
       - PART - A: 5 questions x 2 marks = 10 Marks
       - PART - B: 1 question x 8 marks = 8 Marks
       - PART - C: 2 questions x 16 marks = 32 Marks (supporting 8+8 subquestions)
       - Duration: 100 Mins., Total Attempted: 50 Marks.
    """
    template = str(data.get('template') or data.get('template_type') or 'internal_test').lower().strip()
    subject = (data.get('subject') or 'Database Management Systems').strip()
    department = (data.get('department') or 'Artificial Intelligence & Data Science').strip()
    academic_year = (data.get('academic_year') or '2025-2026').strip()
    semester = (data.get('semester') or 'Semester 6').strip()

    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT * FROM questions
            WHERE subject = %s AND department = %s
            ORDER BY is_in_bank DESC, id ASC
        """, (subject, department))
        all_q_rows = cur.fetchall()
        
        # Fallback if subject has few questions
        if len(all_q_rows) < 15:
            cur.execute("""
                SELECT * FROM questions
                WHERE subject = %s
                ORDER BY is_in_bank DESC, id ASC
            """, (subject,))
            all_q_rows = cur.fetchall()
            
    conn.close()

    if not all_q_rows:
        return False, {
            "status": "error",
            "message": f"No questions found in Question Bank for subject '{subject}'. Please add questions to the Question Bank."
        }, 400

    from services.question_service import format_question_dict
    all_questions = [format_question_dict(q) for q in all_q_rows]
    used_q_ids = set()

    if 'internal' in template:
        # =========================================================================
        # 1. INTERNAL EXAMINATION (Exact structure of inter.pdf)
        # =========================================================================
        # PART - A (5 X 2 = 10 Marks)
        avail_2m = [q for q in all_questions if q['marks'] == 2 and q['id'] not in used_q_ids]
        if len(avail_2m) < 5:
            return False, {
                "status": "error",
                "message": f"Insufficient 2-mark questions in Question Bank for Internal Examination Part A: requires 5 questions, but only {len(avail_2m)} available."
            }, 400

        secA_questions = avail_2m[:5]
        for q in secA_questions:
            used_q_ids.add(q['id'])
            q['co_tag'] = get_co_tag(q.get('unit'))
            q['bloom_tag'] = get_bloom_tag(q.get('bloom_level'))

        section_a = {
            "name": "PART - A (5 X 2 = 10 Marks)",
            "title": "PART - A (5 X 2 = 10 Marks)",
            "type": "compulsory",
            "instructions": "Answer ALL Questions",
            "count": 5,
            "marks_per_q": 2,
            "attempted_marks": 10,
            "total_marks": 10,
            "questions": secA_questions
        }

        # PART - B (1 X 8 = 8 Marks) — Question 6: Either/Or from different lessons
        avail_8m = [q for q in all_questions if q['marks'] == 8 and q['id'] not in used_q_ids]
        q_alt_a = None
        q_alt_b = None
        for i in range(len(avail_8m)):
            for j in range(i + 1, len(avail_8m)):
                if (avail_8m[i].get('topic') or '') != (avail_8m[j].get('topic') or ''):
                    q_alt_a = avail_8m[i]
                    q_alt_b = avail_8m[j]
                    break
            if q_alt_a and q_alt_b:
                break

        if not q_alt_a or not q_alt_b:
            if len(avail_8m) >= 2:
                q_alt_a, q_alt_b = avail_8m[0], avail_8m[1]
            else:
                return False, {
                    "status": "error",
                    "message": "Insufficient 8-mark questions in Question Bank for Internal Examination Part B (requires 2 questions for Alternative a vs b)."
                }, 400

        used_q_ids.add(q_alt_a['id'])
        used_q_ids.add(q_alt_b['id'])
        q_alt_a['co_tag'] = get_co_tag(q_alt_a.get('unit'))
        q_alt_b['co_tag'] = get_co_tag(q_alt_b.get('unit'))
        q_alt_a['bloom_tag'] = get_bloom_tag(q_alt_a.get('bloom_level'))
        q_alt_b['bloom_tag'] = get_bloom_tag(q_alt_b.get('bloom_level'))

        secB_group = {
            "group_number": 1,
            "question_number": 6,
            "attempted_marks": 8,
            "lesson_a": q_alt_a.get('topic') or 'Lesson A',
            "lesson_b": q_alt_b.get('topic') or 'Lesson B',
            "alternative_a": q_alt_a,
            "alternative_b": q_alt_b
        }

        section_b = {
            "name": "PART - B (1 X 8 = 8 Marks)",
            "title": "PART - B (1 X 8 = 8 Marks)",
            "type": "either_or",
            "instructions": "Answer EITHER Alternative (a) OR Alternative (b).",
            "count": 1,
            "marks_per_q": 8,
            "attempted_marks": 8,
            "total_marks": 8,
            "groups": [secB_group],
            "either_or_groups": [secB_group]
        }

        # PART - C (2 X 16 = 32 Marks) — Questions 7 and 8 (supporting 16m single or 8+8 subquestions)
        def build_16m_alt_it(pool):
            cand_16 = [q for q in pool if q['marks'] == 16 and q['id'] not in used_q_ids]
            if cand_16:
                sel = cand_16[0]
                used_q_ids.add(sel['id'])
                sel['co_tag'] = get_co_tag(sel.get('unit'))
                sel['bloom_tag'] = get_bloom_tag(sel.get('bloom_level'))
                return sel
            cand_8 = [q for q in pool if q['marks'] == 8 and q['id'] not in used_q_ids]
            if len(cand_8) >= 2:
                s1, s2 = cand_8[0], cand_8[1]
                used_q_ids.add(s1['id'])
                used_q_ids.add(s2['id'])
                s1['co_tag'] = get_co_tag(s1.get('unit'))
                s2['co_tag'] = get_co_tag(s2.get('unit'))
                s1['bloom_tag'] = get_bloom_tag(s1.get('bloom_level'))
                s2['bloom_tag'] = get_bloom_tag(s2.get('bloom_level'))
                return {
                    "is_subquestion": True,
                    "marks": 16,
                    "unit": s1.get('unit') or 'Unit III',
                    "topic": s1.get('topic') or 'Advanced Topic',
                    "subquestions": [
                        {"part": "(i)", "id": s1['id'], "text": s1['question_text'], "marks": 8, "co_tag": s1['co_tag'], "bloom_tag": s1['bloom_tag'], "topic": s1.get('topic')},
                        {"part": "(ii)", "id": s2['id'], "text": s2['question_text'], "marks": 8, "co_tag": s2['co_tag'], "bloom_tag": s2['bloom_tag'], "topic": s2.get('topic')}
                    ]
                }
            return None

        pool_c = all_questions
        c1_alt_a = build_16m_alt_it(pool_c)
        c1_alt_b = build_16m_alt_it(pool_c)
        c2_alt_a = build_16m_alt_it(pool_c)
        c2_alt_b = build_16m_alt_it(pool_c)

        if not c1_alt_a or not c1_alt_b or not c2_alt_a or not c2_alt_b:
            return False, {
                "status": "error",
                "message": "Insufficient 16-mark or 8-mark questions in Question Bank for Internal Examination Part C (requires 4 alternatives across Questions 7 and 8)."
            }, 400

        secC_groups = [
            {
                "group_number": 1,
                "question_number": 7,
                "attempted_marks": 16,
                "alternative_a": c1_alt_a,
                "alternative_b": c1_alt_b
            },
            {
                "group_number": 2,
                "question_number": 8,
                "attempted_marks": 16,
                "alternative_a": c2_alt_a,
                "alternative_b": c2_alt_b
            }
        ]

        section_c = {
            "name": "PART - C (2 X 16 = 32 Marks)",
            "title": "PART - C (2 X 16 = 32 Marks)",
            "type": "either_or",
            "instructions": "Answer EITHER Alternative (a) OR Alternative (b) from each question.",
            "count": 2,
            "marks_per_q": 16,
            "attempted_marks": 32,
            "total_marks": 32,
            "groups": secC_groups,
            "either_or_groups": secC_groups
        }

        sections = [section_a, section_b, section_c]
        total_attempted = calculate_attempted_marks(sections)
        exam_type = "Internal Examination"
        title = f"{subject} Internal Examination"
        duration = "100 Mins."
        instructions = "1. Answer ALL Questions.\n2. Part A: 5 Questions x 2 Marks = 10 Marks.\n3. Part B: 1 Question x 8 Marks = 8 Marks.\n4. Part C: 2 Questions x 16 Marks = 32 Marks.\n5. Maximum Attempted Marks: 50 Marks."

    else:
        # =========================================================================
        # 2. SEMESTER EXAMINATION (Exact structure of April May 2024 ML.pdf)
        # =========================================================================
        # PART - A (10 x 2 = 20 Marks): Questions 1 to 10
        avail_2m = [q for q in all_questions if q['marks'] == 2 and q['id'] not in used_q_ids]
        if len(avail_2m) < 10:
            return False, {
                "status": "error",
                "message": f"Insufficient 2-mark questions in Question Bank for Semester Examination Part A: requires 10 questions, but only {len(avail_2m)} available."
            }, 400

        secA_questions = avail_2m[:10]
        for q in secA_questions:
            used_q_ids.add(q['id'])
            q['bloom_tag'] = get_bloom_tag(q.get('bloom_level'))

        section_a = {
            "name": "PART - A (10 x 2 = 20 Marks)",
            "title": "PART - A (10 x 2 = 20 Marks)",
            "type": "compulsory",
            "instructions": "Answer ALL Questions",
            "count": 10,
            "marks_per_q": 2,
            "attempted_marks": 20,
            "total_marks": 20,
            "questions": secA_questions
        }

        # PART - B (5 x 13 = 65 Marks): Questions 11 to 15 (supporting 8+5 subquestions or 13m single)
        units = ["Unit I", "Unit II", "Unit III", "Unit IV", "Unit V"]
        secB_groups = []

        for i, u in enumerate(units, 1):
            pool_u = [q for q in all_questions if normalize_unit(q.get('unit')) == u and q['id'] not in used_q_ids]
            if not pool_u:
                pool_u = [q for q in all_questions if q['id'] not in used_q_ids]

            cand_13 = [q for q in pool_u if q['marks'] == 13 and q['id'] not in used_q_ids]
            cand_8 = [q for q in pool_u if q['marks'] == 8 and q['id'] not in used_q_ids]
            cand_5 = [q for q in pool_u if q['marks'] == 5 and q['id'] not in used_q_ids]

            alt_a = None
            # Alternate between (8+5) subquestions and 13m single to replicate reference paper pattern
            if (i in [1, 5] or not cand_13) and len(cand_8) >= 1 and len(cand_5) >= 1:
                q8, q5 = cand_8[0], cand_5[0]
                used_q_ids.add(q8['id'])
                used_q_ids.add(q5['id'])
                q8['bloom_tag'] = get_bloom_tag(q8.get('bloom_level'))
                q5['bloom_tag'] = get_bloom_tag(q5.get('bloom_level'))
                alt_a = {
                    "is_subquestion": True,
                    "marks": 13,
                    "unit": u,
                    "topic": q8.get('topic') or f"{u} Lesson A",
                    "subquestions": [
                        {"part": "(i)", "id": q8['id'], "text": q8['question_text'], "marks": 8, "bloom_tag": q8['bloom_tag'], "topic": q8.get('topic')},
                        {"part": "(ii)", "id": q5['id'], "text": q5['question_text'], "marks": 5, "bloom_tag": q5['bloom_tag'], "topic": q5.get('topic')}
                    ]
                }
            elif cand_13:
                q13 = cand_13[0]
                used_q_ids.add(q13['id'])
                q13['bloom_tag'] = get_bloom_tag(q13.get('bloom_level'))
                alt_a = q13

            # Alt B
            pool_u_b = [q for q in all_questions if normalize_unit(q.get('unit')) == u and q['id'] not in used_q_ids]
            if not pool_u_b:
                pool_u_b = [q for q in all_questions if q['id'] not in used_q_ids]

            cand_13_b = [q for q in pool_u_b if q['marks'] == 13 and q['id'] not in used_q_ids]
            cand_8_b = [q for q in pool_u_b if q['marks'] == 8 and q['id'] not in used_q_ids]
            cand_5_b = [q for q in pool_u_b if q['marks'] == 5 and q['id'] not in used_q_ids]

            alt_b = None
            if cand_13_b:
                q13_b = cand_13_b[0]
                used_q_ids.add(q13_b['id'])
                q13_b['bloom_tag'] = get_bloom_tag(q13_b.get('bloom_level'))
                alt_b = q13_b
            elif len(cand_8_b) >= 1 and len(cand_5_b) >= 1:
                q8_b, q5_b = cand_8_b[0], cand_5_b[0]
                used_q_ids.add(q8_b['id'])
                used_q_ids.add(q5_b['id'])
                q8_b['bloom_tag'] = get_bloom_tag(q8_b.get('bloom_level'))
                q5_b['bloom_tag'] = get_bloom_tag(q5_b.get('bloom_level'))
                alt_b = {
                    "is_subquestion": True,
                    "marks": 13,
                    "unit": u,
                    "topic": q8_b.get('topic') or f"{u} Lesson B",
                    "subquestions": [
                        {"part": "(i)", "id": q8_b['id'], "text": q8_b['question_text'], "marks": 8, "bloom_tag": q8_b['bloom_tag'], "topic": q8_b.get('topic')},
                        {"part": "(ii)", "id": q5_b['id'], "text": q5_b['question_text'], "marks": 5, "bloom_tag": q5_b['bloom_tag'], "topic": q5_b.get('topic')}
                    ]
                }

            if not alt_a or not alt_b:
                return False, {
                    "status": "error",
                    "message": f"Insufficient questions in Question Bank for Semester Examination Part B: {u} requires questions totaling 13 marks for both Alternative (a) and Alternative (b) (either 13m questions or 8m + 5m subquestions)."
                }, 400

            secB_groups.append({
                "group_number": i,
                "question_number": 10 + i,
                "unit": u,
                "attempted_marks": 13,
                "alternative_a": alt_a,
                "alternative_b": alt_b
            })

        section_b = {
            "name": "PART - B (5 x 13 = 65 Marks)",
            "title": "PART - B (5 x 13 = 65 Marks)",
            "type": "either_or",
            "instructions": "Answer EITHER Alternative (a) OR Alternative (b) from each question.",
            "count": 5,
            "marks_per_q": 13,
            "attempted_marks": 65,
            "total_marks": 65,
            "groups": secB_groups,
            "either_or_groups": secB_groups
        }

        # PART - C (1 x 15 = 15 Marks): Question 16
        cand_15 = [q for q in all_questions if q['marks'] == 15 and q['id'] not in used_q_ids]
        if len(cand_15) < 2:
            cand_15 = [q for q in all_questions if q['marks'] == 15]

        if len(cand_15) < 2:
            return False, {
                "status": "error",
                "message": "Insufficient 15-mark questions in Question Bank for Semester Examination Part C (requires 2 questions for Alternative a vs b)."
            }, 400

        q16_a = cand_15[0]
        q16_b = cand_15[1]
        used_q_ids.add(q16_a['id'])
        used_q_ids.add(q16_b['id'])
        q16_a['bloom_tag'] = get_bloom_tag(q16_a.get('bloom_level'))
        q16_b['bloom_tag'] = get_bloom_tag(q16_b.get('bloom_level'))

        secC_groups = [{
            "group_number": 1,
            "question_number": 16,
            "attempted_marks": 15,
            "alternative_a": q16_a,
            "alternative_b": q16_b
        }]

        section_c = {
            "name": "PART - C (1 x 15 = 15 Marks)",
            "title": "PART - C (1 x 15 = 15 Marks)",
            "type": "either_or",
            "instructions": "Answer EITHER Alternative (a) OR Alternative (b).",
            "count": 1,
            "marks_per_q": 15,
            "attempted_marks": 15,
            "total_marks": 15,
            "groups": secC_groups,
            "either_or_groups": secC_groups
        }

        sections = [section_a, section_b, section_c]
        total_attempted = calculate_attempted_marks(sections)
        exam_type = "Semester Examination"
        title = f"{subject} End Semester Theory Examinations"
        duration = "Three Hours"
        instructions = "1. Answer ALL Questions.\n2. Part A: 10 Questions x 2 Marks = 20 Marks.\n3. Part B: 5 Questions x 13 Marks = 65 Marks.\n4. Part C: 1 Question x 15 Marks = 15 Marks.\n5. Maximum Attempted Marks: 100 Marks."

    paper_data = {
        "title": title,
        "subject": subject,
        "department": department,
        "academic_year": academic_year,
        "semester": semester,
        "exam_type": exam_type,
        "total_marks": total_attempted,
        "max_marks": total_attempted,
        "duration": duration,
        "instructions": instructions,
        "sections": sections,
        "question_ids": sorted(list(used_q_ids))
    }

    valid, err_msg = validate_question_paper_structure(paper_data, total_attempted)
    if not valid:
        return False, {"status": "error", "message": f"Generated paper failed validation: {err_msg}"}, 400

    return True, {
        "status": "success",
        "message": f"Successfully generated {title} with {total_attempted} attempted marks.",
        "paper": paper_data,
        "total_attempted_marks": total_attempted
    }, 200
'''

def main():
    with open(SERVICE_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    cutoff_idx = content.find('def calculate_attempted_marks')
    if cutoff_idx == -1:
        print("Error: calculate_attempted_marks not found")
        sys.exit(1)

    clean_prefix = content[:cutoff_idx].rstrip()
    updated_service = clean_prefix + "\n" + NEW_FUNCTIONS.lstrip()

    with open(SERVICE_PATH, 'w', encoding='utf-8') as f:
        f.write(updated_service)

    print("Updated backend/services/question_paper_service.py successfully!")

if __name__ == '__main__':
    main()
