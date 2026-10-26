import re

app_js_path = r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\js\app.js"

with open(app_js_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add calculateAttemptedMarks and onExamTypeChanged
helper_functions = '''
// =========================================================================
// Strict Marks Calculation & Validation Engine
// =========================================================================
function calculateAttemptedMarks(sections) {
  if (!sections || !Array.isArray(sections)) return 0;
  let total = 0;
  sections.forEach(sec => {
    if (!sec || typeof sec !== 'object') return;
    const groups = sec.groups || sec.either_or_groups;
    if (groups && Array.isArray(groups) && groups.length > 0) {
      groups.forEach(g => {
        if (!g || typeof g !== 'object') return;
        const getAltMarks = (alt) => {
          if (!alt) return 0;
          if (Array.isArray(alt)) {
            return alt.reduce((sum, q) => sum + parseInt(q.marks || 0, 10), 0);
          } else if (typeof alt === 'object') {
            if (alt.is_subquestion || (alt.subquestions && Array.isArray(alt.subquestions))) {
              return (alt.subquestions || []).reduce((sum, sq) => sum + parseInt(sq.marks || 0, 10), 0);
            }
            return parseInt(alt.marks || 0, 10);
          }
          return 0;
        };
        const altA = g.alternative_a || g.option_a || g.alt_a;
        const altB = g.alternative_b || g.option_b || g.alt_b;
        const mA = getAltMarks(altA);
        const mB = getAltMarks(altB);
        let gMarks = 0;
        if (g.attempted_marks !== undefined && parseInt(g.attempted_marks, 10) > 0) {
          gMarks = parseInt(g.attempted_marks, 10);
        } else if (mA > 0) {
          gMarks = mA;
        } else if (mB > 0) {
          gMarks = mB;
        } else {
          gMarks = parseInt(sec.marks_per_q || 16, 10);
        }
        total += gMarks;
      });
    } else if (sec.questions && Array.isArray(sec.questions) && sec.questions.length > 0) {
      total += sec.questions.reduce((sum, q) => sum + parseInt(q.marks || 2, 10), 0);
    } else if (sec.attempted_marks !== undefined && parseInt(sec.attempted_marks, 10) > 0) {
      total += parseInt(sec.attempted_marks, 10);
    } else {
      const c = parseInt(sec.count || 0, 10);
      const m = parseInt(sec.marks_per_q || 2, 10);
      total += (c * m);
    }
  });
  return total;
}

function onExamTypeChanged() {
  const examType = document.getElementById('paperExamType')?.value || 'Semester Examination';
  const isSemester = examType.toLowerCase().includes('semester') || examType.toLowerCase().includes('model');
  const maxMarksInput = document.getElementById('paperMaxMarks');
  const durationInput = document.getElementById('paperDuration');

  if (isSemester) {
    if (maxMarksInput) maxMarksInput.value = 100;
    if (durationInput) durationInput.value = 'Three Hours';
  } else {
    if (maxMarksInput) maxMarksInput.value = 50;
    if (durationInput) durationInput.value = '100 Mins.';
  }

  calculatePaperMarksValidation();
  generateAcademicPaperPreview();
}
'''

# Insert calculateAttemptedMarks right before function renderPaperSectionStructure
old_render_sig = "function renderPaperSectionStructure(sections) {"
assert old_render_sig in content, "Could not find renderPaperSectionStructure"

# Replace renderPaperSectionStructure with improved marks calculation
new_render_func = '''
function renderPaperSectionStructure(sections) {
  const container = document.getElementById('paperSectionsStructureContainer');
  const overallMarksDisp = document.getElementById('overallMarksDisplay');
  const validationMsg = document.getElementById('marksValidationMsg');
  const maxMarksInput = document.getElementById('paperMaxMarks');
  const examTypeInput = document.getElementById('paperExamType');
  const examType = examTypeInput?.value || 'Semester Examination';
  const isSemester = examType.toLowerCase().includes('semester') || examType.toLowerCase().includes('model');
  const targetMaxMarks = parseInt(maxMarksInput?.value || (isSemester ? '100' : '50'), 10);

  if (!container) return;

  const activeSections = sections || window.currentGeneratedTemplate?.sections || null;

  if (!activeSections || !Array.isArray(activeSections) || activeSections.length === 0) {
    const defaultAttempted = isSemester ? 100 : 50;
    if (isSemester) {
      container.innerHTML = `
        <div class="row g-3">
          <div class="col-md-6"><div class="p-3 border rounded bg-white"><h6 class="fw-bold text-success mb-1">PART - A</h6><div class="small text-muted">10 Compulsory Questions × 2 Marks = 20 Attempted Marks</div></div></div>
          <div class="col-md-6"><div class="p-3 border rounded bg-white"><h6 class="fw-bold text-success mb-1">PART - B</h6><div class="small text-muted">5 Either/Or Groups × 16 Marks (Direct 16M or Split 8+8) = 80 Attempted Marks</div></div></div>
        </div>
      `;
    } else {
      container.innerHTML = `
        <div class="row g-3">
          <div class="col-md-4"><div class="p-3 border rounded bg-white"><h6 class="fw-bold text-primary mb-1">PART - A</h6><div class="small text-muted">5 Compulsory Questions × 2 Marks = 10 Attempted Marks</div></div></div>
          <div class="col-md-4"><div class="p-3 border rounded bg-white"><h6 class="fw-bold text-primary mb-1">PART - B</h6><div class="small text-muted">1 Either/Or Group × 8 Marks = 8 Attempted Marks</div></div></div>
          <div class="col-md-4"><div class="p-3 border rounded bg-white"><h6 class="fw-bold text-primary mb-1">PART - C</h6><div class="small text-muted">2 Either/Or Groups × 16 Marks = 32 Attempted Marks</div></div></div>
        </div>
      `;
    }
    if (overallMarksDisp) {
      overallMarksDisp.textContent = `Attempted Marks: ${defaultAttempted} / ${targetMaxMarks}`;
      overallMarksDisp.className = defaultAttempted === targetMaxMarks ? 'fw-bold text-success fs-6' : 'fw-bold text-danger fs-6';
    }
    if (validationMsg) {
      validationMsg.innerHTML = `<span class="alert alert-info d-inline-block py-2 px-3 mb-0 small"><i class="bi bi-info-circle me-1"></i> Ready to assemble ${isSemester ? 'Semester (100 Marks)' : 'Internal (50 Marks)'} examination paper.</span>`;
    }
    renderPartBGroupManager(null);
    return;
  }

  let totalAttempted = 0;
  const colSize = activeSections.length <= 2 ? 'col-md-6' : 'col-md-4';
  let html = '<div class="row g-3">';

  activeSections.forEach((sec) => {
    let secAttempted = 0;
    let details = '';
    const groups = sec.groups || sec.either_or_groups;

    if (groups && groups.length > 0) {
      const groupCount = groups.length;
      groups.forEach(g => {
        const getAltMarks = (alt) => {
          if (!alt) return 0;
          if (Array.isArray(alt)) return alt.reduce((sum, q) => sum + parseInt(q.marks || 0, 10), 0);
          if (typeof alt === 'object') {
            if (alt.is_subquestion || (alt.subquestions && Array.isArray(alt.subquestions))) {
              return (alt.subquestions || []).reduce((sum, sq) => sum + parseInt(sq.marks || 0, 10), 0);
            }
            return parseInt(alt.marks || 0, 10);
          }
          return 0;
        };
        const mA = getAltMarks(g.alternative_a || g.option_a || g.alt_a);
        const mB = getAltMarks(g.alternative_b || g.option_b || g.alt_b);
        let gM = g.attempted_marks ? parseInt(g.attempted_marks, 10) : (mA > 0 ? mA : (mB > 0 ? mB : parseInt(sec.marks_per_q || 16, 10)));
        secAttempted += gM;
      });
      const marksPerGroup = Math.round(secAttempted / groupCount);
      details = `${groupCount} Either/Or Group${groupCount > 1 ? 's' : ''} × ${marksPerGroup} Marks (Students answer only 1 alternative per group)`;
    } else {
      const qCount = (sec.questions && sec.questions.length) || sec.count || 0;
      const marksPerQ = sec.marks_per_q || 2;
      secAttempted = sec.questions && sec.questions.length > 0
        ? sec.questions.reduce((sum, q) => sum + parseInt(q.marks || marksPerQ, 10), 0)
        : (qCount * marksPerQ);
      details = `${qCount} Compulsory Questions × ${marksPerQ} Marks`;
    }

    totalAttempted += secAttempted;

    html += `
      <div class="${colSize}">
        <div class="p-3 border rounded bg-white h-100 shadow-sm">
          <div class="d-flex justify-content-between align-items-center mb-1">
            <h6 class="fw-bold text-primary mb-0">${sec.name || sec.title}</h6>
            <span class="badge bg-primary-subtle text-primary border">${secAttempted} Marks</span>
          </div>
          <p class="small text-muted mb-2">${details}</p>
          <div class="small text-success fw-semibold"><i class="bi bi-check2-circle me-1"></i>Attempted: ${secAttempted} Marks</div>
        </div>
      </div>
    `;
  });

  html += '</div>';
  container.innerHTML = html;

  if (overallMarksDisp) {
    overallMarksDisp.textContent = `Attempted Marks: ${totalAttempted} / ${targetMaxMarks}`;
    overallMarksDisp.className = totalAttempted === targetMaxMarks ? 'fw-bold text-success fs-6' : 'fw-bold text-danger fs-6';
  }

  if (validationMsg) {
    if (totalAttempted === targetMaxMarks) {
      if (isSemester) {
        validationMsg.innerHTML = `<span class="alert alert-success d-inline-block py-2 px-3 mb-0 small"><i class="bi bi-check-circle-fill me-1"></i> <strong>Official Semester Exam Structure Validated:</strong> Part A (20 Marks) + Part B (80 Marks: 5 Either/Or groups × 16 Marks) = Exactly ${totalAttempted} Attempted Marks. Strictly Part A & B only.</span>`;
      } else {
        validationMsg.innerHTML = `<span class="alert alert-success d-inline-block py-2 px-3 mb-0 small"><i class="bi bi-check-circle-fill me-1"></i> <strong>Official Internal Exam Structure Validated:</strong> Part A (10 Marks) + Part B (8 Marks) + Part C (32 Marks) = Exactly ${totalAttempted} Attempted Marks.</span>`;
      }
    } else {
      validationMsg.innerHTML = `<span class="alert alert-danger d-inline-block py-2 px-3 mb-0 small"><i class="bi bi-exclamation-triangle-fill me-1"></i> Total attempted marks (${totalAttempted}) differ from Target Maximum Marks (${targetMaxMarks}). ${isSemester ? 'Semester Examination requires exactly 100 attempted marks.' : 'Internal Examination requires exactly 50 attempted marks.'}</span>`;
    }
  }

  renderPartBGroupManager(activeSections);
  return totalAttempted === targetMaxMarks;
}
'''

# Replace old renderPaperSectionStructure block
# Find end of old renderPaperSectionStructure (ends with return totalAttempted === targetMaxMarks;\n})
render_end_marker = "return totalAttempted === targetMaxMarks;\n\n\n\n}"
assert render_end_marker in content, "Could not find render_end_marker"

render_start_pos = content.index(old_render_sig)
render_end_pos = content.index(render_end_marker) + len(render_end_marker)

content = content[:render_start_pos] + helper_functions + "\n" + new_render_func + "\n" + content[render_end_pos:]

# 2. Update publishQuestionPaperAction
old_pub = "async function publishQuestionPaperAction() {\n\n\n\n  await saveQuestionPaperToBackend('Published');\n\n\n\n}"
assert old_pub in content, "Could not find old_pub"

new_pub = '''async function publishQuestionPaperAction() {
  const examType = document.getElementById('paperExamType')?.value || 'Semester Examination';
  const sections = window.currentGeneratedTemplate?.sections || [];
  const isSemester = examType.toLowerCase().includes('semester') || examType.toLowerCase().includes('model');
  const attempted = calculateAttemptedMarks(sections);

  if (isSemester && attempted !== 100) {
    showToastNotice(
      'Validation Error',
      `Semester Examination must have exactly 100 attempted marks (calculated: ${attempted} marks). The marks calculation must count only the marks students actually attempt, not both Either/Or alternatives. Please click "Generate Semester Exam (100 Marks)" to assemble the required 100-mark structure.`,
      'danger'
    );
    return;
  }

  if (!isSemester && attempted !== 50) {
    showToastNotice(
      'Validation Error',
      `Internal Examination must have exactly 50 attempted marks (calculated: ${attempted} marks). The marks calculation must count only the marks students actually attempt, not both Either/Or alternatives. Please click "Generate Internal Exam (50 Marks)" to assemble the required 50-mark structure.`,
      'danger'
    );
    return;
  }

  await saveQuestionPaperToBackend('Published');
}'''

content = content.replace(old_pub, new_pub, 1)

# 3. Update initQuestionPaperBuilder to support paper_id from URL
old_init = "function initQuestionPaperBuilder() {\n\n\n\n  loadQuestionPaperBuilderPage();\n\n\n\n}"
assert old_init in content, "Could not find old_init"

new_init = '''async function loadExistingPaperById(paperId) {
  try {
    const res = await fetch(`http://localhost:5000/api/question-papers/${paperId}`, { credentials: 'include' });
    if (!res.ok) return;
    const data = await res.json();
    const paper = data.paper || data.question_paper;
    if (!paper) return;

    window.currentSavedPaper = paper;
    window.currentGeneratedTemplate = paper;

    if (document.getElementById('paperDept')) document.getElementById('paperDept').value = paper.department || '';
    if (document.getElementById('paperSubject')) document.getElementById('paperSubject').value = paper.subject || '';
    if (document.getElementById('paperYear')) document.getElementById('paperYear').value = paper.academic_year || '2025-2026';
    if (document.getElementById('paperSem')) document.getElementById('paperSem').value = paper.semester || 'Sixth Semester';
    if (document.getElementById('paperExamType')) document.getElementById('paperExamType').value = paper.exam_type || 'Semester Examination';
    if (document.getElementById('paperMaxMarks')) document.getElementById('paperMaxMarks').value = paper.total_marks || 100;
    if (document.getElementById('paperDuration')) document.getElementById('paperDuration').value = paper.duration || 'Three Hours';
    if (document.getElementById('paperInstructions')) document.getElementById('paperInstructions').value = paper.instructions || '';

    const questionsList = [];
    if (paper.sections && Array.isArray(paper.sections)) {
      paper.sections.forEach(sec => {
        if (sec.questions && Array.isArray(sec.questions)) {
          sec.questions.forEach(q => questionsList.push(q));
        }
        const groups = sec.groups || sec.either_or_groups || [];
        groups.forEach(g => {
          const addAlt = (alt) => {
            if (Array.isArray(alt)) alt.forEach(q => questionsList.push(q));
            else if (alt && alt.subquestions && Array.isArray(alt.subquestions)) {
              alt.subquestions.forEach(sq => questionsList.push(sq));
            } else if (alt) questionsList.push(alt);
          };
          addAlt(g.alternative_a || g.option_a || g.alt_a);
          addAlt(g.alternative_b || g.option_b || g.alt_b);
        });
      });
    }
    window.paperSelectedQuestions = questionsList;
    renderPaperSelectedQuestions();
    renderPaperSectionStructure(paper.sections);
    generateAcademicPaperPreview();
  } catch (err) {
    console.warn('Could not load paper by ID:', err);
  }
}

function initQuestionPaperBuilder() {
  const urlParams = new URLSearchParams(window.location.search);
  const paperId = urlParams.get('paper_id');
  if (paperId) {
    loadExistingPaperById(paperId);
  } else {
    loadQuestionPaperBuilderPage();
  }
}'''

content = content.replace(old_init, new_init, 1)

with open(app_js_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Successfully updated js/app.js with client-side calculateAttemptedMarks, onExamTypeChanged, pre-publishing validation, and paper_id URL loading!")
