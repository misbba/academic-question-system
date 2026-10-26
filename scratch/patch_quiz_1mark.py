import re
import os
import sys

BASE_DIR = r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system"

def patch_document_parser():
    path = os.path.join(BASE_DIR, "backend", "utils", "document_parser.py")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Validation check
    old_val = re.search(r"# Validate requested marks: must be 2, 8, 16 or Mixed\s*req_marks = str\(config\.get\('marks'\) or config\.get\('marks_per_question'\) or ''\)\.strip\(\)\s*if req_marks and req_marks not in \('2', '8', '16', 'Mixed', 'mixed', 'Balanced', 'balanced', 'all', 'ALL', ''\):\s*return \{\s*\"status\": \"error\",\s*\"message\": f\"Invalid marks requested: '\{req_marks\}'\. Only 2, 8, and 16 marks are supported\.\"\s*\}", content)
    if not old_val:
        print("[WARN] Could not regex match old_val in document_parser.py, checking manual match")
        target = "    # Validate requested marks: must be 2, 8, 16 or Mixed\n    req_marks = str(config.get('marks') or config.get('marks_per_question') or '').strip()\n    if req_marks and req_marks not in ('2', '8', '16', 'Mixed', 'mixed', 'Balanced', 'balanced', 'all', 'ALL', ''):\n        return {\n            \"status\": \"error\",\n            \"message\": f\"Invalid marks requested: '{req_marks}'. Only 2, 8, and 16 marks are supported.\"\n        }"
        target_crlf = target.replace("\n", "\r\n")
        assert target in content or target_crlf in content, "Failed to find marks validation block in document_parser.py"
    
    new_val = (
        "    # Validate requested marks:\n"
        "    req_marks = str(config.get('marks') or config.get('marks_per_question') or '').strip()\n"
        "    if is_quiz:\n"
        "        # Quiz Generator specifically supports 1 mark questions (along with 2, 8, 16 marks)\n"
        "        if req_marks and req_marks not in ('1', '2', '8', '16', 'Mixed', 'mixed', 'Balanced', 'balanced', 'all', 'ALL', ''):\n"
        "            return {\n"
        "                \"status\": \"error\",\n"
        "                \"message\": f\"Invalid marks requested: '{req_marks}'. Quiz Generator supports 1 mark questions (or 2, 8, 16 marks).\"\n"
        "            }\n"
        "    else:\n"
        "        # All other academic question and examination workflows must strictly support ONLY 2, 8, and 16 marks\n"
        "        if req_marks and req_marks not in ('2', '8', '16', 'Mixed', 'mixed', 'Balanced', 'balanced', 'all', 'ALL', ''):\n"
        "            return {\n"
        "                \"status\": \"error\",\n"
        "                \"message\": f\"Invalid marks requested: '{req_marks}'. Only 2, 8, and 16 marks are supported.\"\n"
        "            }"
    )
    if old_val:
        content = content[:old_val.start()] + new_val + content[old_val.end():]
    else:
        if target in content:
            content = content.replace(target, new_val, 1)
        else:
            content = content.replace(target_crlf, new_val.replace("\n", "\r\n"), 1)

    # 2. Determine marks
    old_det = (
        "        # Determine marks for this question strictly in (2, 8, 16)\n"
        "        if req_marks in ('2', '8', '16'):\n"
        "            q_marks = int(req_marks)\n"
        "        else:\n"
        "            # Mixed marks: 40% 2M, 40% 8M, 20% 16M\n"
        "            cut2 = max(1, round(num_questions * 0.4))\n"
        "            cut8 = max(cut2 + 1, round(num_questions * 0.8))\n"
        "            if i < cut2:\n"
        "                q_marks = 2\n"
        "            elif i < cut8:\n"
        "                q_marks = 8\n"
        "            else:\n"
        "                q_marks = 16"
    )
    new_det = (
        "        # Determine marks for this question\n"
        "        if is_quiz:\n"
        "            # Quiz Generator workflow defaults to 1 mark per question\n"
        "            if req_marks in ('1', '2', '8', '16'):\n"
        "                q_marks = int(req_marks)\n"
        "            else:\n"
        "                q_marks = 1\n"
        "        else:\n"
        "            # All other workflows strictly enforce 2, 8, or 16 marks\n"
        "            if req_marks in ('2', '8', '16'):\n"
        "                q_marks = int(req_marks)\n"
        "            else:\n"
        "                # Mixed marks: 40% 2M, 40% 8M, 20% 16M\n"
        "                cut2 = max(1, round(num_questions * 0.4))\n"
        "                cut8 = max(cut2 + 1, round(num_questions * 0.8))\n"
        "                if i < cut2:\n"
        "                    q_marks = 2\n"
        "                elif i < cut8:\n"
        "                    q_marks = 8\n"
        "                else:\n"
        "                    q_marks = 16"
    )
    if old_det in content:
        content = content.replace(old_det, new_det, 1)
    else:
        content = content.replace(old_det.replace("\n", "\r\n"), new_det.replace("\n", "\r\n"), 1)

    # 3. Quiz question type label
    old_qtype = (
        "                \"question_type\": f\"Quiz Question ({q_marks} Marks)\",\n"
        "                \"type\": f\"Quiz Question ({q_marks} Marks)\","
    )
    new_qtype = (
        "                \"question_type\": f\"Quiz Question ({q_marks} Mark)\" if q_marks == 1 else f\"Quiz Question ({q_marks} Marks)\",\n"
        "                \"type\": f\"Quiz Question ({q_marks} Mark)\" if q_marks == 1 else f\"Quiz Question ({q_marks} Marks)\","
    )
    if old_qtype in content:
        content = content.replace(old_qtype, new_qtype, 1)
    else:
        content = content.replace(old_qtype.replace("\n", "\r\n"), new_qtype.replace("\n", "\r\n"), 1)

    # 4. Add marks_per_question to q_item
    old_marks = (
        "                \"marks\": q_marks,\n"
        "                \"options\": rotated_options,"
    )
    new_marks = (
        "                \"marks\": q_marks,\n"
        "                \"marks_per_question\": q_marks,\n"
        "                \"options\": rotated_options,"
    )
    if old_marks in content:
        content = content.replace(old_marks, new_marks, 1)
    else:
        content = content.replace(old_marks.replace("\n", "\r\n"), new_marks.replace("\n", "\r\n"), 1)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("[OK] backend/utils/document_parser.py patched successfully")


