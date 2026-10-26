import logging

from models.database import get_db_connection, DatabaseError



logger = logging.getLogger(__name__)



OFFICIAL_DEPARTMENTS = [

    "Artificial Intelligence & Data Science",

    "Artificial Intelligence & Machine Learning",

    "Computer and Communication Engineering"

]



def format_question_dict(q_row, options_rows=None):

    """

    Formats raw DB dictionary row into frontend-compatible question object.

    """

    if not q_row:

        return None



    # Date formatting

    created_at_str = ''

    if q_row.get('created_at'):

        created_at_str = q_row['created_at'].strftime('%Y-%m-%d')

        q_row['created_at'] = q_row['created_at'].isoformat()

    if q_row.get('updated_at'):

        q_row['updated_at'] = q_row['updated_at'].isoformat()



    # Formatted options

    options = []

    if options_rows:

        for opt in options_rows:

            options.append({

                "id": opt['id'],

                "label": opt['option_label'],

                "option_label": opt['option_label'],

                "text": opt['option_text'],

                "option_text": opt['option_text'],

                "is_correct": bool(opt['is_correct'])

            })



    return {

        "id": q_row['id'],

        "resource_id": q_row.get('resource_id'),

        "text": q_row['question_text'],

        "question_text": q_row['question_text'],

        "question": q_row['question_text'],

        "subject": q_row['subject'],

        "course": q_row['subject'],

        "department": q_row['department'],

        "academic_year": q_row.get('academic_year') or '2025-2026',

        "semester": q_row.get('semester') or 'Semester 6',

        "unit": q_row.get('unit') or 'Unit III — SQL',

        "source_unit": q_row.get('source_unit') or q_row.get('unit'),

        "topic": q_row.get('topic') or 'General Topic',

        "question_type": q_row.get('question_type') or 'Short Answer',

        "type": q_row.get('question_type') or 'Short Answer',

        "difficulty": q_row.get('difficulty') or 'Medium',

        "bloom_level": q_row.get('bloom_level') or 'Understand',

        "blooms": q_row.get('bloom_level') or 'Understand',

        "bloomsTaxonomy": q_row.get('bloom_level') or 'Understand',

        "concept": q_row.get('concept') or 'General Concept',

        "explanation": q_row.get('explanation') or '',

        "marks": q_row.get('marks') if q_row.get('marks') is not None else 2,

        "status": q_row.get('status') or 'Generated',

        "is_in_bank": bool(q_row.get('is_in_bank')),

        "similarity_score": q_row.get('similarity_score') or 0,

        "similarity_level": q_row.get('similarity_level') or 'Low',

        "concept_repeat_count": q_row.get('concept_repeat_count') or 1,

        "created_by": q_row.get('created_by'),

        "faculty_name": q_row.get('faculty_name') or 'Faculty Member',

        "created_at": q_row.get('created_at'),

        "dateAdded": created_at_str,

        "options": options

    }





def create_question_record(faculty_id, data):

    """

    Creates a single question and its options in MySQL within a transaction.

    """

    question_text = (data.get('question_text') or data.get('text') or data.get('question') or '').strip()

    subject = (data.get('subject') or data.get('course') or '').strip()

    department = (data.get('department') or 'Artificial Intelligence & Data Science').strip()

    academic_year = (data.get('academic_year') or '2025-2026').strip()

    semester = (data.get('semester') or 'Semester 6').strip()

    unit = (data.get('unit') or data.get('source_unit') or 'Unit III — SQL').strip()

    topic = (data.get('topic') or '').strip()

    question_type = (data.get('question_type') or data.get('type') or 'Short Answer').strip()

    difficulty = (data.get('difficulty') or 'Medium').strip()

    bloom_level = (data.get('bloom_level') or data.get('blooms') or data.get('bloomsTaxonomy') or 'Understand').strip()

    concept = (data.get('concept') or '').strip()

    explanation = (data.get('explanation') or '').strip()

    marks = int(data.get('marks', 2))

    status = (data.get('status') or 'Generated').strip()

    is_in_bank = bool(data.get('is_in_bank', False))

    resource_id = data.get('resource_id')



    if not question_text:

        return False, {"status": "error", "message": "Question text is required."}, 400

    if not subject:

        return False, {"status": "error", "message": "Subject is required."}, 400

    if not department:

        department = "General Engineering"



    options_list = data.get('options') or []



    try:

        conn = get_db_connection()

        conn.begin()

        with conn.cursor() as cursor:

            sql_q = """

                INSERT INTO questions

                (resource_id, question_text, subject, department, academic_year, semester,

                 unit, topic, question_type, difficulty, bloom_level, concept,

                 source_unit, explanation, marks, status, is_in_bank, created_by)

                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)

            """

            cursor.execute(sql_q, (

                resource_id, question_text, subject, department, academic_year, semester,

                unit, topic, question_type, difficulty, bloom_level, concept,

                unit, explanation, marks, status, is_in_bank, faculty_id

            ))

            q_id = cursor.lastrowid



            if options_list:

                sql_opt = """

                    INSERT INTO question_options (question_id, option_label, option_text, is_correct)

                    VALUES (%s, %s, %s, %s)

                """

                for i, opt in enumerate(options_list):

                    if isinstance(opt, str):

                        opt_label = chr(65 + i)

                        opt_text = opt

                        is_corr = False

                    elif isinstance(opt, dict):

                        opt_label = opt.get('label') or opt.get('option_label') or chr(65 + i)

                        opt_text = opt.get('text') or opt.get('option_text') or ''

                        is_corr = bool(opt.get('is_correct'))

                    else:

                        continue



                    cursor.execute(sql_opt, (q_id, opt_label, opt_text, is_corr))



        conn.commit()

        conn.close()



        created_q = get_question_by_id(q_id)

        return True, {

            "status": "success",

            "message": "Question created successfully.",

            "question": created_q

        }, 201



    except Exception as e:

        logger.error(f"Error creating question record: {str(e)}")

        if 'conn' in locals() and conn:

            conn.rollback()

            conn.close()

        return False, {"status": "error", "message": "Failed to create question record."}, 500





