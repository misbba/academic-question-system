import re

file_path = r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\js\app.js"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replacement block
new_block = '''// Universal Faculty Header Profile Synchronizer
function updateFacultyHeaderProfile(userObj) {
  const user = userObj || JSON.parse(localStorage.getItem('academic_user') || '{}');
  const fullName = user.full_name || user.name || (user.email ? user.email.split('@')[0] : 'Faculty Member');
  const dept = user.department || 'Artificial Intelligence & Data Science';
  const year = user.academic_year || '2025-2026';

  const facName = document.getElementById('facultyNameDisplay');
  const facDept = document.getElementById('facultyDeptDisplay');
  const welcomeHeading = document.querySelector('.dashboard-main h1');
  const paperAuthor = document.getElementById('paperAuthorDisplay');

  if (facName) facName.textContent = fullName;
  if (facDept) facDept.textContent = `${dept} • ${year}`;
  if (paperAuthor) paperAuthor.textContent = fullName;
  if (welcomeHeading && window.location.pathname.toLowerCase().includes('faculty-dashboard')) {
    welcomeHeading.textContent = `Welcome back, ${fullName}!`;
  }
}

// Populate Real Questions Table on Dashboard
function renderDashboardQuestionsTable(displayQuestions, totalCount) {
  const tableBody = document.getElementById('facultyQuestionsTableBody');
  if (!tableBody) return;

  if (!displayQuestions || displayQuestions.length === 0) {
    tableBody.innerHTML = `<tr><td colspan="8" class="text-center py-4 text-muted">No questions in Question Bank yet. Generate questions to populate repository.</td></tr>`;
  } else {
    tableBody.innerHTML = displayQuestions.map(q => {
      let diffBadge = 'badge bg-secondary';
      if (q.difficulty === 'Easy') diffBadge = 'badge bg-success-subtle text-success border border-success';
      else if (q.difficulty === 'Medium') diffBadge = 'badge bg-warning-subtle text-warning border border-warning';
      else if (q.difficulty === 'Hard') diffBadge = 'badge bg-danger-subtle text-danger border border-danger';

      return `
        <tr>
          <td><strong class="font-monospace text-primary">#${q.id}</strong></td>
          <td><span class="badge bg-light text-dark border">${q.subject || 'DBMS'}</span></td>
          <td><small class="text-muted">${q.topic || q.unit || 'General'}</small></td>
          <td><span class="fw-semibold text-dark">${q.question_text}</span></td>
          <td><span class="${diffBadge}">${q.difficulty}</span></td>
          <td><span class="badge bg-info-subtle text-info border">${q.bloom_level || 'Understand'}</span></td>
          <td><strong>${q.marks || 2}M</strong></td>
          <td>
            <a href="faculty-generate-questions.html" class="btn btn-sm btn-outline-primary py-0 px-2">
              <i class="bi bi-pencil me-1"></i> View
            </a>
          </td>
        </tr>
      `;
    }).join('');
  }

  const countFooter = document.getElementById('facultyQuestionsCountFooter');
  if (countFooter) {
    const total = totalCount !== undefined ? totalCount : (displayQuestions ? displayQuestions.length : 0);
    const count = displayQuestions ? displayQuestions.length : 0;
    countFooter.textContent = `Showing ${count} of ${total} total questions in Question Bank`;
  }
}

// Render Faculty Dashboard Data
async function renderFacultyData(userObj) {
  updateFacultyHeaderProfile(userObj);

  const qCountEl = document.getElementById('totalQuestionsCount');
  const coursesEl = document.getElementById('activeCoursesCount');
  const draftEl = document.getElementById('draftPapersCount');
  const pubEl = document.getElementById('publishedExamsCount');

  if (!window.location.pathname.toLowerCase().includes('faculty-dashboard')) return;

  // 1. Primary: Dedicated Real-Time Dashboard Statistics Endpoint
  try {
    const sRes = await fetch('http://localhost:5000/api/faculty/dashboard-stats', { credentials: 'include' });
    if (sRes.ok) {
      const stats = await sRes.json();
      if (stats.status === 'success') {
        const totalQ = stats.total_questions !== undefined ? stats.total_questions : 0;
        const activeC = stats.active_courses !== undefined ? stats.active_courses : 0;
        const draftP = stats.draft_papers !== undefined ? stats.draft_papers : 0;
        const pubE = stats.published_exams !== undefined ? stats.published_exams : 0;

        if (qCountEl) qCountEl.textContent = totalQ;
        if (coursesEl) coursesEl.textContent = `${activeC} Course${activeC === 1 ? '' : 's'}`;
        if (draftEl) draftEl.textContent = `${draftP} Paper${draftP === 1 ? '' : 's'}`;
        if (pubEl) pubEl.textContent = `${pubE} Exam${pubE === 1 ? '' : 's'}`;

        if (stats.active_paper) {
          const titleEl = document.getElementById('paperTitleDisplay');
          if (titleEl) titleEl.textContent = `${stats.active_paper.title} (${stats.active_paper.paper_code})`;
        }

        renderDashboardQuestionsTable(stats.recent_questions, totalQ);
        return; // Successfully rendered via dedicated endpoint
      }
    }
  } catch (err) {
    console.warn('Dedicated stats endpoint fetch error, falling back:', err);
  }

  // 2. Secondary Fallback: Direct Entity Queries
  let questions = [];
  try {
    const res = await fetch('http://localhost:5000/api/questions', { credentials: 'include' });
    if (res.ok) {
      const data = await res.json();
      questions = data.questions || [];
    }
  } catch (e) {
    console.warn('Could not fetch questions from API:', e);
  }

  if (qCountEl) qCountEl.textContent = questions.length;
  const uniqueSubjects = new Set(questions.map(q => q.subject).filter(Boolean));
  if (coursesEl) {
    const count = uniqueSubjects.size;
    coursesEl.textContent = `${count} Course${count === 1 ? '' : 's'}`;
  }

  renderDashboardQuestionsTable(questions.slice(0, 8), questions.length);

  try {
    const pRes = await fetch('http://localhost:5000/api/question-papers', { credentials: 'include' });
    if (pRes.ok) {
      const pData = await pRes.json();
      const papers = pData.question_papers || pData.papers || [];
      const drafts = papers.filter(p => p.status === 'Draft');
      const published = papers.filter(p => p.status === 'Published');

      if (draftEl) draftEl.textContent = `${drafts.length} Paper${drafts.length !== 1 ? '' : 's'}`;
      if (pubEl) pubEl.textContent = `${published.length} Exam${published.length !== 1 ? '' : 's'}`;

      const activePaper = papers[0];
      if (activePaper) {
        const titleEl = document.getElementById('paperTitleDisplay');
        if (titleEl) titleEl.textContent = `${activePaper.title} (${activePaper.paper_code})`;
      }
    } else {
      if (draftEl) draftEl.textContent = '0 Papers';
      if (pubEl) pubEl.textContent = '0 Exams';
    }
  } catch (e) {
    console.warn('Could not fetch papers:', e);
    if (draftEl) draftEl.textContent = '0 Papers';
    if (pubEl) pubEl.textContent = '0 Exams';
  }
}

// Universal Student Header Profile Synchronizer
function updateStudentHeaderProfile(userObj) {
  const user = userObj || JSON.parse(localStorage.getItem('academic_user') || '{}');
  const fullName = user.full_name || user.name || (user.email ? user.email.split('@')[0] : 'Student User');
  const dept = user.department || 'Artificial Intelligence & Data Science';
  const sem = user.semester || 'Sem 6';

  const studName = document.getElementById('studentNameDisplay');
  const studRoll = document.getElementById('studentRollDisplay');
  const welcomeHeading = document.getElementById('studentWelcomeHeading') || document.querySelector('.dashboard-main h1');

  if (studName) studName.textContent = fullName;
  if (studRoll) studRoll.textContent = `${dept} • ${sem}`;
  if (welcomeHeading && window.location.pathname.toLowerCase().includes('student-dashboard')) {
    welcomeHeading.textContent = `Welcome back, ${fullName.split(' ')[0]}!`;
  }
}

// Render Student Dashboard Data
async function renderStudentData(userObj) {
  updateStudentHeaderProfile(userObj);

  if (!window.location.pathname.toLowerCase().includes('student-dashboard')) return;

  // 1. Quizzes Container on Dashboard
  const quizContainer = document.getElementById('studentQuizContainer');
  try {
    const qRes = await fetch('http://localhost:5000/api/quizzes', { credentials: 'include' });
    if (qRes.ok) {
      const qData = await qRes.json();
      const quizzes = (qData.quizzes || []).filter(q => q.status === 'Published');
      if (quizContainer) {
        if (quizzes.length === 0) {
          quizContainer.innerHTML = `<div class="p-3 text-center text-muted small"><i class="bi bi-calendar-check me-1"></i> No active quizzes scheduled at this time.</div>`;
        } else {
          quizContainer.innerHTML = quizzes.slice(0, 3).map(q => `
            <div class="d-flex justify-content-between align-items-center p-2 mb-2 border rounded bg-light">
              <div>
                <div class="fw-bold text-dark">${q.title}</div>
                <small class="text-muted">${q.subject} • ${q.duration_minutes || 15} Mins • ${q.total_questions || 10} Qs</small>
              </div>
              <a href="student-quizzes.html" class="btn btn-sm btn-academic-primary py-1 px-3">
                <i class="bi bi-play-circle me-1"></i> Take Quiz
              </a>
            </div>
          `).join('');
        }
      }
    }
  } catch (e) {
    console.warn('Could not fetch quizzes for student dashboard:', e);
  }

  // 2. Exam Papers Container on Dashboard
  const paperContainer = document.getElementById('studentExamPapersContainer');
  try {
    const pRes = await fetch('http://localhost:5000/api/question-papers?status=Published', { credentials: 'include' });
    if (pRes.ok) {
      const pData = await pRes.json();
      const papers = pData.question_papers || pData.papers || [];
      if (paperContainer) {
        if (papers.length === 0) {
          paperContainer.innerHTML = `<div class="p-3 text-center text-muted small"><i class="bi bi-file-earmark-pdf me-1"></i> No published examination papers available.</div>`;
        } else {
          paperContainer.innerHTML = papers.slice(0, 3).map(p => `
            <div class="d-flex justify-content-between align-items-center p-2 mb-2 border rounded bg-light">
              <div>
                <div class="fw-bold text-dark">${p.title}</div>
                <small class="text-muted">${p.subject} • ${p.exam_type || 'Examination'} • ${p.total_marks || 100} Marks</small>
              </div>
              <a href="student-question-papers.html" class="btn btn-sm btn-outline-primary py-1 px-3">
                <i class="bi bi-eye me-1"></i> View Paper
              </a>
            </div>
          `).join('');
        }
      }
    }
  } catch (e) {
    console.warn('Could not fetch papers for student dashboard:', e);
  }
}

// Role & Session Management (Flask + MySQL Integration)
async function initRoleManagement() {
  const path = window.location.pathname.toLowerCase();

  const isFacultyPage = path.includes('faculty-dashboard.html') || path.includes('faculty-resources.html') || path.includes('faculty-generate-questions.html') || path.includes('faculty-question-paper.html') || path.includes('faculty-generate-quiz.html') || path.includes('faculty-generate-assignment.html') || path.includes('faculty-generate-ppt.html') || path.includes('faculty-generate-lesson-plan.html') || path.includes('faculty-voice-question.html') || path.includes('faculty-image-question.html') || path.includes('faculty-language-converter.html') || path.includes('faculty-results.html') || path.includes('faculty-performance.html') || path.includes('faculty-history.html') || path.includes('faculty-profile.html');

  const isStudentPage = path.includes('student-dashboard.html') || path.includes('student-subjects.html') || path.includes('student-materials.html') || path.includes('student-question-papers.html') || path.includes('student-quizzes.html') || path.includes('student-assignments.html') || path.includes('student-presentations.html') || path.includes('student-lesson-plans.html') || path.includes('student-results.html') || path.includes('student-performance.html') || path.includes('student-history.html') || path.includes('student-profile.html');

  if (isFacultyPage) {
    updateFacultyHeaderProfile(); // Immediate rendering from localStorage

    let verifiedUser = null;
    if (typeof Auth !== 'undefined') {
      verifiedUser = await Auth.requireRole('faculty');
      if (!verifiedUser) return; // Redirected
    }
    updateFacultyHeaderProfile(verifiedUser);

    if (path.includes('faculty-dashboard')) {
      await renderFacultyData(verifiedUser);
    }
    if (path.includes('faculty-resources.html') && typeof renderFacultyResourcesTable === 'function') renderFacultyResourcesTable();
    if (path.includes('faculty-generate-questions.html') && typeof initQuestionGeneratorPage === 'function') initQuestionGeneratorPage();
    if (path.includes('faculty-question-paper.html') && typeof loadQuestionPaperBuilderPage === 'function') loadQuestionPaperBuilderPage();
    if (path.includes('faculty-generate-quiz.html') && typeof initQuizGeneratorPage === 'function') initQuizGeneratorPage();
    if (path.includes('faculty-generate-assignment.html') && typeof initAssignmentGeneratorPage === 'function') initAssignmentGeneratorPage();
    if (path.includes('faculty-generate-ppt.html') && typeof initPPTGeneratorPage === 'function') initPPTGeneratorPage();
    if (path.includes('faculty-generate-lesson-plan.html') && typeof initLessonPlanGeneratorPage === 'function') initLessonPlanGeneratorPage();
    if (path.includes('faculty-voice-question.html') && typeof initVoiceQuestionPage === 'function') initVoiceQuestionPage();
    if (path.includes('faculty-image-question.html') && typeof initImageQuestionPage === 'function') initImageQuestionPage();
    if (path.includes('faculty-language-converter.html') && typeof initLanguageConverterPage === 'function') initLanguageConverterPage();
    if (path.includes('faculty-results.html') && typeof renderFacultyResultsPage === 'function') renderFacultyResultsPage();
    if (path.includes('faculty-performance.html') && typeof renderFacultyPerformancePage === 'function') renderFacultyPerformancePage();
    if (path.includes('faculty-history.html') && typeof renderFacultyHistoryPage === 'function') renderFacultyHistoryPage();
  } else if (isStudentPage) {
    updateStudentHeaderProfile(); // Immediate rendering from localStorage

    let verifiedUser = null;
    if (typeof Auth !== 'undefined') {
      verifiedUser = await Auth.requireRole('student');
      if (!verifiedUser) return; // Redirected
    }
    updateStudentHeaderProfile(verifiedUser);

    if (path.includes('student-dashboard')) {
      await renderStudentData(verifiedUser);
    }
    if (path.includes('student-materials.html') && typeof renderStudentMaterialsTable === 'function') renderStudentMaterialsTable();
    if (path.includes('student-question-papers.html') && typeof renderStudentQuestionPapers === 'function') renderStudentQuestionPapers();
    if (path.includes('student-quizzes.html') && typeof renderStudentQuizzes === 'function') renderStudentQuizzes();
    if (path.includes('student-assignments.html') && typeof renderStudentAssignments === 'function') renderStudentAssignments();
    if (path.includes('student-presentations.html') && typeof renderStudentPresentations === 'function') renderStudentPresentations();
    if (path.includes('student-lesson-plans.html') && typeof renderStudentLessonPlans === 'function') renderStudentLessonPlans();
    if (path.includes('student-results.html') && typeof renderStudentResultsPage === 'function') renderStudentResultsPage();
    if (path.includes('student-performance.html') && typeof renderStudentPerformancePage === 'function') renderStudentPerformancePage();
    if (path.includes('student-history.html') && typeof renderStudentHistoryPage === 'function') renderStudentHistoryPage();
  }
}'''

# Find boundaries
start_marker = "// Render Faculty Dashboard Data"
end_marker = "function handleLogin(role, identifier, name) {"

start_pos = content.find(start_marker)
end_pos = content.find(end_marker)

if start_pos == -1 or end_pos == -1:
    print("Could not find start or end markers!")
else:
    updated_content = content[:start_pos] + new_block + "\n\n" + content[end_pos:]
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    print("Successfully updated js/app.js!")
