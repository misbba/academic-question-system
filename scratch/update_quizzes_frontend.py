import os

app_path = r'C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\js\app.js'
with open(app_path, 'r', encoding='utf-8') as f:
    text = f.read()

idx_quiz = text.find('async function renderStudentQuizzes')
idx_start = text.find('function startStudentQuizAttempt', idx_quiz)

new_quizzes_code = """
async function renderStudentQuizzes() {
  const tableBody = document.getElementById('studentQuizzesTableBody');
  const historyBody = document.getElementById('studentQuizHistoryBody');

  const urlParams = new URLSearchParams(window.location.search);
  const filterSelect = document.getElementById('studentQuizSubjectFilter');
  let currentSubject = urlParams.get('subject') || (filterSelect ? filterSelect.value : 'ALL') || 'ALL';

  let publishedOnly = [];
  let history = [];

  try {
    const res = await fetch(API_QUIZZES_BASE, { credentials: 'include' });
    if (res.ok) {
      const data = await res.json();
      if (data.status === 'success' && Array.isArray(data.quizzes)) {
        globalPublishedQuizzes = data.quizzes;
        publishedOnly = data.quizzes.filter(q => q.status === 'Published');
      }
    }
  } catch (err) {
    console.warn('Backend API quiz fetch failed, using fallback:', err);
    const storedQuizzes = JSON.parse(localStorage.getItem('academic_quizzes') || '[]').concat(AcademicMockData.publishedQuizzes || []);
    publishedOnly = storedQuizzes.filter(q => q.status === 'Published');
    globalPublishedQuizzes = publishedOnly;
  }

  // Populate subject filter dropdown if present
  if (filterSelect) {
    const subjects = Array.from(new Set(globalPublishedQuizzes.map(q => q.subject).filter(Boolean)));
    if (!subjects.includes('Database Management Systems')) subjects.push('Database Management Systems');
    if (!subjects.includes('Distributed Computing')) subjects.push('Distributed Computing');
    if (!subjects.includes('Machine Learning')) subjects.push('Machine Learning');

    filterSelect.innerHTML = `<option value="ALL">All Subjects (${globalPublishedQuizzes.length})</option>` +
      subjects.map(s => {
        const cnt = globalPublishedQuizzes.filter(q => q.subject === s).length;
        return `<option value="${s}" ${s === currentSubject ? 'selected' : ''}>${s} (${cnt})</option>`;
      }).join('');

    if (currentSubject && subjects.includes(currentSubject)) {
      filterSelect.value = currentSubject;
    }
  }

  let filtered = publishedOnly;
  if (currentSubject && currentSubject !== 'ALL') {
    filtered = filtered.filter(q => q.subject === currentSubject);
  }

  if (tableBody) {
    if (filtered.length === 0) {
      tableBody.innerHTML = `<tr><td colspan="7" class="text-center py-5 text-muted"><i class="bi bi-patch-question fs-2 d-block mb-2 text-secondary"></i>No published quizzes available ${currentSubject !== 'ALL' ? `for <strong>${currentSubject}</strong>` : ''}. Check back later!</td></tr>`;
    } else {
      tableBody.innerHTML = filtered.map(q => {
        const qId = q.id || q.quizId || q.quiz_code;
        let qCount = 0;
        if (Array.isArray(q.questions)) {
          qCount = q.questions.length;
        } else if (typeof q.questions === 'string') {
          try { qCount = JSON.parse(q.questions).length; } catch(e) { qCount = 0; }
        } else if (q.total_questions) {
          qCount = q.total_questions;
        }

        const dur = q.duration_minutes || q.durationMins || 10;
        const marksPerQ = (q.marks_per_question !== undefined && q.marks_per_question !== null) ? q.marks_per_question : ((q.marksPerQuestion !== undefined && q.marksPerQuestion !== null) ? q.marksPerQuestion : 1);
        const totalMarks = q.total_marks || (marksPerQ * qCount);

        return `
          <tr>
            <td>
              <strong class="text-dark">${q.title}</strong>
              <div class="small text-muted font-monospace">${q.quiz_code || q.quizId || ''}</div>
            </td>
            <td><span class="badge bg-primary-subtle text-primary border">${q.subject}</span></td>
            <td><small class="text-muted">${q.unit || 'General'}</small></td>
            <td><small>${qCount} Qs</small></td>
            <td><small class="fw-semibold">${dur} Mins</small></td>
            <td><strong>${totalMarks} Marks</strong></td>
            <td>
              <button class="btn btn-academic-accent btn-sm py-0 px-2" onclick="startStudentQuizAttempt('${qId}')">
                <i class="bi bi-play-circle me-1"></i> Start Quiz
              </button>
            </td>
          </tr>
        `;
      }).join('');
    }
  }

  // Render Student Quiz Attempt History
  if (historyBody) {
    try {
      const resH = await fetch(`${API_QUIZZES_BASE}/attempts`, { credentials: 'include' });
      if (resH.ok) {
        const dataH = await resH.json();
        if (dataH.status === 'success' && Array.isArray(dataH.attempts)) {
          history = dataH.attempts;
        }
      }
    } catch (err) {
      console.warn('Backend API quiz attempts fetch failed, using fallback:', err);
      history = JSON.parse(localStorage.getItem('academic_quiz_results') || '[]').concat(AcademicMockData.studentQuizHistory || []);
    }

    if (history.length === 0) {
      historyBody.innerHTML = `<tr><td colspan="5" class="text-center py-3 text-muted">No past quiz attempts recorded.</td></tr>`;
    } else {
      historyBody.innerHTML = history.map(h => `
        <tr>
          <td><strong>${h.title}</strong></td>
          <td><small>${h.subject}</small></td>
          <td><span class="badge bg-success-subtle text-success border border-success fw-bold">${h.score} (${h.percentage})</span></td>
          <td><small class="text-muted">${h.date || h.completed_at || 'Recent'}</small></td>
          <td><span class="badge bg-light text-dark border">Completed</span></td>
        </tr>
      `).join('');
    }
  }
}

function filterStudentQuizzes() {
  const filterSelect = document.getElementById('studentQuizSubjectFilter');
  const sel = filterSelect ? filterSelect.value : 'ALL';
  const url = new URL(window.location);
  if (sel === 'ALL') {
    url.searchParams.delete('subject');
  } else {
    url.searchParams.set('subject', sel);
  }
  window.history.replaceState({}, '', url);
  renderStudentQuizzes();
}

"""

text = text[:idx_quiz] + new_quizzes_code.strip() + "\n\n" + text[idx_start:]

with open(app_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated quizzes in app.js successfully!")
