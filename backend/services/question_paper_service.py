import json



import hashlib



import logging



import uuid



from datetime import datetime



from models.database import get_db_connection, DatabaseError



from services.question_service import get_question_by_id, OFFICIAL_DEPARTMENTS







logger = logging.getLogger(__name__)







def generate_paper_fingerprint(paper_data):



    """



    Computes a deterministic SHA-256 fingerprint hash for an exam question paper.



    Hash is derived from paper metadata, section structure, and selected question IDs.



    """



    subject = str(paper_data.get('subject') or '').strip()



    department = str(paper_data.get('department') or '').strip()



    semester = str(paper_data.get('semester') or '').strip()



    academic_year = str(paper_data.get('academic_year') or '').strip()



    exam_type = str(paper_data.get('exam_type') or '').strip()



    total_marks = str(paper_data.get('total_marks') or paper_data.get('max_marks') or '100').strip()



    instructions = str(paper_data.get('instructions') or '').strip()







    # Question IDs normalized as sorted/ordered list of ints



    q_ids = paper_data.get('question_ids') or []



    if isinstance(q_ids, str):



        try:



            q_ids = json.loads(q_ids)



        except Exception:



            q_ids = []



    normalized_q_ids = [int(x) for x in q_ids if str(x).isdigit()]







    # Sections normalized



    sections = paper_data.get('sections') or []



    if isinstance(sections, str):



        try:



            sections = json.loads(sections)



        except Exception:



            sections = []







    canonical_obj = {



        "subject": subject,



        "department": department,



        "semester": semester,



        "academic_year": academic_year,



        "exam_type": exam_type,



        "total_marks": total_marks,



        "instructions": instructions,



        "question_ids": normalized_q_ids,



        "sections": sections



    }







    canonical_str = json.dumps(canonical_obj, sort_keys=True)



    return hashlib.sha256(canonical_str.encode('utf-8')).hexdigest()











def format_paper_dict(paper_row, question_records=None):



    """



    Formats raw DB dictionary row into frontend-compatible question paper dictionary.



    """



    if not paper_row:



        return None







    # Parse JSON fields safely



    sections = []



    if paper_row.get('sections'):



        try:



            sections = json.loads(paper_row['sections']) if isinstance(paper_row['sections'], str) else paper_row['sections']



        except Exception:



            sections = []







    question_ids = []



    if paper_row.get('question_ids'):



        try:



            question_ids = json.loads(paper_row['question_ids']) if isinstance(paper_row['question_ids'], str) else paper_row['question_ids']



        except Exception:



            question_ids = []







    # Dates formatting



    created_at_str = ''



    if paper_row.get('created_at'):



        if isinstance(paper_row['created_at'], (datetime,)):



            created_at_str = paper_row['created_at'].strftime('%Y-%m-%d')



            paper_row['created_at'] = paper_row['created_at'].isoformat()



        else:



            created_at_str = str(paper_row['created_at'])







    if paper_row.get('published_at') and isinstance(paper_row['published_at'], (datetime,)):



        paper_row['published_at'] = paper_row['published_at'].isoformat()







    exam_date_str = ''



    if paper_row.get('exam_date'):



        if isinstance(paper_row['exam_date'], (datetime,)):



            exam_date_str = paper_row['exam_date'].strftime('%Y-%m-%d')



            paper_row['exam_date'] = paper_row['exam_date'].isoformat()



        else:



            exam_date_str = str(paper_row['exam_date'])







    fingerprint = paper_row.get('fingerprint') or paper_row.get('sha256_hash') or ''







    return {



        "id": paper_row['id'],



        "paper_id": paper_row.get('paper_code') or f"EXAM-{paper_row['id']}",



        "paper_code": paper_row.get('paper_code') or f"EXAM-{paper_row['id']}",



        "title": paper_row.get('title') or 'Question Paper',



        "subject": paper_row['subject'],



        "course": paper_row['subject'],



        "department": paper_row['department'],



        "academic_year": paper_row.get('academic_year') or '2025-2026',



        "semester": paper_row.get('semester') or 'Semester 6',



        "exam_type": paper_row.get('exam_type') or 'Model Examination',



        "exam_date": exam_date_str,



        "exam_time": paper_row.get('exam_time') or '10:00 AM - 01:00 PM',



        "duration": paper_row.get('duration') or '3 Hours',



        "total_marks": paper_row.get('total_marks') or paper_row.get('max_marks') or 100,



        "max_marks": paper_row.get('total_marks') or paper_row.get('max_marks') or 100,



        "instructions": paper_row.get('instructions') or '',



        "sections": sections,



        "question_ids": question_ids,



        "questions": question_records or [],



        "fingerprint": fingerprint,



        "sha256_hash": fingerprint,



        "qr_payload": paper_row.get('qr_payload') or f"{paper_row.get('paper_code')}|{fingerprint}",



        "status": paper_row.get('status') or 'Draft',



        "created_by": paper_row.get('created_by'),



        "created_at": paper_row.get('created_at'),



        "createdDate": created_at_str



    }











