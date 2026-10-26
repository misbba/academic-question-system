with open('backend/utils/document_parser.py', 'r', encoding='utf-8') as f:
    orig = f.read()

# 1. Update extract_text_from_file to support pptx and ppt
pdf_target = """            return ""
        except Exception as e:
            logger.error(f"Error reading pdf {file_path}: {e}")
            return ""

    return \"\""""

pptx_code = """            return ""
        except Exception as e:
            logger.error(f"Error reading pdf {file_path}: {e}")
            return ""

    elif ext == '.pptx':
        try:
            import zipfile
            lines = []
            with zipfile.ZipFile(file_path, 'r') as z:
                slide_files = sorted([n for n in z.namelist() if n.startswith('ppt/slides/slide') and n.endswith('.xml')])
                for s in slide_files:
                    xml_data = z.read(s).decode('utf-8', errors='ignore')
                    texts = re.findall(r'<a:t[^>]*>(.*?)</a:t>', xml_data)
                    slide_text = ' '.join(texts).strip()
                    if slide_text:
                        lines.append(slide_text)
            return '\\n'.join(lines)
        except Exception as e:
            logger.error(f"Error reading pptx {file_path}: {e}")
            return ""

    elif ext == '.ppt':
        try:
            with open(file_path, 'rb') as f:
                c_bytes = f.read()
            raw_strs = re.findall(rb'[\\x20-\\x7E\\t\\r\\n]{4,}', c_bytes)
            return '\\n'.join([s.decode('utf-8', errors='ignore').strip() for s in raw_strs if len(s.strip()) > 5])
        except Exception as e:
            logger.error(f"Error reading ppt {file_path}: {e}")
            return ""

    return \"\""""

# Handle both CRLF and LF in target
orig_norm = orig.replace('\r\n', '\n')
pdf_target_norm = pdf_target.replace('\r\n', '\n')
assert pdf_target_norm in orig_norm, "pdf_target_norm must be in orig_norm!"
updated = orig_norm.replace(pdf_target_norm, pptx_code.replace('\r\n', '\n'), 1)
print("PPTX code inserted.")

# 2. Extract grounded quiz MCQ code from scratch/build_grounded_quiz_service.py
with open('scratch/build_grounded_quiz_service.py', 'r', encoding='utf-8') as f:
    service_code = f.read().replace('\r\n', '\n')

start_idx = service_code.find("TOPIC_QUESTIONS_BANK = {")
end_idx = service_code.find("print(\"generate_grounded_quiz_mcqs defined.\")")
mcq_code_block = service_code[start_idx:end_idx].strip()

# 3. Insert mcq_code_block before generate_grounded_questions
gen_q_target = "def generate_grounded_questions(source_info, config):"
assert gen_q_target in updated, "gen_q_target must be in updated!"
updated = updated.replace(gen_q_target, mcq_code_block + "\n\n\n" + gen_q_target, 1)
print("MCQ code block inserted.")

# 4. In generate_grounded_questions, delegate when is_quiz is True
quiz_check_target = """    if is_quiz:
        # Quiz Generator specifically supports 1 mark questions (along with 2, 8, 16 marks)
        if req_marks and req_marks not in ('1', '2', '8', '16', 'Mixed', 'mixed', 'Balanced', 'balanced', 'all', 'ALL', ''):
            return {
                "status": "error",
                "message": f"Invalid marks requested: '{req_marks}'. Quiz Generator supports 1 mark questions (or 2, 8, 16 marks)."
            }"""

quiz_replacement = """    if is_quiz:
        # Quiz Generator specifically supports 1 mark questions (along with 2, 8, 16 marks)
        if req_marks and req_marks not in ('1', '2', '8', '16', 'Mixed', 'mixed', 'Balanced', 'balanced', 'all', 'ALL', ''):
            return {
                "status": "error",
                "message": f"Invalid marks requested: '{req_marks}'. Quiz Generator supports 1 mark questions (or 2, 8, 16 marks)."
            }
        return generate_grounded_quiz_mcqs(source_info, config)"""

assert quiz_check_target in updated, "quiz_check_target must be in updated!"
updated = updated.replace(quiz_check_target, quiz_replacement, 1)
print("Quiz delegation inserted.")

# Write back preserving CRLF
with open('backend/utils/document_parser.py', 'w', encoding='utf-8', newline='\r\n') as f:
    f.write(updated)

print("document_parser.py updated and written successfully!")
