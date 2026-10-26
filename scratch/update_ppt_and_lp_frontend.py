import os

app_path = r'C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\js\app.js'
with open(app_path, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update savePPTDraft
idx_ppt = text.find('function savePPTDraft')
idx_after_ppt = text.find('// ==========================================', idx_ppt)

new_save_ppt = """
async function savePPTDraft(status = 'Draft') {
  if (activeGeneratedSlides.length === 0) {
    showToastNotice('Cannot Save', 'Please generate slides first.', 'warning');
    return;
  }

  const pptObj = {
    id: `PPT-2026-${Date.now().toString().slice(-4)}`,
    title: activePPTConfig.title || "Academic Presentation",
    department: activePPTConfig.dept || "Artificial Intelligence & Data Science",
    subject: activePPTConfig.subject || "Database Management Systems",
    academicYear: activePPTConfig.year || "2025-2026",
    semester: activePPTConfig.sem || "Semester 6",
    unit: activePPTConfig.unit || "Unit III — SQL",
    topic: activePPTConfig.topic || "SQL Joins",
    sourceMaterial: activePPTConfig.sourceMat || "DBMS Syllabus 2026",
    slideCount: activeGeneratedSlides.length,
    presentationType: activePPTConfig.presType || "Classroom Teaching",
    slides: activeGeneratedSlides,
    status: status,
    createdAt: new Date().toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }),
    publishedAt: status === 'Published' ? new Date().toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }) : null,
    createdBy: (JSON.parse(localStorage.getItem('academic_user') || '{}').name) || "Faculty Member"
  };

  let ppts = JSON.parse(localStorage.getItem('academic_ppts') || '[]');
  ppts.unshift(pptObj);
  localStorage.setItem(getScopedStorageKey('academic_ppts'), JSON.stringify(ppts));
  AcademicMockData.publishedPPTs.unshift(pptObj);

  // MySQL persistence
  try {
    const res = await fetch('http://localhost:5000/api/presentations', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({
        title: pptObj.title,
        department: pptObj.department,
        subject: pptObj.subject,
        academic_year: pptObj.academicYear,
        semester: pptObj.semester,
        unit: pptObj.unit,
        topic: pptObj.topic,
        slide_count: pptObj.slideCount,
        presentation_type: pptObj.presentationType,
        source_material: pptObj.sourceMaterial,
        status: status
      })
    });
    if (res.ok) {
      const data = await res.json();
      if (data.id) pptObj.db_id = data.id;
    }
  } catch (err) {
    console.warn('Backend presentation creation warning:', err);
  }
}
"""

text = text[:idx_ppt] + new_save_ppt.strip() + "\n\n" + text[idx_after_ppt:]

# 2. Update saveLessonPlanDraft
idx_lp = text.find('function saveLessonPlanDraft')
idx_after_lp = text.find('// ==========================================', idx_lp)

new_save_lp = """
async function saveLessonPlanDraft(status = 'Draft') {
  if (!activeLessonPlanObj) {
    showToastNotice('Cannot Save', 'Please generate a lesson plan first.', 'warning');
    return;
  }

  activeLessonPlanObj.title = document.getElementById('lpEditTitle')?.value || activeLessonPlanObj.title;
  activeLessonPlanObj.objectives = document.getElementById('lpEditObjectives')?.value || activeLessonPlanObj.objectives;
  activeLessonPlanObj.prerequisites = document.getElementById('lpEditPrereqs')?.value || activeLessonPlanObj.prerequisites;
  activeLessonPlanObj.concepts = document.getElementById('lpEditConcepts')?.value || activeLessonPlanObj.concepts;
  activeLessonPlanObj.activities = document.getElementById('lpEditActivities')?.value || activeLessonPlanObj.activities;
  activeLessonPlanObj.resources = document.getElementById('lpEditResources')?.value || activeLessonPlanObj.resources;
  activeLessonPlanObj.explanationPoints = document.getElementById('lpEditExplanations')?.value || activeLessonPlanObj.explanationPoints;
  activeLessonPlanObj.studentActivities = document.getElementById('lpEditStudentActs')?.value || activeLessonPlanObj.studentActivities;
  activeLessonPlanObj.assessment = document.getElementById('lpEditAssessment')?.value || activeLessonPlanObj.assessment;
  activeLessonPlanObj.homework = document.getElementById('lpEditHomework')?.value || activeLessonPlanObj.homework;
  activeLessonPlanObj.outcomes = document.getElementById('lpEditOutcomes')?.value || activeLessonPlanObj.outcomes;
  activeLessonPlanObj.summary = document.getElementById('lpEditSummary')?.value || activeLessonPlanObj.summary;
  activeLessonPlanObj.status = status;
  if (status === 'Published') activeLessonPlanObj.publishedAt = new Date().toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });

  let lps = JSON.parse(localStorage.getItem('academic_lesson_plans') || '[]');
  lps.unshift(activeLessonPlanObj);
  localStorage.setItem(getScopedStorageKey('academic_lesson_plans'), JSON.stringify(lps));
  AcademicMockData.publishedLessonPlans.unshift(activeLessonPlanObj);

  // MySQL persistence
  try {
    await fetch('http://localhost:5000/api/lesson-plans', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({
        title: activeLessonPlanObj.title,
        department: activeLessonPlanObj.department || "Artificial Intelligence & Data Science",
        subject: activeLessonPlanObj.subject || "Database Management Systems",
        academic_year: activeLessonPlanObj.academicYear || "2025-2026",
        semester: activeLessonPlanObj.semester || "Semester 6",
        unit: activeLessonPlanObj.unit || "Unit 1",
        topic: activeLessonPlanObj.topic || "Core Curriculum",
        duration_minutes: parseInt(activeLessonPlanObj.duration || 50, 10),
        teaching_method: activeLessonPlanObj.method || "Interactive Lecture",
        status: status
      })
    });
  } catch (err) {
    console.warn('Backend lesson plan creation warning:', err);
  }

  showToastNotice(`Lesson Plan ${status}`, `Lesson plan successfully saved as ${status}!`, status === 'Published' ? 'success' : 'info');
}
"""

text = text[:idx_lp] + new_save_lp.strip() + "\n\n" + text[idx_after_lp:]

# 3. Update renderStudentPresentations & openStudentPresentationViewer
idx_r_ppt = text.find('function renderStudentPresentations')
idx_r_ppt_end = text.find('// ==========================================', idx_r_ppt)

new_render_ppt = """
let globalStudentPPTs = [];

async function renderStudentPresentations() {
  const tableBody = document.getElementById('studentPresentationsTableBody');
  if (!tableBody) return;

  const urlParams = new URLSearchParams(window.location.search);
  const currentSubject = urlParams.get('subject') || 'ALL';

  tableBody.innerHTML = `<tr><td colspan="7" class="text-center py-4 text-muted"><span class="spinner-border spinner-border-sm me-2 text-primary"></span>Loading course presentations...</td></tr>`;

  try {
    const res = await fetch('http://localhost:5000/api/presentations', { credentials: 'include' });
    if (res.ok) {
      const data = await res.json();
      if (data.status === 'success' && Array.isArray(data.presentations)) {
        globalStudentPPTs = data.presentations;
      }
    }
  } catch (err) {
    console.warn('API fetch presentations warning:', err);
  }

  if (!globalStudentPPTs || globalStudentPPTs.length === 0) {
    const storedPPTs = JSON.parse(localStorage.getItem(getScopedStorageKey('academic_ppts')) || '[]');
    globalStudentPPTs = storedPPTs.filter(p => p.status === 'Published');
  }

  let filtered = globalStudentPPTs;
  if (currentSubject && currentSubject !== 'ALL') {
    filtered = filtered.filter(p => p.subject === currentSubject);
  }

  if (filtered.length === 0) {
    tableBody.innerHTML = `<tr><td colspan="7" class="text-center py-5 text-muted"><i class="bi bi-easel fs-2 d-block mb-2 text-secondary"></i>No published presentations available ${currentSubject !== 'ALL' ? `for <strong>${currentSubject}</strong>` : ''}. Check back soon!</td></tr>`;
    return;
  }

  tableBody.innerHTML = filtered.map(p => {
    const pId = p.id || p.presentationId;
    const slideCnt = p.slide_count || p.slideCount || 8;
    const pubDate = p.created_at || p.publishedAt || p.createdAt || 'Recent';

    return `
      <tr>
        <td><strong class="text-dark">${p.title}</strong></td>
        <td><span class="badge bg-primary-subtle text-primary border">${p.subject}</span></td>
        <td><small class="text-muted">${p.unit || 'General'}</small></td>
        <td><small>${p.topic || 'General Topic'}</small></td>
        <td><small class="fw-semibold">${slideCnt} Slides</small></td>
        <td><small class="text-muted">${pubDate}</small></td>
        <td>
          <button class="btn btn-academic-primary btn-sm py-0 px-2" onclick="openStudentPresentationViewer('${pId}')">
            <i class="bi bi-play-circle me-1"></i> View Presentation
          </button>
        </td>
      </tr>
    `;
  }).join('');
}

function openStudentPresentationViewer(pptId) {
  let p = (globalStudentPPTs || []).find(x => String(x.id) === String(pptId));
  if (!p) {
    const storedPPTs = JSON.parse(localStorage.getItem(getScopedStorageKey('academic_ppts')) || '[]');
    p = storedPPTs.find(x => String(x.id) === String(pptId));
  }

  if (!p) return;

  studentCurrentPPT = p;
  if (!studentCurrentPPT.slides || studentCurrentPPT.slides.length === 0) {
    studentCurrentPPT.slides = [
      {
        slideNumber: 1,
        title: studentCurrentPPT.title,
        layout: 'title',
        bullets: [
          `Subject: ${studentCurrentPPT.subject}`,
          `Unit: ${studentCurrentPPT.unit || 'Unit 1'}`,
          `Topic: ${studentCurrentPPT.topic || 'Core Curriculum'}`
        ],
        speakerNotes: `Welcome to the lecture presentation for ${studentCurrentPPT.title}.`
      },
      {
        slideNumber: 2,
        title: `Overview: ${studentCurrentPPT.topic || 'Foundational Principles'}`,
        layout: 'content',
        bullets: [
          `Core concepts and formal definitions in ${studentCurrentPPT.subject}`,
          'Architectural models and operational flow',
          'Industry relevance and benchmark use-cases'
        ],
        speakerNotes: 'Key foundational lecture points.'
      },
      {
        slideNumber: 3,
        title: 'Analytical Depth & Examination Focus',
        layout: 'content',
        bullets: [
          'Detailed analytical formulations and proofs',
          'Comparative trade-offs and complexity analysis',
          'High-frequency examination problem categories'
        ],
        speakerNotes: 'Analytical deep-dive.'
      },
      {
        slideNumber: 4,
        title: 'Key Takeaways & Summary',
        layout: 'summary',
        bullets: [
          `Summary of ${studentCurrentPPT.title}`,
          'Suggested practice problems and revision checklist',
          'Recommended reference materials in the Course Materials portal'
        ],
        speakerNotes: 'Conclude and take student questions.'
      }
    ];
  }

  studentPreviewSlideIndex = 0;
  renderCurrentStudentSlide();

  const modalEl = document.getElementById('studentPresentationViewerModal');
  if (modalEl) {
    const bsModal = bootstrap.Modal.getOrCreateInstance(modalEl);
    bsModal.show();
  }
}
"""

text = text[:idx_r_ppt] + new_render_ppt.strip() + "\n\n" + text[idx_r_ppt_end:]

# 4. Update renderStudentLessonPlans & openStudentLessonPlanViewer
idx_r_lp = text.find('function renderStudentLessonPlans')
idx_r_lp_end = text.find('// ==========================================', idx_r_lp)

new_render_lp = """
let globalStudentLessonPlans = [];

async function renderStudentLessonPlans() {
  const tableBody = document.getElementById('studentLessonPlansTableBody');
  if (!tableBody) return;

  const urlParams = new URLSearchParams(window.location.search);
  const currentSubject = urlParams.get('subject') || 'ALL';

  tableBody.innerHTML = `<tr><td colspan="7" class="text-center py-4 text-muted"><span class="spinner-border spinner-border-sm me-2 text-primary"></span>Loading published lesson plans...</td></tr>`;

  try {
    const res = await fetch('http://localhost:5000/api/lesson-plans', { credentials: 'include' });
    if (res.ok) {
      const data = await res.json();
      if (data.status === 'success' && Array.isArray(data.lesson_plans)) {
        globalStudentLessonPlans = data.lesson_plans;
      }
    }
  } catch (err) {
    console.warn('API fetch lesson plans warning:', err);
  }

  if (!globalStudentLessonPlans || globalStudentLessonPlans.length === 0) {
    const storedLPs = JSON.parse(localStorage.getItem(getScopedStorageKey('academic_lesson_plans')) || '[]');
    globalStudentLessonPlans = storedLPs.filter(l => l.status === 'Published');
  }

  let filtered = globalStudentLessonPlans;
  if (currentSubject && currentSubject !== 'ALL') {
    filtered = filtered.filter(l => l.subject === currentSubject);
  }

  if (filtered.length === 0) {
    tableBody.innerHTML = `<tr><td colspan="7" class="text-center py-5 text-muted"><i class="bi bi-list-columns fs-2 d-block mb-2 text-secondary"></i>No published lesson plans available ${currentSubject !== 'ALL' ? `for <strong>${currentSubject}</strong>` : ''}. Check back soon!</td></tr>`;
    return;
  }

  tableBody.innerHTML = filtered.map(l => {
    const lpId = l.id || l.lessonPlanId;
    const dur = l.duration_minutes ? `${l.duration_minutes} Mins` : (l.duration || '50 Mins');
    const method = l.teaching_method || l.teachingMethod || 'Interactive Lecture';

    return `
      <tr>
        <td><strong class="text-dark">${l.title}</strong></td>
        <td><span class="badge bg-primary-subtle text-primary border">${l.subject}</span></td>
        <td><small class="text-muted">${l.unit || 'General'}</small></td>
        <td><small>${l.topic || 'General Topic'}</small></td>
        <td><small class="fw-semibold">${dur}</small></td>
        <td><small class="text-muted">${method}</small></td>
        <td>
          <button class="btn btn-academic-primary btn-sm py-0 px-2" onclick="openStudentLessonPlanViewer('${lpId}')">
            <i class="bi bi-file-earmark-text me-1"></i> View Plan
          </button>
        </td>
      </tr>
    `;
  }).join('');
}

function openStudentLessonPlanViewer(lpId) {
  let lp = (globalStudentLessonPlans || []).find(x => String(x.id) === String(lpId));
  if (!lp) {
    const storedLPs = JSON.parse(localStorage.getItem(getScopedStorageKey('academic_lesson_plans')) || '[]');
    lp = storedLPs.find(x => String(x.id) === String(lpId));
  }

  if (!lp) return;

  const modalEl = document.getElementById('studentLessonPlanViewerModal');
  if (!modalEl) return;

  const dur = lp.duration_minutes ? `${lp.duration_minutes} Mins` : (lp.duration || '50 Mins');
  const method = lp.teaching_method || lp.teachingMethod || 'Interactive Lecture';

  document.getElementById('studentLpTitle').innerText = lp.title;
  document.getElementById('studentLpMeta').innerText = `${lp.subject} • ${lp.unit || 'Unit 1'} • Duration: ${dur} • Method: ${method}`;

  const objectives = lp.objectives || `1. Understand fundamental theoretical concepts of ${lp.topic || lp.title}.\\n2. Analyze practical implementation paradigms and constraints.\\n3. Evaluate system trade-offs through real-world case studies.`;
  const prereqs = lp.prerequisites || `Foundational knowledge of ${lp.subject} prerequisite courses.`;
  const concepts = lp.concepts || `Core algorithmic definitions, lifecycle workflows, data structures, and state transitions.`;
  const activities = lp.activities || `Whiteboard walkthrough, live simulation code demonstration, peer discussion exercise.`;
  const outcomes = lp.outcomes || `Students will be able to formulate and solve complex domain problems in ${lp.subject}.`;

  document.getElementById('studentLpBody').innerHTML = `
    <div class="card card-academic p-3 mb-3">
      <h6 class="lesson-section-title"><i class="bi bi-bullseye me-1 text-primary"></i> Learning Objectives</h6>
      <p class="text-dark small mb-0" style="white-space: pre-line;">${objectives}</p>
    </div>

    <div class="row g-3 mb-3">
      <div class="col-md-6">
        <div class="card card-academic p-3 h-100">
          <h6 class="lesson-section-title"><i class="bi bi-bookmark-check me-1 text-info"></i> Prerequisites</h6>
          <p class="text-dark small mb-0">${prereqs}</p>
        </div>
      </div>
      <div class="col-md-6">
        <div class="card card-academic p-3 h-100">
          <h6 class="lesson-section-title"><i class="bi bi-lightbulb me-1 text-warning"></i> Key Concepts</h6>
          <p class="text-dark small mb-0">${concepts}</p>
        </div>
      </div>
    </div>

    <div class="card card-academic p-3 mb-3">
      <h6 class="lesson-section-title"><i class="bi bi-person-workspace me-1 text-success"></i> Teaching Activities & Methodology</h6>
      <p class="text-dark small mb-0">${activities}</p>
    </div>

    <div class="card card-academic p-3">
      <h6 class="lesson-section-title"><i class="bi bi-trophy me-1 text-danger"></i> Expected Learning Outcomes</h6>
      <p class="text-dark small mb-0">${outcomes}</p>
    </div>
  `;

  const bsModal = bootstrap.Modal.getOrCreateInstance(modalEl);
  bsModal.show();
}
"""

text = text[:idx_r_lp] + new_render_lp.strip() + "\n\n" + text[idx_r_lp_end:]

with open(app_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated presentations and lesson plans in app.js successfully!")