def patch_quiz_service():
    path = os.path.join(BASE_DIR, "backend", "services", "quiz_service.py")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Add build_quiz_ai_prompt before generate_quiz_service
    ai_prompt_func = (
        "def build_quiz_ai_prompt(config):\n"
        "    \"\"\"\n"
        "    Constructs explicit AI prompt for Quiz Generation specifying 1-mark objective questions.\n"
        "    \"\"\"\n"
        "    subject = (config.get('subject') or 'Academic Course').strip()\n"
        "    department = (config.get('department') or 'General Engineering').strip()\n"
        "    unit = (config.get('unit') or 'All Units').strip()\n"
        "    topic = (config.get('topic') or 'Complete Syllabus').strip()\n"
        "    num_questions = int(config.get('total_questions') or config.get('num_questions') or 30)\n"
        "    marks_per_q = int(config.get('marks_per_question') or config.get('marksPerQuestion') or 1)\n"
        "    duration = int(config.get('duration_minutes') or config.get('durationMins') or 30)\n"
        "\n"
        "    return (\n"
        "        f\"You are an academic course examiner. Generate {num_questions} objective multiple-choice questions (MCQs) \"\n"
        "        f\"for the course '{subject}' ({department}).\\n\"\n"
        "        f\"Unit: {unit}\\n\"\n"
        "        f\"Topic: {topic}\\n\"\n"
        "        f\"Assessment Duration: {duration} Minutes\\n\\n\"\n"
        "        f\"CRITICAL MARKS & EVALUATION SPECIFICATION:\\n\"\n"
        "        f\"- Each quiz question must be worth exactly {marks_per_q} mark ({marks_per_q} {'Mark' if marks_per_q == 1 else 'Marks'} per question).\\n\"\n"
        "        f\"- Total assessment marks: {num_questions * marks_per_q} Marks ({num_questions} questions x {marks_per_q} mark).\\n\"\n"
        "        f\"- Question Format: 4 distinct options (A, B, C, D) with exactly one verified correct answer.\\n\"\n"
        "        f\"- Scope: Concise, objective conceptual questions tailored to {marks_per_q}-mark evaluation.\"\n"
        "    )\n\n\n"
    )

    if "def build_quiz_ai_prompt" not in content:
        target = "def generate_quiz_service(faculty_id, data):"
        assert target in content, "Could not find generate_quiz_service in quiz_service.py"
        content = content.replace(target, ai_prompt_func + target, 1)

    # 2. In format_quiz_dict: marks_per_q default to 1, preserve in questions
    old_fmt = "marks_per_q = int(quiz_row.get('marks_per_question') or 2)"
    new_fmt = "marks_per_q = int(quiz_row['marks_per_question']) if quiz_row.get('marks_per_question') is not None else 1"
    content = content.replace(old_fmt, new_fmt)

    # In format_quiz_dict, ensure questions have marks
    old_q_json = (
        "    questions = []\n"
        "    if quiz_row.get('questions'):\n"
        "        try:\n"
        "            questions = json.loads(quiz_row['questions']) if isinstance(quiz_row['questions'], str) else quiz_row['questions']\n"
        "        except Exception:\n"
        "            questions = []"
    )
    new_q_json = (
        "    questions = []\n"
        "    if quiz_row.get('questions'):\n"
        "        try:\n"
        "            questions = json.loads(quiz_row['questions']) if isinstance(quiz_row['questions'], str) else quiz_row['questions']\n"
        "        except Exception:\n"
        "            questions = []\n"
        "    if isinstance(questions, list):\n"
        "        for q in questions:\n"
        "            if isinstance(q, dict):\n"
        "                if 'marks' not in q or q['marks'] is None:\n"
        "                    q['marks'] = int(quiz_row.get('marks_per_question') or 1)\n"
        "                if 'marks_per_question' not in q or q['marks_per_question'] is None:\n"
        "                    q['marks_per_question'] = q['marks']"
    )
    if old_q_json in content:
        content = content.replace(old_q_json, new_q_json, 1)
    elif old_q_json.replace("\n", "\r\n") in content:
        content = content.replace(old_q_json.replace("\n", "\r\n"), new_q_json.replace("\n", "\r\n"), 1)

    # 3. In create_quiz_record: marks_per_question default to 1 and attach to questions
    old_create_marks = "marks_per_question = int(data.get('marks_per_question') or data.get('marksPerQuestion') or 2)"
    new_create_marks = (
        "marks_val = data.get('marks_per_question') if data.get('marks_per_question') is not None else data.get('marksPerQuestion')\n"
        "    marks_per_question = int(marks_val) if marks_val is not None else 1\n"
        "    if marks_per_question not in (1, 2, 8, 16):\n"
        "        marks_per_question = 1"
    )
    content = content.replace(old_create_marks, new_create_marks)

    old_total_q = "total_questions = int(data.get('total_questions') or data.get('totalQuestions') or len(questions) or 5)"
    new_total_q = (
        "total_questions = int(data.get('total_questions') or data.get('totalQuestions') or len(questions) or 5)\n"
        "    for q in questions:\n"
        "        if isinstance(q, dict):\n"
        "            if 'marks' not in q or q['marks'] is None:\n"
        "                q['marks'] = marks_per_question\n"
        "            if 'marks_per_question' not in q or q['marks_per_question'] is None:\n"
        "                q['marks_per_question'] = marks_per_question"
    )
    if old_total_q in content:
        content = content.replace(old_total_q, new_total_q, 1)
    elif old_total_q.replace("\n", "\r\n") in content:
        content = content.replace(old_total_q.replace("\n", "\r\n"), new_total_q.replace("\n", "\r\n"), 1)

    # 4. In update_quiz_record
    old_upd_marks = "marks_per_question = int(data.get('marks_per_question') or existing_quiz['marks_per_question'])"
    new_upd_marks = (
        "marks_val = data.get('marks_per_question') if data.get('marks_per_question') is not None else data.get('marksPerQuestion')\n"
        "    if marks_val is not None:\n"
        "        marks_per_question = int(marks_val)\n"
        "    else:\n"
        "        marks_per_question = int(existing_quiz.get('marks_per_question') if existing_quiz.get('marks_per_question') is not None else 1)\n"
        "    for q in questions:\n"
        "        if isinstance(q, dict):\n"
        "            if 'marks' not in q or q['marks'] is None:\n"
        "                q['marks'] = marks_per_question\n"
        "            if 'marks_per_question' not in q or q['marks_per_question'] is None:\n"
        "                q['marks_per_question'] = marks_per_question"
    )
    content = content.replace(old_upd_marks, new_upd_marks)

    # 5. In submit_student_quiz_attempt
    old_sub_marks = "marks_per_q = quiz.get('marksPerQuestion') or quiz.get('marks_per_question') or 2"
    new_sub_marks = "marks_per_q = int(quiz.get('marksPerQuestion') if quiz.get('marksPerQuestion') is not None else (quiz.get('marks_per_question') if quiz.get('marks_per_question') is not None else 1))"
    content = content.replace(old_sub_marks, new_sub_marks)

    # 6. In generate_quiz_service: pass marks explicitly and include ai_prompt
    old_gen_marks = (
        "    duration_mins = int(data.get('duration_minutes') or data.get('durationMins') or 30)\n"
        "    marks_per_q = int(data.get('marks_per_question') or data.get('marksPerQuestion') or 1)\n"
        "    total_q = int(data.get('total_questions') or data.get('totalQuestions') or 30)\n"
        "\n"
        "    data['duration_minutes'] = duration_mins\n"
        "    data['marks_per_question'] = marks_per_q\n"
        "    data['num_questions'] = total_q\n"
        "    data['question_type'] = 'Multiple Choice Question'\n"
        "    data['is_quiz'] = True"
    )
    new_gen_marks = (
        "    duration_mins = int(data.get('duration_minutes') or data.get('durationMins') or 30)\n"
        "    marks_val = data.get('marks_per_question') if data.get('marks_per_question') is not None else data.get('marksPerQuestion')\n"
        "    marks_per_q = int(marks_val) if marks_val is not None else 1\n"
        "    total_q = int(data.get('total_questions') or data.get('totalQuestions') or 30)\n"
        "\n"
        "    data['duration_minutes'] = duration_mins\n"
        "    data['marks_per_question'] = marks_per_q\n"
        "    data['marks'] = marks_per_q\n"
        "    data['num_questions'] = total_q\n"
        "    data['question_type'] = 'Multiple Choice Question'\n"
        "    data['is_quiz'] = True\n"
        "    ai_prompt = build_quiz_ai_prompt(data)"
    )
    if old_gen_marks in content:
        content = content.replace(old_gen_marks, new_gen_marks, 1)
    elif old_gen_marks.replace("\n", "\r\n") in content:
        content = content.replace(old_gen_marks.replace("\n", "\r\n"), new_gen_marks.replace("\n", "\r\n"), 1)

    # In quiz_preview: include ai_prompt
    old_prev_total = (
        "            \"total_marks\": total_marks,\n"
        "            \"totalMarks\": total_marks,\n"
        "            \"status\": \"Published\","
    )
    new_prev_total = (
        "            \"total_marks\": total_marks,\n"
        "            \"totalMarks\": total_marks,\n"
        "            \"ai_prompt\": ai_prompt,\n"
        "            \"status\": \"Published\","
    )
    if old_prev_total in content:
        content = content.replace(old_prev_total, new_prev_total, 1)
    elif old_prev_total.replace("\n", "\r\n") in content:
        content = content.replace(old_prev_total.replace("\n", "\r\n"), new_prev_total.replace("\n", "\r\n"), 1)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("[OK] backend/services/quiz_service.py patched successfully")


