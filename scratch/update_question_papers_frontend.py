import os

app_path = r'C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\js\app.js'
with open(app_path, 'r', encoding='utf-8') as f:
    text = f.read()

start_idx = text.find('async function renderStudentQuestionPapers')
end_idx = text.find('function initResourceForm')

new_paper_code = """
let globalStudentPapers = [];

async function renderStudentQuestionPapers() {
  const tableBody = document.getElementById('studentQuestionPapersBody');
  if (!tableBody) return;

  const urlParams = new URLSearchParams(window.location.search);
  const filterSelect = document.getElementById('studentPaperSubjectFilter');
  let currentSubject = urlParams.get('subject') || (filterSelect ? filterSelect.value : 'ALL') || 'ALL';

  tableBody.innerHTML = `<tr><td colspan="7" class="text-center py-4 text-muted"><span class="spinner-border spinner-border-sm me-2 text-primary"></span>Loading published examination papers...</td></tr>`;

  try {
    const res = await fetch('http://localhost:5000/api/question-papers?status=Published', {
      credentials: 'include'
    });
    if (res.ok) {
      const data = await res.json();
      globalStudentPapers = data.question_papers || data.papers || [];
    } else {
      globalStudentPapers = [];
    }
  } catch (err) {
    console.warn('Error fetching student papers from API, using fallback:', err);
    globalStudentPapers = (AcademicMockData.publishedQuestionPapers || []).filter(p => p.status === 'Published');
  }

  // Populate subject dropdown if present
  if (filterSelect) {
    const subjects = Array.from(new Set(globalStudentPapers.map(p => p.subject).filter(Boolean)));
    if (!subjects.includes('Database Management Systems')) subjects.push('Database Management Systems');
    if (!subjects.includes('Distributed Computing')) subjects.push('Distributed Computing');
    if (!subjects.includes('Machine Learning')) subjects.push('Machine Learning');

    filterSelect.innerHTML = `<option value="ALL">All Subjects (${globalStudentPapers.length})</option>` +
      subjects.map(s => {
        const cnt = globalStudentPapers.filter(p => p.subject === s).length;
        return `<option value="${s}" ${s === currentSubject ? 'selected' : ''}>${s} (${cnt})</option>`;
      }).join('');

    if (currentSubject && subjects.includes(currentSubject)) {
      filterSelect.value = currentSubject;
    }
  }

  let filtered = globalStudentPapers;
  if (currentSubject && currentSubject !== 'ALL') {
    filtered = filtered.filter(p => p.subject === currentSubject);
  }

  if (!filtered || filtered.length === 0) {
    tableBody.innerHTML = `<tr><td colspan="7" class="text-center py-5 text-muted"><i class="bi bi-file-earmark-x fs-2 d-block mb-2 text-secondary"></i>No published examination papers found ${currentSubject !== 'ALL' ? `for <strong>${currentSubject}</strong>` : ''}. Check back later!</td></tr>`;
    return;
  }

  tableBody.innerHTML = filtered.map(p => {
    const pId = p.id || p.paper_code;
    const duration = p.duration || (p.duration_minutes ? `${p.duration_minutes} Mins` : '3 Hours');
    const marks = p.total_marks || p.max_marks || 100;
    const examDate = p.exam_date || 'Upcoming';
    const dept = p.department || 'Artificial Intelligence & Data Science';

    return `
      <tr>
        <td>
          <div class="fw-bold text-dark">${p.title || p.paper_code}</div>
          <small class="text-muted font-monospace">${p.paper_code} | ${p.subject}</small>
        </td>
        <td><span class="badge bg-primary-subtle text-primary border">${p.exam_type || 'Model Exam'}</span></td>
        <td><small class="text-muted"><i class="bi bi-calendar3 me-1"></i>${examDate}</small></td>
        <td><small class="fw-semibold">${duration}</small></td>
        <td><strong>${marks} Marks</strong></td>
        <td><small class="text-muted">${dept}</small></td>
        <td>
          <button class="btn btn-academic-primary btn-sm py-1 px-3" onclick="viewStudentPaperModal('${pId}')">
            <i class="bi bi-eye me-1"></i> View Paper
          </button>
        </td>
      </tr>
    `;
  }).join('');
}

function filterStudentPapers() {
  const filterSelect = document.getElementById('studentPaperSubjectFilter');
  const sel = filterSelect ? filterSelect.value : 'ALL';
  const url = new URL(window.location);
  if (sel === 'ALL') {
    url.searchParams.delete('subject');
  } else {
    url.searchParams.set('subject', sel);
  }
  window.history.replaceState({}, '', url);
  renderStudentQuestionPapers();
}

async function viewStudentPaperModal(paperId) {
  let paper = (globalStudentPapers || []).find(p => String(p.id) === String(paperId) || p.paper_code === paperId);

  try {
    const res = await fetch(`http://localhost:5000/api/question-papers/${paperId}`, {
      credentials: 'include'
    });
    if (res.ok) {
      const data = await res.json();
      if (data.question_paper || data.paper) {
        paper = data.question_paper || data.paper;
      }
    }
  } catch (e) {
    console.warn('Could not fetch paper details from API:', e);
  }

  if (!paper) {
    showToastNotice('Error', 'Unable to load examination paper details.', 'danger');
    return;
  }

  const modalTitle = document.getElementById('studentModalPaperTitle');
  const modalBody = document.getElementById('studentModalPaperBody');
  const modalEl = document.getElementById('studentPaperViewModal');

  if (modalTitle) modalTitle.textContent = `${paper.title} (${paper.paper_code})`;

  if (modalBody) {
    let sections = paper.sections || [];
    if (typeof sections === 'string') {
      try { sections = JSON.parse(sections); } catch(e) { sections = []; }
    }

    let questionsHtml = '';

    if (sections && sections.length > 0) {
      questionsHtml = sections.map((sec, sIdx) => {
        let secContent = '';

        // 1. Compulsory Questions (e.g. Part A)
        if (sec.questions && Array.isArray(sec.questions) && sec.questions.length > 0) {
          secContent += `
            <div class="ps-2 mb-3">
              ${sec.questions.map((q, qIdx) => {
                const qNum = q.question_number || (qIdx + 1);
                const marks = q.marks || sec.marks_per_question || 2;
                return `
                  <div class="mb-3 pb-2 border-bottom">
                    <div class="d-flex justify-content-between align-items-baseline">
                      <span class="fw-semibold text-dark">${qNum}. ${q.question_text || q.question || q.text || ''}</span>
                      <span class="badge bg-secondary-subtle text-dark border ms-2">${marks} Marks</span>
                    </div>
                    <div class="d-flex gap-2 small text-muted mt-1">
                      <span><strong>Difficulty:</strong> ${q.difficulty || 'Medium'}</span>
                      <span>•</span>
                      <span><strong>Bloom:</strong> ${q.bloom_level || q.bloomsTaxonomy || 'Understand'}</span>
                      ${q.unit ? `<span>•</span><span><strong>Unit:</strong> ${q.unit}</span>` : ''}
                      ${q.topic ? `<span>•</span><span><strong>Topic:</strong> ${q.topic}</span>` : ''}
                    </div>
                  </div>
                `;
              }).join('')}
            </div>
          `;
        }

        // 2. Either/Or Groups (Part B / Part C)
        if (sec.either_or_groups && Array.isArray(sec.either_or_groups) && sec.either_or_groups.length > 0) {
          const renderAlt = (alt, letter) => {
            const isSplit = Boolean(alt.format === 'split' || alt.is_subquestion || (alt.subquestions && alt.subquestions.length > 0));
            if (isSplit && alt.subquestions && alt.subquestions.length >= 2) {
              const sq1 = alt.subquestions[0];
              const sq2 = alt.subquestions[1];
              return `
                <div class="p-3 border rounded bg-light mb-2">
                  <div class="d-flex justify-content-between align-items-center mb-2">
                    <span class="badge bg-primary text-white">Alternative (${letter}) — Split Format (8 + 8 = 16 Marks)</span>
                    <span class="badge bg-info-subtle text-dark border">16 Marks Total</span>
                  </div>
                  <div class="mb-2 pb-2 border-bottom">
                    <div class="d-flex justify-content-between align-items-baseline">
                      <div><strong class="text-primary me-1">${sq1.part || '(i)'}</strong> <span class="fw-semibold text-dark">${sq1.question_text || sq1.text || sq1.question || ''}</span></div>
                      <span class="badge bg-secondary-subtle text-dark border ms-2">${sq1.marks || 8} Marks</span>
                    </div>
                    <div class="small text-muted mt-1">Bloom: ${sq1.bloom_level || 'Analyze'}${sq1.topic ? ` • Topic: ${sq1.topic}` : ''}</div>
                  </div>
                  <div>
                    <div class="d-flex justify-content-between align-items-baseline">
                      <div><strong class="text-primary me-1">${sq2.part || '(ii)'}</strong> <span class="fw-semibold text-dark">${sq2.question_text || sq2.text || sq2.question || ''}</span></div>
                      <span class="badge bg-secondary-subtle text-dark border ms-2">${sq2.marks || 8} Marks</span>
                    </div>
                    <div class="small text-muted mt-1">Bloom: ${sq2.bloom_level || 'Apply'}${sq2.topic ? ` • Topic: ${sq2.topic}` : ''}</div>
                  </div>
                </div>
              `;
            } else {
              const qText = alt.question_text || alt.text || alt.question || 'Comprehensive Analytical Question';
              const marks = alt.marks || 16;
              return `
                <div class="p-3 border rounded bg-light mb-2">
                  <div class="d-flex justify-content-between align-items-center mb-2">
                    <span class="badge bg-primary text-white">Alternative (${letter}) — Direct (${marks} Marks)</span>
                    <span class="badge bg-info-subtle text-dark border">${marks} Marks</span>
                  </div>
                  <div class="fw-semibold text-dark mb-1">${qText}</div>
                  <div class="d-flex gap-2 small text-muted">
                    <span><strong>Difficulty:</strong> ${alt.difficulty || 'Medium'}</span>
                    <span>•</span>
                    <span><strong>Bloom:</strong> ${alt.bloom_level || alt.bloomsTaxonomy || 'Analyze'}</span>
                    ${alt.topic ? `<span>•</span><span><strong>Topic:</strong> ${alt.topic}</span>` : ''}
                  </div>
                </div>
              `;
            }
          };

          secContent += `
            <div class="ps-2">
              ${sec.either_or_groups.map((grp, gIdx) => {
                const qNum = grp.question_number || (11 + gIdx);
                const unit = grp.unit || `Unit ${gIdx + 1}`;
                const attemptedMarks = grp.attempted_marks || sec.marks_per_question || 16;
                const altA = grp.alternative_a || grp.option_a || grp.alt_a || {};
                const altB = grp.alternative_b || grp.option_b || grp.alt_b || {};

                return `
                  <div class="mb-4 pb-3 border-bottom">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                      <span class="fw-bold fs-6 text-dark"><i class="bi bi-diagram-2 me-1 text-primary"></i> Question ${qNum} [${unit}]</span>
                      <span class="badge bg-success-subtle text-success border border-success fw-bold">${attemptedMarks} Attempted Marks</span>
                    </div>
                    ${renderAlt(altA, 'a')}
                    <div class="text-center my-2">
                      <span class="badge bg-secondary px-3 py-1 text-uppercase fw-bold" style="letter-spacing: 2px;">[ OR ]</span>
                    </div>
                    ${renderAlt(altB, 'b')}
                  </div>
                `;
              }).join('')}
            </div>
          `;
        }

        return `
          <div class="mb-4">
            <div class="p-2 bg-light border fw-bold text-dark d-flex justify-content-between mb-3 rounded">
              <span>SECTION ${String.fromCharCode(65 + sIdx)}: ${sec.title || 'General'}</span>
              <span>${sec.attempted_marks ? `[Attempted: ${sec.attempted_marks} Marks]` : ''}</span>
            </div>
            ${sec.instructions ? `<div class="small fst-italic text-muted mb-2 px-2">${sec.instructions}</div>` : ''}
            ${secContent}
          </div>
        `;
      }).join('');
    } else {
      questionsHtml = `<p class="text-muted p-3 text-center">Examination paper sections are published and available in print format.</p>`;
    }

    const fingerprint = paper.fingerprint || paper.sha256_hash || '';

    modalBody.innerHTML = `
      <div class="p-4 bg-white border rounded">
        <div class="text-center border-bottom pb-3 mb-4">
          <h4 class="fw-bold mb-1">V.S.B. ENGINEERING COLLEGE</h4>
          <h6 class="text-muted text-uppercase mb-2">${paper.department || 'Department of Computer Science & Engineering'}</h6>
          <h5 class="fw-bold text-primary mb-1">${paper.title}</h5>
          <div class="small text-muted">Course: <strong>${paper.subject}</strong> | Paper Code: <strong>${paper.paper_code}</strong></div>
        </div>

        <div class="row g-2 mb-4 p-3 bg-light rounded border text-sm">
          <div class="col-sm-4"><strong>Academic Year:</strong> ${paper.academic_year || '2025-2026'}</div>
          <div class="col-sm-4"><strong>Semester:</strong> ${paper.semester || 'Semester 6'}</div>
          <div class="col-sm-4"><strong>Exam Type:</strong> ${paper.exam_type || 'Semester Examination'}</div>
          <div class="col-sm-4"><strong>Max Marks:</strong> ${paper.total_marks || paper.max_marks || 100}</div>
          <div class="col-sm-4"><strong>Duration:</strong> ${paper.duration || (paper.duration_minutes ? `${paper.duration_minutes} Mins` : '3 Hours')}</div>
          <div class="col-sm-4"><strong>Exam Date:</strong> ${paper.exam_date || 'As per Schedule'}</div>
        </div>

        ${paper.instructions ? `
          <div class="alert alert-warning py-2 px-3 small mb-4">
            <strong>Instructions:</strong> ${paper.instructions}
          </div>
        ` : ''}

        ${questionsHtml}

        ${fingerprint ? `
          <div class="p-3 bg-dark text-white rounded mt-4 small font-monospace">
            <div class="text-warning fw-bold mb-1"><i class="bi bi-shield-lock me-1"></i> SHA-256 Digital Fingerprint:</div>
            <div style="word-break: break-all; font-size: 0.8rem;">${fingerprint}</div>
          </div>
        ` : ''}
      </div>
    `;
  }

  if (modalEl) {
    const bsModal = bootstrap.Modal.getOrCreateInstance(modalEl);
    bsModal.show();
  }
}

window.printStudentPaper = function() {
  const paperBody = document.getElementById('studentModalPaperBody');
  if (!paperBody) return;
  const printWin = window.open('', '_blank');
  printWin.document.write(`
    <!DOCTYPE html>
    <html>
    <head>
      <title>Examination Paper</title>
      <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
      <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; padding: 25px; color: #111; }
        .badge { border: 1px solid #999; color: #111 !important; background: transparent !important; }
        @media print {
          .no-print { display: none !important; }
          body { padding: 0; }
        }
      </style>
    </head>
    <body>
      <div class="text-end mb-3 no-print">
        <button class="btn btn-primary btn-sm" onclick="window.print()">Print Paper</button>
        <button class="btn btn-secondary btn-sm" onclick="window.close()">Close</button>
      </div>
      ${paperBody.innerHTML}
    </body>
    </html>
  `);
  printWin.document.close();
  printWin.focus();
  setTimeout(() => { printWin.print(); }, 500);
};

"""

text = text[:start_idx] + new_paper_code + "\n\n" + text[end_idx:]

with open(app_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated renderStudentQuestionPapers and viewStudentPaperModal successfully!")