def create_question_paper(faculty_id, data):



    """



    Creates and stores a complete question paper in MySQL within a transaction.



    """



    title = str(data.get('title') or data.get('paper_title') or '').strip()



    subject = str(data.get('subject') or data.get('course') or '').strip()



    department = str(data.get('department') or 'Artificial Intelligence & Data Science').strip()



    academic_year = str(data.get('academic_year') or '2025-2026').strip()



    sem_val = data.get('semester') or 'Semester 6'



    semester = f"Semester {sem_val}" if str(sem_val).isdigit() else str(sem_val).strip()



    exam_type = str(data.get('exam_type') or 'Model Examination').strip()



    exam_date = data.get('exam_date') or None



    exam_time = str(data.get('exam_time') or '10:00 AM - 01:00 PM').strip()



    duration = str(data.get('duration') or '3 Hours').strip()



    total_marks = int(data.get('total_marks') or data.get('max_marks') or 100)



    instructions = str(data.get('instructions') or '').strip()



    status = str(data.get('status') or 'Draft').strip()







    if not title:



        title = f"{subject} {exam_type}"



    if not subject:



        return False, {"status": "error", "message": "Subject is required."}, 400



    if not department:
        department = "General Engineering"







    q_ids = data.get('question_ids') or []



    if isinstance(q_ids, str):



        try:



            q_ids = json.loads(q_ids)



        except Exception:



            q_ids = []







    if not q_ids or len(q_ids) == 0:



        return False, {"status": "error", "message": "At least one question must be selected for the question paper."}, 400







    sections = data.get('sections') or []



    if isinstance(sections, str):



        try:



            sections = json.loads(sections)



        except Exception:



            sections = []







    paper_code = data.get('paper_code') or data.get('paper_id') or f"EXAM-{datetime.now().strftime('%Y')}-{uuid.uuid4().hex[:6].upper()}"







    # Calculate attempted marks strictly (counting only one Either/Or alternative)



    calculated_attempted = calculate_attempted_marks(sections)



    if calculated_attempted > 0:



        total_marks = calculated_attempted







    valid, err_msg = validate_question_paper_structure(data, total_marks)



    if not valid:



        return False, {"status": "error", "message": err_msg}, 400







    # Compute deterministic fingerprint and QR payload



    data['subject'] = subject



    data['department'] = department



    data['semester'] = semester



    data['academic_year'] = academic_year



    data['exam_type'] = exam_type



    data['total_marks'] = total_marks



    data['instructions'] = instructions



    data['question_ids'] = q_ids



    data['sections'] = sections







    fingerprint = generate_paper_fingerprint(data)



    qr_payload = f"{paper_code}|{fingerprint}"







    sections_json = json.dumps(sections)



    q_ids_json = json.dumps(q_ids)







    try:



        conn = get_db_connection()



        conn.begin()



        with conn.cursor() as cursor:



            sql = """



                INSERT INTO question_papers



                (paper_code, title, subject, department, academic_year, semester,



                 exam_type, exam_date, duration_minutes, duration, max_marks, total_marks,



                 instructions, sha256_hash, fingerprint, qr_payload, status, sections,



                 question_ids, exam_time, created_by, published_at)



                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)



            """



            published_at = datetime.now() if status == 'Published' else None







            cursor.execute(sql, (



                paper_code, title, subject, department, academic_year, semester,



                exam_type, exam_date, 180, duration, total_marks, total_marks,



                instructions, fingerprint, fingerprint, qr_payload, status, sections_json,



                q_ids_json, exam_time, faculty_id, published_at



            ))



            paper_db_id = cursor.lastrowid







        conn.commit()



        conn.close()







        created_paper = get_question_paper_by_id(paper_db_id, faculty_id)



        return True, {



            "status": "success",



            "message": "Question paper saved successfully.",



            "paper": created_paper,



            "fingerprint": fingerprint



        }, 201







    except Exception as e:



        logger.error(f"Error creating question paper: {str(e)}")



        if 'conn' in locals() and conn:



            conn.rollback()



            conn.close()



        return False, {"status": "error", "message": "Failed to save question paper record to database."}, 500