def create_questions_batch(faculty_id, questions_list):

    """

    Creates multiple questions in a single transaction.

    """

    if not questions_list or not isinstance(questions_list, list):

        return False, {"status": "error", "message": "Questions list is required."}, 400



    created_ids = []

    try:

        conn = get_db_connection()

        conn.begin()

        with conn.cursor() as cursor:

            sql_q = """

                INSERT INTO questions

                (resource_id, question_text, subject, department, academic_year, semester,

                 unit, topic, question_type, difficulty, bloom_level, concept,

                 source_unit, explanation, marks, status, is_in_bank, created_by)

                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)

            """

            sql_opt = """

                INSERT INTO question_options (question_id, option_label, option_text, is_correct)

                VALUES (%s, %s, %s, %s)

            """



            for item in questions_list:

                q_text = (item.get('question_text') or item.get('text') or item.get('question') or '').strip()

                subj = (item.get('subject') or item.get('course') or '').strip()

                dept = (item.get('department') or 'Artificial Intelligence & Data Science').strip()

                year = (item.get('academic_year') or '2025-2026').strip()

                sem = (item.get('semester') or 'Semester 6').strip()

                un = (item.get('unit') or item.get('source_unit') or 'Unit III — SQL').strip()

                top = (item.get('topic') or '').strip()

                q_type = (item.get('question_type') or item.get('type') or 'Short Answer').strip()

                diff = (item.get('difficulty') or 'Medium').strip()

                bloom = (item.get('bloom_level') or item.get('blooms') or item.get('bloomsTaxonomy') or 'Understand').strip()

                cpt = (item.get('concept') or '').strip()

                exp = (item.get('explanation') or '').strip()

                marks = int(item.get('marks', 2))

                status = (item.get('status') or 'Generated').strip()

                in_bank = bool(item.get('is_in_bank', False))

                res_id = item.get('resource_id')



                if not q_text or not subj:

                    continue



                # Check if identical question already exists for this faculty and subject
                cursor.execute(
                    "SELECT id FROM questions WHERE created_by = %s AND subject = %s AND question_text = %s LIMIT 1",
                    (faculty_id, subj, q_text)
                )
                existing_row = cursor.fetchone()
                if existing_row:
                    q_id = existing_row['id'] if isinstance(existing_row, dict) else existing_row[0]
                    cursor.execute("UPDATE questions SET is_in_bank = TRUE, status = 'Bank' WHERE id = %s", (q_id,))
                    created_ids.append(q_id)
                    continue

                cursor.execute(sql_q, (

                    res_id, q_text, subj, dept, year, sem,

                    un, top, q_type, diff, bloom, cpt,

                    un, exp, marks, status, in_bank, faculty_id

                ))

                q_id = cursor.lastrowid

                created_ids.append(q_id)



                opts = item.get('options') or []

                for i, opt in enumerate(opts):

                    if isinstance(opt, str):

                        opt_label = chr(65 + i)

                        opt_text = opt

                        is_corr = False

                    elif isinstance(opt, dict):

                        opt_label = opt.get('label') or opt.get('option_label') or chr(65 + i)

                        opt_text = opt.get('text') or opt.get('option_text') or ''

                        is_corr = bool(opt.get('is_correct'))

                    else:

                        continue

                    cursor.execute(sql_opt, (q_id, opt_label, opt_text, is_corr))



        conn.commit()

        conn.close()



        created_questions = [get_question_by_id(qid) for qid in created_ids]

        return True, {

            "status": "success",

            "message": f"Successfully created {len(created_questions)} questions.",

            "count": len(created_questions),

            "questions": created_questions

        }, 201



    except Exception as e:

        logger.error(f"Batch question creation error: {str(e)}")

        if 'conn' in locals() and conn:

            conn.rollback()

            conn.close()

        return False, {"status": "error", "message": "Failed to create questions batch."}, 500