def patch_faculty_generate_quiz_html():
    path = os.path.join(BASE_DIR, "faculty-generate-quiz.html")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    old_select = (
        '                <select class="form-select" id="quizMarksPerQ">\n'
        '                  <option value="2" selected>2 Marks (Concise Conceptual Questions)</option>\n'
        '                  <option value="8">8 Marks (In-Depth Analytical Questions)</option>\n'
        '                  <option value="16">16 Marks (Comprehensive Multi-Part Questions)</option>\n'
        '                </select>'
    )
    new_select = (
        '                <select class="form-select" id="quizMarksPerQ">\n'
        '                  <option value="1" selected>1 Mark (Objective / MCQ Questions)</option>\n'
        '                  <option value="2">2 Marks (Concise Conceptual Questions)</option>\n'
        '                  <option value="8">8 Marks (In-Depth Analytical Questions)</option>\n'
        '                  <option value="16">16 Marks (Comprehensive Multi-Part Questions)</option>\n'
        '                </select>'
    )
    if old_select in content:
        content = content.replace(old_select, new_select, 1)
    elif old_select.replace("\n", "\r\n") in content:
        content = content.replace(old_select.replace("\n", "\r\n"), new_select.replace("\n", "\r\n"), 1)
    else:
        print("[WARN] Could not find old_select in faculty-generate-quiz.html")

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("[OK] faculty-generate-quiz.html patched successfully")


