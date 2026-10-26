# Update js/app.js for escapeHtml, strict 2, 8, 16 marks across all workflows
import os

WORKSPACE = r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system"
APP_JS_PATH = os.path.join(WORKSPACE, "js", "app.js")

with open(APP_JS_PATH, 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Add escapeHtml at the very top if not present
if "function escapeHtml" not in code:
    escape_html_def = """// Utility: escapeHtml to prevent XSS and prevent undefined reference errors
function escapeHtml(str) {
  if (str === null || str === undefined) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}
window.escapeHtml = escapeHtml;

"""
    code = escape_html_def + code
    print("Added global escapeHtml definition to js/app.js")

# 2. Update initQuestionGeneratorPage marks reading & payload
old_gen_q_block = """      const question_type = document.getElementById('genQuestionType')?.value || 'Short Answer';
      const blooms_choice = document.getElementById('genBloomsLevel')?.value || 'Auto Select';
      const pEasy = parseInt(document.getElementById('pctEasy')?.value || '30', 10);
      const pMedium = parseInt(document.getElementById('pctMedium')?.value || '50', 10);
      const pHard = parseInt(document.getElementById('pctHard')?.value || '20', 10);
      const resourceId = document.getElementById('genResourceSelect')?.value || null;
      const useQb = document.getElementById('genUseQuestionBank')?.checked || false;

      // Persist values
      localStorage.setItem('academic_last_gen_q_config', JSON.stringify({
        department, subject, academic_year, semester, unit, topic, numQuestions, question_type, blooms_choice, pEasy, pMedium, pHard
      }));"""

new_gen_q_block = """      const marksVal = document.getElementById('genMarks')?.value || document.getElementById('genQuestionType')?.value || 'Mixed';
      let marks_per_question = 2;
      if (marksVal === '8') marks_per_question = 8;
      else if (marksVal === '16') marks_per_question = 16;
      else if (marksVal === 'Mixed') marks_per_question = 'Mixed';
      const question_type = marksVal === '2' ? 'Concise Definition (2 Marks)' : (marksVal === '8' ? 'Working Principle / Analysis (8 Marks)' : (marksVal === '16' ? 'Comprehensive Architecture (16 Marks)' : 'Mixed Marks (2, 8, 16M)'));
      const blooms_choice = document.getElementById('genBloomsLevel')?.value || 'Auto Select';
      const pEasy = parseInt(document.getElementById('pctEasy')?.value || '30', 10);
      const pMedium = parseInt(document.getElementById('pctMedium')?.value || '50', 10);
      const pHard = parseInt(document.getElementById('pctHard')?.value || '20', 10);
      const resourceId = document.getElementById('genResourceSelect')?.value || null;
      const useQb = document.getElementById('genUseQuestionBank')?.checked || false;

      // Persist values
      localStorage.setItem('academic_last_gen_q_config', JSON.stringify({
        department, subject, academic_year, semester, unit, topic, numQuestions, question_type, marks: marksVal, blooms_choice, pEasy, pMedium, pHard
      }));"""

# Normalize CRLF
code_norm = code.replace('\r\n', '\n')
old_norm = old_gen_q_block.replace('\r\n', '\n')
new_norm = new_gen_q_block.replace('\r\n', '\n')

if old_norm in code_norm:
    code_norm = code_norm.replace(old_norm, new_norm, 1)
    print("Updated initQuestionGeneratorPage marks extraction")
else:
    print("Warning: old_gen_q_block not found in code_norm")

# Update payload to pass marks
old_payload = """      const payload = {
        department,
        subject,
        academic_year,
        semester,
        unit,
        topic,
        num_questions: numQuestions,
        question_type,
        bloom_level: blooms_choice,"""

new_payload = """      const payload = {
        department,
        subject,
        academic_year,
        semester,
        unit,
        topic,
        num_questions: numQuestions,
        marks: marksVal,
        marks_per_question: marks_per_question,
        question_type,
        bloom_level: blooms_choice,"""

if old_payload in code_norm:
    code_norm = code_norm.replace(old_payload, new_payload, 1)
    print("Updated payload to include marks and marks_per_question")
else:
    print("Warning: old_payload not found in code_norm")

# 3. Update image question generator marks reading
old_img_config = """  const count = parseInt(document.getElementById('imgCountSelect')?.value || "5", 10);
  const qType = document.getElementById('imgTypeSelect')?.value || "Diagram Interpretation";
  const diff = document.getElementById('imgDiffSelect')?.value || "Balanced";
  const blooms = document.getElementById('imgBloomsSelect')?.value || "Analyze";
  const desc = document.getElementById('imageDescriptionInput')?.value?.trim() || `Diagram of ${topic || subject}`;

  activeImageConfig = { dept, subject, unit: unitText, topic, count, qType, diff, blooms, desc, fileName: fileNameToUse };"""

new_img_config = """  const count = parseInt(document.getElementById('imgCountSelect')?.value || "5", 10);
  const imgMarks = document.getElementById('imgMarksSelect')?.value || document.getElementById('imgTypeSelect')?.value || "Mixed";
  const qType = imgMarks === '2' ? 'Concise Definition (2 Marks)' : (imgMarks === '8' ? 'Working Principle / Analysis (8 Marks)' : (imgMarks === '16' ? 'Comprehensive Architecture (16 Marks)' : 'Diagram Interpretation'));
  const diff = document.getElementById('imgDiffSelect')?.value || "Balanced";
  const blooms = document.getElementById('imgBloomsSelect')?.value || "Analyze";
  const desc = document.getElementById('imageDescriptionInput')?.value?.trim() || `Diagram of ${topic || subject}`;

  activeImageConfig = { dept, subject, unit: unitText, topic, count, marks: imgMarks, qType, diff, blooms, desc, fileName: fileNameToUse };"""

if old_img_config in code_norm:
    code_norm = code_norm.replace(old_img_config, new_img_config, 1)
    print("Updated activeImageConfig with imgMarks")
else:
    print("Warning: old_img_config not found in code_norm")

# Append marks to formData for image generation
old_formdata = """    formData.append('count', count);
    formData.append('question_type', qType);"""

new_formdata = """    formData.append('count', count);
    formData.append('marks', imgMarks);
    formData.append('marks_per_question', imgMarks);
    formData.append('question_type', qType);"""

if old_formdata in code_norm:
    code_norm = code_norm.replace(old_formdata, new_formdata, 1)
    print("Updated formData with marks and marks_per_question")
else:
    print("Warning: old_formdata not found in code_norm")

# Add marks badge to renderGeneratedImageQuestions
old_badge_render = """        <div class="d-flex align-items-center gap-2">
          <span class="badge bg-primary me-1">Q${q.num}</span>
          <span class="badge ${q.difficulty === 'Easy' ? 'bg-success' : q.difficulty === 'Medium' ? 'bg-warning text-dark' : 'bg-danger'}">${q.difficulty}</span>
          <span class="badge bg-info-subtle text-info border border-info">${q.type}</span>
          <span class="badge bg-light text-muted border">${q.blooms}</span>
        </div>"""

new_badge_render = """        <div class="d-flex align-items-center gap-2">
          <span class="badge bg-primary me-1">Q${q.num}</span>
          <span class="badge bg-dark fw-bold">${q.marks || 2} Marks</span>
          <span class="badge ${q.difficulty === 'Easy' ? 'bg-success' : q.difficulty === 'Medium' ? 'bg-warning text-dark' : 'bg-danger'}">${q.difficulty}</span>
          <span class="badge bg-info-subtle text-info border border-info">${q.type}</span>
          <span class="badge bg-light text-muted border">${q.blooms}</span>
        </div>"""

if old_badge_render in code_norm:
    code_norm = code_norm.replace(old_badge_render, new_badge_render, 1)
    print("Updated renderGeneratedImageQuestions with Marks badge")
else:
    print("Warning: old_badge_render not found in code_norm")

# Add validation to Paper Builder Add/Edit
old_add_q = """  const marks = parseInt(document.getElementById('addQMarks')?.value || '2', 10);



  const topic = document.getElementById('addQTopic')?.value;"""

new_add_q = """  const marks = parseInt(document.getElementById('addQMarks')?.value || '2', 10);
  if (![2, 8, 16].includes(marks)) {
    showToastNotice('Invalid Marks', 'Only 2, 8, and 16 marks questions are allowed.', 'warning');
    return;
  }



  const topic = document.getElementById('addQTopic')?.value;"""

if old_add_q in code_norm:
    code_norm = code_norm.replace(old_add_q, new_add_q, 1)
    print("Updated Paper Builder add question marks validation")
else:
    print("Warning: old_add_q not found in code_norm")

old_edit_q = """  const marks = parseInt(document.getElementById('editQMarks')?.value || '2', 10);



  const difficulty = document.getElementById('editQDifficulty')?.value;"""

new_edit_q = """  const marks = parseInt(document.getElementById('editQMarks')?.value || '2', 10);
  if (![2, 8, 16].includes(marks)) {
    showToastNotice('Invalid Marks', 'Only 2, 8, and 16 marks questions are allowed.', 'warning');
    return;
  }



  const difficulty = document.getElementById('editQDifficulty')?.value;"""

if old_edit_q in code_norm:
    code_norm = code_norm.replace(old_edit_q, new_edit_q, 1)
    print("Updated Paper Builder edit question marks validation")
else:
    print("Warning: old_edit_q not found in code_norm")

# Write back updated js/app.js
with open(APP_JS_PATH, 'w', encoding='utf-8', newline='\r\n') as f:
    f.write(code_norm)

print("ALL js/app.js updates applied successfully!")