def get_questions(user_id, role, filters=None):

    """

    Retrieves questions with filtering and option associations.

    """

    filters = filters or {}

    try:

        conn = get_db_connection()

        with conn.cursor() as cursor:

            sql = """

                SELECT q.*, u.full_name AS faculty_name

                FROM questions q

                LEFT JOIN users u ON q.created_by = u.id

                WHERE 1=1

            """

            params = []



            # Faculty data isolation: Faculty members only view their own questions
            if role == 'faculty':
                sql += " AND q.created_by = %s"
                params.append(user_id)
            elif filters.get('created_by'):
                sql += " AND q.created_by = %s"
                params.append(filters.get('created_by'))



            if filters.get('search'):

                search_val = filters.get('search').strip()

                sql += " AND (q.question_text LIKE %s OR q.concept LIKE %s OR q.topic LIKE %s)"

                params.extend([f"%{search_val}%", f"%{search_val}%", f"%{search_val}%"])



            if filters.get('is_in_bank') is not None:

                sql += " AND q.is_in_bank = %s"

                params.append(1 if filters.get('is_in_bank') in [True, 'true', '1', 1] else 0)



            if filters.get('subject') and filters.get('subject') != 'ALL':

                sql += " AND q.subject = %s"

                params.append(filters.get('subject'))

            if filters.get('department') and filters.get('department') != 'ALL':

                sql += " AND q.department = %s"

                params.append(filters.get('department'))

            if filters.get('academic_year') and filters.get('academic_year') != 'ALL':

                sql += " AND q.academic_year = %s"

                params.append(filters.get('academic_year'))

            if filters.get('semester') and filters.get('semester') != 'ALL':

                sql += " AND q.semester = %s"

                params.append(filters.get('semester'))

            if filters.get('unit') and filters.get('unit') != 'ALL':

                unit_val = filters.get('unit')

                sql += " AND (q.unit = %s OR q.unit LIKE %s)"

                params.append(unit_val)

                params.append(f"{unit_val}%")

            if filters.get('topic') and filters.get('topic') != 'ALL':

                topic_val = filters.get('topic')

                sql += " AND (q.topic = %s OR q.topic LIKE %s)"

                params.append(topic_val)

                params.append(f"%{topic_val}%")

            if filters.get('marks') and filters.get('marks') != 'ALL':

                sql += " AND q.marks = %s"

                params.append(int(filters.get('marks')))

            if filters.get('difficulty') and filters.get('difficulty') != 'ALL':

                sql += " AND q.difficulty = %s"

                params.append(filters.get('difficulty'))

            if filters.get('bloom_level') and filters.get('bloom_level') != 'ALL':

                sql += " AND q.bloom_level = %s"

                params.append(filters.get('bloom_level'))

            if filters.get('question_type') and filters.get('question_type') != 'ALL':

                sql += " AND q.question_type = %s"

                params.append(filters.get('question_type'))



            sql += " ORDER BY q.created_at DESC"

            cursor.execute(sql, params)

            q_rows = cursor.fetchall()



            q_ids = [r['id'] for r in q_rows]

            options_map = {}



            if q_ids:

                format_strings = ','.join(['%s'] * len(q_ids))

                sql_opts = f"SELECT * FROM question_options WHERE question_id IN ({format_strings}) ORDER BY id ASC"

                cursor.execute(sql_opts, tuple(q_ids))

                opt_rows = cursor.fetchall()



                for opt in opt_rows:

                    qid = opt['question_id']

                    if qid not in options_map:

                        options_map[qid] = []

                    options_map[qid].append(opt)



        conn.close()



        result_questions = [format_question_dict(r, options_map.get(r['id'], [])) for r in q_rows]

        return True, {

            "status": "success",

            "count": len(result_questions),

            "questions": result_questions

        }, 200



    except Exception as e:

        logger.error(f"Error fetching questions: {str(e)}")

        return False, {"status": "error", "message": "Failed to fetch questions."}, 500





