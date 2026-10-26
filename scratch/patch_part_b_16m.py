import sys

path = r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\backend\services\question_paper_service.py"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Normalize CRLF to LF for reliable substring replacement
content_lf = content.replace("\r\n", "\n")

# 1. Update validate_question_paper_structure Semester Exam portion
old_val = """    # 2. Semester Examination
    elif 'semester' in exam_type or 'model' in exam_type or 'end semester' in exam_type:
        if attempted_marks != 100:
            return False, f"Validation Error: Semester Examination must have exactly 100 attempted marks (calculated: {attempted_marks} marks). The marks calculation must count only the marks students actually attempt, not both Either/Or alternatives."

        sec_a = next((s for s in sections if 'A' in str(s.get('name') or s.get('title') or '').upper()), None)
        if sec_a and sec_a.get('questions'):
            qs = sec_a['questions']
            if len(qs) != 10:
                return False, f"Validation Error: Section A of Semester Examination must have exactly 10 questions of 2 marks (found {len(qs)})."

        sec_b = next((s for s in sections if 'B' in str(s.get('name') or s.get('title') or '').upper()), None)
        if sec_b:
            b_groups = sec_b.get('groups') or sec_b.get('either_or_groups') or []
            if len(b_groups) != 5:
                return False, f"Validation Error: Section B of Semester Examination must contain exactly 5 Either/Or groups of 13 marks each (found {len(b_groups)})."

        sec_c = next((s for s in sections if 'C' in str(s.get('name') or s.get('title') or '').upper()), None)
        if sec_c:
            c_groups = sec_c.get('groups') or sec_c.get('either_or_groups') or []
            if len(c_groups) != 1:
                return False, f"Validation Error: Section C of Semester Examination must contain exactly 1 Either/Or group of 15 marks (found {len(c_groups)})."

    return True, \"\""""

new_val = """    # 2. Semester Examination
    elif 'semester' in exam_type or 'model' in exam_type or 'end semester' in exam_type or attempted_marks == 100:
        if attempted_marks != 100:
            return False, f"Validation Error: Semester Examination must have exactly 100 attempted marks (calculated: {attempted_marks} marks). The marks calculation must count only the marks students actually attempt, not both Either/Or alternatives."

        # The Semester Examination must contain only Part A and Part B. Do not add Part C.
        sec_c = next((s for s in sections if 'C' in str(s.get('name') or s.get('title') or '').upper()), None)
        if sec_c:
            return False, "Validation Error: The Semester Examination must contain only Part A and Part B. Do not add Part C."

        sec_a = next((s for s in sections if 'A' in str(s.get('name') or s.get('title') or '').upper()), None)
        if not sec_a:
            return False, "Validation Error: Semester Examination must contain Part A."
        qs = sec_a.get('questions') or []
        if len(qs) != 10:
            return False, f"Validation Error: Section A of Semester Examination must have exactly 10 compulsory questions of 2 marks (found {len(qs)})."
        for idx, q in enumerate(qs, start=1):
            if int(q.get('marks', 2)) != 2:
                return False, f"Validation Error: Part A Question {idx} must be worth 2 marks (found {q.get('marks')})."

        sec_b = next((s for s in sections if 'B' in str(s.get('name') or s.get('title') or '').upper()), None)
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
                    m = sum(int(q.get('marks', 0)) for q in alt)
                    if m != 16:
                        return f"In Part B Question {q_num}, Alternative ({letter}) must represent exactly 16 marks (found {m} marks)."
                    return None
                elif isinstance(alt, dict):
                    if alt.get('is_subquestion') or alt.get('subquestions'):
                        subs = alt.get('subquestions') or []
                        if len(subs) != 2:
                            return f"In Part B Question {q_num}, Split Alternative ({letter}) must contain exactly two 8-mark subquestions (found {len(subs)})."
                        sub_sum = sum(int(sq.get('marks', 0)) for sq in subs)
                        if sub_sum != 16:
                            return f"In Part B Question {q_num}, Split Alternative ({letter}) subquestions must combine to exactly 16 marks (found {sub_sum} marks: {subs[0].get('marks')} + {subs[1].get('marks')})."
                        return None
                    else:
                        m = int(alt.get('marks', 0))
                        if m != 16:
                            return f"In Part B Question {q_num}, Direct Alternative ({letter}) must be worth exactly 16 marks (found {m} marks)."
                        return None
                return f"In Part B Question {q_num}, Alternative ({letter}) has invalid data structure."

            err_a = validate_alternative(grp.get('alternative_a') or grp.get('option_a'), 'a')
            if err_a:
                return False, f"Validation Error: {err_a} Each alternative must represent exactly 16 marks (either Direct 16M or Split 8 + 8)."

            err_b = validate_alternative(grp.get('alternative_b') or grp.get('option_b'), 'b')
            if err_b:
                return False, f"Validation Error: {err_b} Each alternative must represent exactly 16 marks (either Direct 16M or Split 8 + 8)."

    return True, \"\""""