def get_question_papers(faculty_id=None, filters=None, is_student=False):



    """



    Retrieves question papers.



    If student, retrieves all Published question papers.



    If faculty, retrieves question papers created by logged-in faculty with optional filtering.



    """



    filters = filters or {}



    if is_student or faculty_id is None:



        sql = "SELECT * FROM question_papers WHERE status = 'Published'"



        params = []



    else:



        sql = "SELECT * FROM question_papers WHERE created_by = %s"



        params = [faculty_id]







    if filters.get('subject'):



        sql += " AND subject = %s"



        params.append(filters['subject'])



    if filters.get('department'):



        sql += " AND department = %s"



        params.append(filters['department'])



    if filters.get('semester'):



        sql += " AND semester = %s"



        params.append(filters['semester'])



    if filters.get('academic_year'):



        sql += " AND academic_year = %s"



        params.append(filters['academic_year'])



    if filters.get('exam_type'):



        sql += " AND exam_type = %s"



        params.append(filters['exam_type'])



    if filters.get('status'):



        sql += " AND status = %s"



        params.append(filters['status'])







    sql += " ORDER BY created_at DESC"







    try:



        conn = get_db_connection()



        with conn.cursor() as cursor:



            cursor.execute(sql, tuple(params))



            rows = cursor.fetchall()



        conn.close()







        papers = [format_paper_dict(row) for row in rows]



        return True, {



            "status": "success",



            "count": len(papers),



            "question_papers": papers,



            "papers": papers



        }, 200







    except Exception as e:



        logger.error(f"Error fetching question papers: {str(e)}")



        return False, {"status": "error", "message": "Failed to fetch question papers."}, 500











def get_question_paper_by_id(paper_id, faculty_id=None):



    """



    Retrieves a single question paper by ID or paper_code, along with its selected questions.



    """



    try:



        conn = get_db_connection()



        with conn.cursor() as cursor:



            if str(paper_id).isdigit():



                sql = "SELECT * FROM question_papers WHERE id = %s"



                cursor.execute(sql, (int(paper_id),))



            else:



                sql = "SELECT * FROM question_papers WHERE paper_code = %s"



                cursor.execute(sql, (str(paper_id),))







            paper_row = cursor.fetchone()



        conn.close()







        if not paper_row:



            return None







        # Verify faculty ownership if specified



        if faculty_id is not None and paper_row['created_by'] != faculty_id:



            return None







        # Resolve selected questions details



        q_ids = []



        if paper_row.get('question_ids'):



            try:



                q_ids = json.loads(paper_row['question_ids']) if isinstance(paper_row['question_ids'], str) else paper_row['question_ids']



            except Exception:



                q_ids = []







        question_records = []



        for qid in q_ids:



            q_rec = get_question_by_id(qid)



            if q_rec:



                question_records.append(q_rec)







        return format_paper_dict(paper_row, question_records)







    except Exception as e:



        logger.error(f"Error fetching question paper by ID: {str(e)}")



        return None











