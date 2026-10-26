import os

base_dir = r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system"

# 1. Patch question_routes.py
q_routes_path = os.path.join(base_dir, "backend", "routes", "question_routes.py")
with open(q_routes_path, "r", encoding="utf-8") as f:
    q_routes = f.read()

target_q = """@question_bp.route('/api/questions/<int:question_id>', methods=['GET'])
def get_question_api(question_id):
    \"\"\"
    GET /api/questions/<id>
    Retrieves single question details by ID.
    \"\"\"
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"status": "error", "message": "Authentication required. Please log in."}), 401

    question = get_question_by_id(question_id)
    if not question:
        return jsonify({"status": "error", "message": "Question not found."}), 404

    return jsonify({"status": "success", "question": question}), 200"""

repl_q = """@question_bp.route('/api/questions/<int:question_id>', methods=['GET'])
def get_question_api(question_id):
    \"\"\"
    GET /api/questions/<id>
    Retrieves single question details by ID.
    \"\"\"
    user_id = session.get('user_id')
    role = session.get('role')
    if not user_id:
        return jsonify({"status": "error", "message": "Authentication required. Please log in."}), 401

    question = get_question_by_id(question_id)
    if not question:
        return jsonify({"status": "error", "message": "Question not found."}), 404

    # Faculty data isolation check: Faculty members can only view their own questions
    if role == 'faculty' and question.get('created_by') != user_id:
        return jsonify({"status": "error", "message": "Forbidden. You are not authorized to view this question."}), 403

    return jsonify({"status": "success", "question": question}), 200"""

# Normalize CRLF
if target_q.replace('\r\n', '\n') in q_routes.replace('\r\n', '\n'):
    q_routes = q_routes.replace('\r\n', '\n').replace(target_q.replace('\r\n', '\n'), repl_q.replace('\r\n', '\n'))
    with open(q_routes_path, "w", encoding="utf-8") as f:
        f.write(q_routes)
    print("1. Successfully patched question_routes.py")
else:
    print("1. Target not found in question_routes.py")


# 2. Patch question_service.py get_questions
q_serv_path = os.path.join(base_dir, "backend", "services", "question_service.py")
with open(q_serv_path, "r", encoding="utf-8") as f:
    q_serv = f.read()

target_q_serv = """            # Faculty data isolation: Faculty members only view their own questions

            if role == 'faculty' or filters.get('created_by'):

                sql += " AND q.created_by = %s"

                params.append(filters.get('created_by') or user_id)"""

repl_q_serv = """            # Faculty data isolation: Faculty members only view their own questions
            if role == 'faculty':
                sql += " AND q.created_by = %s"
                params.append(user_id)
            elif filters.get('created_by'):
                sql += " AND q.created_by = %s"
                params.append(filters.get('created_by'))"""

if target_q_serv.replace('\r\n', '\n') in q_serv.replace('\r\n', '\n'):
    q_serv = q_serv.replace('\r\n', '\n').replace(target_q_serv.replace('\r\n', '\n'), repl_q_serv.replace('\r\n', '\n'))
    with open(q_serv_path, "w", encoding="utf-8") as f:
        f.write(q_serv)
    print("2. Successfully patched question_service.py")
else:
    print("2. Target not found in question_service.py")


# 3. Patch question_paper_routes.py
qp_routes_path = os.path.join(base_dir, "backend", "routes", "question_paper_routes.py")
with open(qp_routes_path, "r", encoding="utf-8") as f:
    qp_routes = f.read()

target_qp = """    # Faculty can view owned paper or published paper; student can view published paper
    if role == 'faculty' and paper['created_by'] != user_id and paper['status'] != 'Published':
        return jsonify({"status": "error", "message": "Forbidden. You can only view your own draft papers."}), 403
    elif role == 'student' and paper['status'] != 'Published':
        return jsonify({"status": "error", "message": "Forbidden. Students can only view published examination papers."}), 403"""

repl_qp = """    # Faculty can only view their own question papers; student can view published paper
    if role == 'faculty' and paper.get('created_by') != user_id:
        return jsonify({"status": "error", "message": "Forbidden. You can only view your own question papers."}), 403
    elif role == 'student' and paper.get('status') != 'Published':
        return jsonify({"status": "error", "message": "Forbidden. Students can only view published examination papers."}), 403"""

if target_qp.replace('\r\n', '\n') in qp_routes.replace('\r\n', '\n'):
    qp_routes = qp_routes.replace('\r\n', '\n').replace(target_qp.replace('\r\n', '\n'), repl_qp.replace('\r\n', '\n'))
    with open(qp_routes_path, "w", encoding="utf-8") as f:
        f.write(qp_routes)
    print("3. Successfully patched question_paper_routes.py")
else:
    print("3. Target not found in question_paper_routes.py")