def patch_app_js():
    path = os.path.join(BASE_DIR, "js", "app.js")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. generateQuizAction button spinner text
    old_spinner = "Generating Grounded ${numQuestions}-Question Quiz (30 Marks)..."
    new_spinner = "Generating Grounded ${numQuestions}-Question Quiz (${numQuestions * marksPerQ} Marks)..."
    content = content.replace(old_spinner, new_spinner)

    # 2. saveQuizToStorage marksPerQ fallback to 1 instead of 2
    old_save_marks = "const marksPerQ = parseInt(document.getElementById('quizMarksPerQ')?.value || 2, 10);"
    new_save_marks = "const marksPerQ = parseInt(document.getElementById('quizMarksPerQ')?.value || 1, 10);"
    content = content.replace(old_save_marks, new_save_marks)

    # In saveQuizToStorage, ensure activeGeneratedQuizQuestions each have marks:
    old_storage_payload = (
        "    status: statusMode,\n"
        "\n"
        "\n"
        "\n"
        "    questions: activeGeneratedQuizQuestions"
    )
    # Check if exact
    if "questions: activeGeneratedQuizQuestions" in content:
        content = content.replace(
            "questions: activeGeneratedQuizQuestions",
            "questions: activeGeneratedQuizQuestions.map(q => ({ ...q, marks: (q.marks !== undefined && q.marks !== null) ? q.marks : marksPerQ, marks_per_question: (q.marks !== undefined && q.marks !== null) ? q.marks : marksPerQ }))"
        )

    # 3. renderGeneratedQuiz question card marks badge
    old_badge_area = (
        '            <span class="badge bg-secondary-subtle text-dark border"><i class="bi bi-tag me-1"></i>${q.concept}</span>'
    )
    new_badge_area = (
        '            <span class="badge bg-secondary-subtle text-dark border"><i class="bi bi-tag me-1"></i>${q.concept || "Core Concept"}</span>\n'
        '            <span class="badge bg-info-subtle text-info-emphasis border border-info-subtle"><i class="bi bi-award me-1"></i>${q.marks !== undefined && q.marks !== null ? q.marks : 1} ${(q.marks === 1 || q.marks === undefined) ? "Mark" : "Marks"}</span>'
    )
    if old_badge_area in content:
        content = content.replace(old_badge_area, new_badge_area, 1)
    elif old_badge_area.replace("\n", "\r\n") in content:
        content = content.replace(old_badge_area.replace("\n", "\r\n"), new_badge_area.replace("\n", "\r\n"), 1)

    # 4. editQuizQuestion: also update question_text and preserve marks
    old_edit = (
        "function editQuizQuestion(idx) {\n"
        "\n"
        "\n"
        "\n"
        "  const q = activeGeneratedQuizQuestions[idx];\n"
        "\n"
        "\n"
        "\n"
        "  if (!q) return;\n"
        "\n"
        "\n"
        "\n"
        '  const newText = prompt("Edit Quiz Question Text:", q.text);\n'
        "\n"
        "\n"
        "\n"
        "  if (newText && newText.trim()) {\n"
        "\n"
        "\n"
        "\n"
        "    q.text = newText.trim();\n"
        "\n"
        "\n"
        "\n"
        "    renderGeneratedQuiz();\n"
        "\n"
        "\n"
        "\n"
        "  }\n"
        "\n"
        "\n"
        "\n"
        "}"
    )
    new_edit = (
        "function editQuizQuestion(idx) {\n"
        "  const q = activeGeneratedQuizQuestions[idx];\n"
        "  if (!q) return;\n"
        "  const newText = prompt(\"Edit Quiz Question Text:\", q.text || q.question_text || q.question);\n"
        "  if (newText && newText.trim()) {\n"
        "    q.text = newText.trim();\n"
        "    q.question_text = newText.trim();\n"
        "    q.question = newText.trim();\n"
        "    renderGeneratedQuiz();\n"
        "  }\n"
        "}"
    )
    if old_edit in content:
        content = content.replace(old_edit, new_edit, 1)
    elif old_edit.replace("\n", "\r\n") in content:
        content = content.replace(old_edit.replace("\n", "\r\n"), new_edit.replace("\n", "\r\n"), 1)

    # 5. regenerateQuizQuestion: preserve marks
    old_regen = (
        'function regenerateQuizQuestion(idx) {\n'
        '\n'
        '\n'
        '\n'
        '  const q = activeGeneratedQuizQuestions[idx];\n'
        '\n'
        '\n'
        '\n'
        '  if (!q) return;\n'
        '\n'
        '\n'
        '\n'
        '  q.text = "Which SQL clause is used to group tuples having identical values in specified columns?";\n'
        '\n'
        '\n'
        '\n'
        '  q.options = ["ORDER BY", "GROUP BY", "WHERE", "HAVING"];\n'
        '\n'
        '\n'
        '\n'
        '  q.correctAnswer = "B. GROUP BY";\n'
        '\n'
        '\n'
        '\n'
        '  q.correctIndex = 1;\n'
        '\n'
        '\n'
        '\n'
        '  renderGeneratedQuiz();\n'
        '\n'
        '\n'
        '\n'
        '  renderQuizConceptCoverage();\n'
        '\n'
        '\n'
        '\n'
        '}'
    )
    new_regen = (
        "function regenerateQuizQuestion(idx) {\n"
        "  const q = activeGeneratedQuizQuestions[idx];\n"
        "  if (!q) return;\n"
        "  const curMarks = (q.marks !== undefined && q.marks !== null) ? q.marks : parseInt(document.getElementById('quizMarksPerQ')?.value || 1, 10);\n"
        "  q.text = \"Which SQL clause is used to group tuples having identical values in specified columns?\";\n"
        "  q.question_text = q.text;\n"
        "  q.question = q.text;\n"
        "  q.options = [\"ORDER BY\", \"GROUP BY\", \"WHERE\", \"HAVING\"];\n"
        "  q.correctAnswer = \"B. GROUP BY\";\n"
        "  q.correct_answer = \"B\";\n"
        "  q.correctIndex = 1;\n"
        "  q.marks = curMarks;\n"
        "  q.marks_per_question = curMarks;\n"
        "  q.type = `Quiz Question (${curMarks} ${curMarks === 1 ? 'Mark' : 'Marks'})`;\n"
        "  q.question_type = q.type;\n"
        "  renderGeneratedQuiz();\n"
        "  renderQuizConceptCoverage();\n"
        "}"
    )
    if old_regen in content:
        content = content.replace(old_regen, new_regen, 1)
    elif old_regen.replace("\n", "\r\n") in content:
        content = content.replace(old_regen.replace("\n", "\r\n"), new_regen.replace("\n", "\r\n"), 1)

    # 6. previewStudentQuizView marks display
    old_prev = (
        "    <div class=\"p-3 bg-light rounded border mb-3 small\">\n"
        "\n"
        "\n"
        "\n"
        "      <strong>Subject:</strong> ${document.getElementById('quizSubject')?.value} | \n"
        "\n"
        "\n"
        "\n"
        "      <strong>Time Limit:</strong> ${document.getElementById('quizTimeLimit')?.value} Mins | \n"
        "\n"
        "\n"
        "\n"
        "      <strong>Questions:</strong> ${activeGeneratedQuizQuestions.length}\n"
        "\n"
        "\n"
        "\n"
        "    </div>"
    )
    new_prev = (
        "    <div class=\"p-3 bg-light rounded border mb-3 small\">\n"
        "      <strong>Subject:</strong> ${document.getElementById('quizSubject')?.value} | \n"
        "      <strong>Time Limit:</strong> ${document.getElementById('quizTimeLimit')?.value} Mins | \n"
        "      <strong>Questions:</strong> ${activeGeneratedQuizQuestions.length} | \n"
        "      <strong>Marks Per Question:</strong> ${document.getElementById('quizMarksPerQ')?.value || 1} ${parseInt(document.getElementById('quizMarksPerQ')?.value || 1, 10) === 1 ? 'Mark' : 'Marks'} | \n"
        "      <strong>Total Marks:</strong> ${activeGeneratedQuizQuestions.length * parseInt(document.getElementById('quizMarksPerQ')?.value || 1, 10)} Marks\n"
        "    </div>"
    )
    if old_prev in content:
        content = content.replace(old_prev, new_prev, 1)
    elif old_prev.replace("\n", "\r\n") in content:
        content = content.replace(old_prev.replace("\n", "\r\n"), new_prev.replace("\n", "\r\n"), 1)

    # 7. Student portal fallbacks
    content = content.replace(
        "const marksPerQ = q.marks_per_question || q.marksPerQuestion || 2;",
        "const marksPerQ = (q.marks_per_question !== undefined && q.marks_per_question !== null) ? q.marks_per_question : ((q.marksPerQuestion !== undefined && q.marksPerQuestion !== null) ? q.marksPerQuestion : 1);"
    )
    content = content.replace(
        "marksPerQuestion: found.marks_per_question || found.marksPerQuestion || 2",
        "marksPerQuestion: (found.marks_per_question !== undefined && found.marks_per_question !== null) ? found.marks_per_question : ((found.marksPerQuestion !== undefined && found.marksPerQuestion !== null) ? found.marksPerQuestion : 1)"
    )
    content = content.replace(
        "const marksPerQ = activeStudentQuiz.marksPerQuestion || 2;",
        "const marksPerQ = (activeStudentQuiz.marksPerQuestion !== undefined && activeStudentQuiz.marksPerQuestion !== null) ? activeStudentQuiz.marksPerQuestion : 1;"
    )

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("[OK] js/app.js patched successfully")


if __name__ == "__main__":
    patch_document_parser()
    patch_quiz_service()
    patch_faculty_generate_quiz_html()
    patch_app_js()
    print("All patches completed!")