def update_question_paper(paper_id, faculty_id, data):



    """



    Updates an existing question paper record owned by the faculty.



    """



    existing_paper = get_question_paper_by_id(paper_id, faculty_id)



    if not existing_paper:



        return False, {"status": "error", "message": "Question paper not found or access forbidden."}, 404







    db_id = existing_paper['id']







    title = str(data.get('title') or data.get('paper_title') or existing_paper['title']).strip()



    subject = str(data.get('subject') or data.get('course') or existing_paper['subject']).strip()



    department = str(data.get('department') or existing_paper['department']).strip()



    academic_year = str(data.get('academic_year') or existing_paper['academic_year']).strip()



    sem_val = data.get('semester') or existing_paper['semester']



    semester = f"Semester {sem_val}" if str(sem_val).isdigit() else str(sem_val).strip()



    exam_type = str(data.get('exam_type') or existing_paper['exam_type']).strip()



    raw_exam_date = data.get('exam_date') if data.get('exam_date') is not None else existing_paper.get('exam_date')



    exam_date = raw_exam_date if (raw_exam_date and str(raw_exam_date).strip() not in ['', 'None']) else None



    exam_time = str(data.get('exam_time') or existing_paper['exam_time']).strip()



    duration = str(data.get('duration') or existing_paper['duration']).strip()



    total_marks = int(data.get('total_marks') or data.get('max_marks') or existing_paper['total_marks'])



    instructions = str(data.get('instructions') or existing_paper['instructions']).strip()



    status = str(data.get('status') or existing_paper['status']).strip()







    q_ids = data.get('question_ids') if data.get('question_ids') is not None else existing_paper['question_ids']



    if isinstance(q_ids, str):



        try:



            q_ids = json.loads(q_ids)



        except Exception:



            q_ids = []







    sections = data.get('sections') if data.get('sections') is not None else existing_paper['sections']



    if isinstance(sections, str):



        try:



            sections = json.loads(sections)



        except Exception:



            sections = []







    # Calculate attempted marks strictly (counting only one Either/Or alternative)



    calculated_attempted = calculate_attempted_marks(sections)



    if calculated_attempted > 0:



        total_marks = calculated_attempted







    valid, err_msg = validate_question_paper_structure(data, total_marks)



    if not valid:



        return False, {"status": "error", "message": err_msg}, 400







    # Compute updated fingerprint



    update_data = {



        "subject": subject,



        "department": department,



        "semester": semester,



        "academic_year": academic_year,



        "exam_type": exam_type,



        "total_marks": total_marks,



        "instructions": instructions,



        "question_ids": q_ids,



        "sections": sections



    }



    fingerprint = generate_paper_fingerprint(update_data)



    paper_code = existing_paper['paper_code']



    qr_payload = f"{paper_code}|{fingerprint}"







    sections_json = json.dumps(sections)



    q_ids_json = json.dumps(q_ids)







    try:



        conn = get_db_connection()



        conn.begin()



        with conn.cursor() as cursor:



            sql = """



                UPDATE question_papers



                SET title = %s, subject = %s, department = %s, academic_year = %s,



                    semester = %s, exam_type = %s, exam_date = %s, duration = %s,



                    max_marks = %s, total_marks = %s, instructions = %s, sha256_hash = %s,



                    fingerprint = %s, qr_payload = %s, status = %s, sections = %s,



                    question_ids = %s, exam_time = %s, published_at = %s



                WHERE id = %s AND created_by = %s



            """



            published_at = datetime.now() if status == 'Published' else None







            cursor.execute(sql, (



                title, subject, department, academic_year,



                semester, exam_type, exam_date, duration,



                total_marks, total_marks, instructions, fingerprint,



                fingerprint, qr_payload, status, sections_json,



                q_ids_json, exam_time, published_at,



                db_id, faculty_id



            ))







        conn.commit()



        conn.close()







        updated_paper = get_question_paper_by_id(db_id, faculty_id)



        return True, {



            "status": "success",



            "message": "Question paper updated successfully.",



            "paper": updated_paper,



            "fingerprint": fingerprint



        }, 200







    except Exception as e:



        logger.error(f"Error updating question paper: {str(e)}")



        if 'conn' in locals() and conn:



            conn.rollback()



            conn.close()



        return False, {"status": "error", "message": "Failed to update question paper record."}, 500











def delete_question_paper(paper_id, faculty_id):



    """



    Deletes a question paper record owned by the faculty.



    """



    existing_paper = get_question_paper_by_id(paper_id, faculty_id)



    if not existing_paper:



        return False, {"status": "error", "message": "Question paper not found or access forbidden."}, 404







    db_id = existing_paper['id']







    try:



        conn = get_db_connection()



        conn.begin()



        with conn.cursor() as cursor:



            cursor.execute("DELETE FROM question_papers WHERE id = %s AND created_by = %s", (db_id, faculty_id))



        conn.commit()



        conn.close()







        return True, {



            "status": "success",



            "message": "Question paper deleted successfully."



        }, 200







    except Exception as e:



        logger.error(f"Error deleting question paper: {str(e)}")



        if 'conn' in locals() and conn:



            conn.rollback()



            conn.close()



        return False, {"status": "error", "message": "Failed to delete question paper record."}, 500











