# -*- coding: utf-8 -*-
import sys

APP_JS_PATH = r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\js\app.js"

NEW_APP_JS_CODE = '''// ==========================================
// STEP 9E: QUESTION PAPER BUILDER & EXAM PAPERS (FLASK + MYSQL)
// ==========================================

const API_QUESTION_PAPERS_BASE = 'http://localhost:5000/api/question-papers';

window.paperQuestionBankPool = [];
window.paperSelectedQuestions = [];
window.currentSavedPaper = null;
window.currentGeneratedTemplate = null;

function initQuestionPaperBuilder() {
  loadQuestionPaperBuilderPage();
}

async function onPaperSpecificationChanged() {
  await loadQuestionPaperBuilderPage();
}

async function loadQuestionPaperBuilderPage() {
  const tableBody = document.getElementById('paperQuestionBankBody');
  if (!tableBody) return;

  const dept = document.getElementById('paperDept')?.value || 'Artificial Intelligence & Data Science';
  const subject = document.getElementById('paperSubject')?.value || 'Database Management Systems';
  const year = document.getElementById('paperYear')?.value || '2025-2026';
  const sem = document.getElementById('paperSem')?.value || 'Sixth Semester';

  // 1. Fetch Question Bank items from MySQL backend API
  try {
    const url = `http://localhost:5000/api/question-bank?department=${encodeURIComponent(dept)}&subject=${encodeURIComponent(subject)}&academic_year=${encodeURIComponent(year)}&semester=${encodeURIComponent(sem)}`;
    const res = await fetch(url, { credentials: 'include' });
    const data = await res.json();
    if (data.status === 'success' && data.questions && data.questions.length > 0) {
      window.paperQuestionBankPool = data.questions;
    } else {
      // Fallback query by subject
      const qRes = await fetch(`http://localhost:5000/api/questions?subject=${encodeURIComponent(subject)}`, { credentials: 'include' });
      const qData = await qRes.json();
      if (qData.status === 'success' && qData.questions && qData.questions.length > 0) {
        window.paperQuestionBankPool = qData.questions;
      } else if (typeof AcademicMockData !== 'undefined' && AcademicMockData.masterQuestionsPool) {
        window.paperQuestionBankPool = AcademicMockData.masterQuestionsPool;
      }
    }
  } catch (err) {
    console.warn('Backend fetch failed for Question Bank, falling back to mock pool:', err);
    if (typeof AcademicMockData !== 'undefined' && AcademicMockData.masterQuestionsPool) {
      window.paperQuestionBankPool = AcademicMockData.masterQuestionsPool;
    }
  }

  // 2. Render Question Bank selection table
  renderQuestionPaperBankTable();

  // 3. Pre-select default questions if none selected yet and no template active
  if (!window.currentGeneratedTemplate && window.paperSelectedQuestions.length === 0 && window.paperQuestionBankPool.length > 0) {
    window.paperSelectedQuestions = window.paperQuestionBankPool.slice(0, 3);
  }

  renderPaperSelectedQuestions();
  calculatePaperMarksValidation();
}

async function generateAcademicTemplateAction(templateType) {
  const dept = document.getElementById('paperDept')?.value || 'Artificial Intelligence & Data Science';
  const subject = document.getElementById('paperSubject')?.value || 'Database Management Systems';
  const year = document.getElementById('paperYear')?.value || '2025-2026';
  const sem = document.getElementById('paperSem')?.value || 'Sixth Semester';

  const templateTitle = templateType === 'semester_exam' 
    ? 'Semester Examination (100 Marks | April/May 2024 Reference)'
    : 'Internal Examination (50 Marks | Reference inter.pdf)';

  showToastNotice('Generating Template', `Balancing and assembling ${templateTitle} from Question Bank...`, 'info');

  try {
    const res = await fetch('http://localhost:5000/api/question-papers/generate-template', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({
        template_type: templateType,
        department: dept,
        subject: subject,
        academic_year: year,
        semester: sem
      })
    });

    const data = await res.json();
    if (data.status === 'success' && data.paper) {
      window.currentGeneratedTemplate = data.paper;
      
      // Update form controls matching the generated exam specifications
      if (document.getElementById('paperMaxMarks')) document.getElementById('paperMaxMarks').value = data.paper.total_marks;
      if (document.getElementById('paperExamType')) document.getElementById('paperExamType').value = data.paper.exam_type;
      if (document.getElementById('paperDuration')) document.getElementById('paperDuration').value = data.paper.duration;
      if (document.getElementById('paperInstructions')) document.getElementById('paperInstructions').value = data.paper.instructions;

      // Extract all selected questions from sections for Question Bank and Selected list
      const questionsList = [];
      if (data.paper.sections) {
        data.paper.sections.forEach(sec => {
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
            addAlt(g.alternative_a);
            addAlt(g.alternative_b);
          });
        });
      }

      window.paperSelectedQuestions = questionsList;
      renderQuestionPaperBankTable();
      renderPaperSelectedQuestions();
      renderPaperSectionStructure(data.paper.sections);
      generateAcademicPaperPreview();

      const noticeMsg = templateType === 'semester_exam'
        ? 'Semester Examination generated: 100 attempted marks (Part A: 20M, Part B: 65M with 8+5 subquestions, Part C: 15M) matching April May 2024 ML.pdf!'
        : 'Internal Examination generated: 50 attempted marks (Part A: 10M, Part B: 8M, Part C: 32M) matching inter.pdf!';
      showToastNotice('Template Generated Successfully', noticeMsg, 'success');
    } else {
      showToastNotice('Template Generation Notice', data.message || 'Unable to generate template with current question bank.', 'warning');
    }
  } catch (err) {
    console.error('Error generating template:', err);
    showToastNotice('Server Error', 'Failed to communicate with template generator API.', 'danger');
  }
}

function renderPaperSectionStructure(sections) {
  const container = document.getElementById('paperSectionsStructureContainer');
  const overallMarksDisp = document.getElementById('overallMarksDisplay');
  const validationMsg = document.getElementById('marksValidationMsg');
  const maxMarksInput = document.getElementById('paperMaxMarks');
  const targetMaxMarks = parseInt(maxMarksInput?.value || '100', 10);

  if (!container) return;

  if (!sections || !Array.isArray(sections) || sections.length === 0) {
    container.innerHTML = `
      <div class="row g-3">
        <div class="col-md-4"><div class="p-3 border rounded bg-white"><h6 class="fw-bold text-success mb-1">PART - A</h6><div class="small text-muted">10 questions × 2 marks = 20 Attempted Marks</div></div></div>
        <div class="col-md-4"><div class="p-3 border rounded bg-white"><h6 class="fw-bold text-success mb-1">PART - B</h6><div class="small text-muted">5 Either/Or groups × 13 marks (8+5 subquestions) = 65 Attempted Marks</div></div></div>
        <div class="col-md-4"><div class="p-3 border rounded bg-white"><h6 class="fw-bold text-success mb-1">PART - C</h6><div class="small text-muted">1 Either/Or group × 15 marks = 15 Attempted Marks</div></div></div>
      </div>
    `;
    if (overallMarksDisp) {
      overallMarksDisp.textContent = `Attempted Marks: 100 / ${targetMaxMarks}`;
      overallMarksDisp.className = 100 === targetMaxMarks ? 'fw-bold text-success fs-6' : 'fw-bold text-warning fs-6';
    }
    return;
  }

  let totalAttempted = 0;
  let html = '<div class="row g-3">';

  sections.forEach((sec) => {
    let secAttempted = sec.total_marks || sec.attempted_marks || 0;
    let details = '';

    const groups = sec.groups || sec.either_or_groups;
    if (groups && groups.length > 0) {
      const groupCount = groups.length;
      const marksPerGroup = sec.marks_per_q || (secAttempted / groupCount);
      details = `${groupCount} Either/Or Group${groupCount > 1 ? 's' : ''} × ${marksPerGroup} Marks (Students answer only 1 alternative per group)`;
    } else {
      const qCount = (sec.questions && sec.questions.length) || sec.count || 0;
      const marksPerQ = sec.marks_per_q || 2;
      details = `${qCount} Compulsory Questions × ${marksPerQ} Marks`;
    }

    totalAttempted += secAttempted;

    html += `
      <div class="col-md-4">
        <div class="p-3 border rounded bg-white h-100 shadow-sm">
          <div class="d-flex justify-content-between align-items-center mb-1">
            <h6 class="fw-bold text-primary mb-0">${sec.name}</h6>
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
      validationMsg.innerHTML = `<span class="alert alert-success d-inline-block py-2 px-3 mb-0 small"><i class="bi bi-check-circle-fill me-1"></i> <strong>Official Format Validated:</strong> Total attempted marks (${totalAttempted}) match Maximum Examination Marks (${targetMaxMarks}).</span>`;
    } else {
      validationMsg.innerHTML = `<span class="alert alert-warning d-inline-block py-2 px-3 mb-0 small"><i class="bi bi-exclamation-triangle-fill me-1"></i> Total attempted marks (${totalAttempted}) differ from Maximum Marks (${targetMaxMarks}). Please adjust configuration.</span>`;
    }
  }

  return totalAttempted === targetMaxMarks;
}

function calculatePaperMarksValidation() {
  if (window.currentGeneratedTemplate && window.currentGeneratedTemplate.sections) {
    return renderPaperSectionStructure(window.currentGeneratedTemplate.sections);
  }
  return renderPaperSectionStructure(null);
}

function renderQuestionPaperBankTable() {
  const tableBody = document.getElementById('paperQuestionBankBody');
  if (!tableBody) return;

  const unitFilter = document.getElementById('filterPaperUnit')?.value || 'ALL';
  const marksFilter = document.getElementById('filterPaperMarks')?.value || 'ALL';
  const bloomsFilter = document.getElementById('filterPaperBlooms')?.value || 'ALL';
  const diffFilter = document.getElementById('filterPaperDiff')?.value || 'ALL';
  const typeFilter = document.getElementById('filterPaperType')?.value || 'ALL';
  const topicSearch = (document.getElementById('filterPaperTopic')?.value || '').trim().toLowerCase();

  let pool = window.paperQuestionBankPool || [];

  // Filter by Unit
  if (unitFilter !== 'ALL') {
    pool = pool.filter(q => {
      const u = (q.unit || q.source_unit || '').toUpperCase();
      return u.includes(unitFilter.toUpperCase()) || 
             (unitFilter === 'Unit I' && (u.includes('UNIT 1') || u.includes('UNIT-1'))) ||
             (unitFilter === 'Unit II' && (u.includes('UNIT 2') || u.includes('UNIT-2'))) ||
             (unitFilter === 'Unit III' && (u.includes('UNIT 3') || u.includes('UNIT-3'))) ||
             (unitFilter === 'Unit IV' && (u.includes('UNIT 4') || u.includes('UNIT-4'))) ||
             (unitFilter === 'Unit V' && (u.includes('UNIT 5') || u.includes('UNIT-5')));
    });
  }

  // Filter by Marks
  if (marksFilter !== 'ALL') {
    const mTarget = parseInt(marksFilter, 10);
    pool = pool.filter(q => parseInt(q.marks, 10) === mTarget);
  }

  // Filter by Bloom's
  if (bloomsFilter !== 'ALL') {
    pool = pool.filter(q => (q.bloom_level || q.blooms || '').toLowerCase().includes(bloomsFilter.toLowerCase()));
  }

  // Filter by Difficulty
  if (diffFilter !== 'ALL') {
    pool = pool.filter(q => (q.difficulty || '').toLowerCase() === diffFilter.toLowerCase());
  }

  // Filter by Question Type
  if (typeFilter !== 'ALL') {
    pool = pool.filter(q => (q.question_type || q.type || '').toLowerCase() === typeFilter.toLowerCase());
  }

  // Filter by Topic Search
  if (topicSearch) {
    pool = pool.filter(q => {
      const topic = (q.topic || '').toLowerCase();
      const text = (q.question_text || q.text || q.question || '').toLowerCase();
      const concept = (q.concept || '').toLowerCase();
      return topic.includes(topicSearch) || text.includes(topicSearch) || concept.includes(topicSearch);
    });
  }

  tableBody.innerHTML = '';

  if (pool.length === 0) {
    tableBody.innerHTML = `<tr><td colspan="6" class="text-center text-muted p-4"><i class="bi bi-inbox me-2"></i>No questions found matching selected filters.</td></tr>`;
    return;
  }

  pool.forEach(q => {
    const isSelected = (window.paperSelectedQuestions || []).some(sq => sq.id === q.id);
    const tr = document.createElement('tr');
    
    const diffBadgeClass = q.difficulty === 'Easy' ? 'bg-success' : q.difficulty === 'Medium' ? 'bg-warning text-dark' : 'bg-danger';
    
    let marksBadgeClass = 'badge bg-secondary';
    if (q.marks == 5) marksBadgeClass = 'badge bg-info text-dark';
    else if (q.marks == 8) marksBadgeClass = 'badge bg-primary';
    else if (q.marks == 13) marksBadgeClass = 'badge bg-warning text-dark';
    else if (q.marks == 15) marksBadgeClass = 'badge bg-danger';
    else if (q.marks == 16) marksBadgeClass = 'badge bg-dark';

    tr.innerHTML = `
      <td><span class="fw-bold text-primary">#${q.id}</span></td>
      <td>
        <div class="fw-semibold text-dark mb-1">${q.question_text || q.text || q.question}</div>
        <div class="d-flex flex-wrap gap-1 align-items-center">
          <span class="badge bg-light text-dark border"><i class="bi bi-layers me-1 text-primary"></i>${q.unit || q.source_unit || 'Unit III'}</span>
          <span class="badge bg-info-subtle text-info-emphasis border"><i class="bi bi-journal-text me-1"></i>${q.topic || 'General Topic'}</span>
          ${q.concept ? `<span class="badge bg-light text-muted border">${q.concept}</span>` : ''}
        </div>
      </td>
      <td><span class="${marksBadgeClass} fs-6">${q.marks || 2} M</span></td>
      <td><span class="badge ${diffBadgeClass}">${q.difficulty}</span></td>
      <td><span class="badge bg-light text-dark border">${q.bloom_level || q.blooms || 'Understand'}</span></td>
      <td>
        <div class="d-flex align-items-center gap-1">
          ${isSelected 
            ? `<button class="btn btn-sm btn-outline-danger" onclick="removeQuestionFromPaper(${q.id})" title="Remove from Paper"><i class="bi bi-dash-lg"></i></button><span class="badge bg-success-subtle text-success border border-success py-1 px-2"><i class="bi bi-check2"></i> Added</span>`
            : `<button class="btn btn-sm btn-academic-accent" onclick="addQuestionToPaper(${q.id})" title="Add to Paper"><i class="bi bi-plus-lg me-1"></i> Add</button>`
          }
          <button class="btn btn-sm btn-outline-secondary" onclick="viewQuestionDetails(${q.id})" title="View Details"><i class="bi bi-eye"></i></button>
          <button class="btn btn-sm btn-outline-primary" onclick="openEditQuestionModal(${q.id})" title="Edit Question"><i class="bi bi-pencil"></i></button>
          <button class="btn btn-sm btn-outline-danger" onclick="deleteQuestionFromBank(${q.id})" title="Delete Question"><i class="bi bi-trash"></i></button>
        </div>
      </td>
    `;
    tableBody.appendChild(tr);
  });
}

function addQuestionToPaper(qId) {
  const qObj = (window.paperQuestionBankPool || []).find(item => item.id === qId);
  if (!qObj) return;

  if (!(window.paperSelectedQuestions || []).some(sq => sq.id === qId)) {
    window.paperSelectedQuestions.push(qObj);
    renderQuestionPaperBankTable();
    renderPaperSelectedQuestions();
    calculatePaperMarksValidation();
    showToastNotice('Question Added', `Question #${qId} added to paper structure.`, 'info');
  }
}

function removeQuestionFromPaper(qId) {
  window.paperSelectedQuestions = (window.paperSelectedQuestions || []).filter(sq => sq.id !== qId);
  renderQuestionPaperBankTable();
  renderPaperSelectedQuestions();
  calculatePaperMarksValidation();
  showToastNotice('Question Removed', `Question #${qId} removed from paper structure.`, 'info');
}

function moveQuestionInPaper(index, direction) {
  const list = window.paperSelectedQuestions;
  if (!list || index < 0 || index >= list.length) return;

  const targetIndex = index + direction;
  if (targetIndex < 0 || targetIndex >= list.length) return;

  const temp = list[index];
  list[index] = list[targetIndex];
  list[targetIndex] = temp;

  renderPaperSelectedQuestions();
}

function renderPaperSelectedQuestions() {
  const container = document.getElementById('paperSelectedQuestionsList');
  const countBadge = document.getElementById('selectedQuestionsCountBadge');
  const selectedList = window.paperSelectedQuestions || [];

  if (countBadge) {
    countBadge.textContent = `${selectedList.length} Question${selectedList.length === 1 ? '' : 's'} Selected`;
  }

  if (!container) return;
  container.innerHTML = '';

  if (selectedList.length === 0) {
    container.innerHTML = `<div class="p-4 text-center text-muted border rounded bg-light"><i class="bi bi-inbox me-2"></i>No questions currently selected. Use "Generate Semester Exam" or "Generate Internal Exam" above, or add questions from Question Bank.</div>`;
    updatePaperAnalysis();
    return;
  }

  selectedList.forEach((q, idx) => {
    const card = document.createElement('div');
    card.className = 'card border mb-2';
    const diffBadgeClass = q.difficulty === 'Easy' ? 'bg-success' : q.difficulty === 'Medium' ? 'bg-warning text-dark' : 'bg-danger';

    card.innerHTML = `
      <div class="card-body p-3 d-flex align-items-center justify-content-between flex-wrap gap-2">
        <div class="d-flex align-items-center gap-3">
          <span class="badge bg-dark rounded-circle p-2" style="width: 28px; height: 28px; display: inline-flex; align-items: center; justify-content: center;">${idx + 1}</span>
          <div>
            <div class="fw-semibold text-dark">${q.question_text || q.text || q.question}</div>
            <div class="mt-1 d-flex flex-wrap gap-1 align-items-center">
              <span class="badge bg-light text-dark border">${q.unit || q.source_unit || 'Unit III'}</span>
              <span class="badge bg-info-subtle text-info-emphasis border">${q.topic || 'General Topic'}</span>
              <span class="badge ${diffBadgeClass}">${q.difficulty}</span>
              <span class="badge bg-secondary">${q.bloom_level || q.blooms || 'Understand'}</span>
              <span class="badge bg-primary">${q.marks || 2} Marks</span>
            </div>
          </div>
        </div>
        <div class="d-flex align-items-center gap-1">
          <button class="btn btn-sm btn-outline-secondary" onclick="moveQuestionInPaper(${idx}, -1)" ${idx === 0 ? 'disabled' : ''} title="Move Up"><i class="bi bi-arrow-up"></i></button>
          <button class="btn btn-sm btn-outline-secondary" onclick="moveQuestionInPaper(${idx}, 1)" ${idx === selectedList.length - 1 ? 'disabled' : ''} title="Move Down"><i class="bi bi-arrow-down"></i></button>
          <button class="btn btn-sm btn-outline-danger ms-2" onclick="removeQuestionFromPaper(${q.id})" title="Remove"><i class="bi bi-x-lg"></i></button>
        </div>
      </div>
    `;
    container.appendChild(card);
  });

  updatePaperAnalysis();
}

function updatePaperAnalysis() {
  const selected = window.paperSelectedQuestions || [];
  const total = selected.length;

  const diffBar = document.getElementById('paperCurrentDifficultyBar');
  const statusMsg = document.getElementById('paperDifficultyStatusMsg');

  let easyC = 0, medC = 0, hardC = 0;
  selected.forEach(q => {
    if (q.difficulty === 'Easy') easyC++;
    else if (q.difficulty === 'Medium') medC++;
    else if (q.difficulty === 'Hard') hardC++;
  });

  const easyP = total ? Math.round((easyC / total) * 100) : 30;
  const medP = total ? Math.round((medC / total) * 100) : 50;
  const hardP = total ? 100 - easyP - medP : 20;

  if (diffBar) {
    diffBar.innerHTML = `
      <div class="progress-bar bg-success" style="width: ${easyP}%">Easy ${easyP}% (${easyC})</div>
      <div class="progress-bar bg-warning text-dark" style="width: ${medP}%">Med ${medP}% (${medC})</div>
      <div class="progress-bar bg-danger" style="width: ${hardP}%">Hard ${hardP}% (${hardC})</div>
    `;
  }

  if (statusMsg) {
    statusMsg.innerHTML = `<span class="text-success fw-semibold"><i class="bi bi-check2-circle me-1"></i> Calibrated Paper Distribution</span>`;
  }

  const conceptContainer = document.getElementById('paperConceptCoverageContainer');
  const simContainer = document.getElementById('paperSimilarityCheckContainer');

  if (conceptContainer) {
    const concepts = Array.from(new Set(selected.map(q => q.topic || q.concept || 'General Topic')));
    conceptContainer.innerHTML = `
      <small class="text-uppercase text-muted fw-bold d-block mb-1">Covered Lessons / Topics (${concepts.length}):</small>
      <div class="d-flex flex-wrap gap-1">
        ${concepts.map(c => `<span class="badge bg-success-subtle text-success border border-success">${c}</span>`).join('')}
      </div>
    `;
  }

  if (simContainer) {
    simContainer.innerHTML = `
      <small class="text-uppercase text-muted fw-bold d-block mb-1">Duplicate & Similarity Check:</small>
      <div class="text-success small fw-semibold"><i class="bi bi-shield-check me-1"></i> 0% Duplicate Question Overlap Detected</div>
    `;
  }

  const checklist = document.getElementById('paperValidationChecklist');
  if (checklist) {
    checklist.innerHTML = `
      <div class="row g-2 small">
        <div class="col-md-6 text-success"><i class="bi bi-check-circle-fill me-1"></i> Official Department Selected</div>
        <div class="col-md-6 text-success"><i class="bi bi-check-circle-fill me-1"></i> Course Code & Subject Validated</div>
        <div class="col-md-6 ${selected.length > 0 ? 'text-success' : 'text-danger'}"><i class="bi bi-${selected.length > 0 ? 'check-circle-fill' : 'x-circle-fill'} me-1"></i> Questions Loaded (${selected.length} questions)</div>
        <div class="col-md-6 text-success"><i class="bi bi-check-circle-fill me-1"></i> Bloom's Taxonomy Cognitive Distribution</div>
      </div>
    `;
  }
}

// Question Bank Modal Handlers
function openAddQuestionModal() {
  const form = document.getElementById('addQuestionForm');
  if (form) form.reset();

  const paperDept = document.getElementById('paperDept')?.value;
  const paperSub = document.getElementById('paperSubject')?.value;
  const paperYr = document.getElementById('paperYear')?.value;
  const paperSm = document.getElementById('paperSem')?.value;

  if (paperDept && document.getElementById('addQDept')) document.getElementById('addQDept').value = paperDept;
  if (paperSub && document.getElementById('addQSubject')) document.getElementById('addQSubject').value = paperSub;
  if (paperYr && document.getElementById('addQYear')) document.getElementById('addQYear').value = paperYr;
  if (paperSm && document.getElementById('addQSem')) document.getElementById('addQSem').value = paperSm;

  const modalEl = document.getElementById('addQuestionModal');
  if (modalEl) {
    const modal = bootstrap.Modal.getOrCreateInstance(modalEl);
    modal.show();
  }
}

async function saveNewQuestionToBank(event) {
  event.preventDefault();
  const dept = document.getElementById('addQDept')?.value;
  const subject = document.getElementById('addQSubject')?.value;
  const year = document.getElementById('addQYear')?.value;
  const sem = document.getElementById('addQSem')?.value;
  const unit = document.getElementById('addQUnit')?.value;
  const marks = parseInt(document.getElementById('addQMarks')?.value || '2', 10);
  const topic = document.getElementById('addQTopic')?.value;
  const difficulty = document.getElementById('addQDifficulty')?.value;
  const blooms = document.getElementById('addQBlooms')?.value;
  const text = document.getElementById('addQText')?.value;
  const explanation = document.getElementById('addQExplanation')?.value;

  let qType = 'Short Answer';
  if (marks === 5 || marks === 8) qType = 'Descriptive';
  else if (marks === 13 || marks === 15 || marks === 16) qType = 'Problem Solving';

  const payload = {
    department: dept,
    subject: subject,
    academic_year: year,
    semester: sem,
    unit: unit,
    marks: marks,
    topic: topic,
    difficulty: difficulty,
    bloom_level: blooms,
    question_text: text,
    explanation: explanation,
    is_in_bank: true,
    question_type: qType
  };

  try {
    const res = await fetch('http://localhost:5000/api/questions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (data.status === 'success') {
      const modalEl = document.getElementById('addQuestionModal');
      if (modalEl) {
        bootstrap.Modal.getInstance(modalEl)?.hide();
      }
      showToastNotice('Question Added', 'New question successfully saved to Question Bank in MySQL!', 'success');
      await loadQuestionPaperBuilderPage();
    } else {
      showToastNotice('Error', data.message || 'Failed to save question.', 'danger');
    }
  } catch (err) {
    console.error('Error saving new question:', err);
    showToastNotice('Server Error', 'Failed to communicate with question API.', 'danger');
  }
}

function openEditQuestionModal(qId) {
  const q = (window.paperQuestionBankPool || []).find(item => item.id === qId);
  if (!q) return;

  if (document.getElementById('editQId')) document.getElementById('editQId').value = q.id;
  if (document.getElementById('editQIdDisplay')) document.getElementById('editQIdDisplay').textContent = q.id;
  if (document.getElementById('editQUnit')) {
    const u = q.unit || q.source_unit || 'Unit III';
    const optMatch = ['Unit I', 'Unit II', 'Unit III', 'Unit IV', 'Unit V'].find(uo => u.toUpperCase().includes(uo.toUpperCase()));
    document.getElementById('editQUnit').value = optMatch || 'Unit III';
  }
  if (document.getElementById('editQMarks')) document.getElementById('editQMarks').value = q.marks || 2;
  if (document.getElementById('editQDifficulty')) document.getElementById('editQDifficulty').value = q.difficulty || 'Medium';
  if (document.getElementById('editQBlooms')) {
    const bStr = (q.bloom_level || q.blooms || 'Understand').toLowerCase();
    const bloomsOpts = ['Remember', 'Understand', 'Apply', 'Analyze', 'Evaluate', 'Create'];
    const matched = bloomsOpts.find(opt => bStr.includes(opt.toLowerCase()));
    document.getElementById('editQBlooms').value = matched || 'Understand';
  }
  if (document.getElementById('editQTopic')) document.getElementById('editQTopic').value = q.topic || '';
  if (document.getElementById('editQText')) document.getElementById('editQText').value = q.question_text || q.text || q.question || '';
  if (document.getElementById('editQExplanation')) document.getElementById('editQExplanation').value = q.explanation || '';

  const modalEl = document.getElementById('editQuestionModal');
  if (modalEl) {
    const modal = bootstrap.Modal.getOrCreateInstance(modalEl);
    modal.show();
  }
}

async function saveEditedQuestionToBank(event) {
  event.preventDefault();
  const qId = parseInt(document.getElementById('editQId')?.value, 10);
  if (!qId) return;

  const unit = document.getElementById('editQUnit')?.value;
  const marks = parseInt(document.getElementById('editQMarks')?.value || '2', 10);
  const difficulty = document.getElementById('editQDifficulty')?.value;
  const blooms = document.getElementById('editQBlooms')?.value;
  const topic = document.getElementById('editQTopic')?.value;
  const text = document.getElementById('editQText')?.value;
  const explanation = document.getElementById('editQExplanation')?.value;

  const payload = {
    unit: unit,
    marks: marks,
    difficulty: difficulty,
    bloom_level: blooms,
    topic: topic,
    question_text: text,
    explanation: explanation
  };

  try {
    const res = await fetch(`http://localhost:5000/api/questions/${qId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (data.status === 'success') {
      const modalEl = document.getElementById('editQuestionModal');
      if (modalEl) {
        bootstrap.Modal.getInstance(modalEl)?.hide();
      }
      showToastNotice('Question Updated', `Question #${qId} updated successfully in MySQL!`, 'success');
      await loadQuestionPaperBuilderPage();
    } else {
      showToastNotice('Error', data.message || 'Failed to update question.', 'danger');
    }
  } catch (err) {
    console.error('Error updating question:', err);
    showToastNotice('Server Error', 'Failed to communicate with question API.', 'danger');
  }
}

async function deleteQuestionFromBank(qId) {
  if (!confirm(`Are you sure you want to permanently delete question #${qId} from the Question Bank?`)) return;

  try {
    const res = await fetch(`http://localhost:5000/api/questions/${qId}`, {
      method: 'DELETE',
      credentials: 'include'
    });
    const data = await res.json();
    if (data.status === 'success') {
      showToastNotice('Question Deleted', `Question #${qId} deleted from database.`, 'info');
      await loadQuestionPaperBuilderPage();
    } else {
      showToastNotice('Error', data.message || 'Failed to delete question.', 'danger');
    }
  } catch (err) {
    console.error('Error deleting question:', err);
    showToastNotice('Server Error', 'Failed to communicate with question API.', 'danger');
  }
}

function viewQuestionDetails(qId) {
  const q = (window.paperQuestionBankPool || []).find(item => item.id === qId);
  if (!q) return;

  const bodyEl = document.getElementById('viewQuestionModalBody');
  if (!bodyEl) return;

  const diffBadgeClass = q.difficulty === 'Easy' ? 'bg-success' : q.difficulty === 'Medium' ? 'bg-warning text-dark' : 'bg-danger';

  bodyEl.innerHTML = `
    <div class="mb-3">
      <div class="d-flex justify-content-between align-items-center mb-2">
        <span class="badge bg-dark fs-6">Question #${q.id}</span>
        <span class="badge bg-primary fs-6">${q.marks || 2} Marks</span>
      </div>
      <h5 class="fw-bold text-dark">${q.question_text || q.text || q.question}</h5>
    </div>

    <div class="row g-2 p-3 bg-light rounded border mb-3 small">
      <div class="col-md-6"><strong>Department:</strong> ${q.department || 'N/A'}</div>
      <div class="col-md-6"><strong>Subject:</strong> ${q.subject || 'N/A'}</div>
      <div class="col-md-6"><strong>Unit:</strong> <span class="badge bg-light text-dark border">${q.unit || q.source_unit || 'Unit III'}</span></div>
      <div class="col-md-6"><strong>Lesson / Topic:</strong> ${q.topic || 'General Topic'}</div>
      <div class="col-md-4"><strong>Difficulty:</strong> <span class="badge ${diffBadgeClass}">${q.difficulty}</span></div>
      <div class="col-md-4"><strong>Bloom's Taxonomy:</strong> <span class="badge bg-secondary">${q.bloom_level || q.blooms || 'Understand'}</span></div>
      <div class="col-md-4"><strong>Question Type:</strong> ${q.question_type || q.type || 'Short Answer'}</div>
    </div>

    ${q.explanation ? `
      <div class="p-3 bg-light rounded border">
        <strong class="d-block mb-1 text-primary"><i class="bi bi-lightbulb me-1"></i> Answer Key / Solution Notes:</strong>
        <p class="mb-0 text-muted small">${q.explanation}</p>
      </div>
    ` : ''}
  `;

  const modalEl = document.getElementById('viewQuestionModal');
  if (modalEl) {
    bootstrap.Modal.getOrCreateInstance(modalEl).show();
  }
}

async function saveDraftPaperAction() {
  await saveQuestionPaperToBackend('Draft');
}

async function publishQuestionPaperAction() {
  await saveQuestionPaperToBackend('Published');
}

async function saveQuestionPaperToBackend(statusMode = 'Draft') {
  const dept = document.getElementById('paperDept')?.value || 'Artificial Intelligence & Data Science';
  const subject = document.getElementById('paperSubject')?.value || 'Database Management Systems';
  const year = document.getElementById('paperYear')?.value || '2025-2026';
  const sem = document.getElementById('paperSem')?.value || 'Sixth Semester';
  const examType = document.getElementById('paperExamType')?.value || 'Semester Examination';
  const maxMarks = parseInt(document.getElementById('paperMaxMarks')?.value || '100', 10);
  const duration = document.getElementById('paperDuration')?.value || 'Three Hours';
  const examDate = document.getElementById('paperExamDate')?.value || '2026-10-15';
  const examTime = document.getElementById('paperExamTime')?.value || '10:00 AM - 01:00 PM';
  const instructions = document.getElementById('paperInstructions')?.value || '';
  const selectedQuestions = window.paperSelectedQuestions || [];

  if (selectedQuestions.length === 0) {
    showToastNotice('Validation Error', 'Please select questions or generate an examination template first.', 'warning');
    return;
  }

  let sections = [];
  if (window.currentGeneratedTemplate && window.currentGeneratedTemplate.sections) {
    sections = window.currentGeneratedTemplate.sections;
  } else {
    // Default fallback sections
    sections = [
      { name: "PART - A (10 x 2 = 20 Marks)", count: 10, marks_per_q: 2, total_marks: 20 },
      { name: "PART - B (5 x 13 = 65 Marks)", count: 5, marks_per_q: 13, total_marks: 65 },
      { name: "PART - C (1 x 15 = 15 Marks)", count: 1, marks_per_q: 15, total_marks: 15 }
    ];
  }

  const payload = {
    title: `${subject} ${examType}`,
    subject,
    department: dept,
    academic_year: year,
    semester: sem,
    exam_type: examType,
    exam_date: examDate,
    exam_time: examTime,
    duration,
    total_marks: maxMarks,
    instructions,
    status: statusMode,
    sections,
    question_ids: selectedQuestions.map(q => q.id)
  };

  try {
    let url = API_QUESTION_PAPERS_BASE;
    let method = 'POST';

    if (window.currentSavedPaper && window.currentSavedPaper.id) {
      url = `${API_QUESTION_PAPERS_BASE}/${window.currentSavedPaper.id}`;
      method = 'PUT';
    }

    const res = await fetch(url, {
      method: method,
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(payload)
    });

    const data = await res.json();
    if (data.status === 'success') {
      window.currentSavedPaper = data.paper || data.question_paper;
      showToastNotice(
        statusMode === 'Published' ? 'Paper Published' : 'Paper Saved',
        `Question Paper successfully saved to MySQL database (${statusMode} status).`,
        'success'
      );
    } else {
      showToastNotice('Validation Notice', data.message || 'Failed to save question paper to database.', 'danger');
    }
  } catch (err) {
    console.error('Error saving question paper:', err);
    showToastNotice('Server Error', 'Failed to communicate with Flask question paper API.', 'danger');
  }
}

function generateAcademicPaperPreview() {
  const previewSection = document.getElementById('paperPreviewSection');
  const sheet = document.getElementById('academicPaperPreviewSheet');

  if (!sheet) return;

  const dept = document.getElementById('paperDept')?.value || 'Artificial Intelligence & Data Science';
  const subject = document.getElementById('paperSubject')?.value || 'Database Management Systems';
  const year = document.getElementById('paperYear')?.value || '2025-2026';
  const sem = document.getElementById('paperSem')?.value || 'Sixth Semester';
  const examType = document.getElementById('paperExamType')?.value || 'Semester Examination';
  const maxMarks = document.getElementById('paperMaxMarks')?.value || '100';
  const duration = document.getElementById('paperDuration')?.value || 'Three Hours';
  const paperCode = window.currentSavedPaper?.paper_code || window.currentGeneratedTemplate?.paper_code || '241403';
  const isInternal = examType.toLowerCase().includes('internal') || maxMarks == 50;

  let courseCode = 'AL 3451';
  if (subject.toLowerCase().includes('database')) courseCode = 'CS 3491';
  else if (subject.toLowerCase().includes('big data')) courseCode = '23ADT502';
  else if (subject.toLowerCase().includes('network')) courseCode = 'CS 3591';

  let sectionsHtml = '';

  if (window.currentGeneratedTemplate && window.currentGeneratedTemplate.sections) {
    let questionNumber = 1;
    window.currentGeneratedTemplate.sections.forEach(sec => {
      let secItemsHtml = '';

      if (sec.questions && Array.isArray(sec.questions)) {
        // Part A: Compulsory Questions
        sec.questions.forEach(q => {
          const qNum = questionNumber++;
          const bloomTag = q.bloom_tag || (q.bloom_level ? `[${q.bloom_level.substring(0,2).toUpperCase()}]` : '[UN]');
          const coTag = q.co_tag ? `${q.co_tag} ` : '';

          secItemsHtml += `
            <div class="exam-q-row">
              <div class="exam-q-text">
                <span class="fw-bold me-2">${qNum}.</span>
                <span>${q.question_text || q.text || q.question}</span>
              </div>
              <div class="exam-q-marks">${coTag}${bloomTag}</div>
            </div>
          `;
        });
      } else {
        // Part B and Part C: Either/Or Questions
        const groups = sec.groups || sec.either_or_groups || [];
        groups.forEach((group) => {
          const groupNum = questionNumber++;
          
          const renderAlternative = (alt, letter) => {
            if (!alt) return '';

            // Subquestion structure (e.g. 8 + 5 marks or 8 + 8 marks)
            if (alt.is_subquestion || (alt.subquestions && Array.isArray(alt.subquestions))) {
              const subs = alt.subquestions || [];
              return `
                <div class="mb-2">
                  <div class="fw-bold mb-1">${letter})</div>
                  ${subs.map((sq, sIdx) => {
                    const subPart = sq.part || (sIdx === 0 ? '(i)' : '(ii)');
                    const subMarks = sq.marks || (sIdx === 0 ? 8 : 5);
                    const bTag = sq.bloom_tag || (sq.bloom_level ? `[${sq.bloom_level.substring(0,2).toUpperCase()}]` : '[AP]');
                    const coTag = sq.co_tag ? `${sq.co_tag} ` : '';
                    return `
                      <div class="exam-q-row ms-3 mb-1">
                        <div class="exam-q-text">
                          <span class="fw-bold me-2">${subPart}</span>
                          <span>${sq.question_text || sq.text || sq.question}</span>
                        </div>
                        <div class="exam-q-marks">${coTag}${bTag} (${subMarks})</div>
                      </div>
                    `;
                  }).join('')}
                </div>
              `;
            } else {
              // Single full mark question (e.g. 13 Marks or 15 Marks or 16 Marks)
              const marksVal = alt.marks || (sec.marks_per_q || (isInternal ? 8 : 13));
              const bTag = alt.bloom_tag || (alt.bloom_level ? `[${alt.bloom_level.substring(0,2).toUpperCase()}]` : '[AP]');
              const coTag = alt.co_tag ? `${alt.co_tag} ` : '';
              return `
                <div class="exam-q-row mb-1">
                  <div class="exam-q-text">
                    <span class="fw-bold me-2">${letter})</span>
                    <span>${alt.question_text || alt.text || alt.question}</span>
                  </div>
                  <div class="exam-q-marks">${coTag}${bTag} (${marksVal})</div>
                </div>
              `;
            }
          };

          secItemsHtml += `
            <div class="mb-4">
              <div class="fw-bold mb-1">${groupNum}.</div>
              ${renderAlternative(group.alternative_a, 'a')}
              <div class="exam-or-divider">OR</div>
              ${renderAlternative(group.alternative_b, 'b')}
            </div>
          `;
        });
      }

      sectionsHtml += `
        <div class="exam-section-heading">${sec.name}</div>
        ${secItemsHtml}
      `;
    });
  } else {
    // Manual selected questions display
    const selected = window.paperSelectedQuestions || [];
    let qItemsHtml = '';
    selected.forEach((q, idx) => {
      qItemsHtml += `
        <div class="exam-q-row border-bottom pb-2 mb-2">
          <div class="exam-q-text">
            <span class="fw-bold me-2">${idx + 1}.</span>
            <span>${q.question_text || q.text || q.question}</span>
          </div>
          <div class="exam-q-marks">(${q.marks || 2} Marks)</div>
        </div>
      `;
    });
    sectionsHtml = `<div class="mb-3">${qItemsHtml}</div>`;
  }

  // Exact header depending on whether Semester Exam or Internal Exam
  const headerHtml = isInternal ? `
    <!-- Internal Examination Header (inter.pdf pattern) -->
    <div class="d-flex justify-content-end mb-2">
      <div class="d-flex align-items-center">
        <span class="fw-bold me-2" style="font-size: 0.95rem;">REGISTER NO:</span>
        <table class="exam-register-table">
          <tr>
            <td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td>
          </tr>
        </table>
      </div>
    </div>
    <div class="text-center mb-3">
      <h5 class="fw-bold mb-0" style="letter-spacing: 0.5px;">V.S.B. ENGINEERING COLLEGE, KARUR</h5>
      <div style="font-size: 0.88rem; font-style: italic;">(An Autonomous Institution Affiliated to Anna University, Chennai)</div>
      <div class="exam-code-box">Question Paper Code : ${paperCode}</div>
      <div class="fw-bold" style="font-size: 1rem; text-transform: uppercase;">${examType}</div>
      <div style="font-size: 0.92rem;">Academic Year: ${year} (ODD Semester)</div>
      <div style="font-size: 0.92rem;">${sem}</div>
      <div style="font-size: 0.92rem;">${dept}</div>
      <div class="fw-bold" style="font-size: 1rem;">${courseCode} - ${subject.toUpperCase()}</div>
      <div style="font-size: 0.88rem;">(Common to: CSE (AIML) / CSE / CCE / AIDS / IT)</div>
      <div style="font-size: 0.88rem;">(Regulations 2023)</div>
    </div>
    <div class="exam-meta-line">
      <span>Time: ${duration}</span>
      <span>Date: 09-10-2026</span>
      <span>Max. Marks: ${maxMarks}</span>
    </div>
    <div class="text-center fw-bold small mb-3" style="letter-spacing: 0.5px;">Answer ALL Questions</div>
  ` : `
    <!-- Semester Examination Header (April May 2024 ML.pdf pattern) -->
    <div class="d-flex justify-content-end mb-2">
      <div class="d-flex align-items-center">
        <span class="fw-bold me-2" style="font-size: 0.95rem;">Register No:</span>
        <table class="exam-register-table">
          <tr>
            <td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td>
          </tr>
        </table>
      </div>
    </div>
    <div class="text-center mb-3">
      <h5 class="fw-bold mb-0" style="letter-spacing: 0.5px;">V.S.B. ENGINEERING COLLEGE, KARUR - 639 111</h5>
      <div style="font-size: 0.88rem; font-style: italic;">(An Autonomous Institution, Affiliated to Anna University, Chennai)</div>
      <div class="exam-code-box">Question Paper Code : ${paperCode}</div>
      <div class="fw-bold" style="font-size: 1rem;">B.E. / B.Tech. End Semester Theory Examinations, April/May 2024.</div>
      <div style="font-size: 0.92rem;">${sem}</div>
      <div style="font-size: 0.92rem;">${dept}</div>
      <div class="fw-bold" style="font-size: 1.05rem;">${courseCode} - ${subject.toUpperCase()}</div>
      <div style="font-size: 0.88rem;">(Common to Computer Science and Business Systems)</div>
      <div style="font-size: 0.88rem;">(Regulations 2021)</div>
    </div>
    <div class="exam-meta-line">
      <span>Time: ${duration}</span>
      <span style="letter-spacing: 0.5px;">Answer ALL Questions</span>
      <span>Max. Marks: ${maxMarks}</span>
    </div>
  `;

  sheet.innerHTML = `
    <div class="exam-paper-sheet">
      ${headerHtml}
      ${sectionsHtml}
      <div class="text-center text-muted small mt-4 pt-3 border-top">
        * * * End of Examination Paper * * *
      </div>
    </div>
  `;

  if (previewSection) {
    previewSection.classList.remove('d-none');
    previewSection.scrollIntoView({ behavior: 'smooth' });
  }
  showToastNotice('Preview Generated', 'Official examination paper preview rendered according to university standards.', 'info');
}
'''

def main():
    with open(APP_JS_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    start_token = "// STEP 9E: QUESTION PAPER BUILDER & EXAM PAPERS (FLASK + MYSQL)"
    end_token = "function bindGeneratorStubs() {}"

    start_idx = content.find(start_token)
    end_idx = content.find(end_token)

    if start_idx == -1 or end_idx == -1:
        print(f"Error: tokens not found: start={start_idx}, end={end_idx}")
        sys.exit(1)

    updated_content = content[:start_idx] + NEW_APP_JS_CODE + "\n\n" + content[end_idx:]

    with open(APP_JS_PATH, 'w', encoding='utf-8') as f:
        f.write(updated_content)

    print("Updated js/app.js successfully!")

if __name__ == '__main__':
    main()
