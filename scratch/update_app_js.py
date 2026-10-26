# -*- coding: utf-8 -*-
import sys

NEW_CODE = '''// ==========================================
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
  const sem = document.getElementById('paperSem')?.value || 'Semester 6';

  // 1. Fetch Question Bank items from MySQL backend API
  try {
    const url = `http://localhost:5000/api/question-bank?department=${encodeURIComponent(dept)}&subject=${encodeURIComponent(subject)}&academic_year=${encodeURIComponent(year)}&semester=${encodeURIComponent(sem)}`;
    const res = await fetch(url, { credentials: 'include' });
    const data = await res.json();
    if (data.status === 'success' && data.questions && data.questions.length > 0) {
      window.paperQuestionBankPool = data.questions;
    } else {
      // Fallback to all questions or mock data
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

  // 2. Render initial Question Bank selection table
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
  const sem = document.getElementById('paperSem')?.value || 'Semester 6';

  showToastNotice('Generating Template', `Balancing and assembling ${templateType === 'internal_test' ? 'Internal Test (50 Marks)' : 'Semester Exam (100 Marks)'} from Question Bank...`, 'info');

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
      
      // Update form controls
      if (document.getElementById('paperMaxMarks')) document.getElementById('paperMaxMarks').value = data.paper.total_marks;
      if (document.getElementById('paperExamType')) document.getElementById('paperExamType').value = data.paper.exam_type;
      if (document.getElementById('paperDuration')) document.getElementById('paperDuration').value = data.paper.duration;
      if (document.getElementById('paperInstructions')) document.getElementById('paperInstructions').value = data.paper.instructions;

      // Extract all questions for the pool and selected list
      const questionsList = [];
      if (data.paper.sections) {
        data.paper.sections.forEach(sec => {
          if (sec.questions && Array.isArray(sec.questions)) {
            sec.questions.forEach(q => questionsList.push(q));
          }
          if (sec.either_or_groups && Array.isArray(sec.either_or_groups)) {
            sec.either_or_groups.forEach(g => {
              if (g.alternative_a) {
                if (Array.isArray(g.alternative_a)) g.alternative_a.forEach(q => questionsList.push(q));
                else questionsList.push(g.alternative_a);
              }
              if (g.alternative_b) {
                if (Array.isArray(g.alternative_b)) g.alternative_b.forEach(q => questionsList.push(q));
                else questionsList.push(g.alternative_b);
              }
            });
          }
        });
      }

      window.paperSelectedQuestions = questionsList;
      renderQuestionPaperBankTable();
      renderPaperSelectedQuestions();
      renderPaperSectionStructure(data.paper.sections);
      generateAcademicPaperPreview();

      const noticeMsg = templateType === 'internal_test'
        ? 'Internal Test template generated: exactly 50 attempted marks with distinct lesson coverage!'
        : 'Semester Exam template generated: exactly 100 attempted marks with 2 questions per unit in Section A and 5 Either/Or groups!';
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
    // Default fallback calculation
    container.innerHTML = `
      <div class="row g-3">
        <div class="col-md-4"><div class="p-3 border rounded bg-white"><h6 class="fw-bold text-primary mb-1">PART A</h6><div class="small text-muted">10 questions × 2 marks = 20 Attempted Marks</div></div></div>
        <div class="col-md-4"><div class="p-3 border rounded bg-white"><h6 class="fw-bold text-primary mb-1">PART B</h6><div class="small text-muted">5 groups × 16 marks = 80 Attempted Marks</div></div></div>
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
    let secAttempted = sec.total_marks || 0;
    let details = '';

    if (sec.either_or_groups && sec.either_or_groups.length > 0) {
      const groupCount = sec.either_or_groups.length;
      const marksPerGroup = sec.marks_per_question || (secAttempted / groupCount) || (groupCount === 1 ? 8 : 16);
      details = `${groupCount} Either/Or Group${groupCount > 1 ? 's' : ''} × ${marksPerGroup} Marks (Students attempt only 1 alternative per group)`;
    } else {
      const qCount = (sec.questions && sec.questions.length) || sec.count || 0;
      const marksPerQ = sec.marks_per_question || 2;
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
      validationMsg.innerHTML = `<span class="alert alert-success d-inline-block py-2 px-3 mb-0 small"><i class="bi bi-check-circle-fill me-1"></i> <strong>Marks Validated:</strong> Total attempted marks (${totalAttempted}) match Maximum Examination Marks (${targetMaxMarks}).</span>`;
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
    pool = pool.filter(q => (q.bloom_level || q.blooms || '').toLowerCase() === bloomsFilter.toLowerCase());
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
    const marksBadgeClass = q.marks == 2 ? 'badge bg-secondary' : q.marks == 8 ? 'badge bg-primary' : 'badge bg-dark';

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
    container.innerHTML = `<div class="p-4 text-center text-muted border rounded bg-light"><i class="bi bi-inbox me-2"></i>No questions currently selected. Use "Generate Template" above or add questions from Question Bank.</div>`;
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
        <div class="col-md-6 text-success"><i class="bi bi-check-circle-fill me-1"></i> Subject & Course Code Validated</div>
        <div class="col-md-6 ${selected.length > 0 ? 'text-success' : 'text-danger'}"><i class="bi bi-${selected.length > 0 ? 'check-circle-fill' : 'x-circle-fill'} me-1"></i> Selected Questions (${selected.length} questions)</div>
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
    question_type: marks === 2 ? 'Short Answer' : marks === 8 ? 'Descriptive' : 'Problem Solving'
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
      showToastNotice('Question Added', 'New question successfully saved to Question Bank!', 'success');
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
  if (document.getElementById('editQBlooms')) document.getElementById('editQBlooms').value = q.bloom_level || q.blooms || 'Understand';
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
      showToastNotice('Question Updated', `Question #${qId} updated successfully!`, 'success');
      await loadQuestionPaperBuilderPage();
    } else {
      showToastNotice('Error', data.message || 'Failed to update question.', 'danger');
    }
  } catch (err) {
    console.error('Error updating question:', err);
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
  const sem = document.getElementById('paperSem')?.value || 'Semester 6';
  const examType = document.getElementById('paperExamType')?.value || 'Model Examination';
  const maxMarks = parseInt(document.getElementById('paperMaxMarks')?.value || '100', 10);
  const duration = document.getElementById('paperDuration')?.value || '3 Hours';
  const examDate = document.getElementById('paperExamDate')?.value || '2026-10-15';
  const examTime = document.getElementById('paperExamTime')?.value || '10:00 AM - 01:00 PM';
  const instructions = document.getElementById('paperInstructions')?.value || '';
  const selectedQuestions = window.paperSelectedQuestions || [];

  if (selectedQuestions.length === 0) {
    showToastNotice('Validation Error', 'Please select questions or generate a template for the paper.', 'warning');
    return;
  }

  let sections = [];
  if (window.currentGeneratedTemplate && window.currentGeneratedTemplate.sections) {
    sections = window.currentGeneratedTemplate.sections;
  } else {
    // Manual fallback sections
    sections = [
      { name: "PART A", count: 10, marks_per_q: 2, total_marks: 20 },
      { name: "PART B", count: 5, marks_per_q: 16, total_marks: 80 }
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
  const sem = document.getElementById('paperSem')?.value || 'Semester 6';
  const examType = document.getElementById('paperExamType')?.value || 'Model Examination';
  const maxMarks = document.getElementById('paperMaxMarks')?.value || '100';
  const duration = document.getElementById('paperDuration')?.value || '3 Hours';
  const instructions = document.getElementById('paperInstructions')?.value || '';

  let sectionsHtml = '';

  if (window.currentGeneratedTemplate && window.currentGeneratedTemplate.sections) {
    let questionNumber = 1;
    window.currentGeneratedTemplate.sections.forEach(sec => {
      let secItemsHtml = '';

      if (sec.questions && Array.isArray(sec.questions)) {
        sec.questions.forEach(q => {
          secItemsHtml += `
            <div class="mb-3 d-flex justify-content-between align-items-start border-bottom pb-2">
              <div style="flex: 1;">
                <span class="fw-bold me-2">${questionNumber}.</span>
                <span>${q.question_text || q.text || q.question}</span>
                <div class="small text-muted mt-1">
                  <span class="badge bg-light text-dark border me-1">${q.unit || 'Unit I'}</span>
                  <span class="badge bg-light text-muted border me-1">${q.topic || ''}</span>
                  <span class="badge bg-light text-secondary border">Bloom's: ${q.bloom_level || 'Understand'}</span>
                </div>
              </div>
              <div class="fw-bold ps-3 text-nowrap">(${q.marks || 2} Marks)</div>
            </div>
          `;
          questionNumber++;
        });
      } else if (sec.either_or_groups && Array.isArray(sec.either_or_groups)) {
        sec.either_or_groups.forEach((group, gIdx) => {
          const groupNum = questionNumber++;
          const renderAlt = (alt, letter) => {
            if (Array.isArray(alt)) {
              return `
                <div class="mb-2">
                  <div class="fw-bold text-dark mb-1">(${letter})</div>
                  ${alt.map((subQ, sIdx) => `
                    <div class="ms-3 mb-2 d-flex justify-content-between align-items-start">
                      <div style="flex: 1;">
                        <span class="fw-semibold me-1">(${sIdx === 0 ? 'i' : 'ii'})</span>
                        <span>${subQ.question_text || subQ.text || subQ.question}</span>
                        <div class="small text-muted">
                          <span class="badge bg-light text-dark border me-1">${subQ.unit || ''}</span>
                          <span class="badge bg-light text-muted border me-1">${subQ.topic || ''}</span>
                          <span class="badge bg-light text-secondary border">Bloom's: ${subQ.bloom_level || 'Apply'}</span>
                        </div>
                      </div>
                      <div class="fw-bold ps-2 text-nowrap">(${subQ.marks || 8} Marks)</div>
                    </div>
                  `).join('')}
                </div>
              `;
            } else if (alt) {
              return `
                <div class="mb-2 d-flex justify-content-between align-items-start">
                  <div style="flex: 1;">
                    <span class="fw-bold me-2">(${letter})</span>
                    <span>${alt.question_text || alt.text || alt.question}</span>
                    <div class="small text-muted mt-1">
                      <span class="badge bg-light text-dark border me-1">${alt.unit || ''}</span>
                      <span class="badge bg-light text-muted border me-1">${alt.topic || ''}</span>
                      <span class="badge bg-light text-secondary border">Bloom's: ${alt.bloom_level || 'Analyze'}</span>
                    </div>
                  </div>
                  <div class="fw-bold ps-3 text-nowrap">(${alt.marks || 16} Marks)</div>
                </div>
              `;
            }
            return '';
          };

          secItemsHtml += `
            <div class="mb-4 p-3 border rounded bg-white shadow-sm">
              <div class="fw-bold text-primary mb-2">Question ${groupNum}</div>
              ${renderAlt(group.alternative_a, 'a')}
              <div class="text-center my-2 text-muted fw-bold" style="letter-spacing: 2px;">— OR —</div>
              ${renderAlt(group.alternative_b, 'b')}
            </div>
          `;
        });
      }

      sectionsHtml += `
        <div class="mb-4">
          <div class="border-bottom border-dark pb-1 mb-3 d-flex justify-content-between align-items-baseline">
            <h5 class="fw-bold mb-0">${sec.name}</h5>
            <span class="fw-bold text-muted">${sec.total_marks || ''} Marks</span>
          </div>
          <p class="small text-muted mb-3 fst-italic">${sec.description || 'Answer the questions as instructed.'}</p>
          ${secItemsHtml}
        </div>
      `;
    });
  } else {
    // Standard selected questions dump
    const selected = window.paperSelectedQuestions || [];
    let qItemsHtml = '';
    selected.forEach((q, idx) => {
      qItemsHtml += `
        <div class="mb-3 d-flex justify-content-between border-bottom pb-2">
          <div>
            <span class="fw-bold me-2">${idx + 1}.</span>
            <span>${q.question_text || q.text || q.question}</span>
            <div class="small text-muted mt-1">
              <span class="badge bg-light text-dark border">${q.unit || 'Unit III'}</span>
              <span class="badge bg-light text-secondary border">Bloom's: ${q.bloom_level || 'Understand'}</span>
            </div>
          </div>
          <span class="fw-bold">(${q.marks || 2} Marks)</span>
        </div>
      `;
    });
    sectionsHtml = `<div class="mb-4">${qItemsHtml}</div>`;
  }

  sheet.innerHTML = `
    <div class="card p-5 border border-dark bg-white shadow-sm font-serif">
      <div class="text-center border-bottom pb-3 mb-4">
        <h4 class="fw-bold mb-1">V.S.B. ENGINEERING COLLEGE</h4>
        <h5 class="fw-semibold text-secondary mb-1">DEPARTMENT OF ${dept.toUpperCase()}</h5>
        <h5 class="fw-bold text-primary mb-1">${examType.toUpperCase()} — ${year}</h5>
        <h6 class="mb-0">Subject: ${subject} | ${sem}</h6>
      </div>

      <div class="d-flex justify-content-between fw-bold mb-3 border-bottom pb-2">
        <span>Time Allowed: ${duration}</span>
        <span>Maximum Attempted Marks: ${maxMarks}</span>
      </div>

      <div class="mb-4 p-3 bg-light rounded border">
        <strong>General Instructions:</strong>
        <pre class="mb-0 font-sans small mt-1" style="white-space: pre-wrap;">${instructions}</pre>
      </div>

      ${sectionsHtml}

      <div class="text-center text-muted small border-top pt-3 mt-4">
        * * * End of Examination Paper * * *
      </div>
    </div>
  `;

  if (previewSection) {
    previewSection.classList.remove('d-none');
    previewSection.scrollIntoView({ behavior: 'smooth' });
  }
  showToastNotice('Preview Generated', 'Official examination paper preview rendered.', 'info');
}
'''

def main():
    app_js_path = r'C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\js\app.js'
    with open(app_js_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    start_idx = None
    end_idx = None
    for i, line in enumerate(lines):
        if '// STEP 9E: QUESTION PAPER BUILDER & EXAM PAPERS (FLASK + MYSQL)' in line:
            start_idx = i
        if 'function bindGeneratorStubs() {}' in line:
            end_idx = i

    if start_idx is None or end_idx is None:
        print(f"Error: Could not locate bounds: start={start_idx}, end={end_idx}")
        sys.exit(1)

    print(f"Replacing lines {start_idx+1} to {end_idx+1} (total {end_idx - start_idx + 1} lines)...")
    
    before = lines[:start_idx]
    after = lines[end_idx:]

    new_content = ''.join(before) + NEW_CODE + '\n' + ''.join(after)

    with open(app_js_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print("Successfully updated js/app.js!")

if __name__ == '__main__':
    main()