assert old_val in content_lf, "old_val not found in content_lf"
content_lf = content_lf.replace(old_val, new_val)

# 2. Update generate_template_paper Part B & Part C block for Semester Exam
start_marker = "        # PART - B (5 x 13 = 65 Marks): Questions 11 to 15 (supporting 8+5 subquestions or 13m single)"
end_marker = "        instructions = \"1. Answer ALL Questions.\\n2. Part A: 10 Questions x 2 Marks = 20 Marks.\\n3. Part B: 5 Questions x 13 Marks = 65 Marks.\\n4. Part C: 1 Question x 15 Marks = 15 Marks.\\n5. Maximum Attempted Marks: 100 Marks.\""

assert start_marker in content_lf, "start_marker not found in content_lf"
assert end_marker in content_lf, "end_marker not found in content_lf"

pos_start = content_lf.find(start_marker)
pos_end = content_lf.find(end_marker) + len(end_marker)

new_sem_block = """        # PART - B (5 x 16 = 80 Marks): Questions 11 to 15 (Units I to V)
        # Each group has Either/Or choice between Alternative (a) and Alternative (b)
        # Supports flexible Direct 16-Mark Question OR Split 16-Mark Question (8 + 8)
        units = ["Unit I", "Unit II", "Unit III", "Unit IV", "Unit V"]
        secB_groups = []

        part_b_formats = data.get('part_b_formats') or data.get('formats') or {}

        # Default formats if none specified: balanced combination demonstrating both formats
        default_formats = [
            {'option_a': 'direct', 'option_b': 'split'},   # Q11: Direct vs Split
            {'option_a': 'split',  'option_b': 'direct'},  # Q12: Split vs Direct
            {'option_a': 'direct', 'option_b': 'direct'},  # Q13: Direct vs Direct
            {'option_a': 'split',  'option_b': 'split'},   # Q14: Split vs Split
            {'option_a': 'split',  'option_b': 'direct'},  # Q15: Split vs Direct
        ]

        for i, u in enumerate(units, 1):
            q_num = 10 + i
            fmt_pref = part_b_formats.get(f"q{q_num}") or part_b_formats.get(str(i)) or default_formats[i-1]
            fmt_a = fmt_pref.get('option_a') or fmt_pref.get('alternative_a') or 'direct'
            fmt_b = fmt_pref.get('option_b') or fmt_pref.get('alternative_b') or 'split'

            pool_u = [q for q in all_questions if normalize_unit(q.get('unit')) == u and q['id'] not in used_q_ids]
            if not pool_u:
                pool_u = [q for q in all_questions if q['id'] not in used_q_ids]

            def build_alt(target_fmt, letter):
                cand_16 = [q for q in pool_u if q['marks'] == 16 and q['id'] not in used_q_ids]
                cand_8 = [q for q in pool_u if q['marks'] == 8 and q['id'] not in used_q_ids]

                if target_fmt == 'direct' and not cand_16:
                    cand_16 = [q for q in all_questions if q['marks'] == 16 and q['id'] not in used_q_ids]
                if target_fmt == 'split' and len(cand_8) < 2:
                    cand_8 = [q for q in all_questions if q['marks'] == 8 and q['id'] not in used_q_ids]

                if target_fmt == 'direct':
                    if cand_16:
                        q16 = dict(cand_16[0])
                        used_q_ids.add(q16['id'])
                        q16['bloom_tag'] = get_bloom_tag(q16.get('bloom_level'))
                        q16['format'] = 'direct'
                        q16['is_subquestion'] = False
                        return q16
                    elif len(cand_8) >= 2:
                        target_fmt = 'split'
                    else:
                        return None

                if target_fmt == 'split':
                    if len(cand_8) >= 2:
                        q8_1, q8_2 = dict(cand_8[0]), dict(cand_8[1])
                        used_q_ids.add(q8_1['id'])
                        used_q_ids.add(q8_2['id'])
                        q8_1['bloom_tag'] = get_bloom_tag(q8_1.get('bloom_level'))
                        q8_2['bloom_tag'] = get_bloom_tag(q8_2.get('bloom_level'))
                        return {
                            "format": "split",
                            "is_subquestion": True,
                            "marks": 16,
                            "unit": u,
                            "topic": q8_1.get('topic') or f"{u} Topics",
                            "subquestions": [
                                {
                                    "part": "(i)",
                                    "id": q8_1['id'],
                                    "text": q8_1['question_text'],
                                    "question_text": q8_1['question_text'],
                                    "marks": 8,
                                    "bloom_tag": q8_1['bloom_tag'],
                                    "bloom_level": q8_1.get('bloom_level'),
                                    "topic": q8_1.get('topic')
                                },
                                {
                                    "part": "(ii)",
                                    "id": q8_2['id'],
                                    "text": q8_2['question_text'],
                                    "question_text": q8_2['question_text'],
                                    "marks": 8,
                                    "bloom_tag": q8_2['bloom_tag'],
                                    "bloom_level": q8_2.get('bloom_level'),
                                    "topic": q8_2.get('topic')
                                }
                            ]
                        }
                    elif cand_16:
                        q16 = dict(cand_16[0])
                        used_q_ids.add(q16['id'])
                        q16['bloom_tag'] = get_bloom_tag(q16.get('bloom_level'))
                        q16['format'] = 'direct'
                        q16['is_subquestion'] = False
                        return q16
                    else:
                        return None
                return None

            alt_a = build_alt(fmt_a, 'a')
            alt_b = build_alt(fmt_b, 'b')

            if not alt_a or not alt_b:
                return False, {
                    "status": "error",
                    "message": f"Insufficient questions in Question Bank for Semester Examination Part B: {u} requires questions totaling 16 marks for both Alternative (a) and Alternative (b) (either Direct 16M or Split 8+8)."
                }, 400

            secB_groups.append({
                "group_number": i,
                "question_number": q_num,
                "unit": u,
                "attempted_marks": 16,
                "alternative_a": alt_a,
                "alternative_b": alt_b
            })

        section_b = {
            "name": "PART - B (5 x 16 = 80 Marks)",
            "title": "PART - B (5 x 16 = 80 Marks)",
            "type": "either_or",
            "instructions": "Answer EITHER Alternative (a) OR Alternative (b) from each question.",
            "count": 5,
            "marks_per_q": 16,
            "attempted_marks": 80,
            "total_marks": 80,
            "groups": secB_groups,
            "either_or_groups": secB_groups
        }

        # The Semester Examination must contain only Part A and Part B. Do not add Part C.
        sections = [section_a, section_b]
        total_attempted = calculate_attempted_marks(sections)
        exam_type = "Semester Examination"
        title = f"{subject} End Semester Theory Examinations"
        duration = "Three Hours"
        instructions = "1. Answer ALL Questions from PART - A.\\n2. Answer EITHER Alternative (a) OR Alternative (b) from each Question in PART - B.\\n3. PART - A: 10 Questions x 2 Marks = 20 Marks.\\n4. PART - B: 5 Questions x 16 Marks = 80 Marks.\\n5. Maximum Attempted Marks: 100 Marks.\""""

content_lf = content_lf[:pos_start] + new_sem_block + content_lf[pos_end:]

content_crlf = content_lf.replace("\n", "\r\n")
with open(path, "w", encoding="utf-8") as f:
    f.write(content_crlf)

print("backend/services/question_paper_service.py patched successfully.")
