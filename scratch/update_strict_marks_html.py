# Update HTML files for strict 2, 8, 16 marks
import os

WORKSPACE = r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system"

def update_file(rel_path, target_sub, repl_sub):
    full_path = os.path.join(WORKSPACE, rel_path)
    with open(full_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # normalize CRLF to LF for reliable substring matching
    content_norm = content.replace('\r\n', '\n')
    target_norm = target_sub.replace('\r\n', '\n')
    repl_norm = repl_sub.replace('\r\n', '\n')
    
    if target_norm not in content_norm:
        raise ValueError(f"Target string not found in {rel_path}!")
    
    new_content = content_norm.replace(target_norm, repl_norm, 1)
    # Update script cache-buster if present
    new_content = new_content.replace('app.js?v=20261025', 'app.js?v=20261026_strict_marks')
    
    with open(full_path, 'w', encoding='utf-8', newline='\r\n') as f:
        f.write(new_content)
    print(f"Successfully updated {rel_path}!")

# 1. faculty-generate-questions.html
target_gen_q = """              <!-- Question Type -->
              <div class="col-md-3">
                <label for="genQuestionType" class="form-label fw-semibold">Question Type</label>
                <select class="form-select" id="genQuestionType" required>
                  <option value="Short Answer" selected>Short Answer</option>
                  <option value="Multiple Choice Question">Multiple Choice Question</option>
                  <option value="Descriptive">Descriptive</option>
                  <option value="Problem Solving">Problem Solving</option>
                  <option value="Case Study">Case Study</option>
                </select>
              </div>"""

repl_gen_q = """              <!-- Question Marks Configuration -->
              <div class="col-md-3">
                <label for="genMarks" class="form-label fw-semibold">Question Marks</label>
                <select class="form-select" id="genMarks" name="marks" required>
                  <option value="2">2 Marks (Part A - Concise / Concepts)</option>
                  <option value="8">8 Marks (Part B - Working Principle / Detailed)</option>
                  <option value="16">16 Marks (Part C - Comprehensive / Architecture)</option>
                  <option value="Mixed" selected>Mixed Marks (Balanced 2, 8 & 16 Marks)</option>
                </select>
                <input type="hidden" id="genQuestionType" value="Mixed">
              </div>"""

update_file("faculty-generate-questions.html", target_gen_q, repl_gen_q)

# 2. faculty-image-question.html
target_img_q = """                <div class="col-6">

                  <label class="form-label small fw-bold">Question Type</label>

                  <select class="form-select form-select-sm" id="imgTypeSelect">

                    <option value="Diagram Interpretation" selected>Diagram Interpretation</option>

                    <option value="Short Answer">Short Answer</option>

                    <option value="Descriptive">Descriptive</option>

                    <option value="Problem Solving">Problem Solving</option>

                  </select>

                </div>"""

repl_img_q = """                <div class="col-6">

                  <label class="form-label small fw-bold">Question Marks</label>

                  <select class="form-select form-select-sm" id="imgMarksSelect" name="marks">

                    <option value="2">2 Marks (Concise / Identification / Part A)</option>

                    <option value="8">8 Marks (Working Principle / Sequence / Part B)</option>

                    <option value="16">16 Marks (Comprehensive Architecture / Part C)</option>

                    <option value="Mixed" selected>Mixed Marks (Balanced 2, 8 & 16 Marks)</option>

                  </select>

                  <input type="hidden" id="imgTypeSelect" value="Diagram Interpretation">

                </div>"""

update_file("faculty-image-question.html", target_img_q, repl_img_q)

# 3. faculty-question-paper.html - filterPaperMarks
target_paper_filter = """              <select class="form-select form-select-sm" id="filterPaperMarks" onchange="renderQuestionPaperBankTable()">



                <option value="ALL">All Marks</option>



                <option value="2">2 Marks</option>



                <option value="5">5 Marks</option>



                <option value="8">8 Marks</option>



                <option value="13">13 Marks</option>



                <option value="15">15 Marks</option>



                <option value="16">16 Marks</option>"""

repl_paper_filter = """              <select class="form-select form-select-sm" id="filterPaperMarks" onchange="renderQuestionPaperBankTable()">



                <option value="ALL">All Marks (2, 8, 16 Marks)</option>



                <option value="2">2 Marks (Part A)</option>



                <option value="8">8 Marks (Part B Subquestion)</option>



                <option value="16">16 Marks (Part B / Full Question)</option>"""

update_file("faculty-question-paper.html", target_paper_filter, repl_paper_filter)

# 4. faculty-question-paper.html - addQMarks
target_paper_add = """                <select class="form-select" id="addQMarks" required>



                  <option value="2" selected>2 Marks (Part A)</option>



                  <option value="5">5 Marks (Part B Subquestion)</option>



                  <option value="8">8 Marks (Part B Subquestion / Internal)</option>



                  <option value="13">13 Marks (Semester Part B)</option>



                  <option value="15">15 Marks (Semester Part C)</option>



                  <option value="16">16 Marks (Internal Part C)</option>"""

repl_paper_add = """                <select class="form-select" id="addQMarks" required>



                  <option value="2" selected>2 Marks (Part A)</option>



                  <option value="8">8 Marks (Part B Subquestion / Internal)</option>



                  <option value="16">16 Marks (Part B Full / Internal Part C)</option>"""

update_file("faculty-question-paper.html", target_paper_add, repl_paper_add)

# 5. faculty-question-paper.html - editQMarks
target_paper_edit = """                <select class="form-select" id="editQMarks" required>



                  <option value="2">2 Marks</option>



                  <option value="5">5 Marks</option>



                  <option value="8">8 Marks</option>



                  <option value="13">13 Marks</option>



                  <option value="15">15 Marks</option>



                  <option value="16">16 Marks</option>"""

repl_paper_edit = """                <select class="form-select" id="editQMarks" required>



                  <option value="2">2 Marks (Part A)</option>



                  <option value="8">8 Marks (Part B Subquestion)</option>



                  <option value="16">16 Marks (Part B Full Extended)</option>"""

update_file("faculty-question-paper.html", target_paper_edit, repl_paper_edit)

# 6. faculty-generate-quiz.html - quizMarksPerQ
target_quiz_marks = """                <select class="form-select" id="quizMarksPerQ">
                  <option value="1" selected>1 Mark (30 Questions = 30 Marks)</option>
                  <option value="2">2 Marks (15 Questions = 30 Marks)</option>
                </select>"""

repl_quiz_marks = """                <select class="form-select" id="quizMarksPerQ">
                  <option value="2" selected>2 Marks (Concise Conceptual Questions)</option>
                  <option value="8">8 Marks (In-Depth Analytical Questions)</option>
                  <option value="16">16 Marks (Comprehensive Multi-Part Questions)</option>
                </select>"""

update_file("faculty-generate-quiz.html", target_quiz_marks, repl_quiz_marks)

print("\nALL HTML files updated successfully with STRICT 2, 8, 16 MARKS!")
