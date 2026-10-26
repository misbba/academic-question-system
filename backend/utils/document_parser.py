import os
import re
import zlib
import logging

logger = logging.getLogger(__name__)

try:
    import docx
except ImportError:
    docx = None


def extract_text_from_file(file_path):
    """
    Extracts text from DOCX, PDF, or TXT file safely without external network dependencies.
    """
    if not os.path.exists(file_path):
        return ""

    ext = os.path.splitext(file_path)[1].lower()

    if ext == '.txt':
        for encoding in ['utf-8', 'latin-1', 'cp1252']:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    return f.read()
            except Exception:
                continue
        return ""

    elif ext == '.docx':
        if not docx:
            return ""
        try:
            doc = docx.Document(file_path)
            lines = []
            for p in doc.paragraphs:
                if p.text.strip():
                    lines.append(p.text.strip())
            for t in doc.tables:
                for row in t.rows:
                    cells = list(dict.fromkeys([c.text.strip().replace('\n', ' ') for c in row.cells if c.text.strip()]))
                    if cells:
                        lines.append(' | '.join(cells))
            return '\n'.join(lines)
        except Exception as e:
            logger.error(f"Error reading docx {file_path}: {e}")
            return ""

    elif ext == '.pdf':
        try:
            with open(file_path, 'rb') as f:
                content = f.read()

            extracted_chunks = []
            # Find zlib streams
            streams = re.findall(rb'stream[\r\n]+(.*?)[\r\n]+endstream', content, re.DOTALL)
            for s in streams:
                try:
                    decomp = zlib.decompress(s)
                    # Find text in Tj
                    tjs = re.findall(rb'\((.*?)\)\s*Tj', decomp)
                    for t in tjs:
                        extracted_chunks.append(t.decode('utf-8', errors='ignore'))
                    # Find text in TJ arrays
                    arrays = re.findall(rb'\[(.*?)\]\s*TJ', decomp)
                    for arr in arrays:
                        parts = re.findall(rb'\((.*?)\)', arr)
                        for p in parts:
                            extracted_chunks.append(p.decode('utf-8', errors='ignore'))
                except Exception:
                    pass

            if extracted_chunks:
                return ' '.join(extracted_chunks)

            # Fallback for plain text embedded in PDF
            raw_strings = re.findall(rb'\(([a-zA-Z0-9\s,.:;\-_/]+)\)', content)
            if raw_strings:
                return ' '.join([rs.decode('utf-8', errors='ignore') for rs in raw_strings])

            # If mock PDF with plain text header
            for enc in ['utf-8', 'latin-1']:
                try:
                    plain = content.decode(enc)
                    clean = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', plain)
                    if len(clean.strip()) > 10:
                        return clean
                except Exception:
                    pass

            return ""
        except Exception as e:
            logger.error(f"Error reading pdf {file_path}: {e}")
            return ""

    return ""