def verify_paper_fingerprint(paper_id, submitted_fingerprint):



    """



    Verifies if a submitted fingerprint matches the paper record stored in MySQL.



    """



    paper = get_question_paper_by_id(paper_id)



    if not paper:



        return False, {



            "status": "error",



            "valid": False,



            "message": "Question paper not found."



        }, 404







    stored_fp = paper.get('fingerprint') or paper.get('sha256_hash') or ''



    submitted_fp = (submitted_fingerprint or '').strip()







    is_valid = bool(stored_fp and submitted_fp and stored_fp.lower() == submitted_fp.lower())







    return True, {



        "status": "success",



        "valid": is_valid,



        "message": "Fingerprint verified successfully: Valid match." if is_valid else "Fingerprint verification failed: Hash mismatch!",



        "paper_id": paper['paper_code'],



        "stored_fingerprint": stored_fp,



        "submitted_fingerprint": submitted_fp



    }, 200











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



    return str(unit_str).strip()



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



    exam_type = str(paper_data.get('exam_type') or paper_data.get('paper_type') or paper_data.get('template') or paper_data.get('template_type') or '').lower()



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







        sec_a = next((s for s in sections if 'A' in str(s.get('name') or s.get('title') or '').upper()), None)



        if sec_a:



            q_list = sec_a.get('questions') or []



            if len(q_list) > 0 and len(q_list) != 5:



                return False, f"Validation Error: Section A of Internal Examination must contain exactly 5 compulsory questions (found {len(q_list)})."







        sec_b = next((s for s in sections if 'B' in str(s.get('name') or s.get('title') or '').upper()), None)



        if sec_b:



            b_groups = sec_b.get('groups') or sec_b.get('either_or_groups') or []



            if len(b_groups) != 1:



                return False, f"Validation Error: Section B must contain exactly 1 Either/Or group of 8 marks (found {len(b_groups)})."







        sec_c = next((s for s in sections if 'C' in str(s.get('name') or s.get('title') or '').upper()), None)



        if sec_c:



            c_groups = sec_c.get('groups') or sec_c.get('either_or_groups') or []



            if len(c_groups) != 2:



                return False, f"Validation Error: Section C must contain exactly 2 Either/Or groups of 16 marks each (found {len(c_groups)})."







    # 2. Semester Examination

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



    subject = str(data.get('subject') or 'Database Management Systems').strip()



    department = str(data.get('department') or 'Artificial Intelligence & Data Science').strip()



    academic_year = str(data.get('academic_year') or '2025-2026').strip()



    sem_val = data.get('semester') or 'Semester 6'



    semester = f"Semester {sem_val}" if str(sem_val).isdigit() else str(sem_val).strip()







    conn = get_db_connection()



    with conn.cursor() as cur:



        cur.execute("""
            SELECT * FROM questions
            WHERE created_by = %s AND subject = %s AND department = %s
            ORDER BY is_in_bank DESC, id ASC
        """, (faculty_id, subject, department))
        all_q_rows = cur.fetchall()

        # Fallback if subject has few questions (scoped to faculty)
        if len(all_q_rows) < 15:
            cur.execute("""
                SELECT * FROM questions
                WHERE created_by = %s AND subject = %s
                ORDER BY is_in_bank DESC, id ASC
            """, (faculty_id, subject))
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







        # PART - B (5 x 16 = 80 Marks): Questions 11 to 15 (Units I to V)

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

        instructions = "1. Answer ALL Questions from PART - A.\n2. Answer EITHER Alternative (a) OR Alternative (b) from each Question in PART - B.\n3. PART - A: 10 Questions x 2 Marks = 20 Marks.\n4. PART - B: 5 Questions x 16 Marks = 80 Marks.\n5. Maximum Attempted Marks: 100 Marks."







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