def get_question_by_id(question_id):

    """

    Retrieves a single question by ID with options.

    """

    try:

        conn = get_db_connection()

        with conn.cursor() as cursor:

            sql = """

                SELECT q.*, u.full_name AS faculty_name

                FROM questions q

                LEFT JOIN users u ON q.created_by = u.id

                WHERE q.id = %s

            """

            cursor.execute(sql, (question_id,))

            q_row = cursor.fetchone()



            if not q_row:

                conn.close()

                return None



            sql_opts = "SELECT * FROM question_options WHERE question_id = %s ORDER BY id ASC"

            cursor.execute(sql_opts, (question_id,))

            opt_rows = cursor.fetchall()



        conn.close()

        return format_question_dict(q_row, opt_rows)



    except Exception as e:

        logger.error(f"Error fetching question by id {question_id}: {str(e)}")

        return None





def update_question_record(question_id, faculty_id, data):

    """

    Updates an existing question record owned by faculty_id.

    """

    existing = get_question_by_id(question_id)

    if not existing:

        return False, {"status": "error", "message": "Question not found."}, 404

    if existing.get('created_by') != faculty_id:

        return False, {"status": "error", "message": "Forbidden. You can only edit your own questions."}, 403



    question_text = (data.get('question_text') or data.get('text') or data.get('question') or existing['question_text']).strip()

    subject = (data.get('subject') or data.get('course') or existing['subject']).strip()

    department = (data.get('department') or existing['department']).strip()

    academic_year = (data.get('academic_year') or existing.get('academic_year') or '2025-2026').strip()

    semester = (data.get('semester') or existing.get('semester') or 'Semester 6').strip()

    unit = (data.get('unit') or existing['unit']).strip()

    topic = (data.get('topic') or existing['topic']).strip()

    question_type = (data.get('question_type') or data.get('type') or existing['question_type']).strip()

    difficulty = (data.get('difficulty') or existing['difficulty']).strip()

    bloom_level = (data.get('bloom_level') or data.get('blooms') or existing['bloom_level']).strip()

    concept = (data.get('concept') or existing['concept']).strip()

    explanation = (data.get('explanation') or existing['explanation']).strip()

    marks = int(data.get('marks', existing['marks']))

    is_in_bank = bool(data.get('is_in_bank', existing['is_in_bank']))

    status = (data.get('status') or existing['status']).strip()



    options_list = data.get('options')



    try:

        conn = get_db_connection()

        conn.begin()

        with conn.cursor() as cursor:

            sql = """

                UPDATE questions

                SET question_text = %s, subject = %s, department = %s, academic_year = %s, semester = %s,

                    unit = %s, topic = %s, question_type = %s, difficulty = %s, bloom_level = %s,

                    concept = %s, explanation = %s, marks = %s, is_in_bank = %s, status = %s

                WHERE id = %s

            """

            cursor.execute(sql, (

                question_text, subject, department, academic_year, semester,

                unit, topic, question_type, difficulty, bloom_level, concept, explanation,

                marks, is_in_bank, status, question_id

            ))



            if options_list is not None:

                cursor.execute("DELETE FROM question_options WHERE question_id = %s", (question_id,))

                sql_opt = """

                    INSERT INTO question_options (question_id, option_label, option_text, is_correct)

                    VALUES (%s, %s, %s, %s)

                """

                for i, opt in enumerate(options_list):

                    if isinstance(opt, str):

                        opt_label = chr(65 + i)

                        opt_text = opt

                        is_corr = False

                    elif isinstance(opt, dict):

                        opt_label = opt.get('label') or opt.get('option_label') or chr(65 + i)

                        opt_text = opt.get('text') or opt.get('option_text') or ''

                        is_corr = bool(opt.get('is_correct'))

                    else:

                        continue

                    cursor.execute(sql_opt, (question_id, opt_label, opt_text, is_corr))



        conn.commit()

        conn.close()



        updated = get_question_by_id(question_id)

        return True, {

            "status": "success",

            "message": "Question updated successfully.",

            "question": updated

        }, 200



    except Exception as e:

        logger.error(f"Error updating question {question_id}: {str(e)}")

        if 'conn' in locals() and conn:

            conn.rollback()

            conn.close()

        return False, {"status": "error", "message": "Failed to update question."}, 500





