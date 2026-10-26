import os

app_path = r'C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\js\app.js'
with open(app_path, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update saveAssignmentToStorage
idx_save = text.find('function saveAssignmentToStorage')
idx_after_save = text.find('// ==========================================', idx_save)

new_save_code = """
async function saveAssignmentToStorage(status) {
  const dept = document.getElementById('asnDept')?.value || "Artificial Intelligence & Data Science";
  const subject = document.getElementById('asnSubject')?.value || "Database Management Systems";
  const year = document.getElementById('asnYear')?.value || "2025-2026";
  const sem = document.getElementById('asnSem')?.value || "Semester 6";
  const unit = document.getElementById('asnUnit')?.value || "Unit III — SQL";
  const title = document.getElementById('asnTitleInput')?.value || "SQL Query Practice Assignment";
  const dueDate = document.getElementById('asnDueDate')?.value || "2026-09-25";
  const maxMarks = parseInt(document.getElementById('asnTotalMarks')?.value || 50);
  const instructions = document.getElementById('asnInstructions')?.value || "Solve all questions.";

  const asnObj = {
    assignmentId: `ASSIGN-2026-${Date.now().toString().slice(-4)}`,
    title, department: dept, subject, academicYear: year, semester: sem, unit,
    dueDate, maxMarks, status, createdDate: new Date().toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }),
    createdBy: (JSON.parse(localStorage.getItem('academic_user') || '{}').name) || "Faculty Member",
    instructions,
    questions: (typeof activeGeneratedAssignmentQuestions !== 'undefined' ? activeGeneratedAssignmentQuestions : [])
  };

  // Local persistence
  let storedAsns = JSON.parse(localStorage.getItem('academic_assignments') || '[]');
  storedAsns.unshift(asnObj);
  localStorage.setItem(getScopedStorageKey('academic_assignments'), JSON.stringify(storedAsns));
  AcademicMockData.publishedAssignments.unshift(asnObj);

  // MySQL persistence
  try {
    const res = await fetch('http://localhost:5000/api/assignments', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({
        title, department: dept, subject, academic_year: year, semester: sem, unit,
        due_date: dueDate, total_marks: maxMarks, instructions,
        questions: asnObj.questions, status
      })
    });
    if (res.ok) {
      const data = await res.json();
      if (data.id) asnObj.id = data.id;
    }
  } catch (err) {
    console.warn('Backend assignment creation warning:', err);
  }
}
"""

text = text[:idx_save] + new_save_code.strip() + "\n\n" + text[idx_after_save:]

# 2. Update renderStudentAssignments through submitStudentAssignment
idx_render = text.find('function renderStudentAssignments')
idx_after_sub = text.find('// ==========================================', idx_render)

new_render_code = """
let globalStudentAssignments = [];

async function renderStudentAssignments() {
  const tableBody = document.getElementById('studentAssignmentsTableBody');
  if (!tableBody) return;

  const urlParams = new URLSearchParams(window.location.search);
  const filterSelect = document.getElementById('studentAssignmentSubjectFilter');
  let currentSubject = urlParams.get('subject') || (filterSelect ? filterSelect.value : 'ALL') || 'ALL';

  tableBody.innerHTML = `<tr><td colspan="7" class="text-center py-4 text-muted"><span class="spinner-border spinner-border-sm me-2 text-primary"></span>Loading course assignments...</td></tr>`;

  try {
    const res = await fetch('http://localhost:5000/api/assignments', {
      credentials: 'include'
    });
    if (res.ok) {
      const data = await res.json();
      if (data.status === 'success' && Array.isArray(data.assignments)) {
        globalStudentAssignments = data.assignments;
      }
    }
  } catch (err) {
    console.warn('API error fetching assignments, using local storage fallback:', err);
  }

  // Fallback to local storage / mock data if backend empty
  if (!globalStudentAssignments || globalStudentAssignments.length === 0) {
    const storedAsns = JSON.parse(localStorage.getItem(getScopedStorageKey('academic_assignments')) || '[]');
    const mockAsns = (AcademicMockData.publishedAssignments || []).map(a => ({
      ...a,
      id: a.id || a.assignmentId,
      due_date: a.dueDate,
      total_marks: a.maxMarks,
      status: a.status || 'Published'
    }));
    globalStudentAssignments = storedAsns.concat(mockAsns).filter(a => a.status === 'Published');
  }

  // Populate subject filter select if available
  if (filterSelect) {
    const subjects = Array.from(new Set(globalStudentAssignments.map(a => a.subject).filter(Boolean)));
    if (!subjects.includes('Database Management Systems')) subjects.push('Database Management Systems');
    if (!subjects.includes('Distributed Computing')) subjects.push('Distributed Computing');
    if (!subjects.includes('Machine Learning')) subjects.push('Machine Learning');

    filterSelect.innerHTML = `<option value="ALL">All Subjects (${globalStudentAssignments.length})</option>` +
      subjects.map(s => {
        const cnt = globalStudentAssignments.filter(a => a.subject === s).length;
        return `<option value="${s}" ${s === currentSubject ? 'selected' : ''}>${s} (${cnt})</option>`;
      }).join('');

    if (currentSubject && subjects.includes(currentSubject)) {
      filterSelect.value = currentSubject;
    }
  }

  let filtered = globalStudentAssignments;
  if (currentSubject && currentSubject !== 'ALL') {
    filtered = filtered.filter(a => a.subject === currentSubject);
  }

  const submissions = JSON.parse(localStorage.getItem('academic_assignment_submissions') || '[]');

  if (!filtered || filtered.length === 0) {
    tableBody.innerHTML = `<tr><td colspan="7" class="text-center py-5 text-muted"><i class="bi bi-journal-x fs-2 d-block mb-2 text-secondary"></i>No published assignments available ${currentSubject !== 'ALL' ? `for <strong>${currentSubject}</strong>` : ''}. Check back later!</td></tr>`;
    return;
  }

  tableBody.innerHTML = filtered.map(a => {
    const aId = a.id || a.assignmentId;
    const isSubmitted = Boolean(a.is_submitted || submissions.some(sub => String(sub.assignmentId) === String(aId)));
    const dueDate = a.due_date || a.dueDate || '2026-09-30';
    const marks = a.total_marks || a.maxMarks || 20;

    return `
      <tr>
        <td>
          <strong class="text-dark">${a.title}</strong>
          <div class="small text-muted font-monospace">${a.assignmentId || `ASN-${aId}`}</div>
        </td>
        <td><span class="badge bg-primary-subtle text-primary border">${a.subject}</span></td>
        <td><small class="text-muted">${a.unit || 'General'}</small></td>
        <td><small class="text-danger fw-semibold">${dueDate}</small></td>
        <td><strong>${marks} Marks</strong></td>
        <td>
          <span class="badge ${isSubmitted ? 'bg-success-subtle text-success border border-success' : 'bg-warning-subtle text-warning border border-warning'}">
            ${isSubmitted ? 'Submitted' : 'Pending'}
          </span>
        </td>
        <td>
          <button class="btn ${isSubmitted ? 'btn-outline-success' : 'btn-academic-primary'} btn-sm py-0 px-2" onclick="viewStudentAssignmentModal('${aId}')">
            <i class="bi bi-file-earmark-text me-1"></i> ${isSubmitted ? 'View Submission' : 'Complete Assignment'}
          </button>
        </td>
      </tr>
    `;
  }).join('');
}

function filterStudentAssignments() {
  const filterSelect = document.getElementById('studentAssignmentSubjectFilter');
  const sel = filterSelect ? filterSelect.value : 'ALL';
  const url = new URL(window.location);
  if (sel === 'ALL') {
    url.searchParams.delete('subject');
  } else {
    url.searchParams.set('subject', sel);
  }
  window.history.replaceState({}, '', url);
  renderStudentAssignments();
}

function viewStudentAssignmentModal(asnId) {
  let asn = (globalStudentAssignments || []).find(a => String(a.id) === String(asnId) || a.assignmentId === asnId);

  if (!asn) {
    const storedAsns = JSON.parse(localStorage.getItem(getScopedStorageKey('academic_assignments')) || '[]');
    asn = storedAsns.find(a => String(a.id) === String(asnId) || a.assignmentId === asnId);
  }

  if (!asn) {
    showToastNotice('Error', 'Unable to load assignment details.', 'danger');
    return;
  }

  const submissions = JSON.parse(localStorage.getItem('academic_assignment_submissions') || '[]');
  const sub = submissions.find(s => String(s.assignmentId) === String(asnId)) || (asn.is_submitted ? { answers: { Q1: asn.submission_text } } : null);

  const modalEl = document.getElementById('studentAssignmentViewModal');
  if (!modalEl) return;

  const dueDate = asn.due_date || asn.dueDate || '2026-09-30';
  const marks = asn.total_marks || asn.maxMarks || 20;

  document.getElementById('studentAsnTitle').innerText = asn.title;
  document.getElementById('studentAsnMeta').innerHTML = `
    <strong>Subject:</strong> ${asn.subject} | <strong>Due Date:</strong> ${dueDate} | <strong>Max Marks:</strong> ${marks}
  `;

  // Parse questions or fallback to instructions
  let qs = asn.questions;
  if (typeof qs === 'string') {
    try { qs = JSON.parse(qs); } catch(e) { qs = []; }
  }
  if (!qs || !Array.isArray(qs) || qs.length === 0) {
    const rawInstr = asn.instructions || "1. Answer the theoretical concept questions.\\n2. Provide implementation details.";
    qs = [
      { text: rawInstr, marks: marks, concept: "Course Comprehensive Task" }
    ];
  }

  document.getElementById('studentAsnQuestionsBody').innerHTML = qs.map((q, idx) => `
    <div class="card card-academic p-3 mb-3">
      <div class="d-flex justify-content-between align-items-center mb-2">
        <strong class="text-primary">Question ${idx + 1} (${q.marks || 10} Marks)</strong>
        <span class="badge bg-secondary-subtle text-dark border">${q.concept || 'Concept Analysis'}</span>
      </div>
      <p class="fw-semibold text-dark mb-2">${q.text || q.question || q.question_text || 'Explain and solve the assigned task.'}</p>
      <textarea class="form-control small" id="asnAnswer_${idx}" rows="3" placeholder="Type your full answer here..." ${sub ? 'readonly' : ''}>${sub?.answers?.[`Q${idx + 1}`] || (typeof sub?.answers === 'string' ? sub.answers : '') || ''}</textarea>
    </div>
  `).join('');

  const submitBtn = document.getElementById('submitStudentAsnBtn');
  if (submitBtn) {
    if (sub) {
      submitBtn.classList.add('d-none');
    } else {
      submitBtn.classList.remove('d-none');
      submitBtn.onclick = () => submitStudentAssignment(asnId, qs.length);
    }
  }

  const bsModal = bootstrap.Modal.getOrCreateInstance(modalEl);
  bsModal.show();
}

async function submitStudentAssignment(asnId, qCount) {
  const answers = {};
  let combinedText = '';
  for (let i = 0; i < qCount; i++) {
    const text = document.getElementById(`asnAnswer_${i}`)?.value || '';
    answers[`Q${i + 1}`] = text;
    combinedText += `Q${i + 1}: ${text}\\n`;
  }

  const studentAcc = (typeof AcademicMockData !== 'undefined' && AcademicMockData.studentAccount) ? AcademicMockData.studentAccount : { id: 5, name: 'Nisha' };
  const subObj = {
    assignmentId: asnId,
    studentId: studentAcc.id,
    studentName: studentAcc.name,
    answers: answers,
    submission_text: combinedText,
    submittedAt: new Date().toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })
  };

  let subs = JSON.parse(localStorage.getItem('academic_assignment_submissions') || '[]');
  subs.push(subObj);
  localStorage.setItem('academic_assignment_submissions', JSON.stringify(subs));

  // MySQL persistence
  try {
    await fetch(`http://localhost:5000/api/assignments/${asnId}/submit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({
        submission_text: combinedText,
        file_name: '',
        file_path: ''
      })
    });
  } catch (err) {
    console.warn('Backend assignment submission warning:', err);
  }

  const modalEl = document.getElementById('studentAssignmentViewModal');
  if (modalEl) {
    const bsModal = bootstrap.Modal.getInstance(modalEl);
    if (bsModal) bsModal.hide();
  }

  showToastNotice('Assignment Submitted', 'Assignment submitted and saved successfully!', 'success');
  renderStudentAssignments();
}
"""

text = text[:idx_render] + new_render_code.strip() + "\n\n" + text[idx_after_sub:]

with open(app_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated assignments in app.js successfully!")