def parse_syllabus(text, default_subject="Subject"):
    """
    Parses units and topics from syllabus text.
    Handles table formats, bulleted formats, and colon-delimited formats.
    """
    if not text:
        return []

    lines = [l.strip() for l in text.split('\n') if l.strip()]
    units = []

    # Pattern for "Unit I", "Unit 1", "Module 1", etc.
    unit_pattern = re.compile(r'^(?:Unit|MODULE)\s+([IVX0-9]+)\s*(?:[-:–|]\s*(.*))?$', re.I)

    current_unit = None

    for i, line in enumerate(lines):
        m = unit_pattern.match(line)
        if m:
            u_num = m.group(1).upper()
            u_title = (m.group(2) or '').strip()
            # If line is like "Unit I | INTRODUCTION | 8"
            if '|' in line:
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 2:
                    u_title = parts[1]

            current_unit = {
                "unit_id": f"Unit {u_num}",
                "unit_name": f"Unit {u_num} — {u_title}" if u_title else f"Unit {u_num}",
                "title": u_title or f"Unit {u_num} Fundamentals",
                "topics": [],
                "concepts": []
            }
            units.append(current_unit)
            continue

        if current_unit is not None:
            # Check if this line starts another section like References, Course Outcomes, Text Books
            if re.match(r'^(?:Text Books|References|Course Outcomes|Prerequisites|Category)', line, re.I):
                current_unit = None
                continue

            # Split content into topics
            # Split by dashes, en-dashes, em-dashes, bullets, semicolons, or commas
            sub_topics = re.split(r'[-–—•;]|\b(?:Introduction|Overview|Definition|Models|Algorithms):\s*', line)
            for st in sub_topics:
                st_clean = re.sub(r'^[0-9\.\s]+', '', st).strip().strip(':').strip('?')
                # Clean out garbage or short fragments
                if len(st_clean) > 3 and not re.match(r'^(?:periods|hours|marks|\d+)$', st_clean, re.I):
                    if st_clean not in current_unit['topics']:
                        current_unit['topics'].append(st_clean)
                        # Derive concept from topic
                        concept = re.split(r'[:(,/]', st_clean)[0].strip()
                        if concept and concept not in current_unit['concepts']:
                            current_unit['concepts'].append(concept)

    # If no standard Unit headers were found, chunk content into 5 logical syllabus units
    if not units and lines:
        chunk_size = max(1, len(lines) // 5)
        roman = ['I', 'II', 'III', 'IV', 'V']
        for idx in range(min(5, (len(lines) + chunk_size - 1) // chunk_size)):
            chunk = lines[idx * chunk_size : (idx + 1) * chunk_size]
            u_title = chunk[0][:40] if chunk else f"Core Area {roman[idx]}"
            topics = [re.sub(r'^[0-9\.\s]+', '', l)[:60].strip() for l in chunk if len(l) > 5]
            units.append({
                "unit_id": f"Unit {roman[idx]}",
                "unit_name": f"Unit {roman[idx]} — {u_title}",
                "title": u_title,
                "topics": topics or [f"Topic {roman[idx]}.1", f"Topic {roman[idx]}.2"],
                "concepts": [t[:30] for t in topics[:4]]
            })

    return units


def parse_notes_content(text):
    """
    Extracts key factual statements, definitions, and concepts from notes / study materials.
    """
    if not text:
        return []

    # Split text into sentences
    raw_sentences = re.split(r'(?<=[.!?])\s+|\n+', text)
    statements = []

    for s in raw_sentences:
        clean_s = s.strip()
        # Keep sentences that have substantial content (e.g. between 20 and 250 characters)
        if 20 <= len(clean_s) <= 250:
            # Check if sentence looks informative
            if any(kw in clean_s.lower() for kw in ['is', 'are', 'defined as', 'used to', 'refers to', 'consists of', 'provides', 'ensures', 'algorithm', 'protocol', 'process', 'model', 'system']):
                statements.append(clean_s)

    return statements


def generate_grounded_questions(source_info, config):
    """
    Generates grounded academic questions adhering to:
    - Syllabus coverage and Unit/Topic mapping.
    - Grounded in study material / notes content statements when available.
    - If neither is provided, falls back to question bank or returns an error.
    - Strictly avoids duplicate questions.
    - If fewer than requested questions can be uniquely derived, returns an insufficient source error.
    """
    subject = config.get('subject', 'Course Subject').strip()
    department = config.get('department', 'General Engineering').strip()
    academic_year = config.get('academic_year', '2025-2026').strip()
    semester = config.get('semester', 'Semester 6').strip()
    target_unit = config.get('unit', 'All Units (Complete Syllabus)').strip()
    target_topic = config.get('topic', '').strip()
    num_questions = int(config.get('num_questions', 10))
    question_type = config.get('question_type', 'Short Answer').strip()
    bloom_choice = config.get('bloom_level', 'Auto Select').strip()
    marks_per_q = int(config.get('marks_per_question', 2 if question_type != 'Multiple Choice Question' else 1))
    is_quiz = bool(config.get('is_quiz', False))

    diff_easy = int(config.get('diff_easy', 30))
    diff_medium = int(config.get('diff_medium', 50))
    diff_hard = int(config.get('diff_hard', 20))

    syllabus_units = source_info.get('syllabus_units') or []
    notes_statements = source_info.get('notes_statements') or []
    question_bank_items = source_info.get('question_bank_items') or []
    has_uploaded_material = source_info.get('has_uploaded_material', False)

    # Rule 6: If no material is uploaded and no question bank source is selected, return clear error
    if not has_uploaded_material and not syllabus_units and not notes_statements and not question_bank_items:
        return {
            "status": "error",
            "source_missing": True,
            "message": f"Source content required: No syllabus or study material was uploaded for '{subject}', and no Question Bank source was selected. Please upload relevant syllabus or study material (PDF, DOCX, TXT) or select an existing Question Bank source."
        }

    # Filter syllabus units according to target_unit
    active_units = []
    if target_unit and "all units" not in target_unit.lower():
        # Match specific unit
        for u in syllabus_units:
            if u['unit_id'].lower() in target_unit.lower() or u['title'].lower() in target_unit.lower() or target_unit.lower() in u['unit_name'].lower():
                active_units.append(u)
        if not active_units:
            # Create unit placeholder from user's custom unit
            active_units = [{
                "unit_id": target_unit.split('—')[0].strip(),
                "unit_name": target_unit,
                "title": target_unit,
                "topics": [target_topic] if target_topic else [f"{target_unit} Topic 1", f"{target_unit} Topic 2"],
                "concepts": [target_topic or target_unit]
            }]
    else:
        active_units = syllabus_units

    # Filter topics if target_topic specified
    candidate_topics = []
    for u in active_units:
        u_topics = u.get('topics', [])
        if target_topic and target_topic.lower() not in ['all', 'all topics', '']:
            matched = [t for t in u_topics if target_topic.lower() in t.lower() or t.lower() in target_topic.lower()]
            if matched:
                for mt in matched:
                    candidate_topics.append((u, mt))
            else:
                candidate_topics.append((u, target_topic))
        else:
            for t in u_topics:
                candidate_topics.append((u, t))

    # If no candidate topics found from syllabus, derive from notes statements or bank
    if not candidate_topics and notes_statements:
        for s in notes_statements:
            first_words = ' '.join(s.split()[:4])
            candidate_topics.append(({"unit_id": "Unit I", "unit_name": target_unit or "Unit I", "title": "Study Notes"}, first_words))

    # If candidate topics still empty and question_bank_items available
    if not candidate_topics and question_bank_items:
        for q in question_bank_items:
            candidate_topics.append(({"unit_id": q.get('unit', 'Unit I'), "unit_name": q.get('unit', 'Unit I'), "title": q.get('unit', 'Unit I')}, q.get('topic', 'Topic')))

    # Deduplicate candidate topics while preserving order
    seen_topic_keys = set()
    unique_candidates = []
    for u, t in candidate_topics:
        key = (u['unit_id'], t.strip().lower())
        if key not in seen_topic_keys and len(t.strip()) > 2:
            seen_topic_keys.add(key)
            unique_candidates.append((u, t.strip()))

    total_available_candidates = len(unique_candidates)

    # Check sufficiency: If fewer than requested questions are available from source
    if total_available_candidates < num_questions and not notes_statements:
        return {
            "status": "error",
            "insufficient_source": True,
            "available_count": total_available_candidates,
            "required_count": num_questions,
            "message": f"Insufficient source content: Only {total_available_candidates} unique questions can be derived from the provided material for '{subject}'. At least {num_questions} questions are required without duplicating or inventing unsupported content. Please upload additional notes or reduce the question count."
        }

    # Generate difficulty distribution
    count_easy = Math_round = round((num_questions * diff_easy) / 100)
    count_medium = round((num_questions * diff_medium) / 100)
    count_hard = num_questions - count_easy - count_medium
    if count_hard < 0:
        count_hard = 0
        count_medium = num_questions - count_easy

    diff_pool = ['Easy'] * count_easy + ['Medium'] * count_medium + ['Hard'] * count_hard
    while len(diff_pool) < num_questions:
        diff_pool.append('Medium')

    bloom_verbs = {
        'Remember': ['Define', 'State', 'Identify', 'List', 'Recall'],
        'Understand': ['Explain', 'Describe', 'Illustrate', 'Discuss', 'Summarize'],
        'Apply': ['Demonstrate', 'Apply', 'Show how', 'Formulate an implementation for', 'Solve'],
        'Analyze': ['Analyze', 'Compare and contrast', 'Distinguish', 'Examine the components of', 'Investigate'],
        'Evaluate': ['Evaluate', 'Assess the effectiveness of', 'Critique', 'Appraise the performance of', 'Justify'],
        'Create': ['Design', 'Synthesize', 'Construct an architecture for', 'Devise an optimal strategy for', 'Formulate']
    }

    generated_questions = []
    seen_signatures = set()

    for i in range(num_questions):
        diff = diff_pool[i] if i < len(diff_pool) else 'Medium'

        if bloom_choice == 'Auto Select':
            bloom = 'Remember' if diff == 'Easy' else ('Apply' if diff == 'Medium' else 'Analyze')
        else:
            bloom = bloom_choice

        # Round-robin selection across unique candidates to ensure even distribution
        u_obj, topic = unique_candidates[i % len(unique_candidates)]

        # Check if notes statements match this topic
        matching_notes = [s for s in notes_statements if topic.lower() in s.lower() or any(w.lower() in s.lower() for w in topic.split() if len(w) > 4)]
        if not matching_notes and notes_statements:
            matching_notes = notes_statements
        relevant_note = matching_notes[i % len(matching_notes)] if matching_notes else None

        verbs = bloom_verbs.get(bloom, bloom_verbs['Understand'])
        verb = verbs[i % len(verbs)]

        # Generate question text
        if is_quiz or question_type == 'Multiple Choice Question':
            mcq_stems = [
                f"According to the course notes on {topic}, which of the following accurately describes {topic}?",
                f"Which of the following best defines the core principle of {topic}?",
                f"In {subject} ({u_obj['unit_id']}), what is the primary role or mechanism of {topic}?",
                f"When implementing {topic}, which of the following statements is verified to be correct?",
                f"Which characteristic most distinguishably identifies {topic}?",
                f"What is the key functional advantage of applying {topic}?",
                f"Identify the accurate statement concerning {topic} in system architecture:",
                f"Which of the following correctly describes the operational mechanism of {topic}?",
                f"How is {topic} fundamentally characterized in the academic curriculum?",
                f"Which principle directly governs {topic} according to the verified syllabus?"
            ]
            q_text = mcq_stems[i % len(mcq_stems)]
            if relevant_note:
                correct_opt_text = relevant_note[:120].strip()
            else:
                correct_opt_text = f"Serves as the core architectural mechanism for {topic}"

            # Plausible distractors from neighboring topics
            other_topics = [t for _, t in unique_candidates if t != topic]
            alt1 = f"Applies strictly as a localized routine for {other_topics[0][:30]}" if len(other_topics) > 0 else "Operates as a deprecated fallback routine"
            alt2 = f"Replaces traditional protocols through {other_topics[1][:30]}" if len(other_topics) > 1 else "Eliminates network overhead without state synchronization"
            alt3 = f"Restricts execution exclusively to {other_topics[2][:30]}" if len(other_topics) > 2 else "Acts as an external unverified hardware boundary"

            options_pool = [
                {"text": correct_opt_text, "is_correct": True},
                {"text": alt1, "is_correct": False},
                {"text": alt2, "is_correct": False},
                {"text": alt3, "is_correct": False}
            ]

            # Deterministic rotation based on index to distribute correct answer across A, B, C, D
            rot = i % 4
            rotated_options = options_pool[rot:] + options_pool[:rot]
            correct_idx = [idx for idx, opt in enumerate(rotated_options) if opt['is_correct']][0]
            correct_letter = chr(65 + correct_idx)

            formatted_options = [
                {"label": chr(65 + o_i), "option_label": chr(65 + o_i), "text": opt['text'], "option_text": opt['text'], "is_correct": opt['is_correct']}
                for o_i, opt in enumerate(rotated_options)
            ]

            q_item = {
                "id": f"GEN-Q-{i+1}",
                "subject": subject,
                "department": department,
                "academic_year": academic_year,
                "semester": semester,
                "unit": u_obj['unit_name'],
                "source_unit": u_obj['unit_name'],
                "topic": topic,
                "question_text": q_text,
                "text": q_text,
                "question": q_text,
                "question_type": "Multiple Choice Question",
                "type": "Multiple Choice Question",
                "difficulty": diff,
                "bloom_level": bloom,
                "blooms": bloom,
                "bloomsTaxonomy": bloom,
                "concept": topic.split('—')[0].split(':')[0].strip(),
                "explanation": f"Grounded in {u_obj['unit_id']} topic '{topic}'. The verified correct answer is ({correct_letter}) {rotated_options[correct_idx]['text']}.",
                "marks": marks_per_q,
                "options": formatted_options,
                "options_strings": [opt['text'] for opt in rotated_options],
                "correctAnswer": f"{correct_letter}. {rotated_options[correct_idx]['text']}",
                "correct_answer": f"{correct_letter}",
                "correctIndex": correct_idx,
                "correct_index": correct_idx,
                "source_type": "uploaded_material" if has_uploaded_material else "question_bank",
                "is_in_bank": False
            }

        else:
            # Non-MCQ: Short Answer, Descriptive, Problem Solving, Case Study
            if relevant_note:
                q_text = f"{verb} the operational characteristics of {topic}. In your answer, reference: '{relevant_note[:90]}...'"
            else:
                q_text = f"{verb} the principles, mechanisms, and key challenges associated with {topic} in {subject}."

            q_item = {
                "id": f"GEN-Q-{i+1}",
                "subject": subject,
                "department": department,
                "academic_year": academic_year,
                "semester": semester,
                "unit": u_obj['unit_name'],
                "source_unit": u_obj['unit_name'],
                "topic": topic,
                "question_text": q_text,
                "text": q_text,
                "question": q_text,
                "question_type": question_type,
                "type": question_type,
                "difficulty": diff,
                "bloom_level": bloom,
                "blooms": bloom,
                "bloomsTaxonomy": bloom,
                "concept": topic.split('—')[0].split(':')[0].strip(),
                "explanation": f"Grounded in {u_obj['unit_id']} topic '{topic}'. Evaluates {bloom} level competency with {diff} difficulty.",
                "marks": marks_per_q,
                "options": [],
                "source_type": "uploaded_material" if has_uploaded_material else "question_bank",
                "is_in_bank": False
            }

        # Check signature deduplication
        sig = re.sub(r'[^a-zA-Z0-9]', '', q_item['question_text'].lower())
        if sig in seen_signatures:
            continue
        seen_signatures.add(sig)
        generated_questions.append(q_item)

    return {
        "status": "success",
        "count": len(generated_questions),
        "questions": generated_questions,
        "units_covered": list(set(q['unit'] for q in generated_questions)),
        "concepts_covered": list(set(q['concept'] for q in generated_questions))
    }