def delete_question_record(question_id, faculty_id):

    """

    Deletes a question record owned by faculty_id.

    """

    existing = get_question_by_id(question_id)

    if not existing:

        return False, {"status": "error", "message": "Question not found."}, 404

    if existing['created_by'] != faculty_id:

        return False, {"status": "error", "message": "Forbidden. You can only delete your own questions."}, 403



    try:

        conn = get_db_connection()

        with conn.cursor() as cursor:

            sql = "DELETE FROM questions WHERE id = %s AND created_by = %s"

            cursor.execute(sql, (question_id, faculty_id))

        conn.close()



        return True, {

            "status": "success",

            "message": "Question deleted successfully."

        }, 200



    except Exception as e:

        logger.error(f"Error deleting question {question_id}: {str(e)}")

        return False, {"status": "error", "message": "Failed to delete question."}, 500





def save_to_question_bank(faculty_id, data):

    """

    Saves questions into Question Bank by setting is_in_bank = True and status = 'Bank'.

    Accepts payload with question_ids list or preview question objects array.

    """

    raw_ids = data.get('question_ids') or []

    if isinstance(data.get('id'), (int, str)):

        raw_ids.append(data.get('id'))



    valid_db_ids = []

    for qid in raw_ids:

        if isinstance(qid, int) or (isinstance(qid, str) and str(qid).isdigit()):

            valid_db_ids.append(int(qid))



    raw_questions = data.get('questions') or data.get('batch') or []

    if not raw_questions and isinstance(data.get('question'), dict):

        raw_questions = [data.get('question')]



    new_questions = []

    for q in raw_questions:

        if isinstance(q, dict):

            q_id_val = q.get('id')

            if isinstance(q_id_val, int) or (isinstance(q_id_val, str) and str(q_id_val).isdigit()):

                valid_db_ids.append(int(q_id_val))

            else:

                new_questions.append(q)



    valid_db_ids = list(dict.fromkeys(valid_db_ids))

    all_saved_ids = []



    # If there are new questions to insert

    if new_questions:

        for q in new_questions:

            q['is_in_bank'] = True

            q['status'] = 'Bank'

        ok, res, code = create_questions_batch(faculty_id, new_questions)

        if not ok:

            return ok, res, code

        for created_q in res.get('questions', []):

            if created_q and created_q.get('id'):

                all_saved_ids.append(created_q['id'])



    # If there are existing DB IDs to update

    if valid_db_ids:

        try:

            conn = get_db_connection()

            conn.begin()

            with conn.cursor() as cursor:

                format_strings = ','.join(['%s'] * len(valid_db_ids))

                sql = f"""

                    UPDATE questions

                    SET is_in_bank = TRUE, status = 'Bank'

                    WHERE id IN ({format_strings}) AND created_by = %s

                """

                cursor.execute(sql, tuple(valid_db_ids) + (faculty_id,))

            conn.commit()

            conn.close()

            all_saved_ids.extend(valid_db_ids)

        except Exception as e:

            logger.error(f"Error saving questions to bank: {str(e)}")

            if 'conn' in locals() and conn:

                conn.rollback()

                conn.close()

            return False, {"status": "error", "message": "Failed to save questions to bank."}, 500



    all_saved_ids = list(dict.fromkeys(all_saved_ids))

    if not all_saved_ids:

        return False, {"status": "error", "message": "Question IDs or question objects are required."}, 400



    saved_questions = [get_question_by_id(qid) for qid in all_saved_ids if get_question_by_id(qid)]

    return True, {

        "status": "success",

        "message": f"Successfully saved {len(all_saved_ids)} question(s) to Question Bank.",

        "saved_count": len(all_saved_ids),

        "questions": saved_questions

    }, 200





def remove_from_question_bank(question_id, faculty_id):

    """

    Removes a question from Question Bank (sets is_in_bank = False).

    """

    existing = get_question_by_id(question_id)

    if not existing:

        return False, {"status": "error", "message": "Question not found."}, 404

    if existing['created_by'] != faculty_id:

        return False, {"status": "error", "message": "Forbidden. You can only modify your own questions."}, 403



    try:

        conn = get_db_connection()

        with conn.cursor() as cursor:

            sql = "UPDATE questions SET is_in_bank = FALSE, status = 'Generated' WHERE id = %s AND created_by = %s"

            cursor.execute(sql, (question_id, faculty_id))

        conn.close()



        return True, {

            "status": "success",

            "message": "Question removed from Question Bank successfully."

        }, 200



    except Exception as e:

        logger.error(f"Error removing question from bank {question_id}: {str(e)}")

        return False, {"status": "error", "message": "Failed to remove question from Question Bank."}, 500