# 4. Patch question_paper_service.py generate_template_paper
qp_serv_path = os.path.join(base_dir, "backend", "services", "question_paper_service.py")
with open(qp_serv_path, "r", encoding="utf-8") as f:
    qp_serv = f.read()

target_qp_serv = """        cur.execute(\"\"\"



            SELECT * FROM questions



            WHERE subject = %s AND department = %s



            ORDER BY is_in_bank DESC, id ASC



        \"\"\", (subject, department))



        all_q_rows = cur.fetchall()



        



        # Fallback if subject has few questions



        if len(all_q_rows) < 15:



            cur.execute(\"\"\"



                SELECT * FROM questions



                WHERE subject = %s



                ORDER BY is_in_bank DESC, id ASC



            \"\"\", (subject,))



            all_q_rows = cur.fetchall()"""

repl_qp_serv = """        cur.execute(\"\"\"
            SELECT * FROM questions
            WHERE created_by = %s AND subject = %s AND department = %s
            ORDER BY is_in_bank DESC, id ASC
        \"\"\", (faculty_id, subject, department))
        all_q_rows = cur.fetchall()

        # Fallback if subject has few questions (scoped to faculty)
        if len(all_q_rows) < 15:
            cur.execute(\"\"\"
                SELECT * FROM questions
                WHERE created_by = %s AND subject = %s
                ORDER BY is_in_bank DESC, id ASC
            \"\"\", (faculty_id, subject))
            all_q_rows = cur.fetchall()"""

if target_qp_serv.replace('\r\n', '\n') in qp_serv.replace('\r\n', '\n'):
    qp_serv = qp_serv.replace('\r\n', '\n').replace(target_qp_serv.replace('\r\n', '\n'), repl_qp_serv.replace('\r\n', '\n'))
    with open(qp_serv_path, "w", encoding="utf-8") as f:
        f.write(qp_serv)
    print("4. Successfully patched question_paper_service.py")
else:
    print("4. Target not found in question_paper_service.py")


# 5. Patch quiz_service.py get_quiz_by_id
quiz_serv_path = os.path.join(base_dir, "backend", "services", "quiz_service.py")
with open(quiz_serv_path, "r", encoding="utf-8") as f:
    quiz_serv = f.read()

target_quiz_serv = """        # Check role permission
        if role == 'student' and row['status'] != 'Published':
            return None

        return format_quiz_dict(row)"""

repl_quiz_serv = """        # Check role permission
        if role == 'student' and row['status'] != 'Published':
            return None
        if role == 'faculty' and user_id is not None and row.get('created_by') != user_id:
            return None

        return format_quiz_dict(row)"""

if target_quiz_serv.replace('\r\n', '\n') in quiz_serv.replace('\r\n', '\n'):
    quiz_serv = quiz_serv.replace('\r\n', '\n').replace(target_quiz_serv.replace('\r\n', '\n'), repl_quiz_serv.replace('\r\n', '\n'))
    with open(quiz_serv_path, "w", encoding="utf-8") as f:
        f.write(quiz_serv)
    print("5. Successfully patched quiz_service.py")
else:
    print("5. Target not found in quiz_service.py")


# 6. Patch quiz_routes.py get_quiz_by_id_api
quiz_routes_path = os.path.join(base_dir, "backend", "routes", "quiz_routes.py")
with open(quiz_routes_path, "r", encoding="utf-8") as f:
    quiz_routes = f.read()

target_quiz_routes = """    quiz = get_quiz_by_id(id, user_id, role)
    if not quiz:
        return jsonify({"status": "error", "message": "Quiz not found or access forbidden."}), 404

    return jsonify({
        "status": "success",
        "quiz": quiz
    }), 200"""

repl_quiz_routes = """    quiz = get_quiz_by_id(id, user_id, role)
    if not quiz:
        raw_quiz = get_quiz_by_id(id)
        if raw_quiz and role == 'faculty' and raw_quiz.get('created_by') != user_id:
            return jsonify({"status": "error", "message": "Forbidden. You are not authorized to view this quiz."}), 403
        return jsonify({"status": "error", "message": "Quiz not found or access forbidden."}), 404

    return jsonify({
        "status": "success",
        "quiz": quiz
    }), 200"""

if target_quiz_routes.replace('\r\n', '\n') in quiz_routes.replace('\r\n', '\n'):
    quiz_routes = quiz_routes.replace('\r\n', '\n').replace(target_quiz_routes.replace('\r\n', '\n'), repl_quiz_routes.replace('\r\n', '\n'))
    with open(quiz_routes_path, "w", encoding="utf-8") as f:
        f.write(quiz_routes)
    print("6. Successfully patched quiz_routes.py")
else:
    print("6. Target not found in quiz_routes.py")
