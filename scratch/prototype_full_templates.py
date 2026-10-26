# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\backend")

from models.database import get_db_connection
from services.question_service import format_question_dict
from services.question_paper_service import normalize_unit

def get_bloom_tag(bloom_level):
    b = str(bloom_level).lower().strip()
    if 'rem' in b: return '[RE]'
    if 'und' in b: return '[UN]'
    if 'app' in b: return '[AP]'
    if 'ana' in b: return '[AN]'
    if 'eva' in b: return '[EV]'
    if 'cre' in b: return '[CR]'
    return '[UN]'

def get_co_tag(unit_str):
    norm = normalize_unit(unit_str)
    if 'I' == norm.replace('Unit ', ''): return '(CO1)'
    if 'II' == norm.replace('Unit ', ''): return '(CO2)'
    if 'III' == norm.replace('Unit ', ''): return '(CO3)'
    if 'IV' == norm.replace('Unit ', ''): return '(CO4)'
    if 'V' == norm.replace('Unit ', ''): return '(CO5)'
    return '(CO3)'

def calculate_attempted_marks_v2(sections):
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

def run_test():
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM questions WHERE subject = 'Machine Learning' ORDER BY is_in_bank DESC, id ASC")
        ml_rows = cur.fetchall()
        cur.execute("SELECT * FROM questions WHERE subject = 'Database Management Systems' ORDER BY is_in_bank DESC, id ASC")
        dbms_rows = cur.fetchall()
    conn.close()

    for name, rows in [("Machine Learning", ml_rows), ("Database Management Systems", dbms_rows)]:
        all_questions = [format_question_dict(r) for r in rows]
        print(f"\n=================== TESTING {name.upper()} ===================")
        print(f"Total Questions in Pool: {len(all_questions)}")

        # 1. Test Semester Exam (100 Marks, April May 2024 ML pattern)
        used_q_ids = set()
        
        # Part A: 10 x 2 = 20 Marks
        avail_2m = [q for q in all_questions if q['marks'] == 2 and q['id'] not in used_q_ids]
        sec_a_q = avail_2m[:10]
        for q in sec_a_q:
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
            "questions": sec_a_q
        }

        # Part B: 5 x 13 = 65 Marks (Questions 11 to 15)
        units = ["Unit I", "Unit II", "Unit III", "Unit IV", "Unit V"]
        sec_b_groups = []

        for i, u in enumerate(units, 1):
            pool_u = [q for q in all_questions if normalize_unit(q.get('unit')) == u and q['id'] not in used_q_ids]
            
            # Alt A: try subquestion (8+5) or single 13
            alt_a = None
            cand_13 = [q for q in pool_u if q['marks'] == 13 and q['id'] not in used_q_ids]
            cand_8 = [q for q in pool_u if q['marks'] == 8 and q['id'] not in used_q_ids]
            cand_5 = [q for q in pool_u if q['marks'] == 5 and q['id'] not in used_q_ids]

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

            # Alt B:
            pool_u_b = [q for q in all_questions if normalize_unit(q.get('unit')) == u and q['id'] not in used_q_ids]
            cand_13_b = [q for q in pool_u_b if q['marks'] == 13]
            cand_8_b = [q for q in pool_u_b if q['marks'] == 8]
            cand_5_b = [q for q in pool_u_b if q['marks'] == 5]
            
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

            sec_b_groups.append({
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
            "groups": sec_b_groups,
            "either_or_groups": sec_b_groups
        }

        # Part C: 1 x 15 = 15 Marks (Question 16)
        cand_15 = [q for q in all_questions if q['marks'] == 15 and q['id'] not in used_q_ids]
        q16_a, q16_b = cand_15[0], cand_15[1]
        used_q_ids.add(q16_a['id'])
        used_q_ids.add(q16_b['id'])
        q16_a['bloom_tag'] = get_bloom_tag(q16_a.get('bloom_level'))
        q16_b['bloom_tag'] = get_bloom_tag(q16_b.get('bloom_level'))

        sec_c_group = [{
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
            "groups": sec_c_group,
            "either_or_groups": sec_c_group
        }

        sem_sections = [section_a, section_b, section_c]
        sem_attempted = calculate_attempted_marks_v2(sem_sections)
        print(f"  -> Semester Exam Generated! Attempted Marks: {sem_attempted}")
        assert sem_attempted == 100, f"Semester attempted marks must be 100, got {sem_attempted}"

        # 2. Test Internal Exam (50 Marks, inter.pdf pattern)
        used_q_ids_it = set()
        avail_2m_it = [q for q in all_questions if q['marks'] == 2 and q['id'] not in used_q_ids_it]
        sec_a_it = avail_2m_it[:5]
        for q in sec_a_it:
            used_q_ids_it.add(q['id'])
            q['co_tag'] = get_co_tag(q.get('unit'))
            q['bloom_tag'] = get_bloom_tag(q.get('bloom_level'))

        sec_a_it_obj = {
            "name": "PART - A (5 X 2 = 10 Marks)",
            "title": "PART - A (5 X 2 = 10 Marks)",
            "type": "compulsory",
            "instructions": "Answer ALL Questions",
            "count": 5,
            "marks_per_q": 2,
            "attempted_marks": 10,
            "total_marks": 10,
            "questions": sec_a_it
        }

        # Part B: 1 x 8 = 8 Marks (Question 6)
        avail_8m_it = [q for q in all_questions if q['marks'] == 8 and q['id'] not in used_q_ids_it]
        q6_a = avail_8m_it[0]
        q6_b = avail_8m_it[1]
        used_q_ids_it.add(q6_a['id'])
        used_q_ids_it.add(q6_b['id'])
        q6_a['co_tag'] = get_co_tag(q6_a.get('unit'))
        q6_b['co_tag'] = get_co_tag(q6_b.get('unit'))
        q6_a['bloom_tag'] = get_bloom_tag(q6_a.get('bloom_level'))
        q6_b['bloom_tag'] = get_bloom_tag(q6_b.get('bloom_level'))

        sec_b_it_groups = [{
            "group_number": 1,
            "question_number": 6,
            "attempted_marks": 8,
            "alternative_a": q6_a,
            "alternative_b": q6_b
        }]

        sec_b_it_obj = {
            "name": "PART - B (1 X 8 = 8 Marks)",
            "title": "PART - B (1 X 8 = 8 Marks)",
            "type": "either_or",
            "instructions": "Answer EITHER Alternative (a) OR Alternative (b).",
            "count": 1,
            "marks_per_q": 8,
            "attempted_marks": 8,
            "total_marks": 8,
            "groups": sec_b_it_groups,
            "either_or_groups": sec_b_it_groups
        }

        # Part C: 2 x 16 = 32 Marks (Questions 7 & 8)
        # Supporting 16m single or 8+8 subquestions
        def build_16m(pool):
            cand_16 = [q for q in pool if q['marks'] == 16 and q['id'] not in used_q_ids_it]
            if cand_16:
                sel = cand_16[0]
                used_q_ids_it.add(sel['id'])
                sel['co_tag'] = get_co_tag(sel.get('unit'))
                sel['bloom_tag'] = get_bloom_tag(sel.get('bloom_level'))
                return sel
            cand_8 = [q for q in pool if q['marks'] == 8 and q['id'] not in used_q_ids_it]
            if len(cand_8) >= 2:
                s1, s2 = cand_8[0], cand_8[1]
                used_q_ids_it.add(s1['id'])
                used_q_ids_it.add(s2['id'])
                s1['co_tag'] = get_co_tag(s1.get('unit'))
                s2['co_tag'] = get_co_tag(s2.get('unit'))
                s1['bloom_tag'] = get_bloom_tag(s1.get('bloom_level'))
                s2['bloom_tag'] = get_bloom_tag(s2.get('bloom_level'))
                return {
                    "is_subquestion": True,
                    "marks": 16,
                    "subquestions": [
                        {"part": "(i)", "id": s1['id'], "text": s1['question_text'], "marks": 8, "co_tag": s1['co_tag'], "bloom_tag": s1['bloom_tag']},
                        {"part": "(ii)", "id": s2['id'], "text": s2['question_text'], "marks": 8, "co_tag": s2['co_tag'], "bloom_tag": s2['bloom_tag']}
                    ]
                }
            return None

        q7_a = build_16m(all_questions)
        q7_b = build_16m(all_questions)
        q8_a = build_16m(all_questions)
        q8_b = build_16m(all_questions)

        sec_c_it_groups = [
            {"group_number": 1, "question_number": 7, "attempted_marks": 16, "alternative_a": q7_a, "alternative_b": q7_b},
            {"group_number": 2, "question_number": 8, "attempted_marks": 16, "alternative_a": q8_a, "alternative_b": q8_b}
        ]

        sec_c_it_obj = {
            "name": "PART - C (2 X 16 = 32 Marks)",
            "title": "PART - C (2 X 16 = 32 Marks)",
            "type": "either_or",
            "instructions": "Answer EITHER Alternative (a) OR Alternative (b) from each question.",
            "count": 2,
            "marks_per_q": 16,
            "attempted_marks": 32,
            "total_marks": 32,
            "groups": sec_c_it_groups,
            "either_or_groups": sec_c_it_groups
        }

        it_sections = [sec_a_it_obj, sec_b_it_obj, sec_c_it_obj]
        it_attempted = calculate_attempted_marks_v2(it_sections)
        print(f"  -> Internal Exam Generated! Attempted Marks: {it_attempted}")
        assert it_attempted == 50, f"Internal attempted marks must be 50, got {it_attempted}"

if __name__ == '__main__':
    run_test()