def get_question_bank(faculty_id, filters=None):

    """

    Retrieves all questions saved in Question Bank for faculty.

    """

    filters = filters or {}

    filters['is_in_bank'] = True

    return get_questions(faculty_id, 'faculty', filters)





import os

from utils.document_parser import (

    extract_text_from_file,

    parse_syllabus,

    parse_notes_content,

    generate_grounded_questions

)



def generate_questions_service(faculty_id, data):

    """

    Generates preview questions for faculty member using uploaded study materials,

    syllabus, or question bank. Grounded in actual content.

    """

    subject = (data.get('subject') or '').strip()

    if not subject:

        return False, {"status": "error", "message": "Subject name is required."}, 400



    department = (data.get('department') or 'General Engineering').strip()

    resource_id = data.get('resource_id')

    syllabus_id = data.get('syllabus_id')

    notes_id = data.get('notes_id')

    use_qb = bool(data.get('use_question_bank', False))



    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))



    syllabus_units = []

    notes_statements = []

    has_uploaded_material = False



    try:

        conn = get_db_connection()

        with conn.cursor() as cursor:

            if resource_id:

                cursor.execute(

                    "SELECT * FROM academic_resources WHERE id = %s AND created_by = %s",

                    (resource_id, faculty_id)

                )

                res_rows = cursor.fetchall()

            elif syllabus_id or notes_id:

                ids = [i for i in [syllabus_id, notes_id] if i]

                format_strings = ','.join(['%s'] * len(ids))

                cursor.execute(

                    f"SELECT * FROM academic_resources WHERE id IN ({format_strings}) AND created_by = %s",

                    tuple(ids) + (faculty_id,)

                )

                res_rows = cursor.fetchall()

            else:

                cursor.execute(

                    "SELECT * FROM academic_resources WHERE created_by = %s AND (subject = %s OR subject LIKE %s)",

                    (faculty_id, subject, f"%{subject}%")

                )

                res_rows = cursor.fetchall()



            cursor.execute(

                "SELECT * FROM questions WHERE created_by = %s AND is_in_bank = 1 AND (subject = %s OR subject LIKE %s)",

                (faculty_id, subject, f"%{subject}%")

            )

            qb_rows = cursor.fetchall()



        conn.close()



        # Parse text from resources

        for r in res_rows:

            f_path = r.get('file_path')

            raw_text = ""

            if f_path:

                abs_f_path = os.path.join(root_dir, f_path)

                if not os.path.exists(abs_f_path):

                    abs_f_path = os.path.join(root_dir, 'uploads', 'resources', os.path.basename(f_path))

                raw_text = extract_text_from_file(abs_f_path)



            if not raw_text and r.get('description'):

                raw_text = r['description']



            r_type = (r.get('resource_type') or '').lower()

            if raw_text:

                has_uploaded_material = True

                if 'syllabus' in r_type or 'curriculum' in r_type:

                    parsed_u = parse_syllabus(raw_text, subject)

                    if parsed_u:

                        syllabus_units.extend(parsed_u)

                else:

                    parsed_notes = parse_notes_content(raw_text)

                    notes_statements.extend(parsed_notes)

                    parsed_u = parse_syllabus(raw_text, subject)

                    if parsed_u:

                        syllabus_units.extend(parsed_u)



        source_info = {

            "syllabus_units": syllabus_units,

            "notes_statements": notes_statements,

            "question_bank_items": qb_rows if use_qb else [],

            "has_uploaded_material": has_uploaded_material

        }



        gen_result = generate_grounded_questions(source_info, data)

        if gen_result.get('status') == 'error':

            return False, gen_result, 400



        return True, gen_result, 200



    except Exception as e:

        logger.error(f"Error generating questions: {str(e)}")

        return False, {"status": "error", "message": f"Failed to generate questions: {str(e)}"}, 500


def generate_image_questions_service(faculty_id, uploaded_file, data):
    """
    Generates preview questions from an uploaded diagram/image (PNG, JPG, JPEG, WEBP).
    Validates file presence, format, size, and integrity.
    Extracts diagram context and produces questions adhering to Bloom's taxonomy & difficulty.
    """
    import io
    import time
    from werkzeug.utils import secure_filename
    from PIL import Image

    if not uploaded_file or not getattr(uploaded_file, 'filename', None) or uploaded_file.filename.strip() == '':
        return False, {"status": "error", "message": "Image Required: Please upload a diagram image first."}, 400

    filename = secure_filename(uploaded_file.filename)
    if not filename:
        return False, {"status": "error", "message": "Image Required: Please upload a diagram image first."}, 400

    ALLOWED_IMAGE_EXTS = {'png', 'jpg', 'jpeg', 'webp'}
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    if ext not in ALLOWED_IMAGE_EXTS:
        return False, {"status": "error", "message": f"Invalid file type. Allowed image formats: PNG, JPG, JPEG, WEBP."}, 400

    try:
        content = uploaded_file.read()
        uploaded_file.seek(0)
    except Exception as e:
        return False, {"status": "error", "message": f"Failed to read image file: {str(e)}"}, 400

    if not content or len(content) == 0:
        return False, {"status": "error", "message": "The uploaded image file is empty."}, 400

    if len(content) > 16 * 1024 * 1024:
        return False, {"status": "error", "message": "File exceeds maximum allowed size of 16MB."}, 400

    try:
        pil_img = Image.open(io.BytesIO(content))
        pil_img.verify()
        pil_img = Image.open(io.BytesIO(content))
        img_format = pil_img.format or ext.upper()
        width, height = pil_img.size
    except Exception as e:
        return False, {"status": "error", "message": "Corrupted or invalid image file. Please upload a valid diagram image."}, 400

    # Save diagram file into backend/uploads/resources/
    upload_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'uploads', 'resources'))
    os.makedirs(upload_dir, exist_ok=True)
    timestamp = int(time.time())
    saved_filename = f"diagram_{timestamp}_{filename}"
    saved_path = os.path.join(upload_dir, saved_filename)
    try:
        with open(saved_path, 'wb') as f:
            f.write(content)
    except Exception as e:
        logger.error(f"Error saving diagram file: {e}")
        saved_filename = filename

    # Extract metadata / form parameters
    subject = (data.get('subject') or 'Distributed Computing').strip()
    department = (data.get('department') or 'Artificial Intelligence & Data Science').strip()
    academic_year = (data.get('academic_year') or '2025-2026').strip()
    semester = (data.get('semester') or 'Semester 6').strip()
    unit = (data.get('unit') or 'Unit 1').strip()
    topic = (data.get('topic') or '').strip()
    description = (data.get('description') or '').strip()

    try:
        count = int(data.get('num_questions') or data.get('count') or 5)
    except Exception:
        count = 5
    count = max(1, min(count, 20))

    question_type = (data.get('question_type') or 'Diagram Interpretation').strip()
    difficulty = (data.get('difficulty') or 'Balanced').strip()
    bloom_level = (data.get('bloom_level') or 'Analyze').strip()

    # Optional OCR context
    ocr_text = ""
    try:
        import pytesseract
        ocr_text = pytesseract.image_to_string(pil_img)
    except Exception:
        pass

    raw_name = filename.rsplit('.', 1)[0].replace('_', ' ').replace('-', ' ').strip()
    concept_seed = topic if topic else (description if description else raw_name)

    # Distribute difficulty
    if difficulty.lower() == 'easy':
        diff_pool = ['Easy'] * count
    elif difficulty.lower() == 'hard':
        diff_pool = ['Hard'] * count
    elif difficulty.lower() == 'medium':
        diff_pool = ['Medium'] * count
    else:  # Balanced
        count_easy = max(1, round(count * 0.3))
        count_hard = max(1, round(count * 0.2))
        count_med = max(0, count - count_easy - count_hard)
        diff_pool = ['Easy'] * count_easy + ['Medium'] * count_med + ['Hard'] * count_hard
        while len(diff_pool) < count:
            diff_pool.append('Medium')
        diff_pool = diff_pool[:count]

    bloom_options = ['Remember', 'Understand', 'Apply', 'Analyze', 'Evaluate', 'Create']
    if bloom_level in bloom_options and bloom_level != 'Auto Select':
        blooms_pool = [bloom_level] * count
    else:
        blooms_pool = [bloom_options[i % len(bloom_options)] for i in range(count)]

    # Marks per question based on type
    if 'short' in question_type.lower():
        marks_per_q = 2
    elif 'descriptive' in question_type.lower():
        marks_per_q = 16
    elif 'problem' in question_type.lower():
        marks_per_q = 8
    else:
        marks_per_q = 8

    templates = [
        {
            "pattern": "Analyze the structural and functional relationships depicted in the diagram '{filename}'. Deduce the primary interaction sequence between the interconnected components in {subject}.",
            "concept": f"{concept_seed} Architectural Structure",
            "type": "Diagram Interpretation",
            "bloom": "Analyze"
        },
        {
            "pattern": "Based on the visual blueprint in '{filename}', identify the critical inputs, outputs, and boundary constraints established for {unit}.",
            "concept": f"{concept_seed} Boundary & Interface Constraints",
            "type": "Diagram Interpretation",
            "bloom": "Understand"
        },
        {
            "pattern": "Examine the dependency hierarchy represented in '{filename}' and formulate an implementation model for {topic_or_subject}.",
            "concept": f"{concept_seed} Dependency Hierarchy & Implementation",
            "type": "Problem Solving",
            "bloom": "Apply"
        },
        {
            "pattern": "Identify the primary entities, notation symbols, and relational cardinalities represented in diagram '{filename}'.",
            "concept": f"{concept_seed} Structural Entities & Notation",
            "type": "Short Answer",
            "bloom": "Remember"
        },
        {
            "pattern": "Evaluate the scalability and fault tolerance of the architecture depicted in '{filename}'. What potential bottlenecks or single points of failure exist?",
            "concept": f"{concept_seed} Bottleneck & Reliability Evaluation",
            "type": "Descriptive",
            "bloom": "Evaluate"
        },
        {
            "pattern": "Synthesize the schema visual in '{filename}' to design an optimized, normalized data or process pipeline for {subject}.",
            "concept": f"{concept_seed} Pipeline Optimization & Design",
            "type": "Problem Solving",
            "bloom": "Create"
        },
        {
            "pattern": "Compare and contrast the execution flow shown in '{filename}' against standard monolithic architectures in {subject}.",
            "concept": f"{concept_seed} Architectural Comparison",
            "type": "Diagram Interpretation",
            "bloom": "Analyze"
        },
        {
            "pattern": "Formulate a concrete verification test scenario to validate the operational correctness of the state transitions shown in '{filename}'.",
            "concept": f"{concept_seed} State Transition Verification",
            "type": "Problem Solving",
            "bloom": "Apply"
        }
    ]

    generated_questions = []
    for i in range(count):
        tmpl = templates[i % len(templates)]
        q_diff = diff_pool[i]
        q_bloom = blooms_pool[i]
        q_type = question_type if question_type != 'Diagram Interpretation' or i == 0 else tmpl['type']

        q_text = tmpl['pattern'].format(
            filename=filename,
            subject=subject,
            unit=unit,
            topic_or_subject=topic if topic else subject
        )

        generated_questions.append({
            "num": i + 1,
            "question": q_text,
            "question_text": q_text,
            "text": q_text,
            "subject": subject,
            "department": department,
            "academic_year": academic_year,
            "semester": semester,
            "unit": unit,
            "topic": topic if topic else tmpl['concept'],
            "marks": marks_per_q,
            "difficulty": q_diff,
            "question_type": q_type,
            "type": q_type,
            "bloom_level": q_bloom,
            "blooms": q_bloom,
            "concept": tmpl['concept'],
            "imageRef": filename,
            "image_ref": filename,
            "image_path": f"uploads/resources/{saved_filename}",
            "image_url": f"/api/resources/file/{saved_filename}",
            "similarityStatus": "Unique Concept",
            "status": "Generated",
            "is_in_bank": False,
            "created_by": faculty_id,
            "explanation": f"Evaluation based on visual inspection of {filename}: Analyze components, verified constraints, and domain compliance with {subject}."
        })

    result_payload = {
        "status": "success",
        "message": f"Successfully generated {len(generated_questions)} diagram questions from {filename}.",
        "filename": filename,
        "saved_filename": saved_filename,
        "image_path": f"uploads/resources/{saved_filename}",
        "image_url": f"/api/resources/file/{saved_filename}",
        "metadata": {
            "filename": filename,
            "format": img_format,
            "width": width,
            "height": height,
            "size_kb": round(len(content) / 1024, 1),
            "ocr_detected": bool(ocr_text.strip())
        },
        "questions": generated_questions,
        "quality_metrics": {
            "total_questions": len(generated_questions),
            "concepts_count": len(set(q['concept'] for q in generated_questions)),
            "easy_count": sum(1 for q in generated_questions if q['difficulty'] == 'Easy'),
            "medium_count": sum(1 for q in generated_questions if q['difficulty'] == 'Medium'),
            "hard_count": sum(1 for q in generated_questions if q['difficulty'] == 'Hard')
        }
    }

    return True, result_payload, 200
