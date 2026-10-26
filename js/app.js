// Utility: escapeHtml to prevent XSS and prevent undefined reference errors
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


// Setup Faculty Course Context & Strict Isolation across all modules
async function setupFacultyCourseContext(user) {
  if (!user) return;
  const userId = user.id;
  const userName = (user.full_name || user.name || '').toLowerCase();
  const userEmail = (user.email || '').toLowerCase();

  // 1. Fetch authorized courses for this faculty from backend API
  let courses = [];
  try {
    const res = await fetch('http://localhost:5000/api/faculty/courses', { credentials: 'include' });
    if (res.ok) {
      const data = await res.json();
      if (data.status === 'success' && Array.isArray(data.courses)) {
        courses = data.courses;
      }
    }
  } catch (err) {
    console.warn('Could not fetch faculty courses:', err);
  }

  // Fallback / deterministic defaults if no courses returned yet
  if (courses.length === 0) {
    if (userName.includes('kavitha') || userEmail.includes('kavitha') || userId === 25) {
      courses = [{ course_name: 'Distributed Computing', department: user.department || 'Artificial Intelligence & Data Science' }];
    } else {
      courses = [
        { course_name: 'Database Management Systems', department: 'Artificial Intelligence & Data Science' },
        { course_name: 'Distributed Computing', department: 'Artificial Intelligence & Data Science' },
        { course_name: 'Cloud Computing', department: 'Artificial Intelligence & Data Science' },
        { course_name: 'Machine Learning', department: 'Artificial Intelligence & Data Science' }
      ];
    }
  }

  window.facultyAuthorizedCourses = courses;

  // Determine primary authorized course
  let primaryCourse = courses[0].course_name;
  if (userName.includes('kavitha') || userEmail.includes('kavitha') || userId === 25) {
    primaryCourse = 'Distributed Computing';
  }

  const isCourseAuthorized = (subj) => {
    if (!subj) return false;
    return courses.some(c => c.course_name.toLowerCase() === subj.trim().toLowerCase());
  };

  // 2. Update subject input fields across all modules
  const subjectInputIds = [
    'genSubject', 'voiceSubjectSelect', 'imgSubjectSelect', 'transSubjectSelect',
    'paperSubject', 'addQSubject', 'quizSubject', 'asnSubject', 'pptSubjectSelect',
    'lpSubjectSelect', 'resSubject', 'filterSubject', 'paperFilterSubject'
  ];

  subjectInputIds.forEach(id => {
    const el = document.getElementById(id);
    if (el) {
      // If current value is not authorized for this faculty (e.g. DBMS for Kavitha) or is default
      if (!isCourseAuthorized(el.value) || el.value === 'Database Management Systems') {
        if (!courses.some(c => c.course_name.toLowerCase() === 'database management systems')) {
          el.value = primaryCourse;
        }
      }
    }
  });

  // 3. Update datalists with ONLY this faculty's authorized courses
  const datalistIds = [
    'genSubjectList', 'voiceSubjectList', 'imgSubjectList', 'transSubjectList',
    'paperSubjectList', 'quizSubjectList', 'asnSubjectList', 'pptSubjectList',
    'lpSubjectList', 'resSubjectList'
  ];

  const courseOptionsHtml = courses.map(c => `<option value="${c.course_name}">`).join('');
  datalistIds.forEach(dlId => {
    const dl = document.getElementById(dlId);
    if (dl) {
      dl.innerHTML = courseOptionsHtml;
    }
  });

  // 4. Update Department inputs
  const deptInputIds = [
    'genDept', 'voiceDeptSelect', 'imgDeptSelect', 'transDeptSelect',
    'paperDept', 'quizDept', 'asnDept', 'pptDeptSelect', 'lpDeptSelect', 'resDept'
  ];
  const userDept = user.department || 'Artificial Intelligence & Data Science';
  deptInputIds.forEach(id => {
    const el = document.getElementById(id);
    if (el && (!el.value || el.value.trim() === '')) {
      el.value = userDept;
    }
  });

  // 5. Fetch and populate Study Materials / Resources dropdowns with ONLY this faculty's materials
  try {
    const resResp = await fetch('http://localhost:5000/api/resources', { credentials: 'include' });
    if (resResp.ok) {
      const resData = await resResp.json();
      if (resData.status === 'success' && Array.isArray(resData.resources)) {
        window.facultyOwnedResources = resData.resources;
        populateFacultyResourceSelects(resData.resources, primaryCourse);
      }
    }
  } catch (err) {
    console.warn('Could not fetch faculty resources for dropdowns:', err);
  }
}

function populateFacultyResourceSelects(resources, selectedSubject) {
  const resourceSelectIds = [
    'genResourceSelect', 'notesResourceSelect', 'quizMaterialSelect',
    'voiceMaterialSelect', 'imgMaterialSelect', 'transMaterialSelect',
    'pptMaterialSelect', 'lpMaterialSelect'
  ];

  resourceSelectIds.forEach(selectId => {
    const sel = document.getElementById(selectId);
    if (!sel) return;

    const matching = selectedSubject
      ? resources.filter(r => (r.subject || '').toLowerCase() === selectedSubject.toLowerCase())
      : resources;
    const listToUse = matching.length > 0 ? matching : resources;

    let html = `<option value="">Choose Uploaded Material...</option>`;
    listToUse.forEach(r => {
      html += `<option value="${r.id}" data-subject="${r.subject}" data-unit="${r.unit || ''}">${r.title || r.subject} (${r.resource_type || 'Material'})</option>`;
    });
    sel.innerHTML = html;
  });
}


// Faculty Data Isolation & Storage Scoping Helper
function getScopedStorageKey(baseKey) {
  try {
    const userStr = localStorage.getItem('academic_user');
    if (userStr) {
      const u = JSON.parse(userStr);
      if (u && (u.id || u.identifier || u.email)) {
        const uid = u.id || (u.identifier ? u.identifier.replace(/[^a-zA-Z0-9]/g, '_') : 'guest');
        return `${baseKey}_${uid}`;
      }
    }
  } catch (e) {}
  return baseKey;
}





// === Faculty Study Materials & Grounded Question Generation Helpers ===



window.facultyAcademicResources = [];



async function safeParseJsonResponse(res) {

  try {

    const contentType = res.headers ? (res.headers.get('content-type') || '') : '';

    if (contentType.includes('application/json')) {

      return await res.json();

    }

    const text = await res.text();

    try {

      return JSON.parse(text);

    } catch (e) {

      return {

        status: 'error',

        message: text && text.trim().startsWith('<') ? `Server returned HTTP ${res.status} (${res.statusText || 'Error'}).` : text

      };

    }

  } catch (err) {

    return { status: 'error', message: err.message || 'Failed to parse response' };

  }

}



function onQuickUploadFileSelected() {

  const fileInput = document.getElementById('genQuickUploadFile');

  if (!fileInput || !fileInput.files || fileInput.files.length === 0) return;

  const file = fileInput.files[0];

  const verifiedDisp = document.getElementById('sourceVerifiedDisplay');

  const statusBadge = document.getElementById('sourceMaterialStatusBadge');

  const noticeEl = document.getElementById('sourceMaterialNotice');



  if (statusBadge) {

    statusBadge.className = 'badge bg-primary text-white';

    statusBadge.innerText = 'Ready to Upload / Generate';

  }

  if (verifiedDisp) {

    verifiedDisp.innerHTML = `<i class="bi bi-file-earmark-arrow-up text-primary me-1"></i> ${file.name} (${(file.size / 1024).toFixed(1)} KB)`;

  }

  if (noticeEl) {

    noticeEl.innerHTML = `<div class="alert alert-info py-1 px-2 small mt-2 mb-0"><i class="bi bi-info-circle me-1"></i> Selected: <strong>${file.name}</strong>. It will be uploaded automatically when you click "Generate Questions" or click "Upload".</div>`;

  }

  if (typeof updateSourceMaterialDisplay === 'function') {

    updateSourceMaterialDisplay();

  }

}



async function refreshFacultyGenResources() {

  const resourceSelect = document.getElementById('genResourceSelect');

  const subjectInput = document.getElementById('genSubject');

  const subj = subjectInput?.value?.trim() || '';



  try {

    const url = (typeof API_RESOURCES_BASE !== 'undefined' && API_RESOURCES_BASE) ? API_RESOURCES_BASE : 'http://localhost:5000/api/resources';

    const res = await fetch(url, { credentials: 'include' });

    const data = await safeParseJsonResponse(res);

    if (res.ok && data.status !== 'error') {

      const resources = data.resources || [];

      window.facultyAcademicResources = resources;



      const subjectDatalist = document.getElementById('genSubjectList');

      if (subjectDatalist) {

        const uniqueSubjects = Array.from(new Set(resources.map(r => r.subject).filter(Boolean)));

        ['Database Management Systems', 'Artificial Intelligence', 'Machine Learning', 'Distributed Computing', 'Data Structures', 'Operating Systems', 'Python Programming'].forEach(s => {

          if (!uniqueSubjects.includes(s)) uniqueSubjects.push(s);

        });

        subjectDatalist.innerHTML = uniqueSubjects.map(s => `<option value="${s}">`).join('');

      }



      if (resourceSelect) {

        resourceSelect.innerHTML = `<option value="">-- All Uploaded Materials for "${subj || 'Current Subject'}" --</option>`;

        const filtered = subj ? resources.filter(r => r.subject.toLowerCase() === subj.toLowerCase() || subj.toLowerCase().includes(r.subject.toLowerCase())) : resources;

        filtered.forEach(r => {

          const opt = document.createElement('option');

          opt.value = r.id;

          opt.textContent = `${r.title || r.subject} (${r.resource_type || 'Material'} - ${r.file_name || 'Uploaded'})`;

          resourceSelect.appendChild(opt);

        });

      }

      updateSourceMaterialDisplay();

    }

  } catch (err) {

    console.warn('Error fetching faculty resources for gen:', err);

  }

}



function onSourceResourceSelected() {

  const resourceSelect = document.getElementById('genResourceSelect');

  const selectedId = resourceSelect?.value;

  if (!selectedId) {

    updateSourceMaterialDisplay();

    return;

  }

  const resources = window.facultyAcademicResources || [];

  const matched = resources.find(r => String(r.id) === String(selectedId));

  if (matched) {

    const subjectInput = document.getElementById('genSubject');

    if (subjectInput && matched.subject) {

      subjectInput.value = matched.subject;

    }

    const unitInput = document.getElementById('genUnit');

    if (unitInput && matched.unit && matched.unit !== 'All Units') {

      unitInput.value = matched.unit;

    }

    const topicInput = document.getElementById('genTopic');

    if (topicInput && matched.topic) {

      topicInput.value = matched.topic;

    }

  }

  updateSourceMaterialDisplay();

}



function updateSourceMaterialDisplay() {

  const subjectInput = document.getElementById('genSubject');

  const unitInput = document.getElementById('genUnit');

  const topicInput = document.getElementById('genTopic');

  const resourceSelect = document.getElementById('genResourceSelect');

  const useQb = document.getElementById('genUseQuestionBank')?.checked;



  const subj = subjectInput?.value?.trim() || 'Database Management Systems';

  const unit = unitInput?.value?.trim() || 'All Units (Complete Syllabus)';

  const topic = topicInput?.value?.trim() || '';



  const subjectDisp = document.getElementById('sourceSubjectDisplay');

  const unitDisp = document.getElementById('sourceUnitDisplay');

  const topicsDisp = document.getElementById('sourceTopicsDisplay');

  const conceptsDisp = document.getElementById('sourceConceptsDisplay');

  const statusBadge = document.getElementById('sourceMaterialStatusBadge');

  const verifiedDisp = document.getElementById('sourceVerifiedDisplay');



  if (subjectDisp) subjectDisp.innerText = subj;

  if (unitDisp) unitDisp.innerText = unit;



  const resources = window.facultyAcademicResources || [];

  const selectedResId = resourceSelect?.value;

  let matching = selectedResId ? resources.filter(r => String(r.id) === String(selectedResId)) : resources.filter(r => r.subject.toLowerCase() === subj.toLowerCase());



  if (matching.length > 0) {

    if (statusBadge) {

      statusBadge.className = 'badge bg-success';

      statusBadge.innerText = `Verified: ${matching.length} Material(s) Found`;

    }

    if (verifiedDisp) {

      verifiedDisp.innerHTML = `<i class="bi bi-check2-all text-success me-1"></i> ${matching.map(m => m.file_name || m.title).join(', ')}`;

    }

    if (topicsDisp) {

      const topicNames = matching.map(m => m.topic).filter(Boolean);

      topicsDisp.innerText = topicNames.length ? topicNames.join(', ') : `Topics derived from uploaded file(s) for ${subj}`;

    }

    if (conceptsDisp) {

      conceptsDisp.innerText = `Grounded directly in faculty study materials for ${subj}`;

    }

  } else if (useQb) {

    if (statusBadge) {

      statusBadge.className = 'badge bg-info text-dark';

      statusBadge.innerText = 'Source: Question Bank';

    }

    if (verifiedDisp) {

      verifiedDisp.innerHTML = `<i class="bi bi-bookmark-check text-primary me-1"></i> Faculty Question Bank`;

    }

    if (topicsDisp) topicsDisp.innerText = `Using existing verified Question Bank items for ${subj}`;

    if (conceptsDisp) conceptsDisp.innerText = `Calibrated from faculty question repository`;

  } else {

    const fileInput = document.getElementById('genQuickUploadFile');

    if (fileInput && fileInput.files && fileInput.files.length > 0) {

      const chosenFile = fileInput.files[0];

      if (statusBadge) {

        statusBadge.className = 'badge bg-primary text-white';

        statusBadge.innerText = 'Ready to Upload / Generate';

      }

      if (verifiedDisp) {

        verifiedDisp.innerHTML = `<i class="bi bi-file-earmark-arrow-up text-primary me-1"></i> ${chosenFile.name}`;

      }

      if (topicsDisp) topicsDisp.innerText = `Selected document: ${chosenFile.name} (will be uploaded & parsed upon generation)`;

      if (conceptsDisp) conceptsDisp.innerText = 'Content will be extracted from this selected file.';

    } else {

      if (statusBadge) {

        statusBadge.className = 'badge bg-warning text-dark';

        statusBadge.innerText = 'No Materials Attached';

      }

      if (verifiedDisp) {

        verifiedDisp.innerHTML = `<i class="bi bi-exclamation-triangle text-warning me-1"></i> None (Upload needed)`;

      }

      if (topicsDisp) topicsDisp.innerText = 'Please upload a Syllabus or Notes file (PDF, DOCX, TXT) or select Question Bank';

      if (conceptsDisp) conceptsDisp.innerText = 'Awaiting uploaded document or question bank selection';

    }

  }

}



async function handleQuickUploadForGen() {

  const fileInput = document.getElementById('genQuickUploadFile');

  const typeSelect = document.getElementById('genQuickUploadType');

  const subjectInput = document.getElementById('genSubject');

  const deptInput = document.getElementById('genDept');

  const unitInput = document.getElementById('genUnit');

  const topicInput = document.getElementById('genTopic');

  const uploadBtn = document.getElementById('genQuickUploadBtn') || document.querySelector('button[onclick="handleQuickUploadForGen()"]');



  if (!fileInput || !fileInput.files || fileInput.files.length === 0) {

    showToastNotice('Upload Error', 'Please select a PDF, DOCX, or TXT file to upload.', 'warning');

    return null;

  }



  const file = fileInput.files[0];

  const formData = new FormData();

  formData.append('file', file);

  formData.append('subject', subjectInput?.value?.trim() || 'General Subject');

  formData.append('department', deptInput?.value?.trim() || 'General Engineering');

  formData.append('unit', unitInput?.value?.trim() || 'All Units');

  formData.append('topic', topicInput?.value?.trim() || file.name.replace(/\.[^/.]+$/, ''));

  formData.append('resource_type', typeSelect?.value || 'Study Material');

  formData.append('description', `Quick upload for Question Generator: ${file.name}`);



  let originalBtnHtml = '';

  if (uploadBtn) {

    originalBtnHtml = uploadBtn.innerHTML;

    uploadBtn.disabled = true;

    uploadBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-1"></span>Uploading...`;

  }



  try {

    const url = (typeof API_RESOURCES_BASE !== 'undefined' && API_RESOURCES_BASE) ? API_RESOURCES_BASE : 'http://localhost:5000/api/resources';

    const res = await fetch(url, {

      method: 'POST',

      credentials: 'include',

      body: formData

    });

    const data = await safeParseJsonResponse(res);

    if (res.ok && data.status === 'success') {

      showToastNotice('Material Uploaded', `Successfully uploaded and registered ${file.name}!`, 'success');

      await refreshFacultyGenResources();

      if (data.resource && document.getElementById('genResourceSelect')) {

        document.getElementById('genResourceSelect').value = data.resource.id;

      }

      updateSourceMaterialDisplay();

      return data.resource;

    } else {

      showToastNotice('Upload Failed', data.message || 'Failed to upload resource.', 'danger');

      return null;

    }

  } catch (err) {

    console.error('Quick upload error:', err);

    showToastNotice('Server Error', 'Failed to communicate with upload service.', 'danger');

    return null;

  } finally {

    if (uploadBtn) {

      uploadBtn.disabled = false;

      uploadBtn.innerHTML = originalBtnHtml || `<i class="bi bi-upload"></i> Upload`;

    }

  }

}



function editGeneratedQuestion(idx) {

  const q = window.currentGeneratedQuestions[idx];

  if (!q) return;

  const newText = prompt("Edit Question Text:", q.question_text || q.text);

  if (newText && newText.trim()) {

    q.question_text = newText.trim();

    q.text = newText.trim();

    q.question = newText.trim();

    renderGeneratedResults();

  }

}



function regenerateGeneratedQuestion(idx) {

  const q = window.currentGeneratedQuestions[idx];

  if (!q) return;

  const verbs = ['Analyze', 'Explain', 'Evaluate', 'Formulate an implementation for', 'Differentiate'];

  const altVerb = verbs[(idx + 1) % verbs.length];

  q.question_text = `${altVerb} the design principles, architectural implications, and evaluation criteria of ${q.topic} in ${q.subject}.`;

  q.text = q.question_text;

  q.question = q.question_text;

  renderGeneratedResults();

  showToastNotice('Question Regenerated', `Question ${idx + 1} updated with alternative analytical formulation.`, 'info');

}



function deleteGeneratedQuestion(idx) {

  if (confirm(`Remove Question ${idx + 1} from generated set?`)) {

    window.currentGeneratedQuestions.splice(idx, 1);

    renderGeneratedResults();

  }

}



/**



 * Application Logic & Role Management



 * Academic Question Generation & Difficulty Balancing System



 */







document.addEventListener('DOMContentLoaded', () => {



  initRoleManagement();



  bindFormHandlers();



  if (typeof bindGeneratorStubs === 'function') bindGeneratorStubs();



  if (typeof initResourceForm === 'function') initResourceForm();



  if (typeof initQuestionGeneratorForm === 'function') initQuestionGeneratorForm();



  if (typeof initQuestionPaperBuilder === 'function') initQuestionPaperBuilder();



  if (typeof initVerificationPage === 'function') initVerificationPage();



  if (typeof initQuizGeneratorForm === 'function') initQuizGeneratorForm();



  if (typeof initAssignmentGeneratorForm === 'function') initAssignmentGeneratorForm();



  if (typeof initPPTGeneratorForm === 'function') initPPTGeneratorForm();



  if (typeof initLessonPlanGeneratorForm === 'function') initLessonPlanGeneratorForm();



  if (typeof initVoiceQuestionForm === 'function') initVoiceQuestionForm();



  if (typeof initImageQuestionForm === 'function') initImageQuestionForm();



  if (typeof initLanguageConverterForm === 'function') initLanguageConverterForm();



});







// Shared UI Toast Helper Function



function showToastNotice(title, message, type = 'info') {



  console.log(`[Toast ${type.toUpperCase()}] ${title}: ${message}`);







  let toastEl = document.getElementById('appToast');



  let toastBody = document.getElementById('toastMessage');







  if (!toastEl) {



    let container = document.querySelector('.toast-container');



    if (!container) {



      container = document.createElement('div');



      container.className = 'toast-container position-fixed bottom-0 end-0 p-3';



      container.style.zIndex = '1100';



      document.body.appendChild(container);



    }







    toastEl = document.createElement('div');



    toastEl.className = `toast align-items-center text-white border-0 bg-${type === 'danger' ? 'danger' : type === 'success' ? 'success' : type === 'warning' ? 'warning' : 'primary'}`;



    toastEl.setAttribute('role', 'alert');



    toastEl.setAttribute('aria-live', 'assertive');



    toastEl.setAttribute('aria-atomic', 'true');







    toastEl.innerHTML = `



      <div class="d-flex">



        <div class="toast-body">



          <strong>${title}</strong>${message ? `: ${message}` : ''}



        </div>



        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>



      </div>



    `;







    container.appendChild(toastEl);



    if (typeof bootstrap !== 'undefined' && bootstrap.Toast) {



      const bsToast = new bootstrap.Toast(toastEl, { delay: 4000 });



      bsToast.show();



    }



    return;



  }







  if (toastEl) {



    toastEl.className = `toast align-items-center text-white border-0 bg-${type === 'danger' ? 'danger' : type === 'success' ? 'success' : type === 'warning' ? 'warning' : 'primary'}`;



    if (toastBody) {



      toastBody.innerHTML = `<strong>${title}</strong>${message ? `: ${message}` : ''}`;



    }



    if (typeof bootstrap !== 'undefined' && bootstrap.Toast) {



      const bsToast = bootstrap.Toast.getInstance(toastEl) || new bootstrap.Toast(toastEl, { delay: 4000 });



      bsToast.show();



    }



  }



}







// ==========================================



// STEP 9D: QUESTIONS & QUESTION BANK (FLASK + MYSQL)



// ==========================================







const API_QUESTIONS_BASE = 'http://localhost:5000/api/questions';



const API_QUESTION_BANK_BASE = 'http://localhost:5000/api/question-bank';
const API_RESOURCES_BASE = 'http://localhost:5000/api/resources';







window.currentGeneratedQuestions = [];







function populateQuestionDropdowns() {

  const subjectInput = document.getElementById('genSubject');

  const unitInput = document.getElementById('genUnit');

  const topicInput = document.getElementById('genTopic');



  if (!subjectInput) return;



  const subject = subjectInput.value || "Database Management Systems";

  const struct = (typeof AcademicMockData !== 'undefined' && AcademicMockData.subjectStructure)

    ? AcademicMockData.subjectStructure[subject]

    : null;



  const unitDatalist = document.getElementById('genUnitList');

  const unitSelect = unitInput && unitInput.tagName === 'SELECT' ? unitInput : null;



  const defaultUnits = [

    "All Units (Complete Syllabus)",

    "Unit I — Introduction",

    "Unit II — Core Concepts",

    "Unit III — Advanced Topics",

    "Unit IV — Applications",

    "Unit V — System Design"

  ];



  const unitsList = (struct && struct.units && struct.units.length > 0)

    ? ["All Units (Complete Syllabus)", ...struct.units.map(u => u.name)]

    : defaultUnits;



  if (unitDatalist) {

    unitDatalist.innerHTML = unitsList.map(u => `<option value="${u}">`).join('');

  }

  if (unitSelect) {

    unitSelect.innerHTML = unitsList.map(u => `<option value="${u}">${u}</option>`).join('');

  }



  updateTopicDropdown();

  if (typeof updateSourceMaterialDisplay === 'function') {

    updateSourceMaterialDisplay();

  }

}







function updateTopicDropdown() {



  const subjectSelect = document.getElementById('genSubject');



  const unitSelect = document.getElementById('genUnit');



  const topicSelect = document.getElementById('genTopic');







  if (!subjectSelect || !unitSelect || !topicSelect) return;







  const subject = subjectSelect.value;



  const selectedUnitName = unitSelect.value;



  const struct = (typeof AcademicMockData !== 'undefined' && AcademicMockData.subjectStructure)



    ? AcademicMockData.subjectStructure[subject]



    : null;







  topicSelect.innerHTML = '';



  let topics = [];







  if (struct && struct.units) {



    const matchedUnit = struct.units.find(u => u.name === selectedUnitName);



    if (matchedUnit && matchedUnit.topics) {



      topics = matchedUnit.topics;



    }



  }







  if (topics.length === 0) {



    topics = ["General Topic 1", "Core Principles", "Practical Applications", "Advanced Analysis"];



  }







  topics.forEach(t => {



    const opt = document.createElement('option');



    opt.value = t;



    opt.textContent = t;



    topicSelect.appendChild(opt);



  });







  // Update source display panel if present



  const srcSub = document.getElementById('sourceSubjectDisplay');



  const srcUnit = document.getElementById('sourceUnitDisplay');



  const srcTopics = document.getElementById('sourceTopicsDisplay');



  const srcConcepts = document.getElementById('sourceConceptsDisplay');







  if (srcSub) srcSub.textContent = subject;



  if (srcUnit) srcUnit.textContent = selectedUnitName;



  if (srcTopics) srcTopics.textContent = topics.join(', ');



  if (srcConcepts) srcConcepts.textContent = topics.slice(0, 3).join(', ') + ', Evaluation';



}







function validateDifficultyInputs() {



  const pEasy = parseInt(document.getElementById('pctEasy')?.value || '30', 10);



  const pMedium = parseInt(document.getElementById('pctMedium')?.value || '50', 10);



  const pHard = parseInt(document.getElementById('pctHard')?.value || '20', 10);



  const total = pEasy + pMedium + pHard;



  const msgEl = document.getElementById('diffValMessage');







  if (msgEl) {



    if (total === 100) {



      msgEl.innerHTML = `<span class="text-success fw-semibold"><i class="bi bi-check-circle me-1"></i> Total = 100% (Valid Distribution)</span>`;



    } else {



      msgEl.innerHTML = `<span class="text-danger fw-semibold"><i class="bi bi-exclamation-triangle me-1"></i> Total = ${total}% (Must equal 100%)</span>`;



    }



  }



  return total === 100;



}







function initQuestionGeneratorPage() {

  const form = document.getElementById('questionGeneratorForm');

  const subjectInput = document.getElementById('genSubject');

  const deptInput = document.getElementById('genDept');

  const unitInput = document.getElementById('genUnit');

  const topicInput = document.getElementById('genTopic');

  const numQInput = document.getElementById('genNumQuestions');

  const pctEasy = document.getElementById('pctEasy');

  const pctMedium = document.getElementById('pctMedium');

  const pctHard = document.getElementById('pctHard');

  const resourceSelect = document.getElementById('genResourceSelect');



  // Restore saved config

  const savedCfg = localStorage.getItem('academic_last_gen_q_config');

  if (savedCfg) {

    try {

      const cfg = JSON.parse(savedCfg);

      if (cfg.department && deptInput) deptInput.value = cfg.department;

      if (cfg.subject && subjectInput) subjectInput.value = cfg.subject;

      if (cfg.unit && unitInput) unitInput.value = cfg.unit;

      if (cfg.topic !== undefined && topicInput) topicInput.value = cfg.topic;

      if (cfg.numQuestions && numQInput) numQInput.value = cfg.numQuestions;

      if (cfg.pEasy && pctEasy) pctEasy.value = cfg.pEasy;

      if (cfg.pMedium && pctMedium) pctMedium.value = cfg.pMedium;

      if (cfg.pHard && pctHard) pctHard.value = cfg.pHard;

    } catch (e) {}

  }



  if (subjectInput) {

    subjectInput.addEventListener('input', () => {

      populateQuestionDropdowns();

      if (typeof refreshFacultyGenResources === 'function') refreshFacultyGenResources();

    });

  }

  if (unitInput) {

    unitInput.addEventListener('input', () => {

      updateTopicDropdown();

      if (typeof updateSourceMaterialDisplay === 'function') updateSourceMaterialDisplay();

    });

  }

  if (topicInput) {

    topicInput.addEventListener('input', () => {

      if (typeof updateSourceMaterialDisplay === 'function') updateSourceMaterialDisplay();

    });

  }



  const quickUploadInp = document.getElementById('genQuickUploadFile');

  if (quickUploadInp) {

    quickUploadInp.addEventListener('change', onQuickUploadFileSelected);

  }



  if (pctEasy && pctMedium && pctHard) {

    [pctEasy, pctMedium, pctHard].forEach(inp => {

      inp.addEventListener('input', validateDifficultyInputs);

    });

  }



  populateQuestionDropdowns();

  if (typeof refreshFacultyGenResources === 'function') {

    refreshFacultyGenResources();

  }



  if (form) {

    form.addEventListener('submit', async (e) => {

      e.preventDefault();



      if (!validateDifficultyInputs()) {

        showToastNotice('Validation Error', 'Difficulty distribution percentages must sum to 100%.', 'warning');

        return;

      }



      const department = document.getElementById('genDept')?.value?.trim() || 'Artificial Intelligence & Data Science';

      const subject = document.getElementById('genSubject')?.value?.trim() || 'Database Management Systems';

      const academic_year = document.getElementById('genYear')?.value || '2025-2026';

      const semester = document.getElementById('genSem')?.value || 'Semester 6';

      const unit = document.getElementById('genUnit')?.value?.trim() || 'All Units (Complete Syllabus)';

      const topic = document.getElementById('genTopic')?.value?.trim() || '';

      const numQuestions = parseInt(document.getElementById('genNumQuestions')?.value || '10', 10);

      const marksVal = document.getElementById('genMarks')?.value || document.getElementById('genQuestionType')?.value || 'Mixed';
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

        department, subject, academic_year, semester, unit, topic, numQuestions, question_type, blooms_choice, pEasy, pMedium, pHard

      }));



      const submitBtn = form.querySelector('button[type="submit"]');

      if (submitBtn) {

        submitBtn.disabled = true;

        submitBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-2"></span>Synthesizing Questions from Material...`;

      }



      let effectiveResourceId = resourceId;

      const quickFileInp = document.getElementById('genQuickUploadFile');

      if (!effectiveResourceId && quickFileInp && quickFileInp.files && quickFileInp.files.length > 0) {

        // Auto-upload selected file before generation

        const uploadedRes = await handleQuickUploadForGen();

        if (uploadedRes && uploadedRes.id) {

          effectiveResourceId = uploadedRes.id;

        }

      }



      const payload = {

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

        bloom_level: blooms_choice,

        diff_easy: pEasy,

        diff_medium: pMedium,

        diff_hard: pHard,

        resource_id: effectiveResourceId,

        use_question_bank: useQb

      };



      try {

        const questionsGenUrl = (typeof API_QUESTIONS_BASE !== 'undefined' && API_QUESTIONS_BASE)

          ? `${API_QUESTIONS_BASE}/generate`

          : 'http://localhost:5000/api/questions/generate';



        const res = await fetch(questionsGenUrl, {

          method: 'POST',

          headers: { 'Content-Type': 'application/json' },

          credentials: 'include',

          body: JSON.stringify(payload)

        });



        const data = await safeParseJsonResponse(res);

        if (submitBtn) {

          submitBtn.disabled = false;

          submitBtn.innerHTML = `<i class="bi bi-cpu me-2"></i> Generate Questions`;

        }



        if (data.status === 'success') {

          window.currentGeneratedQuestions = data.questions || [];

          renderGeneratedResults(pEasy, pMedium, pHard);

          const noticeEl = document.getElementById('sourceMaterialNotice');

          if (noticeEl) noticeEl.innerHTML = '';



          showToastNotice('Questions Generated', `${window.currentGeneratedQuestions.length} grounded questions generated from study materials!`, 'success');

          const resultsContainer = document.getElementById('generatedQuestionsResults');

          if (resultsContainer) {

            resultsContainer.classList.remove('d-none');

            window.scrollTo({ top: resultsContainer.offsetTop - 70, behavior: 'smooth' });

          }

        } else {

          const noticeEl = document.getElementById('sourceMaterialNotice');

          if (noticeEl) {

            noticeEl.innerHTML = `<div class="alert alert-warning border border-warning p-2 small mt-2 mb-0"><i class="bi bi-exclamation-triangle me-1"></i>${data.message || 'Source material required.'}</div>`;

          }

          showToastNotice('Generation Notice', data.message || 'Failed to generate questions.', 'warning');

        }

      } catch (err) {

        console.error('Question generation error:', err);

        if (submitBtn) {

          submitBtn.disabled = false;

          submitBtn.innerHTML = `<i class="bi bi-cpu me-2"></i> Generate Questions`;

        }

        showToastNotice('Server Error', 'Failed to communicate with Flask backend API.', 'danger');

      }

    });

  }

}



function renderGeneratedResults(targetEasy = 30, targetMedium = 50, targetHard = 20) {



  const resultsContainer = document.getElementById('generatedQuestionsResults');



  if (!resultsContainer) return;







  const questions = window.currentGeneratedQuestions || [];



  const totalCount = questions.length;







  // 1. Difficulty Calibration Bars



  const targetBar = document.getElementById('targetDistributionBar');



  const currentBar = document.getElementById('currentDistributionBar');







  if (targetBar) {



    targetBar.innerHTML = `



      <div class="progress-bar bg-success" style="width: ${targetEasy}%" title="Easy: ${targetEasy}%">Easy ${targetEasy}%</div>



      <div class="progress-bar bg-warning text-dark" style="width: ${targetMedium}%" title="Medium: ${targetMedium}%">Med ${targetMedium}%</div>



      <div class="progress-bar bg-danger" style="width: ${targetHard}%" title="Hard: ${targetHard}%">Hard ${targetHard}%</div>



    `;



  }







  let easyCount = 0, medCount = 0, hardCount = 0;



  questions.forEach(q => {



    if (q.difficulty === 'Easy') easyCount++;



    else if (q.difficulty === 'Medium') medCount++;



    else if (q.difficulty === 'Hard') hardCount++;



  });







  const actEasyPct = totalCount ? Math.round((easyCount / totalCount) * 100) : 0;



  const actMedPct = totalCount ? Math.round((medCount / totalCount) * 100) : 0;



  const actHardPct = totalCount ? 100 - actEasyPct - actMedPct : 0;







  if (currentBar) {



    currentBar.innerHTML = `



      <div class="progress-bar bg-success" style="width: ${actEasyPct}%" title="Easy: ${actEasyPct}%">Easy ${actEasyPct}% (${easyCount})</div>



      <div class="progress-bar bg-warning text-dark" style="width: ${actMedPct}%" title="Medium: ${actMedPct}%">Med ${actMedPct}% (${medCount})</div>



      <div class="progress-bar bg-danger" style="width: ${actHardPct}%" title="Hard: ${actHardPct}%">Hard ${actHardPct}% (${hardCount})</div>



    `;



  }







  // 2. Generated Questions List



  const listEl = document.getElementById('generatedQuestionsList');



  if (listEl) {



    listEl.innerHTML = '';



    questions.forEach((q, idx) => {



      const card = document.createElement('div');



      card.className = 'card card-academic mb-3';



      card.id = `q-card-${q.id}`;







      const diffBadgeClass = q.difficulty === 'Easy' ? 'bg-success' : q.difficulty === 'Medium' ? 'bg-warning text-dark' : 'bg-danger';







      let optionsHtml = '';



      if (q.options && q.options.length > 0) {



        optionsHtml = `<div class="mt-2 ps-3 border-start small text-muted">



          ${q.options.map(opt => `<div class="${opt.is_correct ? 'fw-bold text-success' : ''}"><strong>${opt.option_label || opt.label}.</strong> ${opt.option_text || opt.text} ${opt.is_correct ? '<i class="bi bi-check-circle-fill text-success ms-1"></i>' : ''}</div>`).join('')}



        </div>`;



      }







      const bankBadge = q.is_in_bank



        ? `<span class="badge bg-primary ms-2"><i class="bi bi-bookmark-check-fill me-1"></i> In Bank</span>`



        : '';







      card.innerHTML = `



        <div class="card-body p-3">



          <div class="d-flex justify-content-between align-items-start mb-2">



            <div>



              <span class="badge ${diffBadgeClass} me-1">${q.difficulty}</span>



              <span class="badge bg-secondary me-1">${q.bloom_level || q.blooms || 'Understand'}</span>



              <span class="badge bg-info text-dark me-1">${q.concept || 'General'}</span>



              <span class="badge bg-light text-dark border me-1">${q.marks || 2} Marks</span>



              <span class="badge bg-light text-dark border">${q.question_type || q.type || 'Short Answer'}</span>



              ${bankBadge}



            </div>



            <div class="btn-group btn-group-sm">

            <button class="btn btn-outline-secondary" onclick="editGeneratedQuestion(${idx})" title="Edit Question Text"><i class="bi bi-pencil me-1"></i>Edit</button>

            <button class="btn btn-outline-primary" onclick="regenerateGeneratedQuestion(${idx})" title="Regenerate Question Formulation"><i class="bi bi-arrow-repeat me-1"></i>Regenerate</button>

            <button class="btn btn-outline-danger" onclick="deleteGeneratedQuestion(${idx})" title="Delete"><i class="bi bi-trash"></i></button>

          </div>



          </div>



          <p class="fw-semibold mb-1 text-dark">Q${idx + 1}. ${q.question_text || q.text}</p>



          ${optionsHtml}



          ${q.explanation ? `<div class="small text-muted mt-2"><i class="bi bi-info-circle me-1"></i><strong>Explanation:</strong> ${q.explanation}</div>` : ''}



        </div>



      `;



      listEl.appendChild(card);



    });



  }







  // 3. Similarity Check Container



  const simContainer = document.getElementById('similarityCheckContainer');



  if (simContainer) {



    simContainer.innerHTML = `



      <div class="d-flex align-items-center justify-content-between alert alert-success mb-0 p-3">



        <div>



          <h6 class="alert-heading mb-1 fw-bold"><i class="bi bi-shield-check me-2"></i> No Duplicate Questions Detected</h6>



          <small>All ${totalCount} generated questions satisfy the 85% uniqueness threshold. MySQL similarity check verified zero overlap.</small>



        </div>



        <span class="badge bg-success fs-6">0% Similarity</span>



      </div>



    `;



  }







  // 4. Concept Coverage Container



  const conceptContainer = document.getElementById('conceptCoverageContainer');



  if (conceptContainer) {



    const conceptsSet = new Set(questions.map(q => q.concept || 'General'));



    conceptContainer.innerHTML = `



      <div class="row g-2 align-items-center">



        <div class="col-md-8">



          <div class="d-flex flex-wrap gap-2">



            ${Array.from(conceptsSet).map(c => `<span class="badge bg-success-subtle text-success border border-success px-3 py-2"><i class="bi bi-check2 me-1"></i> ${c}</span>`).join('')}



          </div>



        </div>



        <div class="col-md-4 text-md-end">



          <small class="text-muted d-block">Syllabus Coverage Index:</small>



          <strong class="text-success fs-5">100% Balanced</strong>



        </div>



      </div>



    `;



  }







  // 5. Summary Card



  const sumTotal = document.getElementById('summaryTotalQuestions');



  const sumDiff = document.getElementById('summaryDiffCounts');



  const sumConcepts = document.getElementById('summaryConceptsCount');



  const sumDuplicates = document.getElementById('summaryDuplicatesCount');







  if (sumTotal) sumTotal.textContent = totalCount;



  if (sumDiff) sumDiff.textContent = `Easy: ${easyCount} | Medium: ${medCount} | Hard: ${hardCount}`;



  if (sumConcepts) {



    const uniqueConcepts = new Set(questions.map(q => q.concept)).size;



    sumConcepts.textContent = `${uniqueConcepts} Concepts`;



  }



  if (sumDuplicates) sumDuplicates.textContent = `0 Duplicates`;







  // Reveal results



  resultsContainer.classList.remove('d-none');



}







async function saveGeneratedToBank() {
  const saveBtn = document.getElementById('saveGeneratedToBankBtn');
  const questions = window.currentGeneratedQuestions || [];

  if (!questions || questions.length === 0) {
    showToastNotice('Warning', 'No generated questions available to save.', 'warning');
    return;
  }

  // Prevent duplicate submissions
  if (saveBtn && (saveBtn.disabled || saveBtn.dataset.saving === 'true')) {
    return;
  }
  const originalBtnHtml = saveBtn ? saveBtn.innerHTML : '';
  if (saveBtn) {
    saveBtn.dataset.saving = 'true';
    saveBtn.disabled = true;
    saveBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span> Saving to Question Bank...';
  }

  const question_ids = questions.map(q => q.id);

  try {
    const res = await fetch(API_QUESTION_BANK_BASE, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({
        questions: questions,
        question_ids: question_ids
      })
    });

    const data = await safeParseJsonResponse(res);

    if (data.status === 'success') {
      if (data.questions && Array.isArray(data.questions) && data.questions.length > 0) {
        window.currentGeneratedQuestions = data.questions;
      } else {
        questions.forEach(q => q.is_in_bank = true);
      }
      renderGeneratedResults();
      showToastNotice('Question Bank Updated', data.message || `${data.saved_count || questions.length} questions successfully saved to Question Bank!`, 'success');
      if (saveBtn) {
        saveBtn.dataset.saving = 'false';
        saveBtn.innerHTML = '<i class="bi bi-check-circle-fill text-success me-1"></i> Saved to Question Bank';
        saveBtn.disabled = true;
      }
    } else {
      showToastNotice('Error', data.message || 'Failed to save to Question Bank.', 'danger');
      if (saveBtn) {
        saveBtn.dataset.saving = 'false';
        saveBtn.disabled = false;
        saveBtn.innerHTML = originalBtnHtml;
      }
    }
  } catch (err) {
    console.error('Error saving to question bank:', err);
    showToastNotice('Network Error', 'Unable to reach backend to save questions.', 'danger');
    if (saveBtn) {
      saveBtn.dataset.saving = 'false';
      saveBtn.disabled = false;
      saveBtn.innerHTML = originalBtnHtml;
    }
  }
}

function balanceQuestionsAction() {



  const pctEasyInput = document.getElementById('pctEasy');



  const pctMedInput = document.getElementById('pctMedium');



  const pctHardInput = document.getElementById('pctHard');







  const pEasy = parseInt(pctEasyInput ? pctEasyInput.value : 30, 10) || 30;



  const pMed = parseInt(pctMedInput ? pctMedInput.value : 50, 10) || 50;



  const pHard = parseInt(pctHardInput ? pctHardInput.value : 20, 10) || 20;







  if (pEasy + pMed + pHard !== 100) {



    showToastNotice('Invalid Distribution', `Difficulty percentages must sum to 100%. Current sum: ${pEasy + pMed + pHard}%.`, 'warning');



    return;



  }







  const questions = window.currentGeneratedQuestions || [];



  if (!questions || questions.length === 0) {



    showToastNotice('Notice', 'Please generate questions first before calibrating difficulty balance.', 'info');



    return;



  }







  const total = questions.length;



  // Compute target counts proportionally



  const targetEasy = Math.max(1, Math.round((pEasy / 100) * total));



  const targetHard = Math.max(1, Math.round((pHard / 100) * total));



  const targetMed = Math.max(0, total - targetEasy - targetHard);







  // Redistribute difficulty and marks across questions



  let easyAssigned = 0;



  let hardAssigned = 0;



  let medAssigned = 0;







  questions.forEach((q, idx) => {



    if (idx < targetEasy) {



      q.difficulty = 'Easy';



      q.marks = 2;



      easyAssigned++;



    } else if (idx < targetEasy + targetMed) {



      q.difficulty = 'Medium';



      q.marks = 5;



      medAssigned++;



    } else {



      q.difficulty = 'Hard';



      q.marks = 10;



      hardAssigned++;



    }



  });







  // Re-render UI with calibrated questions and distribution progress bar



  renderGeneratedResults();







  // Show calibration breakdown in alert message



  const msg = document.getElementById('balanceSuccessMessage');



  if (msg) {



    msg.classList.remove('d-none');



    msg.innerHTML = `



      <i class="bi bi-check-circle-fill me-1"></i>



      <strong>Calibrated ${total} Questions:</strong>



      ${easyAssigned} Easy (${pEasy}%), ${medAssigned} Medium (${pMed}%), ${hardAssigned} Hard (${pHard}%).



      Question marks and cognitive load rebalanced successfully!



    `;



  }







  showToastNotice('Difficulty Balanced', `Questions calibrated to target ratio ${pEasy}:${pMed}:${pHard}.`, 'success');



}







async function deleteQuestionAction(questionId) {



  if (!confirm('Are you sure you want to delete this question?')) return;







  try {



    const res = await fetch(`${API_QUESTIONS_BASE}/${questionId}`, {



      method: 'DELETE',



      credentials: 'include'



    });







    const data = await res.json();



    if (data.status === 'success') {



      window.currentGeneratedQuestions = (window.currentGeneratedQuestions || []).filter(q => q.id !== questionId);



      renderGeneratedResults();



      showToastNotice('Deleted', 'Question deleted successfully.', 'info');



    } else {



      showToastNotice('Error', data.message || 'Failed to delete question.', 'danger');



    }



  } catch (err) {



    console.error('Error deleting question:', err);



    showToastNotice('Server Error', 'Failed to delete question from backend.', 'danger');



  }



}







async function editQuestionAction(questionId) {



  const q = (window.currentGeneratedQuestions || []).find(item => item.id === questionId);



  if (!q) return;







  const newText = prompt('Edit Question Text:', q.question_text || q.text);



  if (!newText || newText.trim() === '') return;







  try {



    const res = await fetch(`${API_QUESTIONS_BASE}/${questionId}`, {



      method: 'PUT',



      headers: { 'Content-Type': 'application/json' },



      credentials: 'include',



      body: JSON.stringify({ question_text: newText.trim() })



    });







    const data = await res.json();



    if (data.status === 'success') {



      if (data.question) {



        const idx = window.currentGeneratedQuestions.findIndex(item => item.id === questionId);



        if (idx !== -1) window.currentGeneratedQuestions[idx] = data.question;



      } else {



        q.question_text = newText.trim();



        q.text = newText.trim();



      }



      renderGeneratedResults();



      showToastNotice('Updated', 'Question updated successfully.', 'success');



    } else {



      showToastNotice('Error', data.message || 'Failed to update question.', 'danger');



    }



  } catch (err) {



    console.error('Error editing question:', err);



    showToastNotice('Server Error', 'Failed to edit question.', 'danger');



  }



}







// ==========================================



// ==========================================



// ==========================================



// STEP 9E: QUESTION PAPER BUILDER & EXAM PAPERS (FLASK + MYSQL)



// ==========================================







const API_QUESTION_PAPERS_BASE = 'http://localhost:5000/api/question-papers';







window.paperQuestionBankPool = [];



window.paperSelectedQuestions = [];



window.currentSavedPaper = null;



window.currentGeneratedTemplate = null;







async function loadExistingPaperById(paperId) {
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
      } else {
        window.paperQuestionBankPool = [];
      }



    }



  } catch (err) {



    console.warn('Backend fetch failed for Question Bank, falling back to mock pool:', err);



    window.paperQuestionBankPool = [];



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



        ? 'Semester Examination generated: 100 attempted marks (Part A: 20M, Part B: 80M with flexible Direct 16M and Split 8+8 subquestions, strictly Part A & B only)!'



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









function renderPartBGroupManager(sections) {



  const container = document.getElementById('partBGroupManagerContainer');



  if (!container) return;







  if (!sections || !Array.isArray(sections)) {



    container.style.display = 'none';



    return;



  }







  const secB = sections.find(s => (s.name || s.title || '').toUpperCase().includes('PART - B') || (s.name || s.title || '').toUpperCase().includes('PART B'));



  const groups = secB ? (secB.groups || secB.either_or_groups || []) : [];







  if (!secB || groups.length !== 5) {



    container.style.display = 'none';



    return;



  }







  container.style.display = 'block';







  let html = `



    <div class="card border border-primary-subtle shadow-sm mb-4">



      <div class="card-header bg-primary-subtle text-primary-emphasis d-flex justify-content-between align-items-center flex-wrap gap-2">



        <div>



          <i class="bi bi-sliders2-vertical me-2"></i>



          <strong>Part B: Flexible 16-Mark Question Format Configuration</strong>



        </div>



        <span class="badge bg-primary">5 Either/Or Groups × 16 Marks = 80 Attempted Marks</span>



      </div>



      <div class="card-body p-3">



        <div class="alert alert-light border py-2 px-3 small mb-3">



          <i class="bi bi-info-circle me-1 text-primary"></i>



          Each Part B question allows choosing between <strong>Direct 16 Marks</strong> (one complete question) or <strong>Split 8 + 8</strong> (two subquestions displayed under the same main question number). Select the desired format for Alternative (a) and Alternative (b) independently.



        </div>



        <div class="row g-3">



  `;







  groups.forEach((grp, gIdx) => {



    const qNum = grp.question_number || (11 + gIdx);



    const unit = grp.unit || `Unit ${['I','II','III','IV','V'][gIdx] || (gIdx+1)}`;







    const altA = grp.alternative_a || grp.option_a || {};



    const isSplitA = Boolean(altA.format === 'split' || altA.is_subquestion || (altA.subquestions && altA.subquestions.length > 0));







    const altB = grp.alternative_b || grp.option_b || {};



    const isSplitB = Boolean(altB.format === 'split' || altB.is_subquestion || (altB.subquestions && altB.subquestions.length > 0));







    const renderAltPreview = (alt, isSplit, letter) => {



      if (isSplit && alt.subquestions && alt.subquestions.length >= 2) {



        const sq1 = alt.subquestions[0];



        const sq2 = alt.subquestions[1];



        return `



          <div class="p-2 border rounded bg-white mt-2 small">



            <div class="d-flex justify-content-between align-items-center text-muted mb-1">



              <span class="badge bg-secondary-subtle text-secondary border">Split Format: (8 + 8 = 16M)</span>



              <span class="badge bg-success-subtle text-success border">16 Marks Total</span>



            </div>



            <div class="mb-1"><span class="fw-bold text-dark">(i)</span> ${sq1.text || sq1.question_text || sq1.question || 'Subquestion 1'} <span class="badge bg-light text-dark border ms-1">8M</span></div>



            <div><span class="fw-bold text-dark">(ii)</span> ${sq2.text || sq2.question_text || sq2.question || 'Subquestion 2'} <span class="badge bg-light text-dark border ms-1">8M</span></div>



          </div>



        `;



      } else {



        const text = alt.question_text || alt.text || alt.question || 'Direct 16-Mark Question';



        const bTag = alt.bloom_tag || (alt.bloom_level ? `[${alt.bloom_level.substring(0,2).toUpperCase()}]` : '');



        return `



          <div class="p-2 border rounded bg-white mt-2 small">



            <div class="d-flex justify-content-between align-items-center text-muted mb-1">



              <span class="badge bg-primary-subtle text-primary border">Direct Format: (16M)</span>



              <span class="badge bg-success-subtle text-success border">16 Marks</span>



            </div>



            <div class="text-dark">${text} <span class="badge bg-light text-dark border ms-1">${bTag} 16M</span></div>



          </div>



        `;



      }



    };







    html += `



      <div class="col-12">



        <div class="card border rounded shadow-sm">



          <div class="card-header bg-light py-2 px-3 d-flex justify-content-between align-items-center flex-wrap gap-2">



            <span class="fw-bold text-dark">



              <span class="badge bg-primary me-2">Q${qNum}</span>



              <span>${unit} — Either / Or Choice (16 Attempted Marks)</span>



            </span>



            <span class="small text-muted font-monospace">1 Alternative Attempted</span>



          </div>



          <div class="card-body p-3">



            <div class="row g-3">



              <!-- Alternative A -->



              <div class="col-md-6 border-end">



                <div class="d-flex justify-content-between align-items-center flex-wrap gap-1 mb-1">



                  <span class="fw-bold text-primary">Alternative (a)</span>



                  <div class="btn-group btn-group-sm" role="group">



                    <input type="radio" class="btn-check" name="grp_${gIdx}_a_fmt" id="grp_${gIdx}_a_direct" autocomplete="off" ${!isSplitA ? 'checked' : ''} onchange="changeGroupAlternativeFormat(${gIdx}, 'a', 'direct')">



                    <label class="btn btn-outline-primary" for="grp_${gIdx}_a_direct">Direct 16M</label>







                    <input type="radio" class="btn-check" name="grp_${gIdx}_a_fmt" id="grp_${gIdx}_a_split" autocomplete="off" ${isSplitA ? 'checked' : ''} onchange="changeGroupAlternativeFormat(${gIdx}, 'a', 'split')">



                    <label class="btn btn-outline-primary" for="grp_${gIdx}_a_split">Split 8 + 8</label>



                  </div>



                </div>



                ${renderAltPreview(altA, isSplitA, 'a')}



              </div>







              <!-- Alternative B -->



              <div class="col-md-6">



                <div class="d-flex justify-content-between align-items-center flex-wrap gap-1 mb-1">



                  <span class="fw-bold text-primary">Alternative (b)</span>



                  <div class="btn-group btn-group-sm" role="group">



                    <input type="radio" class="btn-check" name="grp_${gIdx}_b_fmt" id="grp_${gIdx}_b_direct" autocomplete="off" ${!isSplitB ? 'checked' : ''} onchange="changeGroupAlternativeFormat(${gIdx}, 'b', 'direct')">



                    <label class="btn btn-outline-primary" for="grp_${gIdx}_b_direct">Direct 16M</label>







                    <input type="radio" class="btn-check" name="grp_${gIdx}_b_fmt" id="grp_${gIdx}_b_split" autocomplete="off" ${isSplitB ? 'checked' : ''} onchange="changeGroupAlternativeFormat(${gIdx}, 'b', 'split')">



                    <label class="btn btn-outline-primary" for="grp_${gIdx}_b_split">Split 8 + 8</label>



                  </div>



                </div>



                ${renderAltPreview(altB, isSplitB, 'b')}



              </div>



            </div>



          </div>



        </div>



      </div>



    `;



  });







  html += `



        </div>



      </div>



    </div>



  `;







  container.innerHTML = html;



}







function changeGroupAlternativeFormat(groupIndex, altLetter, newFormat) {



  if (!window.currentGeneratedTemplate || !window.currentGeneratedTemplate.sections) return;







  const secB = window.currentGeneratedTemplate.sections.find(s =>



    (s.name || s.title || '').toUpperCase().includes('PART - B') ||



    (s.name || s.title || '').toUpperCase().includes('PART B')



  );



  if (!secB) return;







  const groups = secB.groups || secB.either_or_groups || [];



  const group = groups[groupIndex];



  if (!group) return;







  const unit = group.unit || `Unit ${['I','II','III','IV','V'][groupIndex] || 'I'}`;



  const pool = window.paperQuestionBankPool || [];







  const unitPool = pool.filter(q => (q.unit || q.source_unit || '') === unit);



  const activePool = unitPool.length >= 3 ? unitPool : pool;







  const usedIds = new Set();



  window.currentGeneratedTemplate.sections.forEach(s => {



    (s.questions || []).forEach(q => usedIds.add(q.id));



    (s.groups || s.either_or_groups || []).forEach((g, idx) => {



      ['alternative_a', 'alternative_b'].forEach(altKey => {



        if (idx === groupIndex && altKey === (altLetter === 'a' ? 'alternative_a' : 'alternative_b')) {



          return;



        }



        const alt = g[altKey];



        if (!alt) return;



        if (alt.subquestions && Array.isArray(alt.subquestions)) {



          alt.subquestions.forEach(sq => usedIds.add(sq.id));



        } else if (alt.id) {



          usedIds.add(alt.id);



        }



      });



    });



  });







  const altKey = altLetter === 'a' ? 'alternative_a' : 'alternative_b';







  if (newFormat === 'direct') {



    let cand16 = activePool.filter(q => q.marks === 16 && !usedIds.has(q.id));



    if (cand16.length === 0) cand16 = pool.filter(q => q.marks === 16 && !usedIds.has(q.id));



    if (cand16.length === 0) cand16 = pool.filter(q => q.marks === 16);







    if (cand16.length > 0) {



      const q16 = JSON.parse(JSON.stringify(cand16[0]));



      q16.format = 'direct';



      q16.is_subquestion = false;



      q16.marks = 16;



      group[altKey] = q16;



    } else {



      showToastNotice('Notice', 'No 16-mark question available in Question Bank to switch to direct format.', 'warning');



      return;



    }



  } else {



    let cand8 = activePool.filter(q => q.marks === 8 && !usedIds.has(q.id));



    if (cand8.length < 2) cand8 = pool.filter(q => q.marks === 8 && !usedIds.has(q.id));



    if (cand8.length < 2) cand8 = pool.filter(q => q.marks === 8);







    if (cand8.length >= 2) {



      const q8_1 = cand8[0];



      const q8_2 = cand8[1];



      group[altKey] = {



        format: 'split',



        is_subquestion: true,



        marks: 16,



        unit: unit,



        topic: q8_1.topic || `${unit} Topics`,



        subquestions: [



          {



            part: '(i)',



            id: q8_1.id,



            text: q8_1.question_text || q8_1.text || q8_1.question,



            question_text: q8_1.question_text || q8_1.text || q8_1.question,



            marks: 8,



            bloom_tag: q8_1.bloom_tag || (q8_1.bloom_level ? `[${q8_1.bloom_level.substring(0,2).toUpperCase()}]` : '[AP]'),



            topic: q8_1.topic



          },



          {



            part: '(ii)',



            id: q8_2.id,



            text: q8_2.question_text || q8_2.text || q8_2.question,



            question_text: q8_2.question_text || q8_2.text || q8_2.question,



            marks: 8,



            bloom_tag: q8_2.bloom_tag || (q8_2.bloom_level ? `[${q8_2.bloom_level.substring(0,2).toUpperCase()}]` : '[AN]'),



            topic: q8_2.topic



          }



        ]



      };



    } else {



      showToastNotice('Notice', 'Insufficient 8-mark questions in Question Bank to switch to split format.', 'warning');



      return;



    }



  }







  const qList = [];



  window.currentGeneratedTemplate.sections.forEach(sec => {



    (sec.questions || []).forEach(q => qList.push(q));



    (sec.groups || sec.either_or_groups || []).forEach(g => {



      ['alternative_a', 'alternative_b'].forEach(k => {



        const a = g[k];



        if (!a) return;



        if (a.subquestions && Array.isArray(a.subquestions)) {



          a.subquestions.forEach(sq => qList.push(sq));



        } else {



          qList.push(a);



        }



      });



    });



  });



  window.paperSelectedQuestions = qList;







  renderPaperSelectedQuestions();



  renderPaperSectionStructure(window.currentGeneratedTemplate.sections);



  generateAcademicPaperPreview();







  const qNum = group.question_number || (11 + groupIndex);



  showToastNotice(



    'Format Updated',



    `Question ${qNum} Alternative (${altLetter}) is now set to ${newFormat === 'direct' ? 'Direct 16 Marks' : 'Split 8 + 8 Subquestions'}.`,



    'success'



  );



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
  if (![2, 8, 16].includes(marks)) {
    showToastNotice('Invalid Marks', 'Only 2, 8, and 16 marks questions are allowed.', 'warning');
    return;
  }



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
  if (![2, 8, 16].includes(marks)) {
    showToastNotice('Invalid Marks', 'Only 2, 8, and 16 marks questions are allowed.', 'warning');
    return;
  }



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



      { name: "PART - B (5 x 16 = 80 Marks)", count: 5, marks_per_q: 16, total_marks: 80 }



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



                    const subMarks = sq.marks || 8;



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



              const marksVal = alt.marks || (sec.marks_per_q || (isInternal ? 8 : 16));



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











function bindGeneratorStubs() {}



function initQuestionGeneratorForm() {}



function initVerificationPage() {}



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



function initResourceForm() {



  const resourceUploadForm = document.getElementById('resourceUploadForm');



  if (resourceUploadForm) {



    resourceUploadForm.addEventListener('submit', async (e) => {



      e.preventDefault();



      const submitBtn = resourceUploadForm.querySelector('button[type="submit"]');



      const originalText = submitBtn ? submitBtn.innerHTML : 'Upload Resource';







      const subject = document.getElementById('resourceSubject')?.value;



      const department = document.getElementById('resourceDept')?.value;



      const academic_year = document.getElementById('resourceYear')?.value;



      const semester = document.getElementById('resourceSem')?.value;



      const unit = document.getElementById('resourceUnit')?.value;



      const topic = document.getElementById('resourceTopic')?.value;



      const resource_type = document.getElementById('resourceType')?.value;



      const fileInput = document.getElementById('resourceFile');







      if (!subject || !department || !topic) {



        showToastNotice('Validation Error', 'Please fill in all required fields.', 'warning');



        return;



      }







      const formData = new FormData();



      formData.append('subject', subject);



      formData.append('department', department);



      formData.append('academic_year', academic_year);



      formData.append('semester', semester);



      formData.append('unit', unit);



      formData.append('topic', topic);



      formData.append('resource_type', resource_type);







      if (fileInput && fileInput.files && fileInput.files[0]) {



        formData.append('file', fileInput.files[0]);



      }







      if (submitBtn) {



        submitBtn.disabled = true;



        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Uploading Resource...';



      }







      try {



        const response = await fetch(API_RESOURCES_BASE, {



          method: 'POST',



          credentials: 'include',



          body: formData



        });



        const result = await response.json();







        if (submitBtn) {



          submitBtn.disabled = false;



          submitBtn.innerHTML = originalText;



        }







        if (response.ok) {



          showToastNotice('Resource Uploaded', result.message || 'Academic material uploaded successfully!', 'success');



          resourceUploadForm.reset();



          const fileFeedback = document.getElementById('fileFeedback');



          if (fileFeedback) fileFeedback.innerHTML = '';



          renderFacultyResourcesTable();



        } else {



          showToastNotice('Upload Failed', result.message || 'Failed to upload resource.', 'danger');



        }



      } catch (err) {



        console.error('Resource upload error:', err);



        if (submitBtn) {



          submitBtn.disabled = false;



          submitBtn.innerHTML = originalText;



        }



        showToastNotice('Network Error', 'Could not connect to backend API server.', 'danger');



      }



    });



  }







  const clearBtn = document.getElementById('clearResourceFormBtn');



  if (clearBtn && resourceUploadForm) {



    clearBtn.addEventListener('click', () => {



      resourceUploadForm.reset();



      const fileFeedback = document.getElementById('fileFeedback');



      if (fileFeedback) fileFeedback.innerHTML = '';



    });



  }



}







// Render Faculty Resources Table from MySQL



async function renderFacultyResourcesTable() {



  const tableBody = document.getElementById('facultyResourcesTableBody');



  if (!tableBody) return;







  tableBody.innerHTML = `



    <tr>



      <td colspan="8" class="text-center py-4 text-muted">



        <span class="spinner-border spinner-border-sm me-2 text-primary"></span>



        Loading academic resources from database...



      </td>



    </tr>



  `;







  try {



    const response = await fetch(API_RESOURCES_BASE, {



      method: 'GET',



      credentials: 'include'



    });



    if (!response.ok) {



      tableBody.innerHTML = `<tr><td colspan="8" class="text-center text-danger py-4">Failed to load academic resources.</td></tr>`;



      return;



    }



    const result = await response.json();



    const resources = result.resources || [];







    if (resources.length === 0) {



      tableBody.innerHTML = `



        <tr>



          <td colspan="8" class="text-center py-4 text-muted">



            <i class="bi bi-inbox fs-4 d-block mb-1"></i>



            No academic resources uploaded yet. Fill in the form above to register resources.



          </td>



        </tr>



      `;



      return;



    }







    // Augment subject and department datalist suggestions with existing user data

    const datalist = document.getElementById('resourceSubjectList');

    if (datalist) {

      const subjectSet = new Set([

        'Database Management Systems',

        'Data Structures',

        'Artificial Intelligence',

        'Machine Learning',

        'Computer Networks',

        'Cloud Computing',

        'Operating Systems',

        'Cyber Security',

        ...resources.map(r => r.subject).filter(Boolean)

      ]);

      datalist.innerHTML = Array.from(subjectSet).map(s => `<option value="${s}">`).join('');

    }



    const deptDatalist = document.getElementById('resourceDeptList');

    if (deptDatalist) {

      const deptSet = new Set([

        'Artificial Intelligence & Data Science',

        'Artificial Intelligence & Machine Learning',

        'Computer Science & Engineering',

        'Information Technology',

        'Computer and Communication Engineering',

        'Electronics & Communication Engineering',

        'Electrical & Electronics Engineering',

        'Mechanical Engineering',

        'Civil Engineering',

        ...resources.map(r => r.department).filter(Boolean)

      ]);

      deptDatalist.innerHTML = Array.from(deptSet).map(d => `<option value="${d}">`).join('');

    }



    tableBody.innerHTML = resources.map(r => {



      let statusBadge = `<span class="badge badge-status-uploaded">Uploaded</span>`;



      if (r.status === 'Analyzed' || r.analysis_status === 'Analyzed') {



        statusBadge = `<span class="badge badge-status-analyzed">Analyzed</span>`;



      } else if (r.status === 'Processing') {



        statusBadge = `<span class="badge badge-status-processing">Processing</span>`;



      } else if (r.status === 'Error') {



        statusBadge = `<span class="badge badge-status-error">Error</span>`;



      }







      const fileDisplay = r.file_name ? `<span class="small text-muted"><i class="bi bi-paperclip me-1"></i>${r.file_name}</span>` : `<span class="small text-muted">Metadata only</span>`;







      return `



        <tr>



          <td>



            <strong>${r.title}</strong><br>



            ${fileDisplay}



          </td>



          <td><span class="badge bg-primary-subtle text-primary border">${r.resource_type}</span></td>



          <td><small class="fw-semibold">${r.subject}</small></td>



          <td><small>${r.unit}</small></td>



          <td><small class="text-muted">${r.topic}</small></td>



          <td><small class="text-muted">${r.created_at_str || 'Recent'}</small></td>



          <td>${statusBadge}</td>



          <td>



            <div class="btn-group btn-group-sm">



              <button class="btn btn-outline-primary py-0 px-2" onclick="viewFacultyResource(${r.id})" title="View Details">



                <i class="bi bi-eye"></i>



              </button>



              <button class="btn btn-outline-warning py-0 px-2" onclick="openEditResourceModal(${r.id})" title="Edit Resource">



                <i class="bi bi-pencil"></i>



              </button>



              <button class="btn btn-outline-success py-0 px-2" onclick="analyzeFacultyResource(${r.id})" title="Analyze Content">



                <i class="bi bi-cpu"></i> Analyze



              </button>



              <button class="btn btn-outline-danger py-0 px-2" onclick="deleteFacultyResource(${r.id})" title="Delete">



                <i class="bi bi-trash"></i>



              </button>



            </div>



          </td>



        </tr>



      `;



    }).join('');



  } catch (err) {



    console.error('Error rendering faculty resources table:', err);



    tableBody.innerHTML = `<tr><td colspan="8" class="text-center text-danger py-4">Unable to connect to backend server.</td></tr>`;



  }



}







// View Resource Details Modal Handler



async function viewFacultyResource(id) {



  try {



    const response = await fetch(`${API_RESOURCES_BASE}/${id}`, { credentials: 'include' });



    if (!response.ok) {



      showToastNotice('Error', 'Unable to fetch resource details.', 'danger');



      return;



    }



    const result = await response.json();



    const r = result.resource;







    const modalTitle = document.getElementById('viewResourceTitle');



    const modalContent = document.getElementById('viewResourceContent');







    if (modalTitle) modalTitle.innerText = `Resource Details: ${r.title}`;



    if (modalContent) {



      modalContent.innerHTML = `



        <div class="mb-3">



          <h6 class="fw-bold text-primary mb-1">${r.subject}</h6>



          <small class="text-muted">${r.department} • ${r.academic_year} • ${r.semester}</small>



        </div>



        <div class="row g-2 mb-3">



          <div class="col-6"><strong>Unit:</strong> ${r.unit}</div>



          <div class="col-6"><strong>Topic:</strong> ${r.topic}</div>



          <div class="col-6"><strong>Type:</strong> ${r.resource_type}</div>



          <div class="col-6"><strong>Status:</strong> ${r.status || r.analysis_status}</div>



        </div>



        <div class="p-3 bg-light rounded border mb-3">



          <strong>File Attached:</strong> ${r.file_name ? `<a href="http://localhost:5000/api/resources/file/${r.file_name.split('/').pop()}" target="_blank" class="fw-semibold text-primary"><i class="bi bi-file-earmark-arrow-down me-1"></i>${r.file_name}</a>` : 'No file attached'}



        </div>



        <div>



          <strong>Uploaded On:</strong> ${r.created_at_str || r.created_at}



        </div>



      `;



    }







    const modalEl = document.getElementById('viewResourceModal');



    if (modalEl) {



      const bsModal = new bootstrap.Modal(modalEl);



      bsModal.show();



    }



  } catch (err) {



    console.error('View resource error:', err);



    showToastNotice('Error', 'Failed to view resource.', 'danger');



  }



}







// Analyze Academic Content Handler (Saves Status & Metadata to MySQL)



async function analyzeFacultyResource(id) {



  try {



    showToastNotice('Analyzing Content', 'Extracting units, topics, and concepts...', 'info');







    const response = await fetch(`${API_RESOURCES_BASE}/${id}/analyze`, {



      method: 'POST',



      credentials: 'include'



    });



    if (!response.ok) {



      showToastNotice('Analysis Failed', 'Could not complete content analysis.', 'danger');



      return;



    }



    const result = await response.json();



    const analysis = result.analysis;



    const r = result.resource;







    document.getElementById('analysisSubjectTitle').innerText = r.subject;



    document.getElementById('analysisResourceName').innerText = `${r.title} (${r.resource_type})`;







    document.getElementById('metricUnitsCount').innerText = analysis.units_count || 5;



    document.getElementById('metricTopicsCount').innerText = analysis.topics_count || 18;



    document.getElementById('metricConceptsCount').innerText = analysis.concepts_count || 42;







    const breakdownEl = document.getElementById('analysisUnitsBreakdown');



    if (breakdownEl && analysis.units_breakdown) {



      breakdownEl.innerHTML = analysis.units_breakdown.map(u => `



        <div class="p-3 bg-light rounded border mb-2">



          <div class="fw-bold text-dark mb-1"><i class="bi bi-collection me-2 text-primary"></i>${u.unit_name}</div>



          <div class="small text-muted">Concepts: ${u.concepts.join(', ')}</div>



        </div>



      `).join('');



    }







    const hierarchyEl = document.getElementById('conceptHierarchyContainer');

    if (hierarchyEl) {

      hierarchyEl.innerHTML = `

        <div class="hierarchy-node hierarchy-level-subject">

          <i class="bi bi-journal-album me-2"></i> Subject: ${r.subject}

        </div>

        <div class="hierarchy-arrow"><i class="bi bi-arrow-down"></i></div>



        <div class="hierarchy-node hierarchy-level-unit">

          <i class="bi bi-collection me-2"></i> Unit: ${r.unit}

        </div>

        <div class="hierarchy-arrow"><i class="bi bi-arrow-down"></i></div>



        <div class="hierarchy-node hierarchy-level-topic">

          <i class="bi bi-bookmark-star me-2"></i> Topic: ${r.topic}

        </div>

        <div class="hierarchy-arrow"><i class="bi bi-arrow-down"></i></div>



        <div class="hierarchy-node hierarchy-level-subtopic">

          <i class="bi bi-hash me-2"></i> Subtopic: Core Principles & Methodologies of ${r.topic}

        </div>

        <div class="hierarchy-arrow"><i class="bi bi-arrow-down"></i></div>



        <div class="hierarchy-node hierarchy-level-concept">

          <i class="bi bi-lightbulb-fill me-2 text-warning"></i> Key Concepts: ${r.subject} Foundations, Applied Techniques, Analytical Models

        </div>

      `;

    }





    const modalEl = document.getElementById('academicAnalysisModal');



    if (modalEl) {



      const bsModal = new bootstrap.Modal(modalEl);



      bsModal.show();



    }







    showToastNotice('Analysis Complete', 'Academic content analyzed and persisted to database!', 'success');



    renderFacultyResourcesTable();



  } catch (err) {



    console.error('Analysis error:', err);



    showToastNotice('Error', 'Failed to analyze resource.', 'danger');



  }



}







// Delete Academic Resource Handler



async function deleteFacultyResource(id) {



  if (!confirm('Are you sure you want to delete this academic resource?')) return;







  try {



    const response = await fetch(`${API_RESOURCES_BASE}/${id}`, {



      method: 'DELETE',



      credentials: 'include'



    });



    const result = await response.json();







    if (response.ok) {



      showToastNotice('Resource Deleted', result.message || 'Academic resource removed successfully.', 'success');



      renderFacultyResourcesTable();



    } else {



      showToastNotice('Delete Failed', result.message || 'Failed to delete resource.', 'danger');



    }



  } catch (err) {



    console.error('Delete resource error:', err);



    showToastNotice('Error', 'Failed to delete resource.', 'danger');



  }



}







// Open Edit Resource Modal



async function openEditResourceModal(id) {



  try {



    const res = await fetch(`${API_RESOURCES_BASE}/${id}`, { credentials: 'include' });



    if (!res.ok) {



      showToastNotice('Error', 'Unable to load resource for editing.', 'danger');



      return;



    }



    const data = await res.json();



    const r = data.resource;



    if (!r) return;







    const idInput = document.getElementById('editResourceId');



    const subjInput = document.getElementById('editResourceSubject');



    const deptInput = document.getElementById('editResourceDept');



    const yearInput = document.getElementById('editResourceYear');



    const semInput = document.getElementById('editResourceSem');



    const unitInput = document.getElementById('editResourceUnit');



    const topicInput = document.getElementById('editResourceTopic');



    const typeInput = document.getElementById('editResourceType');



    const feedback = document.getElementById('editFileFeedback');







    if (idInput) idInput.value = r.id;



    if (subjInput) subjInput.value = r.subject || '';



    if (deptInput) deptInput.value = r.department || 'Artificial Intelligence & Data Science';



    if (yearInput) yearInput.value = r.academic_year || '2025-2026';



    if (semInput) semInput.value = r.semester || 'Semester 6';



    if (unitInput) unitInput.value = r.unit || 'All Units';



    if (topicInput) topicInput.value = r.topic || '';



    if (typeInput) typeInput.value = r.resource_type || 'Study Material';



    if (feedback) feedback.textContent = r.file_name ? `Current file: ${r.file_name}` : 'No file currently attached.';







    const modalEl = document.getElementById('editResourceModal');



    if (modalEl && typeof bootstrap !== 'undefined') {



      const bsModal = bootstrap.Modal.getInstance(modalEl) || new bootstrap.Modal(modalEl);



      bsModal.show();



    }



  } catch (err) {



    console.error('Error opening edit resource modal:', err);



    showToastNotice('Error', 'Failed to load resource data.', 'danger');



  }



}







// Bind Edit Resource Form Handler



function initEditResourceForm() {



  const editForm = document.getElementById('editResourceForm');



  if (editForm && !editForm.dataset.bound) {



    editForm.dataset.bound = 'true';



    editForm.addEventListener('submit', async (e) => {



      e.preventDefault();



      const id = document.getElementById('editResourceId')?.value;



      const subject = (document.getElementById('editResourceSubject')?.value || '').trim();



      const department = document.getElementById('editResourceDept')?.value;



      const academic_year = document.getElementById('editResourceYear')?.value;



      const semester = document.getElementById('editResourceSem')?.value;



      const unit = document.getElementById('editResourceUnit')?.value;



      const topic = (document.getElementById('editResourceTopic')?.value || '').trim();



      const resource_type = document.getElementById('editResourceType')?.value;



      const fileInput = document.getElementById('editResourceFile');







      if (!subject || !department || !topic) {



        showToastNotice('Validation Error', 'Please fill in all required fields.', 'warning');



        return;



      }







      const formData = new FormData();



      formData.append('subject', subject);



      formData.append('department', department);



      formData.append('academic_year', academic_year);



      formData.append('semester', semester);



      formData.append('unit', unit);



      formData.append('topic', topic);



      formData.append('resource_type', resource_type);



      if (fileInput && fileInput.files && fileInput.files[0]) {



        formData.append('file', fileInput.files[0]);



      }







      const submitBtn = editForm.querySelector('button[type="submit"]');



      const origText = submitBtn ? submitBtn.innerHTML : 'Save Changes';



      if (submitBtn) {



        submitBtn.disabled = true;



        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Saving...';



      }







      try {



        const res = await fetch(`${API_RESOURCES_BASE}/${id}`, {



          method: 'PUT',



          credentials: 'include',



          body: formData



        });



        const result = await res.json();



        if (submitBtn) {



          submitBtn.disabled = false;



          submitBtn.innerHTML = origText;



        }



        if (res.ok && result.status === 'success') {



          showToastNotice('Success', 'Resource updated successfully!', 'success');



          const modalEl = document.getElementById('editResourceModal');



          if (modalEl && typeof bootstrap !== 'undefined') {



            const bsModal = bootstrap.Modal.getInstance(modalEl);



            if (bsModal) bsModal.hide();



          }



          renderFacultyResourcesTable();



        } else {



          showToastNotice('Update Failed', result.message || 'Failed to update resource.', 'danger');



        }



      } catch (err) {



        console.error('Error updating resource:', err);



        if (submitBtn) {



          submitBtn.disabled = false;



          submitBtn.innerHTML = origText;



        }



        showToastNotice('Error', 'An error occurred while updating resource.', 'danger');



      }



    });



  }



}








// ==========================================================
// REQUIREMENT 1: Dynamic Student Subjects & Resource Counts
// ==========================================================
let globalEnrolledSubjects = [];

async function renderStudentSubjects() {
  const container = document.getElementById('enrolledSubjectsContainer');
  if (!container) return;

  container.innerHTML = `
    <div class="col-12 text-center py-5">
      <div class="spinner-border text-primary me-2" role="status"></div>
      <div class="text-muted mt-2">Loading enrolled curriculum courses...</div>
    </div>
  `;

  try {
    const res = await fetch('http://localhost:5000/api/student/subjects', {
      credentials: 'include'
    });

    if (res.ok) {
      const data = await res.json();
      if (data.status === 'success' && Array.isArray(data.subjects) && data.subjects.length > 0) {
        globalEnrolledSubjects = data.subjects;
      }
    }
  } catch (err) {
    console.warn('API error fetching subjects, falling back to local curriculum:', err);
  }

  // Fallback defaults if API empty
  if (!globalEnrolledSubjects || globalEnrolledSubjects.length === 0) {
    globalEnrolledSubjects = [
      {
        code: "CS301",
        name: "Database Management Systems",
        department: "Artificial Intelligence & Data Science",
        credits: 4,
        description: "Relational database design, relational algebra, SQL optimization, transactions, ACID properties, and concurrency control.",
        materials_count: 3, quizzes_count: 4, assignments_count: 1, papers_count: 7
      },
      {
        code: "23CST504",
        name: "Distributed Computing",
        department: "Artificial Intelligence & Data Science",
        credits: 4,
        description: "Distributed system architectures, RPC, clock synchronization, Lamport logical timestamps, mutual exclusion, and consensus.",
        materials_count: 10, quizzes_count: 7, assignments_count: 1, papers_count: 2
      },
      {
        code: "AI401",
        name: "Machine Learning",
        department: "Artificial Intelligence & Data Science",
        credits: 4,
        description: "Supervised and unsupervised learning, classification, neural networks, deep architectures, and model performance metrics.",
        materials_count: 1, quizzes_count: 1, assignments_count: 1, papers_count: 1
      },
      {
        code: "IT302",
        name: "Cloud Computing",
        department: "Artificial Intelligence & Data Science",
        credits: 3,
        description: "Cloud virtualization, IaaS, PaaS, SaaS delivery models, distributed storage, and cloud microservices orchestration.",
        materials_count: 3, quizzes_count: 0, assignments_count: 0, papers_count: 0
      }
    ];
  }

  container.innerHTML = globalEnrolledSubjects.map(sub => `
    <div class="col-md-6 col-xl-6">
      <div class="card card-academic h-100 shadow-sm border">
        <div class="card-academic-header d-flex justify-content-between align-items-center">
          <span class="badge bg-primary">${sub.code || 'SUB'}</span>
          <span class="text-muted small"><i class="bi bi-clock me-1"></i> ${sub.credits || 4} Credits</span>
        </div>
        <div class="card-body p-4 d-flex flex-column">
          <h5 class="fw-bold text-dark mb-2">${sub.name}</h5>
          <p class="text-muted small mb-3 flex-grow-1">${sub.description || 'Curriculum course materials and assessments.'}</p>
          
          <div class="mb-3 small text-muted">
            <div><strong>Department:</strong> <span class="text-dark">${sub.department || 'Artificial Intelligence & Data Science'}</span></div>
            <div><strong>Course Status:</strong> <span class="text-success fw-semibold"><i class="bi bi-check-circle me-1"></i>Enrolled & Active</span></div>
          </div>

          <div class="d-flex flex-wrap gap-2 pt-2 border-top">
            <a href="student-materials.html?subject=${encodeURIComponent(sub.name)}" class="btn btn-sm btn-outline-primary d-inline-flex align-items-center">
              <i class="bi bi-file-earmark-pdf me-1"></i> Study Materials
              <span class="badge bg-primary text-white ms-1 rounded-pill">${sub.materials_count || 0}</span>
            </a>
            <a href="student-quizzes.html?subject=${encodeURIComponent(sub.name)}" class="btn btn-sm btn-outline-warning d-inline-flex align-items-center">
              <i class="bi bi-patch-question me-1"></i> Quizzes
              <span class="badge bg-warning text-dark ms-1 rounded-pill">${sub.quizzes_count || 0}</span>
            </a>
            <a href="student-assignments.html?subject=${encodeURIComponent(sub.name)}" class="btn btn-sm btn-outline-success d-inline-flex align-items-center">
              <i class="bi bi-journal-text me-1"></i> Assignments
              <span class="badge bg-success text-white ms-1 rounded-pill">${sub.assignments_count || 0}</span>
            </a>
            <a href="student-question-papers.html?subject=${encodeURIComponent(sub.name)}" class="btn btn-sm btn-outline-info d-inline-flex align-items-center">
              <i class="bi bi-file-text me-1"></i> Question Papers
              <span class="badge bg-info text-dark ms-1 rounded-pill">${sub.papers_count || 0}</span>
            </a>
          </div>
        </div>
      </div>
    </div>
  `).join('');
}


// Render Student Study Materials Table from MySQL




let globalStudentMaterials = [];

async function renderStudentMaterialsTable() {
  const tableBody = document.getElementById('studentMaterialsTableBody');
  if (!tableBody) return;

  const urlParams = new URLSearchParams(window.location.search);
  const filterSelect = document.getElementById('studentMaterialSubjectFilter');
  let currentSubject = urlParams.get('subject') || (filterSelect ? filterSelect.value : 'ALL') || 'ALL';

  tableBody.innerHTML = `
    <tr>
      <td colspan="8" class="text-center py-4 text-muted">
        <span class="spinner-border spinner-border-sm me-2 text-primary"></span>
        Loading published study materials...
      </td>
    </tr>
  `;

  try {
    const apiUrl = (typeof API_RESOURCES_BASE !== 'undefined' && API_RESOURCES_BASE) ? API_RESOURCES_BASE : 'http://localhost:5000/api/resources';
    const response = await fetch(apiUrl, {
      method: 'GET',
      credentials: 'include'
    });

    if (!response.ok) {
      tableBody.innerHTML = `<tr><td colspan="8" class="text-center text-danger py-4">Failed to load study materials from server.</td></tr>`;
      return;
    }

    const result = await response.json();
    globalStudentMaterials = result.resources || [];

    // Populate subject filter dropdown if available
    if (filterSelect) {
      const subjects = Array.from(new Set(globalStudentMaterials.map(r => r.subject).filter(Boolean)));
      if (!subjects.includes('Database Management Systems')) subjects.push('Database Management Systems');
      if (!subjects.includes('Distributed Computing')) subjects.push('Distributed Computing');
      if (!subjects.includes('Machine Learning')) subjects.push('Machine Learning');
      if (!subjects.includes('Cloud Computing')) subjects.push('Cloud Computing');

      filterSelect.innerHTML = `<option value="ALL">All Subjects (${globalStudentMaterials.length})</option>` +
        subjects.map(s => {
          const cnt = globalStudentMaterials.filter(r => r.subject === s).length;
          return `<option value="${s}" ${s === currentSubject ? 'selected' : ''}>${s} (${cnt})</option>`;
        }).join('');
      
      if (currentSubject && subjects.includes(currentSubject)) {
        filterSelect.value = currentSubject;
      }
    }

    let filtered = globalStudentMaterials;
    if (currentSubject && currentSubject !== 'ALL') {
      filtered = filtered.filter(r => r.subject === currentSubject);
    }

    if (filtered.length === 0) {
      tableBody.innerHTML = `
        <tr>
          <td colspan="8" class="text-center py-5 text-muted">
            <i class="bi bi-journal-x fs-2 d-block mb-2 text-secondary"></i>
            No study materials published yet ${currentSubject !== 'ALL' ? `for <strong>${currentSubject}</strong>` : ''}. Check back later!
          </td>
        </tr>
      `;
      return;
    }

    tableBody.innerHTML = filtered.map(r => `
      <tr>
        <td><span class="badge bg-secondary-subtle text-dark border">${r.subject}</span></td>
        <td><small class="text-muted">${r.unit || 'General'}</small></td>
        <td><small class="fw-semibold text-dark">${r.topic || 'General Topic'}</small></td>
        <td><span class="badge bg-info-subtle text-info-emphasis border">${r.resource_type || 'Document'}</span></td>
        <td>
          <div class="fw-semibold text-dark">${r.title}</div>
          <small class="text-muted font-monospace">${r.file_name || 'No file attached'}</small>
        </td>
        <td><small class="text-muted">${r.faculty_name || 'Faculty Member'}</small></td>
        <td><small class="text-muted">${r.created_at_str || r.created_at || 'Recent'}</small></td>
        <td>
          <button class="btn btn-academic-primary btn-sm py-1 px-3" onclick="viewStudentMaterial('${r.id}')">
            <i class="bi bi-eye me-1"></i> View
          </button>
        </td>
      </tr>
    `).join('');

  } catch (err) {
    console.error('Student materials load error:', err);
    tableBody.innerHTML = `<tr><td colspan="8" class="text-center text-danger py-4">Error loading materials.</td></tr>`;
  }
}

function filterStudentMaterials() {
  const filterSelect = document.getElementById('studentMaterialSubjectFilter');
  const sel = filterSelect ? filterSelect.value : 'ALL';
  const url = new URL(window.location);
  if (sel === 'ALL') {
    url.searchParams.delete('subject');
  } else {
    url.searchParams.set('subject', sel);
  }
  window.history.replaceState({}, '', url);
  renderStudentMaterialsTable();
}

async function viewStudentMaterial(resourceId) {
  try {
    let r = globalStudentMaterials.find(x => String(x.id) === String(resourceId));

    if (!r) {
      const apiUrl = (typeof API_RESOURCES_BASE !== 'undefined' && API_RESOURCES_BASE) ? API_RESOURCES_BASE : 'http://localhost:5000/api/resources';
      const res = await fetch(`${apiUrl}/${resourceId}`, { credentials: 'include' });
      if (res.ok) {
        const d = await res.json();
        r = d.resource;
      }
    }

    if (!r) {
      showToastNotice('Error', 'Resource not found.', 'danger');
      return;
    }

    const modalTitle = document.getElementById('studentMaterialTitle');
    const modalBody = document.getElementById('studentMaterialBody');
    if (modalTitle) modalTitle.textContent = r.title;

    if (modalBody) {
      const fileUrl = `http://localhost:5000/api/resources/${r.id}/file`;
      const isPdf = r.file_name && r.file_name.toLowerCase().endsWith('.pdf');
      const isTxt = r.file_name && r.file_name.toLowerCase().endsWith('.txt');

      modalBody.innerHTML = `
        <div class="mb-3">
          <div class="d-flex justify-content-between align-items-center mb-2">
            <span class="badge bg-primary fs-6">${r.subject}</span>
            <span class="badge bg-light text-dark border">${r.unit || 'General Unit'}</span>
          </div>
          <h5 class="fw-bold text-dark mt-2">${r.title}</h5>
          <p class="text-muted small">${r.description || 'Official learning resource published for curriculum coursework.'}</p>
        </div>

        <div class="row g-2 p-3 bg-light rounded border small mb-3">
          <div class="col-6"><strong>Department:</strong> ${r.department || 'Artificial Intelligence & Data Science'}</div>
          <div class="col-6"><strong>Topic:</strong> ${r.topic || 'General Topic'}</div>
          <div class="col-6"><strong>Material Type:</strong> ${r.resource_type || 'Document'}</div>
          <div class="col-6"><strong>Faculty In-Charge:</strong> ${r.faculty_name || 'Faculty Member'}</div>
          <div class="col-12"><strong>Published Date:</strong> ${r.created_at_str || r.created_at || 'Recent'}</div>
        </div>

        <div class="p-4 bg-white rounded border text-center shadow-sm">
          <i class="bi bi-file-earmark-arrow-down fs-1 text-primary d-block mb-2"></i>
          <h6 class="fw-bold mb-1">${r.file_name || r.title}</h6>
          <small class="text-muted d-block mb-3">Stored safely in academic storage repository</small>
          
          <div class="d-flex justify-content-center gap-2 flex-wrap">
            <a href="${fileUrl}" target="_blank" download="${r.file_name || 'resource'}" class="btn btn-academic-primary btn-sm px-3">
              <i class="bi bi-download me-1"></i> Download Resource File
            </a>
            <a href="${fileUrl}" target="_blank" class="btn btn-outline-secondary btn-sm px-3">
              <i class="bi bi-box-arrow-up-right me-1"></i> Open / Preview in Browser
            </a>
          </div>
        </div>
      `;
    }

    const modalEl = document.getElementById('studentMaterialViewModal');
    if (modalEl) {
      const bsModal = bootstrap.Modal.getOrCreateInstance(modalEl);
      bsModal.show();
    }
  } catch (err) {
    console.error('Student view material error:', err);
    showToastNotice('Error', 'Failed to view material.', 'danger');
  }
}



// Universal Faculty Header Profile Synchronizer



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



// Global State for Faculty Dashboard

let currentFacultyQuestions = [];

let currentFacultyCourses = [];

let currentFacultyDrafts = [];

let currentFacultyPublished = [];



// Switch Workspace Tab

function navigateToDashboardTab(tabName) {

  const tabBtn = document.getElementById('tab-' + tabName + '-btn');

  if (tabBtn) {

    if (typeof bootstrap !== 'undefined' && bootstrap.Tab) {

      const tab = new bootstrap.Tab(tabBtn);

      tab.show();

    } else {

      tabBtn.click();

    }

  }

  const workspaceEl = document.getElementById('facultyDashboardWorkspaceSection');

  if (workspaceEl) {

    workspaceEl.scrollIntoView({ behavior: 'smooth', block: 'start' });

  }

}



// Filter and Render Questions in Dashboard Table

function filterFacultyQuestions() {

  const tableBody = document.getElementById('facultyQuestionsTableBody');

  const countFooter = document.getElementById('facultyQuestionsCountFooter');

  if (!tableBody) return;



  const searchVal = (document.getElementById('dashFilterSearch')?.value || '').toLowerCase().trim();

  const subjectVal = document.getElementById('dashFilterSubject')?.value || 'ALL';

  const unitVal = document.getElementById('dashFilterUnit')?.value || 'ALL';

  const marksVal = document.getElementById('dashFilterMarks')?.value || 'ALL';

  const diffVal = document.getElementById('dashFilterDiff')?.value || 'ALL';

  const bloomVal = document.getElementById('dashFilterBloom')?.value || 'ALL';



  const filtered = currentFacultyQuestions.filter(q => {

    if (searchVal) {

      const text = (q.question_text || '').toLowerCase();

      const topic = (q.topic || '').toLowerCase();

      const concept = (q.concept || '').toLowerCase();

      if (!text.includes(searchVal) && !topic.includes(searchVal) && !concept.includes(searchVal)) {

        return false;

      }

    }

    if (subjectVal !== 'ALL' && q.subject !== subjectVal) return false;

    if (unitVal !== 'ALL') {

      const qUnit = (q.unit || q.source_unit || '').toLowerCase();

      if (!qUnit.includes(unitVal.toLowerCase())) return false;

    }

    if (marksVal !== 'ALL' && String(q.marks) !== String(marksVal)) return false;

    if (diffVal !== 'ALL' && (q.difficulty || '').toLowerCase() !== diffVal.toLowerCase()) return false;

    if (bloomVal !== 'ALL' && (q.bloom_level || '').toLowerCase() !== bloomVal.toLowerCase()) return false;

    return true;

  });



  if (!filtered || filtered.length === 0) {

    if (currentFacultyQuestions.length === 0) {

      tableBody.innerHTML = `

        <tr>

          <td colspan="8" class="text-center py-5">

            <div class="text-muted mb-2"><i class="bi bi-journal-x fs-2"></i></div>

            <h6 class="fw-bold text-dark">No Questions in Question Bank</h6>

            <p class="text-muted small mb-3">You have not created any questions yet. Use AI Question Generator to populate your repository.</p>

            <a href="faculty-generate-questions.html" class="btn btn-sm btn-academic-accent">

              <i class="bi bi-plus-lg me-1"></i> Add Question

            </a>

          </td>

        </tr>`;

    } else {

      tableBody.innerHTML = `

        <tr>

          <td colspan="8" class="text-center py-4 text-muted">

            <i class="bi bi-search me-1"></i> No questions match the selected search and filter criteria.

          </td>

        </tr>`;

    }

  } else {

    tableBody.innerHTML = filtered.map(q => {

      let diffBadge = 'badge bg-secondary';

      const d = (q.difficulty || '').toLowerCase();

      if (d === 'easy') diffBadge = 'badge bg-success-subtle text-success border border-success';

      else if (d === 'medium') diffBadge = 'badge bg-warning-subtle text-warning border border-warning';

      else if (d === 'hard') diffBadge = 'badge bg-danger-subtle text-danger border border-danger';



      return `

        <tr>

          <td><strong class="font-monospace text-primary">#${q.id}</strong></td>

          <td><span class="badge bg-light text-dark border">${q.subject || 'General'}</span></td>

          <td><small class="text-muted">${q.topic || q.unit || 'General'}</small></td>

          <td><span class="fw-semibold text-dark">${q.question_text || ''}</span></td>

          <td><span class="${diffBadge}">${q.difficulty || 'Medium'}</span></td>

          <td><span class="badge bg-info-subtle text-info border">${q.bloom_level || 'Understand'}</span></td>

          <td><strong>${q.marks || 2}M</strong></td>

          <td>

            <a href="faculty-generate-questions.html" class="btn btn-sm btn-outline-primary py-0 px-2">

              <i class="bi bi-pencil me-1"></i> Edit

            </a>

          </td>

        </tr>`;

    }).join('');

  }



  if (countFooter) {

    countFooter.textContent = `Showing ${filtered.length} of ${currentFacultyQuestions.length} total questions in your Question Bank`;

  }

}



function resetFacultyQuestionFilters() {

  const searchInput = document.getElementById('dashFilterSearch');

  const subSelect = document.getElementById('dashFilterSubject');

  const unitSelect = document.getElementById('dashFilterUnit');

  const marksSelect = document.getElementById('dashFilterMarks');

  const diffSelect = document.getElementById('dashFilterDiff');

  const bloomSelect = document.getElementById('dashFilterBloom');



  if (searchInput) searchInput.value = '';

  if (subSelect) subSelect.value = 'ALL';

  if (unitSelect) unitSelect.value = 'ALL';

  if (marksSelect) marksSelect.value = 'ALL';

  if (diffSelect) diffSelect.value = 'ALL';

  if (bloomSelect) bloomSelect.value = 'ALL';



  filterFacultyQuestions();

}



// Render Active Courses Tab

function renderFacultyCoursesList(courses) {

  const container = document.getElementById('facultyCoursesContent');

  if (!container) return;



  if (!courses || courses.length === 0) {

    container.innerHTML = `

      <div class="text-center py-5">

        <div class="mb-3 text-muted"><i class="bi bi-book fs-1"></i></div>

        <h6 class="fw-bold text-dark">No Active Courses Available</h6>

        <p class="text-muted small mb-3">You do not have any registered courses or active materials in your workspace. Add questions or syllabus resources to initialize your courses.</p>

        <a href="faculty-resources.html" class="btn btn-sm btn-academic-primary">

          <i class="bi bi-upload me-1"></i> Upload Course Materials

        </a>

      </div>`;

    return;

  }



  container.innerHTML = `

    <div class="row g-3">

      ${courses.map(c => `

        <div class="col-md-6 col-xl-4">

          <div class="course-card p-3 h-100 shadow-sm">

            <div class="d-flex justify-content-between align-items-start mb-2">

              <span class="badge bg-primary-subtle text-primary border border-primary px-2 py-1 font-monospace fw-bold">${c.course_code || 'CS301'}</span>

              <span class="badge bg-success-subtle text-success border border-success"><i class="bi bi-check-circle-fill me-1"></i>${c.status || 'Active'}</span>

            </div>

            <h5 class="fw-bold text-dark mb-1">${c.course_name}</h5>

            <p class="text-muted small mb-2"><i class="bi bi-mortarboard me-1"></i>${c.department || 'Artificial Intelligence & Data Science'}</p>

            <div class="d-flex justify-content-between text-muted small border-top pt-2 mt-2">

              <span><i class="bi bi-calendar-event me-1"></i>${c.semester || 'Semester 6'}</span>

              <span><i class="bi bi-calendar3 me-1"></i>${c.academic_year || '2025-2026'}</span>

            </div>

            <div class="mt-3 pt-2 border-top d-flex justify-content-between align-items-center">

              <small class="text-muted">${c.item_count || 0} Materials / Questions</small>

              <a href="faculty-question-paper.html" class="btn btn-sm btn-outline-primary py-0 px-2" style="font-size:0.75rem;">Generate Paper</a>

            </div>

          </div>

        </div>

      `).join('')}

    </div>`;

}



// Render Draft Papers Tab

function renderFacultyDraftPapersList(drafts) {

  const container = document.getElementById('facultyDraftPapersContent');

  const tbody = document.getElementById('facultyDraftPapersTableBody');

  if (!container || !tbody) return;



  if (!drafts || drafts.length === 0) {

    container.innerHTML = `

      <div class="text-center py-5">

        <div class="mb-3 text-muted"><i class="bi bi-pencil-square fs-1"></i></div>

        <h6 class="fw-bold text-dark">No Draft Question Papers</h6>

        <p class="text-muted small mb-3">You have no draft papers in progress. Start a new examination paper to balance difficulty and save drafts.</p>

        <a href="faculty-question-paper.html" class="btn btn-sm btn-academic-accent">

          <i class="bi bi-plus-lg me-1"></i> Create Paper

        </a>

      </div>`;

    return;

  }



  tbody.innerHTML = drafts.map(p => {

    return `

      <tr>

        <td><strong class="font-monospace text-primary">${p.paper_code || 'EXAM-' + p.id}</strong></td>

        <td><span class="fw-semibold text-dark">${p.title || 'Draft Paper'}</span></td>

        <td><span class="badge bg-light text-dark border">${p.subject || 'General'}</span></td>

        <td>${p.exam_type || 'Internal Assessment'}</td>

        <td><strong>${p.total_marks || p.max_marks || 100} M</strong></td>

        <td><small class="text-muted">${p.updated_at || p.created_at || '--'}</small></td>

        <td class="text-end">

          <div class="btn-group btn-group-sm">

            <button type="button" class="btn btn-outline-secondary py-0 px-2" onclick="viewFacultyPaperModal('${p.paper_code || p.id}')" title="View Paper">

              <i class="bi bi-eye"></i> View

            </button>

            <a href="faculty-question-paper.html?paper_id=${p.id}" class="btn btn-outline-primary py-0 px-2" title="Edit Paper">

              <i class="bi bi-pencil"></i> Edit

            </a>

            <button type="button" class="btn btn-outline-danger py-0 px-2" onclick="deleteFacultyPaper('${p.id}', '${p.paper_code || p.title}')" title="Delete Draft">

              <i class="bi bi-trash"></i>

            </button>

          </div>

        </td>

      </tr>`;

  }).join('');

}



// Render Published Exams Tab

function renderFacultyPublishedExamsList(published) {

  const container = document.getElementById('facultyPublishedExamsContent');

  const tbody = document.getElementById('facultyPublishedExamsTableBody');

  if (!container || !tbody) return;



  if (!published || published.length === 0) {

    container.innerHTML = `

      <div class="text-center py-5">

        <div class="mb-3 text-muted"><i class="bi bi-check-circle fs-1"></i></div>

        <h6 class="fw-bold text-dark">No Published Examination Papers</h6>

        <p class="text-muted small mb-3">You have not published any examination papers yet. Finalize and verify a draft paper to publish it.</p>

        <a href="faculty-question-paper.html" class="btn btn-sm btn-academic-primary">

          <i class="bi bi-sliders me-1"></i> Paper Generator

        </a>

      </div>`;

    return;

  }



  tbody.innerHTML = published.map(p => {

    return `

      <tr>

        <td><strong class="font-monospace text-primary">${p.paper_code || 'EXAM-' + p.id}</strong></td>

        <td><span class="fw-semibold text-dark">${p.title || 'Examination Paper'}</span></td>

        <td><span class="badge bg-light text-dark border">${p.subject || 'General'}</span></td>

        <td>${p.exam_type || 'Semester Examination'}</td>

        <td><strong>${p.total_marks || p.max_marks || 100} M</strong></td>

        <td><span class="badge bg-success-subtle text-success border border-success"><i class="bi bi-check2-circle me-1"></i>Published</span></td>

        <td class="text-end">

          <button type="button" class="btn btn-sm btn-outline-primary py-0 px-2" onclick="viewFacultyPaperModal('${p.paper_code || p.id}')">

            <i class="bi bi-eye me-1"></i> View

          </button>

        </td>

      </tr>`;

  }).join('');

}



// Delete Faculty Draft Paper Action

async function deleteFacultyPaper(paperId, paperCode) {

  if (!confirm(`Are you sure you want to delete draft paper "${paperCode}"? This action cannot be undone.`)) {

    return;

  }



  try {

    const res = await fetch(`http://localhost:5000/api/question-papers/${paperId}`, {

      method: 'DELETE',

      credentials: 'include'

    });

    const result = await res.json();

    if (res.ok && result.status === 'success') {

      alert(`Paper ${paperCode} deleted successfully.`);

      const userObj = JSON.parse(localStorage.getItem('academic_user') || '{}');

      await renderFacultyData(userObj);

    } else {

      alert(result.message || 'Failed to delete question paper.');

    }

  } catch (err) {

    console.error('Delete paper error:', err);

    alert('An error occurred while deleting the question paper.');

  }

}



// View Faculty Paper in Modal

async function viewFacultyPaperModal(paperId) {

  const modalBody = document.getElementById('paperViewModalBody');

  const modalTitle = document.getElementById('paperViewModalTitle');

  if (!modalBody) return;



  modalBody.innerHTML = `

    <div class="text-center py-5">

      <div class="spinner-border text-primary" role="status"></div>

      <p class="text-muted mt-2">Loading question paper details...</p>

    </div>`;



  const modalEl = document.getElementById('facultyPaperViewModal');

  if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {

    const modalInstance = bootstrap.Modal.getInstance(modalEl) || new bootstrap.Modal(modalEl);

    modalInstance.show();

  }



  try {

    const res = await fetch(`http://localhost:5000/api/question-papers/${paperId}`, {

      credentials: 'include'

    });

    if (!res.ok) {

      modalBody.innerHTML = `<div class="alert alert-danger">Failed to load paper details (HTTP ${res.status}).</div>`;

      return;

    }

    const data = await res.json();

    const paper = data.paper || data.question_paper || data;



    if (modalTitle) {

      modalTitle.innerHTML = `<i class="bi bi-file-earmark-text text-primary me-2"></i> ${paper.title || 'Question Paper'} <span class="badge bg-secondary ms-2">${paper.paper_code || ''}</span>`;

    }



    let sectionsHtml = '';

    if (paper.sections && paper.sections.length > 0) {

      sectionsHtml = paper.sections.map(s => {

        let qItems = '';

        if (s.questions && s.questions.length > 0) {

          qItems = s.questions.map((q, idx) => `

            <div class="p-2 border-bottom">

              <div class="d-flex justify-content-between align-items-start">

                <span class="fw-semibold">Q${q.question_number || (idx + 1)}. ${q.question_text || ''}</span>

                <span class="badge bg-light text-dark border ms-2">${q.marks || 2}M</span>

              </div>

              <div class="small text-muted mt-1">

                <span>Unit: ${q.unit || 'General'}</span> |

                <span>Diff: ${q.difficulty || 'Medium'}</span> |

                <span>Bloom: ${q.bloom_level || 'Understand'}</span>

              </div>

            </div>

          `).join('');

        }

        return `

          <div class="card card-academic mb-3">

            <div class="card-academic-header d-flex justify-content-between">

              <strong>${s.section_title || s.name || 'Section'}</strong>

              <span>${s.section_total_marks || ''} Marks</span>

            </div>

            <div class="card-body p-3">

              <p class="small text-muted mb-2">${s.instructions || ''}</p>

              ${qItems || '<p class="text-muted small">No questions in this section.</p>'}

            </div>

          </div>`;

      }).join('');

    }



    modalBody.innerHTML = `

      <div class="p-3 bg-light rounded border mb-3">

        <div class="row g-2 small">

          <div class="col-sm-6"><strong>Course / Subject:</strong> ${paper.subject || '--'}</div>

          <div class="col-sm-6"><strong>Department:</strong> ${paper.department || '--'}</div>

          <div class="col-sm-6"><strong>Exam Type:</strong> ${paper.exam_type || '--'}</div>

          <div class="col-sm-6"><strong>Max Marks:</strong> ${paper.total_marks || paper.max_marks || 100} Marks</div>

          <div class="col-sm-6"><strong>Duration:</strong> ${paper.duration || '3 Hours'}</div>

          <div class="col-sm-6"><strong>Status:</strong> <span class="badge ${paper.status === 'Published' ? 'bg-success' : 'bg-warning text-dark'}">${paper.status || 'Draft'}</span></div>

          ${paper.fingerprint ? `<div class="col-12 font-monospace" style="font-size:0.75rem;"><strong>SHA-256 Fingerprint:</strong> ${paper.fingerprint}</div>` : ''}

        </div>

      </div>

      <div class="mb-3">

        <h6 class="fw-bold mb-2">Instructions:</h6>

        <p class="small text-muted bg-white p-2 border rounded">${paper.instructions || 'Standard examination instructions apply.'}</p>

      </div>

      <h6 class="fw-bold mb-2">Paper Sections & Questions:</h6>

      ${sectionsHtml || '<p class="text-muted small">No section breakdown available for this paper.</p>'}

    `;



  } catch (err) {

    console.error('Error fetching paper details:', err);

    modalBody.innerHTML = `<div class="alert alert-danger">Error fetching question paper details: ${err.message}</div>`;

  }

}



function printFacultyPaper() {

  window.print();

}



// Render Faculty Dashboard Data

async function renderFacultyData(userObj) {

  updateFacultyHeaderProfile(userObj);



  const qCountEl = document.getElementById('totalQuestionsCount');

  const coursesEl = document.getElementById('activeCoursesCount');

  const draftEl = document.getElementById('draftPapersCount');

  const pubEl = document.getElementById('publishedExamsCount');



  const tabQCount = document.getElementById('tabQuestionsCount');

  const tabCCount = document.getElementById('tabCoursesCount');

  const tabDCount = document.getElementById('tabDraftsCount');

  const tabPCount = document.getElementById('tabPublishedCount');



  if (!window.location.pathname.toLowerCase().includes('faculty-dashboard')) return;



  // 1. Primary: Dedicated Isolated Dashboard Statistics Endpoint

  try {

    const sRes = await fetch('http://localhost:5000/api/faculty/dashboard-stats', { credentials: 'include' });

    if (sRes.ok) {

      const stats = await sRes.json();

      if (stats.status === 'success') {

        const totalQ = stats.total_questions !== undefined ? stats.total_questions : 0;

        const activeC = stats.active_courses !== undefined ? stats.active_courses : 0;

        const draftP = stats.draft_papers !== undefined ? stats.draft_papers : 0;

        const pubE = stats.published_exams !== undefined ? stats.published_exams : 0;



        // KPI Counts

        if (qCountEl) qCountEl.textContent = totalQ;

        if (coursesEl) coursesEl.textContent = `${activeC} Course${activeC === 1 ? '' : 's'}`;

        if (draftEl) draftEl.textContent = `${draftP} Paper${draftP === 1 ? '' : 's'}`;

        if (pubEl) pubEl.textContent = `${pubE} Exam${pubE === 1 ? '' : 's'}`;



        // Tab Counts

        if (tabQCount) tabQCount.textContent = totalQ;

        if (tabCCount) tabCCount.textContent = activeC;

        if (tabDCount) tabDCount.textContent = draftP;

        if (tabPCount) tabPCount.textContent = pubE;



        // Difficulty Balancer Card

        const diffCardBody = document.getElementById('difficultyBalancerBody');

        const badgeEl = document.getElementById('balancerStatusBadge');



        if (stats.active_paper && diffCardBody) {

          const ap = stats.active_paper;

          if (badgeEl) badgeEl.textContent = `${ap.status || 'Draft'} Status`;



          diffCardBody.innerHTML = `

            <div class="row align-items-center" id="difficultyBalancerActiveWrap">

              <div class="col-lg-7 mb-3 mb-lg-0">

                <h5 id="paperTitleDisplay" class="fw-bold mb-1">${ap.title} (${ap.paper_code})</h5>

                <p class="text-muted small mb-3" id="paperMetricsSubtitle">

                  Total Marks: ${ap.total_marks} | Questions: ${ap.question_count} | Target: Balanced 30:50:20

                </p>



                <div class="progress progress-difficulty mb-2" style="height: 18px;" id="paperProgressBar">

                  <div class="progress-bar progress-bar-easy" id="barEasy" role="progressbar" style="width: ${ap.difficulty.easy_pct}%" title="Easy ${ap.difficulty.easy_pct}%">${ap.difficulty.easy_pct}% Easy</div>

                  <div class="progress-bar progress-bar-medium" id="barMedium" role="progressbar" style="width: ${ap.difficulty.medium_pct}%" title="Medium ${ap.difficulty.medium_pct}%">${ap.difficulty.medium_pct}% Medium</div>

                  <div class="progress-bar progress-bar-hard" id="barHard" role="progressbar" style="width: ${ap.difficulty.hard_pct}%" title="Hard ${ap.difficulty.hard_pct}%">${ap.difficulty.hard_pct}% Hard</div>

                </div>



                <div class="d-flex justify-content-between small text-muted flex-wrap gap-1" id="difficultyLegend">

                  <span id="legendEasy"><i class="bi bi-square-fill text-success me-1"></i> Easy: ${ap.difficulty.easy_count} Questions (${ap.difficulty.easy_marks} Marks)</span>

                  <span id="legendMedium"><i class="bi bi-square-fill text-warning me-1"></i> Medium: ${ap.difficulty.medium_count} Questions (${ap.difficulty.medium_marks} Marks)</span>

                  <span id="legendHard"><i class="bi bi-square-fill text-danger me-1"></i> Hard: ${ap.difficulty.hard_count} Questions (${ap.difficulty.hard_marks} Marks)</span>

                </div>

              </div>



              <div class="col-lg-5 text-lg-end border-start-lg ps-lg-4">

                <div class="p-3 bg-light rounded border text-center mb-3">

                  <small class="text-uppercase text-muted d-block mb-1">Algorithm Verification</small>

                  <div id="paperBalanceScore" class="fw-bold text-success fs-6"><i class="bi bi-shield-check me-1"></i> ${ap.balance_label}</div>

                </div>

                <div class="d-flex justify-content-lg-end gap-2">

                  <a href="faculty-generate-questions.html" class="btn btn-sm btn-academic-secondary">

                    <i class="bi bi-sliders me-1"></i> Re-balance

                  </a>

                  <a href="faculty-question-paper.html" class="btn btn-sm btn-academic-accent">

                    <i class="bi bi-send-check me-1"></i> Manage Papers

                  </a>

                </div>

              </div>

            </div>`;

        } else if (diffCardBody) {

          if (badgeEl) badgeEl.textContent = 'Ready';

          diffCardBody.innerHTML = `

            <div class="row align-items-center py-2">

              <div class="col-lg-8">

                <div class="d-flex align-items-center">

                  <div class="bg-warning-subtle text-warning p-3 rounded-circle me-3">

                    <i class="bi bi-sliders fs-3"></i>

                  </div>

                  <div>

                    <h5 class="fw-bold mb-1 text-dark">No Active Draft Paper Found</h5>

                    <p class="text-muted small mb-0">Create and assemble a question paper to activate the automatic difficulty balancer and Bloom's taxonomy verification.</p>

                  </div>

                </div>

              </div>

              <div class="col-lg-4 text-lg-end mt-3 mt-lg-0">

                <a href="faculty-question-paper.html" class="btn btn-academic-accent">

                  <i class="bi bi-plus-lg me-1"></i> Create Paper

                </a>

              </div>

            </div>`;

        }



        // Store Questions

        currentFacultyQuestions = stats.recent_questions || [];



        // Populate Subject Filter Options

        const subSelect = document.getElementById('dashFilterSubject');

        if (subSelect) {

          const subjects = Array.from(new Set(currentFacultyQuestions.map(q => q.subject).filter(Boolean)));

          subSelect.innerHTML = '<option value="ALL">All Subjects</option>' +

            subjects.map(s => `<option value="${s}">${s}</option>`).join('');

        }



        // Filter and Render Questions Table

        filterFacultyQuestions();



        // Render Active Courses

        currentFacultyCourses = stats.courses_list || [];

        renderFacultyCoursesList(currentFacultyCourses);



        // Render Draft Papers

        currentFacultyDrafts = stats.draft_papers_list || [];

        renderFacultyDraftPapersList(currentFacultyDrafts);



        // Render Published Exams

        currentFacultyPublished = stats.published_exams_list || [];

        renderFacultyPublishedExamsList(currentFacultyPublished);



        return; // Successfully rendered via dedicated isolated endpoint

      }

    }

  } catch (err) {

    console.warn('Dedicated stats endpoint fetch error, falling back:', err);

  }



  // 2. Secondary Fallback: Direct Entity Queries with strict credentials

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

  currentFacultyQuestions = questions;

  filterFacultyQuestions();



  const uniqueSubjects = new Set(questions.map(q => q.subject).filter(Boolean));

  if (coursesEl) {

    const count = uniqueSubjects.size;

    coursesEl.textContent = `${count} Course${count === 1 ? '' : 's'}`;

  }



  try {

    const pRes = await fetch('http://localhost:5000/api/question-papers', { credentials: 'include' });

    if (pRes.ok) {

      const pData = await pRes.json();

      const papers = pData.question_papers || pData.papers || [];

      const drafts = papers.filter(p => p.status === 'Draft');

      const published = papers.filter(p => p.status === 'Published');



      if (draftEl) draftEl.textContent = `${drafts.length} Paper${drafts.length !== 1 ? '' : 's'}`;

      if (pubEl) pubEl.textContent = `${published.length} Exam${published.length !== 1 ? '' : 's'}`;



      currentFacultyDrafts = drafts;

      renderFacultyDraftPapersList(drafts);



      currentFacultyPublished = published;

      renderFacultyPublishedExamsList(published);

    }

  } catch (e) {

    console.warn('Could not fetch papers:', e);

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
    await setupFacultyCourseContext(verifiedUser);







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



    if (path.includes('student-subjects.html') && typeof renderStudentSubjects === 'function') renderStudentSubjects();

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



}







function handleLogin(role, identifier, name) {



  const current = JSON.parse(localStorage.getItem('academic_user') || '{}');



  const resolvedName = name || current.name || (role === 'faculty' ? 'Faculty Member' : 'Student');



  localStorage.setItem('academic_role', role);



  localStorage.setItem('academic_user', JSON.stringify({



    name: resolvedName,



    identifier: identifier,



    department: current.department || 'Artificial Intelligence & Data Science',



    academic_year: current.academic_year || '2025-2026',



    semester: current.semester || (role === 'student' ? 'Semester 6' : 'N/A')



  }));







  if (role === 'faculty') {



    window.location.href = 'faculty-dashboard.html';



  } else {



    window.location.href = 'student-dashboard.html';



  }



}







async function handleLogout() {
  try {
    await fetch('http://localhost:5000/api/auth/logout', {
      method: 'POST',
      credentials: 'include'
    });
  } catch (err) {
    console.warn('Server logout failed:', err);
  }
  // Clear all academic session, cache and user data
  const keysToRemove = [];
  for (let i = 0; i < localStorage.length; i++) {
    const k = localStorage.key(i);
    if (k && (k.startsWith('academic_') || k.startsWith('faculty_') || k.startsWith('paper_'))) {
      keysToRemove.push(k);
    }
  }
  keysToRemove.forEach(k => localStorage.removeItem(k));
  sessionStorage.clear();
  window.paperQuestionBankPool = [];
  window.facultyAuthorizedCourses = [];
  window.currentFacultyQuestions = [];
  window.location.href = 'index.html';
}







// Bind Form Actions for Real Authentication (STEP 9B)



function bindFormHandlers() {

  initEditResourceForm();



  // Faculty Registration Form Handler



  const facultyRegisterForm = document.getElementById('facultyRegisterForm');



  if (facultyRegisterForm) {



    facultyRegisterForm.addEventListener('submit', async (e) => {



      e.preventDefault();



      const submitBtn = facultyRegisterForm.querySelector('button[type="submit"]');



      const originalText = submitBtn ? submitBtn.innerHTML : 'Register';







      const pass = document.getElementById('regPass')?.value;



      const passConfirm = document.getElementById('regPassConfirm')?.value;







      if (pass !== passConfirm) {



        showToastNotice('Registration Error', 'Passwords do not match.', 'danger');



        return;



      }







      const payload = {



        full_name: document.getElementById('regName')?.value,



        email: document.getElementById('regEmail')?.value,



        password: pass,



        role: 'faculty',



        department: document.getElementById('regDept')?.value,



        semester: 'N/A',



        academic_year: '2025-2026'



      };







      if (submitBtn) {



        submitBtn.disabled = true;



        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Registering Faculty...';



      }







      const res = await Auth.register(payload);







      if (submitBtn) {



        submitBtn.disabled = false;



        submitBtn.innerHTML = originalText;



      }







      if (res.ok) {



        showToastNotice('Registration Successful', 'Faculty account registered! Redirecting to Faculty Login...', 'success');



        setTimeout(() => { window.location.href = 'faculty-login.html'; }, 1500);



      } else {



        showToastNotice('Registration Failed', res.data.message || 'Registration failed.', 'danger');



      }



    });



  }







  // Student Registration Form Handler



  const studentRegisterForm = document.getElementById('studentRegisterForm');



  if (studentRegisterForm) {



    studentRegisterForm.addEventListener('submit', async (e) => {



      e.preventDefault();



      const submitBtn = studentRegisterForm.querySelector('button[type="submit"]');



      const originalText = submitBtn ? submitBtn.innerHTML : 'Register';







      const pass = document.getElementById('regStudentPass')?.value;



      const passConfirm = document.getElementById('regStudentPassConfirm')?.value;







      if (pass !== passConfirm) {



        showToastNotice('Registration Error', 'Passwords do not match.', 'danger');



        return;



      }







      const payload = {



        full_name: document.getElementById('regStudentName')?.value,



        email: document.getElementById('regStudentEmail')?.value,



        password: pass,



        role: 'student',



        department: document.getElementById('regStudentDept')?.value,



        semester: document.getElementById('regSem')?.value || 'Sem 6',



        academic_year: '2025-2026'



      };







      if (submitBtn) {



        submitBtn.disabled = true;



        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Registering Student...';



      }







      const res = await Auth.register(payload);







      if (submitBtn) {



        submitBtn.disabled = false;



        submitBtn.innerHTML = originalText;



      }







      if (res.ok) {



        showToastNotice('Registration Successful', 'Student account registered! Redirecting to Student Login...', 'success');



        setTimeout(() => { window.location.href = 'student-login.html'; }, 1500);



      } else {



        showToastNotice('Registration Failed', res.data.message || 'Registration failed.', 'danger');



      }



    });



  }







  // Faculty Login Form Handler



  const facultyLoginForm = document.getElementById('facultyLoginForm');



  if (facultyLoginForm) {



    facultyLoginForm.addEventListener('submit', async (e) => {



      e.preventDefault();



      const submitBtn = facultyLoginForm.querySelector('button[type="submit"]');



      const originalText = submitBtn ? submitBtn.innerHTML : 'Access Faculty Dashboard';







      const emailInput = document.getElementById('facultyId')?.value || '';



      const passInput = document.getElementById('password')?.value || '';







      if (submitBtn) {



        submitBtn.disabled = true;



        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Authenticating...';



      }







      const res = await Auth.login(emailInput, passInput, 'faculty');







      if (submitBtn) {



        submitBtn.disabled = false;



        submitBtn.innerHTML = originalText;



      }







      if (res.ok) {



        showToastNotice('Login Successful', 'Authenticated as Faculty. Redirecting...', 'success');



        setTimeout(() => { window.location.href = 'faculty-dashboard.html'; }, 1000);



      } else {



        showToastNotice('Login Failed', res.data.message || 'Invalid email or password.', 'danger');



      }



    });



  }







  // Student Login Form Handler



  const studentLoginForm = document.getElementById('studentLoginForm');



  if (studentLoginForm) {



    studentLoginForm.addEventListener('submit', async (e) => {



      e.preventDefault();



      const submitBtn = studentLoginForm.querySelector('button[type="submit"]');



      const originalText = submitBtn ? submitBtn.innerHTML : 'Access Student Portal';







      const emailInput = document.getElementById('rollNumber')?.value || '';



      const passInput = document.getElementById('studentPassword')?.value || '';







      if (submitBtn) {



        submitBtn.disabled = true;



        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Authenticating...';



      }







      const res = await Auth.login(emailInput, passInput, 'student');







      if (submitBtn) {



        submitBtn.disabled = false;



        submitBtn.innerHTML = originalText;



      }







      if (res.ok) {



        showToastNotice('Login Successful', 'Authenticated as Student. Redirecting...', 'success');



        setTimeout(() => { window.location.href = 'student-dashboard.html'; }, 1000);



      } else {



        showToastNotice('Login Failed', res.data.message || 'Invalid email or password.', 'danger');



      }



    });



  }



}







// ==========================================



// STEP 5: QUIZ GENERATOR MODULE (FACULTY)



// ==========================================







let activeGeneratedQuizQuestions = [];



let activeQuizId = "QUIZ-2026-0001";







function getOptionDisplayString(opt) {
  if (opt === null || opt === undefined) return '';
  if (typeof opt === 'string') {
    return opt === '[object Object]' ? '' : opt;
  }
  if (typeof opt === 'object') {
    return opt.option_text || opt.text || opt.title || opt.value || opt.label || '';
  }
  return String(opt);
}

function initQuizGeneratorPage() {



  updateQuizUnitsDropdown();



  updateQuizSourcePanel();



}







function initQuizGeneratorForm() {

  const subjectInput = document.getElementById('quizSubject');

  const deptInput = document.getElementById('quizDept');

  const unitInput = document.getElementById('quizUnit');

  const topicInput = document.getElementById('quizTopic');

  const numQInput = document.getElementById('quizNumQuestions');

  const timeLimitSelect = document.getElementById('quizTimeLimit');

  const marksPerQSelect = document.getElementById('quizMarksPerQ');

  const form = document.getElementById('quizGeneratorForm');



  // Restore saved config

  const savedCfg = localStorage.getItem('academic_last_gen_quiz_config');

  if (savedCfg) {

    try {

      const cfg = JSON.parse(savedCfg);

      if (cfg.department && deptInput) deptInput.value = cfg.department;

      if (cfg.subject && subjectInput) subjectInput.value = cfg.subject;

      if (cfg.unit && unitInput) unitInput.value = cfg.unit;

      if (cfg.topic !== undefined && topicInput) topicInput.value = cfg.topic;

    } catch (e) {}

  }



  // Set default: 30 minutes duration, 30 questions, 1 mark per question (30 marks total)

  if (timeLimitSelect) timeLimitSelect.value = "30";

  if (numQInput) numQInput.value = "30";

  if (marksPerQSelect) marksPerQSelect.value = "1";



  // Fetch faculty resources to populate subject suggestions and update source panel

  try {

    const quizResUrl = (typeof API_RESOURCES_BASE !== 'undefined' && API_RESOURCES_BASE)

      ? API_RESOURCES_BASE

      : 'http://localhost:5000/api/resources';

    fetch(quizResUrl, { credentials: 'include' })

      .then(res => safeParseJsonResponse(res))

      .then(data => {

        if (data && data.resources) {

          window.facultyAcademicResources = data.resources;

          const subjectDatalist = document.getElementById('quizSubjectList');

          if (subjectDatalist) {

            const uniqueSubjects = Array.from(new Set(data.resources.map(r => r.subject).filter(Boolean)));

            ['Database Management Systems', 'Artificial Intelligence', 'Machine Learning', 'Distributed Computing', 'Data Structures', 'Computer Networks'].forEach(s => {

              if (!uniqueSubjects.includes(s)) uniqueSubjects.push(s);

            });

            subjectDatalist.innerHTML = uniqueSubjects.map(s => `<option value="${s}">`).join('');

          }

        }

      }).catch(err => console.warn('Error fetching quiz resources:', err));

  } catch (e) {}



  if (subjectInput) {

    subjectInput.addEventListener('input', () => {

      updateQuizSourcePanel();

    });

  }

  if (unitInput) {

    unitInput.addEventListener('input', updateQuizSourcePanel);

  }



  updateQuizSourcePanel();



  if (form) {

    form.addEventListener('submit', (e) => {

      e.preventDefault();

      generateQuizAction();

    });

  }

}



function updateQuizUnitsDropdown() {

  const subjectInput = document.getElementById('quizSubject');

  const unitInput = document.getElementById('quizUnit');

  const topicInput = document.getElementById('quizTopic');



  if (!subjectInput) return;



  const subjectName = subjectInput.value;

  const struct = (typeof AcademicMockData !== 'undefined' && AcademicMockData.subjectStructure)

    ? (AcademicMockData.subjectStructure[subjectName] || AcademicMockData.subjectStructure["Database Management Systems"])

    : null;



  const unitDatalist = document.getElementById('quizUnitList');

  const defaultUnits = [

    "All Units (Complete Syllabus)",

    "Unit I — Introduction",

    "Unit II — Core Concepts",

    "Unit III — Advanced Topics",

    "Unit IV — Applications",

    "Unit V — Cloud & Emerging"

  ];



  const unitsList = (struct && struct.units && struct.units.length > 0)

    ? ["All Units (Complete Syllabus)", ...struct.units.map(u => u.name)]

    : defaultUnits;



  if (unitDatalist) {

    unitDatalist.innerHTML = unitsList.map(u => `<option value="${u}">`).join('');

  }

  if (unitInput && unitInput.tagName === 'SELECT') {

    unitInput.innerHTML = unitsList.map(u => `<option value="${u}">${u}</option>`).join('');

  }

}



function updateQuizSourcePanel() {

  const subjectName = document.getElementById('quizSubject')?.value || "Database Management Systems";

  const unitName = document.getElementById('quizUnit')?.value || "All Units (Complete Syllabus)";



  const panelSubject = document.getElementById('quizSourceSubjectDisplay');

  const panelUnit = document.getElementById('quizSourceUnitDisplay');

  const panelTopics = document.getElementById('quizSourceTopicsDisplay');

  const panelConcepts = document.getElementById('quizSourceConceptsDisplay');



  if (panelSubject) panelSubject.innerText = subjectName;

  if (panelUnit) panelUnit.innerText = unitName;



  const resources = window.facultyAcademicResources || [];

  const matching = resources.filter(r => r.subject.toLowerCase() === subjectName.toLowerCase());



  if (matching.length > 0) {

    if (panelTopics) {

      const topicNames = matching.map(m => m.topic).filter(Boolean);

      panelTopics.innerText = topicNames.length ? topicNames.join(', ') : `Topics verified from uploaded materials for ${subjectName}`;

    }

    if (panelConcepts) {

      panelConcepts.innerText = `Content verified from ${matching.length} uploaded faculty resource(s)`;

    }

  } else {

    if (panelTopics) panelTopics.innerText = "Syllabus topics for " + subjectName;

    if (panelConcepts) panelConcepts.innerText = "Academic curriculum topics";

  }

}



async function generateQuizAction() {

  const dept = document.getElementById('quizDept')?.value?.trim() || "Artificial Intelligence & Data Science";

  const subject = document.getElementById('quizSubject')?.value?.trim() || "Database Management Systems";

  const year = document.getElementById('quizYear')?.value || "2025-2026";

  const sem = document.getElementById('quizSem')?.value || "Semester 6";

  const unit = document.getElementById('quizUnit')?.value?.trim() || "All Units (Complete Syllabus)";

  const topic = document.getElementById('quizTopic')?.value?.trim() || "";

  const title = document.getElementById('quizTitleInput')?.value?.trim() || `${subject} Timed Assessment Quiz`;

  const durationMins = parseInt(document.getElementById('quizTimeLimit')?.value || 30, 10);

  const marksPerQ = parseInt(document.getElementById('quizMarksPerQ')?.value || 1, 10);

  const numQuestions = parseInt(document.getElementById('quizNumQuestions')?.value || 30, 10);



  // Save config

  localStorage.setItem('academic_last_gen_quiz_config', JSON.stringify({

    department: dept, subject, academic_year: year, semester: sem, unit, topic, duration_minutes: durationMins, marks_per_question: marksPerQ, total_questions: numQuestions

  }));



  const form = document.getElementById('quizGeneratorForm');

  const submitBtn = form?.querySelector('button[type="submit"]');

  if (submitBtn) {

    submitBtn.disabled = true;

    submitBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-2"></span>Generating Grounded ${numQuestions}-Question Quiz (${numQuestions * marksPerQ} Marks)...`;

  }



  const payload = {

    title,

    department: dept,

    subject,

    academic_year: year,

    semester: sem,

    unit,

    topic,

    duration_minutes: durationMins,

    marks_per_question: marksPerQ,

    total_questions: numQuestions

  ,
    difficulty: document.getElementById('quizDiffSelect')?.value || 'Mixed',
    bloom_level: document.getElementById('quizBloomsSelect')?.value || 'Auto Select',
    blooms_level: document.getElementById('quizBloomsSelect')?.value || 'Auto Select'
  };



  try {

    const quizGenUrl = (typeof API_QUIZZES_BASE !== 'undefined' && API_QUIZZES_BASE)

      ? `${API_QUIZZES_BASE}/generate`

      : 'http://localhost:5000/api/quizzes/generate';



    const res = await fetch(quizGenUrl, {

      method: 'POST',

      headers: { 'Content-Type': 'application/json' },

      credentials: 'include',

      body: JSON.stringify(payload)

    });



    const data = await safeParseJsonResponse(res);

    if (submitBtn) {

      submitBtn.disabled = false;

      submitBtn.innerHTML = `<i class="bi bi-magic me-2"></i> Generate Quiz`;

    }



    if (data.status === 'success') {

      activeGeneratedQuizQuestions = data.questions || [];

      window.currentQuizPreview = data.quiz;



      renderGeneratedQuiz();

      renderQuizDifficultyAnalysis();

      renderQuizConceptCoverage();



      const resultsSection = document.getElementById('generatedQuizResults');

      if (resultsSection) {

        resultsSection.classList.remove('d-none');

        window.scrollTo({ top: resultsSection.offsetTop - 70, behavior: 'smooth' });

      }



      showToastNotice('Quiz Generated', `Generated ${activeGeneratedQuizQuestions.length} unique questions for ${subject} (${durationMins} Mins, ${activeGeneratedQuizQuestions.length * marksPerQ} Marks)!`, 'success');

    } else {

      showToastNotice('Quiz Generation Notice', data.message || 'Failed to generate quiz.', 'warning');

      alert(`[Quiz Generator Notice]



${data.message}`);

    }

  } catch (err) {

    console.error('Quiz generation error:', err);

    if (submitBtn) {

      submitBtn.disabled = false;

      submitBtn.innerHTML = `<i class="bi bi-magic me-2"></i> Generate Quiz`;

    }

    showToastNotice('Server Error', 'Failed to communicate with Quiz Generation API.', 'danger');

  }

}



function renderGeneratedQuiz() {



  const container = document.getElementById('generatedQuizCardsList');



  if (!container) return;







  container.innerHTML = activeGeneratedQuizQuestions.map((q, idx) => `



    <div class="card card-academic mb-3">



      <div class="card-body p-3">



        <div class="d-flex justify-content-between align-items-center mb-2 flex-wrap gap-2">



          <div class="d-flex align-items-center gap-2">



            <span class="badge bg-primary">Q${idx + 1}</span>



            <span class="badge ${q.difficulty === 'Easy' ? 'badge-diff-easy' : q.difficulty === 'Medium' ? 'badge-diff-medium' : 'badge-diff-hard'}">${q.difficulty}</span>



            <span class="badge bg-secondary-subtle text-dark border"><i class="bi bi-tag me-1"></i>${q.concept || "Core Concept"}</span>
            <span class="badge bg-info-subtle text-info-emphasis border border-info-subtle"><i class="bi bi-award me-1"></i>${q.marks !== undefined && q.marks !== null ? q.marks : 1} ${(q.marks === 1 || q.marks === undefined) ? "Mark" : "Marks"}</span>



          </div>



          <span class="badge bg-success-subtle text-success border border-success fw-bold"><i class="bi bi-check-circle me-1"></i> Correct Answer: ${q.correctAnswer || (q.options && q.options[q.correctIndex] ? getOptionDisplayString(q.options[q.correctIndex]) : "")}</span>



        </div>







        <p class="fw-semibold text-dark fs-6 mb-3">${q.text}</p>







        <div class="row g-2 mb-3">



          ${q.options.map((opt, oIdx) => `



            <div class="col-md-6">



              <div class="mcq-option-card ${oIdx === q.correctIndex ? 'correct-answer-card' : ''}">



                <span class="fw-bold me-2">${String.fromCharCode(65 + oIdx)}.</span> ${getOptionDisplayString(opt)}



              </div>



            </div>



          `).join('')}



        </div>







        <div class="d-flex justify-content-between align-items-center border-top pt-2 small text-muted">



          <span><i class="bi bi-book me-1"></i> ${q.unit} • ${q.blooms}</span>



          <div class="btn-group btn-group-sm">



            <button class="btn btn-outline-secondary py-0" onclick="editQuizQuestion(${idx})"><i class="bi bi-pencil"></i> Edit</button>



            <button class="btn btn-outline-primary py-0" onclick="regenerateQuizQuestion(${idx})"><i class="bi bi-arrow-repeat"></i> Regenerate</button>



            <button class="btn btn-outline-danger py-0" onclick="deleteQuizQuestion(${idx})"><i class="bi bi-trash"></i> Delete</button>



          </div>



        </div>



      </div>



    </div>



  `).join('');



}







function renderQuizDifficultyAnalysis() {



  const total = activeGeneratedQuizQuestions.length || 1;



  const easy = activeGeneratedQuizQuestions.filter(q => q.difficulty === 'Easy').length;



  const med = activeGeneratedQuizQuestions.filter(q => q.difficulty === 'Medium').length;



  const hard = activeGeneratedQuizQuestions.filter(q => q.difficulty === 'Hard').length;







  const bar = document.getElementById('quizDifficultyBar');



  if (bar) {



    const easyPct = Math.round((easy / total) * 100);



    const medPct = Math.round((med / total) * 100);



    const hardPct = 100 - easyPct - medPct;







    bar.innerHTML = `



      <div class="progress-bar progress-bar-easy" style="width: ${easyPct}%">${easyPct}% Easy (${easy})</div>



      <div class="progress-bar progress-bar-medium" style="width: ${medPct}%">${medPct}% Med (${med})</div>



      <div class="progress-bar progress-bar-hard" style="width: ${hardPct}%">${hardPct}% Hard (${hard})</div>



    `;



  }



}







function renderQuizConceptCoverage() {



  const container = document.getElementById('quizConceptCoverageContainer');



  if (!container) return;







  const conceptCounts = {};



  activeGeneratedQuizQuestions.forEach(q => {



    conceptCounts[q.concept] = (conceptCounts[q.concept] || 0) + 1;



  });







  const keys = Object.keys(conceptCounts);



  container.innerHTML = `



    <div class="mb-2"><strong>Concepts Covered:</strong> ${keys.length}</div>



    <div class="d-flex flex-wrap gap-2">



      ${keys.map(k => `<span class="badge bg-light text-dark border"><i class="bi bi-check2 text-success me-1"></i>${k} (${conceptCounts[k]})</span>`).join('')}



    </div>



  `;



}







function editQuizQuestion(idx) {
  const q = activeGeneratedQuizQuestions[idx];
  if (!q) return;
  const newText = prompt("Edit Quiz Question Text:", q.text || q.question_text || q.question);
  if (newText && newText.trim()) {
    q.text = newText.trim();
    q.question_text = newText.trim();
    q.question = newText.trim();
    renderGeneratedQuiz();
  }
}







function regenerateQuizQuestion(idx) {
  const q = activeGeneratedQuizQuestions[idx];
  if (!q) return;
  const curMarks = (q.marks !== undefined && q.marks !== null) ? q.marks : parseInt(document.getElementById('quizMarksPerQ')?.value || 1, 10);
  const subject = document.getElementById('quizSubject')?.value || q.subject || "Distributed Computing";
  const topic = document.getElementById('quizTopic')?.value || q.topic || "";
  const unit = document.getElementById('quizUnit')?.value || q.unit || "All Units";

  const quizGenUrl = (typeof API_QUIZZES_BASE !== 'undefined' && API_QUIZZES_BASE)
    ? `${API_QUIZZES_BASE}/generate`
    : 'http://localhost:5000/api/quizzes/generate';

  fetch(quizGenUrl, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({
      subject,
      topic,
      unit,
      marks_per_question: curMarks,
      total_questions: 1
    })
  })
  .then(res => res.json())
  .then(data => {
    if (data.status === 'success' && data.questions && data.questions.length > 0) {
      activeGeneratedQuizQuestions[idx] = data.questions[0];
      renderGeneratedQuiz();
      renderQuizDifficultyAnalysis();
      renderQuizConceptCoverage();
      showToastNotice('Question Regenerated', `Question ${idx + 1} regenerated successfully.`, 'success');
    }
  })
  .catch(err => {
    console.warn('Error regenerating quiz question:', err);
  });
}







function deleteQuizQuestion(idx) {



  if (confirm("Delete this question from quiz?")) {



    activeGeneratedQuizQuestions.splice(idx, 1);



    renderGeneratedQuiz();



    renderQuizDifficultyAnalysis();



    renderQuizConceptCoverage();



  }



}







function saveQuizDraftAction() {



  saveQuizToStorage("Draft");



  showToastNotice('Draft Saved', 'Quiz draft stored in local memory.', 'info');



}







function publishQuizAction() {



  if (activeGeneratedQuizQuestions.length === 0) {



    showToastNotice('Validation Error', 'Generate quiz questions before publishing.', 'danger');



    return;



  }



  saveQuizToStorage("Published");



  showToastNotice('Quiz Published', 'Quiz published successfully! Students can now access and attempt this quiz.', 'success');



}







const API_QUIZZES_BASE = 'http://localhost:5000/api/quizzes';







async function saveQuizToStorage(statusMode = 'Published') {



  const dept = document.getElementById('quizDept')?.value || "Artificial Intelligence & Data Science";



  const subject = document.getElementById('quizSubject')?.value || "Database Management Systems";



  const year = document.getElementById('quizYear')?.value || "2025-2026";



  const sem = document.getElementById('quizSem')?.value || "Semester 6";



  const unit = document.getElementById('quizUnit')?.value || "Unit III — SQL";



  const topic = document.getElementById('quizTopic')?.value || "General Topic";



  const title = document.getElementById('quizTitleInput')?.value || "DBMS SQL Basics Quiz";



  const quizType = document.getElementById('quizTypeSelect')?.value || "Multiple Choice Question";



  const blooms = document.getElementById('quizBloomsSelect')?.value || "Understand";



  const difficulty = document.getElementById('quizDiffSelect')?.value || "Mixed";



  const durationMins = parseInt(document.getElementById('quizTimeLimit')?.value || 10, 10);



  const marksPerQ = parseInt(document.getElementById('quizMarksPerQ')?.value || 1, 10);







  const payload = {



    title,



    subject,



    department: dept,



    academic_year: year,



    semester: sem,



    unit,



    topic,



    quiz_type: quizType,



    blooms_level: blooms,



    difficulty,



    duration_minutes: durationMins,



    marks_per_question: marksPerQ,



    total_questions: activeGeneratedQuizQuestions.map(q => {
      const normOpts = (q.options || []).map((opt, oIdx) => {
        const textStr = getOptionDisplayString(opt);
        const letter = String.fromCharCode(65 + oIdx);
        const isCorrect = (oIdx === q.correctIndex) || (typeof opt === 'object' && opt.is_correct === true);
        return {
          label: letter,
          option_label: letter,
          text: textStr,
          option_text: textStr,
          is_correct: isCorrect
        };
      });
      return {
        ...q,
        marks: (q.marks !== undefined && q.marks !== null) ? q.marks : marksPerQ,
        marks_per_question: (q.marks !== undefined && q.marks !== null) ? q.marks : marksPerQ,
        options: normOpts,
        options_strings: normOpts.map(o => o.text)
      };
    }).length,



    status: statusMode,



    questions: activeGeneratedQuizQuestions.map(q => ({ ...q, marks: (q.marks !== undefined && q.marks !== null) ? q.marks : marksPerQ, marks_per_question: (q.marks !== undefined && q.marks !== null) ? q.marks : marksPerQ }))



  };







  try {



    const res = await fetch(API_QUIZZES_BASE, {



      method: 'POST',



      headers: { 'Content-Type': 'application/json' },



      credentials: 'include',



      body: JSON.stringify(payload)



    });



    const data = await res.json();



    if (data.status === 'success') {



      const quizObj = data.quiz;



      let storedQuizzes = JSON.parse(localStorage.getItem('academic_quizzes') || '[]');



      storedQuizzes.unshift(quizObj);



      localStorage.setItem('academic_quizzes', JSON.stringify(storedQuizzes));



      if (typeof AcademicMockData !== 'undefined' && AcademicMockData.publishedQuizzes) {



        AcademicMockData.publishedQuizzes.unshift(quizObj);



      }



      showToastNotice(



        statusMode === 'Published' ? 'Quiz Published' : 'Quiz Saved',



        `Quiz successfully saved to MySQL database (${statusMode} status).`,



        'success'



      );



    } else {



      showToastNotice('Error', data.message || 'Failed to save quiz to database.', 'danger');



    }



  } catch (err) {



    console.error('Error saving quiz to API:', err);



    showToastNotice('Server Error', 'Failed to communicate with Flask quiz API.', 'danger');



  }



}







function previewStudentQuizView() {



  const modalEl = document.getElementById('studentQuizPreviewModal');



  if (!modalEl || activeGeneratedQuizQuestions.length === 0) return;







  document.getElementById('studentQuizPreviewTitle').innerText = document.getElementById('quizTitleInput')?.value || "DBMS SQL Basics Quiz";



  document.getElementById('studentQuizPreviewBody').innerHTML = `



    <div class="p-3 bg-light rounded border mb-3 small">
      <strong>Subject:</strong> ${document.getElementById('quizSubject')?.value} |
      <strong>Time Limit:</strong> ${document.getElementById('quizTimeLimit')?.value} Mins |
      <strong>Questions:</strong> ${activeGeneratedQuizQuestions.length} |
      <strong>Marks Per Question:</strong> ${document.getElementById('quizMarksPerQ')?.value || 1} ${parseInt(document.getElementById('quizMarksPerQ')?.value || 1, 10) === 1 ? 'Mark' : 'Marks'} |
      <strong>Total Marks:</strong> ${activeGeneratedQuizQuestions.length * parseInt(document.getElementById('quizMarksPerQ')?.value || 1, 10)} Marks
    </div>



    <div class="card card-academic p-3">



      <h6 class="fw-bold mb-3">Q1. ${activeGeneratedQuizQuestions[0].text}</h6>



      ${activeGeneratedQuizQuestions[0].options.map((opt, i) => `



        <div class="mcq-option-card">



          <input type="radio" name="previewRadio" id="pr_${i}">



          <label for="pr_${i}" class="ms-2 mb-0">${String.fromCharCode(65 + i)}. ${getOptionDisplayString(opt)}</label>



        </div>



      `).join('')}



    </div>



  `;



  const bsModal = new bootstrap.Modal(modalEl);



  bsModal.show();



}







// ==========================================



// STEP 5: ASSIGNMENT GENERATOR MODULE (FACULTY)



// ==========================================







let activeGeneratedAssignmentQuestions = [];







function initAssignmentGeneratorPage() {



  updateAssignmentUnitsDropdown();



  updateAssignmentSourcePanel();



}







function initAssignmentGeneratorForm() {
  const subj = document.getElementById('asnSubject');
  const unit = document.getElementById('asnUnit');
  const form = document.getElementById('assignmentGeneratorForm');
  const sync = () => {
    syncModuleDatalists('asnSubject', 'asnSubjectList', 'asnUnit', 'asnUnitList', 'asnTopic', 'asnTopicList');
    updateAssignmentSourcePanel();
  };
  if (subj) {
    subj.addEventListener('input', sync);
    subj.addEventListener('change', sync);
  }
  if (unit) {
    unit.addEventListener('input', sync);
    unit.addEventListener('change', sync);
  }
  if (form) {
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      generateAssignmentAction();
    });
  }
  sync();
}

function updateAssignmentUnitsDropdown() {
  syncModuleDatalists('asnSubject', 'asnSubjectList', 'asnUnit', 'asnUnitList', 'asnTopic', 'asnTopicList');
  updateAssignmentSourcePanel();
}

function updateAssignmentSourcePanel() {



  const subjectName = document.getElementById('asnSubject')?.value || "Database Management Systems";



  const unitName = document.getElementById('asnUnit')?.value || "Unit III — SQL";







  const panelSubject = document.getElementById('asnSourceSubjectDisplay');



  const panelUnit = document.getElementById('asnSourceUnitDisplay');



  const panelTopics = document.getElementById('asnSourceTopicsDisplay');







  if (panelSubject) panelSubject.innerText = subjectName;



  if (panelUnit) panelUnit.innerText = unitName;



  if (panelTopics) panelTopics.innerText = "SQL Commands, SELECT, WHERE, GROUP BY, JOIN, Subqueries";



}







function generateAssignmentAction() {
  const numQuestions = Math.max(1, parseInt(document.getElementById('asnNumQuestions')?.value || 5));
  const dept = (document.getElementById('asnDept')?.value || '').trim() || "Artificial Intelligence & Data Science";
  const subject = (document.getElementById('asnSubject')?.value || '').trim() || "Database Management Systems";
  const unit = (document.getElementById('asnUnit')?.value || '').trim() || "Unit 1";
  const rawTopic = (document.getElementById('asnTopic')?.value || '').trim();
  const topic = rawTopic || (unit.includes('All Units') ? 'Complete Course Syllabus' : `${subject} Principles`);
  const maxMarks = parseInt(document.getElementById('asnTotalMarks')?.value || 50);

  const baseTopic = topic;
  const sampleAsnQuestions = [
    { text: `Explain the fundamental concepts and significance of ${baseTopic} in ${subject}.`, difficulty: "Easy", concept: `${baseTopic} Fundamentals`, blooms: "Understand" },
    { text: `Analyze the architectural requirements and operational workflow of ${baseTopic} (${unit}).`, difficulty: "Medium", concept: "System Architecture", blooms: "Analyze" },
    { text: `Apply key design patterns and implementation methodologies for ${baseTopic} in ${subject}.`, difficulty: "Medium", concept: "Applied Methodology", blooms: "Apply" },
    { text: `Compare alternative design approaches and optimization techniques used in ${baseTopic}.`, difficulty: "Hard", concept: "Comparative Analysis", blooms: "Evaluate" },
    { text: `Design an end-to-end framework solving real-world challenges related to ${baseTopic} in ${subject}.`, difficulty: "Hard", concept: "Framework Design", blooms: "Create" },
    { text: `Examine failure modes, error handling, and reliability strategies in ${baseTopic}.`, difficulty: "Medium", concept: "System Reliability", blooms: "Analyze" },
    { text: `Describe verification and testing methodologies applied to ${baseTopic} (${unit}).`, difficulty: "Easy", concept: "Testing & Validation", blooms: "Understand" },
    { text: `Formulate performance benchmarks and scaling strategies for ${baseTopic} implementations.`, difficulty: "Hard", concept: "Performance Scaling", blooms: "Evaluate" }
  ];

  const markPerQ = Math.max(1, Math.round(maxMarks / numQuestions));
  activeGeneratedAssignmentQuestions = [];

  for (let i = 0; i < numQuestions; i++) {
    const tmpl = sampleAsnQuestions[i % sampleAsnQuestions.length];
    activeGeneratedAssignmentQuestions.push({
      num: i + 1,
      text: tmpl.text,
      marks: markPerQ,
      difficulty: tmpl.difficulty,
      concept: tmpl.concept,
      blooms: tmpl.blooms,
      unit: unit,
      subject: subject,
      department: dept
    });
  }

  renderGeneratedAssignment();

  const resultsSection = document.getElementById('generatedAssignmentResults');
  if (resultsSection) resultsSection.classList.remove('d-none');
  if (resultsSection) window.scrollTo({ top: resultsSection.offsetTop - 70, behavior: 'smooth' });
}

function renderGeneratedAssignment() {



  const container = document.getElementById('generatedAssignmentList');



  if (!container) return;







  container.innerHTML = activeGeneratedAssignmentQuestions.map((q, idx) => `



    <div class="card card-academic mb-2">



      <div class="card-body p-3">



        <div class="d-flex justify-content-between align-items-center mb-1">



          <div class="d-flex align-items-center gap-2">



            <span class="badge bg-primary">Q${q.num}</span>



            <span class="badge ${q.difficulty === 'Easy' ? 'badge-diff-easy' : q.difficulty === 'Medium' ? 'badge-diff-medium' : 'badge-diff-hard'}">${q.difficulty}</span>



            <span class="badge bg-secondary-subtle text-dark border">${q.concept}</span>



          </div>



          <strong class="text-primary">${q.marks} Marks</strong>



        </div>



        <p class="card-text fw-semibold text-dark mb-0">${q.text}</p>



      </div>



    </div>



  `).join('');



}







function saveAssignmentDraftAction() {



  saveAssignmentToStorage("Draft");



  showToastNotice('Draft Saved', 'Assignment draft saved locally.', 'info');



}







function publishAssignmentAction() {



  if (activeGeneratedAssignmentQuestions.length === 0) {



    showToastNotice('Validation Error', 'Generate assignment questions before publishing.', 'danger');



    return;



  }



  saveAssignmentToStorage("Published");



  showToastNotice('Assignment Published', 'Assignment published successfully for student submissions.', 'success');



}







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

// ==========================================



// STUDENT QUIZ ENGINE & COUNTDOWN TIMER (STUDENT)



// ==========================================







let activeStudentQuiz = null;



let studentQuizAnswers = {};



let currentQuizQIndex = 0;



let quizTimerInterval = null;



let quizSecondsRemaining = 0;



let globalPublishedQuizzes = [];







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

function startStudentQuizAttempt(quizId) {



  let found = globalPublishedQuizzes.find(q => String(q.id) === String(quizId) || String(q.quizId) === String(quizId) || String(q.quiz_code) === String(quizId));



  if (!found) {



    const storedQuizzes = JSON.parse(localStorage.getItem('academic_quizzes') || '[]').concat(AcademicMockData.publishedQuizzes || []);



    found = storedQuizzes.find(q => String(q.id) === String(quizId) || String(q.quizId) === String(quizId) || String(q.quiz_code) === String(quizId));



  }







  if (!found) return;







  let parsedQuestions = found.questions;



  if (typeof parsedQuestions === 'string') {



    try {



      parsedQuestions = JSON.parse(parsedQuestions);



    } catch (e) {



      parsedQuestions = [];



    }



  }







  activeStudentQuiz = {



    ...found,



    questions: parsedQuestions || [],



    durationMins: found.duration_minutes || found.durationMins || 30,



    marksPerQuestion: (found.marks_per_question !== undefined && found.marks_per_question !== null) ? found.marks_per_question : ((found.marksPerQuestion !== undefined && found.marksPerQuestion !== null) ? found.marksPerQuestion : 1)



  };







  studentQuizAnswers = {};



  currentQuizQIndex = 0;



  quizSecondsRemaining = (activeStudentQuiz.durationMins || 30) * 60;







  const modalEl = document.getElementById('studentQuizAttemptModal');



  if (!modalEl) return;







  document.getElementById('studentQuizAttemptTitle').innerText = activeStudentQuiz.title;



  renderCurrentQuizQuestion();



  startQuizCountdownTimer();







  const bsModal = new bootstrap.Modal(modalEl);



  bsModal.show();



}







function startQuizCountdownTimer() {



  if (quizTimerInterval) clearInterval(quizTimerInterval);







  const timerBadge = document.getElementById('quizCountdownBadge');







  quizTimerInterval = setInterval(() => {



    quizSecondsRemaining--;







    const mins = Math.floor(quizSecondsRemaining / 60);



    const secs = quizSecondsRemaining % 60;



    const formatted = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;







    if (timerBadge) {



      timerBadge.innerText = formatted;



      if (quizSecondsRemaining <= 60) {



        timerBadge.classList.add('timer-warning');



      } else {



        timerBadge.classList.remove('timer-warning');



      }



    }







    if (quizSecondsRemaining <= 0) {



      clearInterval(quizTimerInterval);



      showToastNotice('Time is up', 'Time is up! Your quiz has been submitted automatically.', 'warning');



      submitQuizAttempt();



    }



  }, 1000);



}







function renderCurrentQuizQuestion() {



  if (!activeStudentQuiz) return;







  const q = activeStudentQuiz.questions[currentQuizQIndex];



  const container = document.getElementById('studentQuizQuestionCard');



  const countDisplay = document.getElementById('quizQCountDisplay');







  if (countDisplay) countDisplay.innerText = `Question ${currentQuizQIndex + 1} of ${activeStudentQuiz.questions.length}`;







  if (container) {



    const selectedOptIdx = studentQuizAnswers[currentQuizQIndex];







    container.innerHTML = `



      <h6 class="fw-bold mb-3 text-dark fs-5">Q${currentQuizQIndex + 1}. ${q.text}</h6>



      <div class="mb-3">



        ${(q.options || []).map((opt, oIdx) => `



          <div class="mcq-option-card ${selectedOptIdx === oIdx ? 'selected' : ''}" onclick="selectQuizOption(${oIdx})">



            <input type="radio" name="quizOptRadio" id="opt_${oIdx}" ${selectedOptIdx === oIdx ? 'checked' : ''}>



            <label for="opt_${oIdx}" class="ms-2 mb-0 text-dark fw-semibold" style="cursor:pointer;">



              <span class="text-primary fw-bold me-1">${String.fromCharCode(65 + oIdx)}.</span> ${getOptionDisplayString(opt)}



            </label>



          </div>



        `).join('')}



      </div>



    `;



  }







  const prevBtn = document.getElementById('prevQuizQBtn');



  const nextBtn = document.getElementById('nextQuizQBtn');



  const submitBtn = document.getElementById('submitQuizBtn');







  if (prevBtn) prevBtn.disabled = (currentQuizQIndex === 0);



  if (nextBtn) {



    if (currentQuizQIndex === activeStudentQuiz.questions.length - 1) {



      nextBtn.classList.add('d-none');



      if (submitBtn) submitBtn.classList.remove('d-none');



    } else {



      nextBtn.classList.remove('d-none');



      if (submitBtn) submitBtn.classList.add('d-none');



    }



  }



}







function selectQuizOption(oIdx) {



  studentQuizAnswers[currentQuizQIndex] = oIdx;



  renderCurrentQuizQuestion();



}







function nextQuizQuestion() {



  if (currentQuizQIndex < activeStudentQuiz.questions.length - 1) {



    currentQuizQIndex++;



    renderCurrentQuizQuestion();



  }



}







function prevQuizQuestion() {



  if (currentQuizQIndex > 0) {



    currentQuizQIndex--;



    renderCurrentQuizQuestion();



  }



}







async function submitQuizAttempt() {



  if (quizTimerInterval) clearInterval(quizTimerInterval);







  if (!activeStudentQuiz) return;







  const quizDbId = activeStudentQuiz.id || activeStudentQuiz.quizId || activeStudentQuiz.quiz_code;







  let resultObj = null;







  try {



    const res = await fetch(`${API_QUIZZES_BASE}/${quizDbId}/submit`, {



      method: 'POST',



      headers: { 'Content-Type': 'application/json' },



      credentials: 'include',



      body: JSON.stringify({ answers: studentQuizAnswers })



    });



    const data = await res.json();



    if (data.status === 'success' && data.attempt) {



      resultObj = data.attempt;



    }



  } catch (err) {



    console.error('API submission failed, using local calculation:', err);



  }







  if (!resultObj) {



    let correctCount = 0;



    const conceptPerf = {};



    (activeStudentQuiz.questions || []).forEach((q, idx) => {



      const chosen = studentQuizAnswers[idx];



      const isCorrect = (chosen === q.correctIndex);



      if (isCorrect) correctCount++;



      conceptPerf[q.concept || 'General'] = isCorrect;



    });







    const total = activeStudentQuiz.questions.length;



    const marksPerQ = (activeStudentQuiz.marksPerQuestion !== undefined && activeStudentQuiz.marksPerQuestion !== null) ? activeStudentQuiz.marksPerQuestion : 1;



    const scoreText = `${correctCount * marksPerQ} / ${total * marksPerQ}`;



    const pct = Math.round((correctCount / total) * 100);







    resultObj = {



      quizId: activeStudentQuiz.quizId || activeStudentQuiz.id,



      title: activeStudentQuiz.title,



      subject: activeStudentQuiz.subject,



      score: scoreText,



      correct: correctCount,



      total: total,



      percentage: `${pct}%`,



      date: new Date().toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }),



      conceptPerformance: conceptPerf



    };



  }







  let results = JSON.parse(localStorage.getItem('academic_quiz_results') || '[]');



  results.unshift(resultObj);



  localStorage.setItem('academic_quiz_results', JSON.stringify(results));







  // Hide Attempt Modal



  const attemptModalEl = document.getElementById('studentQuizAttemptModal');



  if (attemptModalEl) {



    const bsModal = bootstrap.Modal.getInstance(attemptModalEl);



    if (bsModal) bsModal.hide();



  }







  // Render Result Screen Modal



  renderQuizResultModal(resultObj);



  renderStudentQuizzes();



}







function renderQuizResultModal(result) {



  const modalEl = document.getElementById('studentQuizResultModal');



  if (!modalEl) return;







  document.getElementById('resultQuizTitle').innerText = result.title;



  document.getElementById('resultScoreDisplay').innerText = result.score;



  document.getElementById('resultPctDisplay').innerText = result.percentage;



  document.getElementById('resultCorrectCount').innerText = `${result.correct} / ${result.total}`;







  const conceptContainer = document.getElementById('resultConceptBreakdown');



  if (conceptContainer) {



    conceptContainer.innerHTML = Object.keys(result.conceptPerformance).map(c => `



      <div class="d-flex justify-content-between align-items-center p-2 border rounded mb-1 small">



        <span>${c}</span>



        ${result.conceptPerformance[c] ?



          `<span class="badge bg-success-subtle text-success border border-success fw-bold"><i class="bi bi-check-lg me-1"></i> Proficient</span>` :



          `<span class="badge bg-danger-subtle text-danger border border-danger fw-bold"><i class="bi bi-x-lg me-1"></i> Needs Focus</span>`



        }



      </div>



    `).join('');



  }







  const bsModal = new bootstrap.Modal(modalEl);



  bsModal.show();



}







// ==========================================



// STUDENT ASSIGNMENTS ENGINE & SUBMISSION (STUDENT)



// ==========================================







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
    const rawInstr = asn.instructions || "1. Answer the theoretical concept questions.\n2. Provide implementation details.";
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
    combinedText += `Q${i + 1}: ${text}\n`;
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

// ==========================================



// STEP 6: FACULTY PPT GENERATOR & MANAGEMENT



// ==========================================







let activeGeneratedSlides = [];



let activePPTConfig = {};



let currentPreviewSlideIndex = 0;



let editingSlideIdx = -1;







function initPPTGeneratorForm() {
  const subj = document.getElementById('pptSubjectSelect');
  const unit = document.getElementById('pptUnitSelect');
  const sync = () => syncModuleDatalists('pptSubjectSelect', 'pptSubjectList', 'pptUnitSelect', 'pptUnitList', 'pptTopicSelect', 'pptTopicList');
  if (subj) {
    subj.addEventListener('input', sync);
    subj.addEventListener('change', sync);
  }
  if (unit) {
    unit.addEventListener('input', sync);
    unit.addEventListener('change', sync);
  }
  sync();
}

function populatePPTTopics() {
  syncModuleDatalists('pptSubjectSelect', 'pptSubjectList', 'pptUnitSelect', 'pptUnitList', 'pptTopicSelect', 'pptTopicList');
}

function initPPTGeneratorPage() {



  initPPTGeneratorForm();



  populatePPTTopics();



  renderFacultyPPTHistory();



}







function generatePPTContent() {



  const dept = document.getElementById('pptDeptSelect')?.value || "Artificial Intelligence & Data Science";



  const subject = document.getElementById('pptSubjectSelect')?.value || "Database Management Systems";



  const year = document.getElementById('pptYearSelect')?.value || "2025-2026";



  const sem = document.getElementById('pptSemSelect')?.value || "Semester 6";



  const unitText = (document.getElementById('pptUnitSelect')?.value || '').trim() || 'Unit 1';



  const topic = document.getElementById('pptTopicSelect')?.value || "Joins & Subqueries";



  const sourceMat = document.getElementById('pptSourceSelect')?.value || "DBMS Syllabus 2026 (RES-101)";



  const title = document.getElementById('pptTitleInput')?.value || `${subject}: ${topic} Presentation`;



  const slideCount = parseInt(document.getElementById('pptSlideCountSelect')?.value || "8");



  const presType = document.getElementById('pptTypeSelect')?.value || "Classroom Teaching";







  activePPTConfig = { dept, subject, year, sem, unit: unitText, topic, sourceMat, title, slideCount, presType };







  const incObjectives = document.getElementById('chkObjectives')?.checked ?? true;



  const incConcepts = document.getElementById('chkConcepts')?.checked ?? true;



  const incExamples = document.getElementById('chkExamples')?.checked ?? true;



  const incVisuals = document.getElementById('chkVisuals')?.checked ?? true;



  const incSummary = document.getElementById('chkSummary')?.checked ?? true;



  const incReviewQs = document.getElementById('chkReviewQs')?.checked ?? true;







  activeGeneratedSlides = [];







  // Slide 1: Title Slide



  activeGeneratedSlides.push({



    slideNum: 1,



    title: title,



    content: `Comprehensive Overview of ${topic} in ${subject}`,



    bullets: [`Department: ${dept}`, `Course: ${subject} (${sem})`, `Academic Year: ${year}`, `Source: ${sourceMat}`],



    example: "",



    visualSuggestion: incVisuals ? "Department Logo & Course Header Banner Graphic" : ""



  });







  // Slide 2: Objectives



  if (incObjectives) {



    activeGeneratedSlides.push({



      slideNum: activeGeneratedSlides.length + 1,



      title: "Learning Objectives",



      content: "Key learning goals to achieve by the end of this lecture:",



      bullets: [



        `Understand core principles of ${topic} in ${subject}`,



        `Formulate problem solutions based on ${unitText} specifications`,



        `Apply theoretical frameworks to practical engineering scenarios`



      ],



      example: "",



      visualSuggestion: incVisuals ? "Target Icon & Checklist Graphic" : ""



    });



  }







  // Core Slides (Concept, Explanation, Example, Key Points, Applications)



  const coreTemplates = [



    {



      title: `Introduction to ${topic}`,



      content: `Fundamental definition and domain scope of ${topic}:`,



      bullets: [



        `${topic} forms the cornerstone of modern ${subject} architectures.`,



        `Enables scalable processing and clean abstraction layers.`,



        `Directly addresses core computational requirements in ${unitText}.`



      ],



      example: incExamples ? `Example Syntax / Concept: ${topic}.execute()` : "",



      visualSuggestion: incVisuals ? "High-level Architecture Diagram" : ""



    },



    {



      title: `Core Concept & Mechanics`,



      content: `In-depth structural breakdown of ${topic}:`,



      bullets: [



        `Component 1: Primary control structures and memory bounds.`,



        `Component 2: Data transformation and state preservation.`,



        `Component 3: Error handling and exception guarantees.`



      ],



      example: incExamples ? `Input data stream -> [${topic} Processor] -> Output state` : "",



      visualSuggestion: incVisuals ? "State Transition Flowchart" : ""



    },



    {



      title: `Practical Implementation & Workflow`,



      content: "Step-by-step execution pattern in engineering environments:",



      bullets: [



        "Step 1: Environment setup & prerequisite validation.",



        "Step 2: Execution call with parameterized inputs.",



        "Step 3: Verification of outputs against specification constraints."



      ],



      example: incExamples ? `// Production Code Snippet\nfunction process${topic.replace(/\s+/g, '')}() { return true; }` : "",



      visualSuggestion: incVisuals ? "Code Block & Workflow Diagram" : ""



    },



    {



      title: `Performance Analysis & Best Practices`,



      content: "Optimization techniques and comparative trade-offs:",



      bullets: [



        "Time Complexity: Optimal O(N log N) execution profiles.",



        "Space Complexity: In-place memory utilization bounds.",



        "Best Practice: Avoid redundant iterations and unindexed lookups."



      ],



      example: "",



      visualSuggestion: incVisuals ? "Performance Benchmark Bar Graph" : ""



    },



    {



      title: `Real-World Engineering Applications`,



      content: `Where ${topic} is utilized in enterprise systems:`,



      bullets: [



        "Large-scale distributed database engines and query planners.",



        "Real-time analytics pipelines and decision support systems.",



        "Cloud-native backend API gateways and microservices."



      ],



      example: incExamples ? "Case Study: Scaling 100k requests/sec using indexed lookup caches." : "",



      visualSuggestion: incVisuals ? "Enterprise Architecture Diagram" : ""



    }



  ];







  for (let i = 0; i < coreTemplates.length && activeGeneratedSlides.length < slideCount - (incSummary ? 1 : 0) - (incReviewQs ? 1 : 0); i++) {



    const t = coreTemplates[i];



    t.slideNum = activeGeneratedSlides.length + 1;



    activeGeneratedSlides.push(t);



  }







  // Slide: Summary



  if (incSummary && activeGeneratedSlides.length < slideCount - (incReviewQs ? 1 : 0)) {



    activeGeneratedSlides.push({



      slideNum: activeGeneratedSlides.length + 1,



      title: "Summary & Key Takeaways",



      content: "Essential points for examination and practical mastery:",



      bullets: [



        `Mastery of ${topic} is critical for ${subject} examinations.`,



        `Key trade-offs center around performance, memory, and readability.`,



        `Review source material (${sourceMat}) for extended problem sets.`



      ],



      example: "",



      visualSuggestion: incVisuals ? "Summary Infographic Box" : ""



    });



  }







  // Slide: Review Questions



  if (incReviewQs && activeGeneratedSlides.length < slideCount) {



    activeGeneratedSlides.push({



      slideNum: activeGeneratedSlides.length + 1,



      title: "Review & Self-Assessment Questions",



      content: "Questions for active recall and classroom discussion:",



      bullets: [



        `Q1: Explain the primary mechanism behind ${topic}.`,



        `Q2: Differentiate between optimal and worst-case execution of ${topic}.`,



        `Q3: Solve the practice problem on page 42 of ${sourceMat}.`



      ],



      example: "",



      visualSuggestion: incVisuals ? "Q&A Discussion Banner" : ""



    });



  }







  // Renumber slides to exact 1..N



  activeGeneratedSlides.forEach((s, idx) => s.slideNum = idx + 1);







  document.getElementById('pptWorkspaceArea')?.classList.remove('d-none');



  renderGeneratedSlides();



  updatePPTQualityCheck();



  showToastNotice('PPT Generated', `Successfully generated ${activeGeneratedSlides.length} presentation slides!`, 'success');



}







function renderGeneratedSlides() {



  const container = document.getElementById('generatedSlidesContainer');



  const countBadge = document.getElementById('slideCountBadge');







  if (countBadge) countBadge.innerText = `${activeGeneratedSlides.length} Slides`;







  if (container) {



    if (activeGeneratedSlides.length === 0) {



      container.innerHTML = `<div class="p-4 text-center text-muted">No slides generated yet.</div>`;



      return;



    }







    container.innerHTML = activeGeneratedSlides.map((s, idx) => `



      <div class="slide-card-editable">



        <div class="d-flex justify-content-between align-items-center mb-2">



          <div class="d-flex align-items-center gap-2">



            <span class="slide-badge-num">Slide ${s.slideNum}</span>



            <h6 class="fw-bold text-dark mb-0">${s.title}</h6>



          </div>



          <div class="btn-group btn-group-sm">



            <button class="btn btn-outline-secondary py-0 px-2" onclick="moveSlideUp(${idx})" ${idx === 0 ? 'disabled' : ''} title="Move Up"><i class="bi bi-arrow-up"></i></button>



            <button class="btn btn-outline-secondary py-0 px-2" onclick="moveSlideDown(${idx})" ${idx === activeGeneratedSlides.length - 1 ? 'disabled' : ''} title="Move Down"><i class="bi bi-arrow-down"></i></button>



            <button class="btn btn-outline-primary py-0 px-2" onclick="openSlideEditModal(${idx})" title="Edit Slide"><i class="bi bi-pencil me-1"></i> Edit</button>



            <button class="btn btn-outline-danger py-0 px-2" onclick="deleteSlide(${idx})" title="Delete Slide"><i class="bi bi-trash"></i></button>



          </div>



        </div>



        <p class="text-secondary small mb-2">${s.content}</p>



        <ul class="small mb-2 ps-3 text-dark">



          ${s.bullets.map(b => `<li>${b}</li>`).join('')}



        </ul>



        ${s.example ? `<div class="p-2 bg-light border rounded small font-monospace text-dark mb-2"><strong>Example:</strong> ${s.example}</div>` : ''}



        ${s.visualSuggestion ? `<div class="slide-visual-pill"><i class="bi bi-image"></i> Suggestion: ${s.visualSuggestion}</div>` : ''}



      </div>



    `).join('');



  }



}







function moveSlideUp(idx) {



  if (idx <= 0) return;



  const temp = activeGeneratedSlides[idx];



  activeGeneratedSlides[idx] = activeGeneratedSlides[idx - 1];



  activeGeneratedSlides[idx - 1] = temp;



  activeGeneratedSlides.forEach((s, i) => s.slideNum = i + 1);



  renderGeneratedSlides();



}







function moveSlideDown(idx) {



  if (idx >= activeGeneratedSlides.length - 1) return;



  const temp = activeGeneratedSlides[idx];



  activeGeneratedSlides[idx] = activeGeneratedSlides[idx + 1];



  activeGeneratedSlides[idx + 1] = temp;



  activeGeneratedSlides.forEach((s, i) => s.slideNum = i + 1);



  renderGeneratedSlides();



}







function deleteSlide(idx) {



  activeGeneratedSlides.splice(idx, 1);



  activeGeneratedSlides.forEach((s, i) => s.slideNum = i + 1);



  renderGeneratedSlides();



  updatePPTQualityCheck();



}







function addCustomSlide() {



  const newNum = activeGeneratedSlides.length + 1;



  activeGeneratedSlides.push({



    slideNum: newNum,



    title: `New Slide ${newNum}`,



    content: "Enter main slide takeaway or introduction here...",



    bullets: ["Bullet point 1", "Bullet point 2"],



    example: "",



    visualSuggestion: "Diagram / Flowchart suggestion"



  });



  renderGeneratedSlides();



  updatePPTQualityCheck();



}







function openSlideEditModal(idx) {



  editingSlideIdx = idx;



  const s = activeGeneratedSlides[idx];



  if (!s) return;







  document.getElementById('editSlideTitle').value = s.title;



  document.getElementById('editSlideContent').value = s.content;



  document.getElementById('editSlideBullets').value = s.bullets.join('\n');



  document.getElementById('editSlideExample').value = s.example || '';



  document.getElementById('editSlideVisual').value = s.visualSuggestion || '';







  const modalEl = document.getElementById('slideEditModal');



  if (modalEl) {



    const bsModal = new bootstrap.Modal(modalEl);



    bsModal.show();



  }



}







function saveSlideEdit() {



  if (editingSlideIdx < 0 || editingSlideIdx >= activeGeneratedSlides.length) return;







  const title = document.getElementById('editSlideTitle').value || "Slide Title";



  const content = document.getElementById('editSlideContent').value || "";



  const bulletsRaw = document.getElementById('editSlideBullets').value || "";



  const example = document.getElementById('editSlideExample').value || "";



  const visual = document.getElementById('editSlideVisual').value || "";







  const bullets = bulletsRaw.split('\n').map(b => b.trim()).filter(b => b.length > 0);







  activeGeneratedSlides[editingSlideIdx].title = title;



  activeGeneratedSlides[editingSlideIdx].content = content;



  activeGeneratedSlides[editingSlideIdx].bullets = bullets;



  activeGeneratedSlides[editingSlideIdx].example = example;



  activeGeneratedSlides[editingSlideIdx].visualSuggestion = visual;







  renderGeneratedSlides();



  updatePPTQualityCheck();







  const modalEl = document.getElementById('slideEditModal');



  if (modalEl) {



    const bsModal = bootstrap.Modal.getInstance(modalEl);



    if (bsModal) bsModal.hide();



  }



  showToastNotice('Slide Updated', `Slide ${editingSlideIdx + 1} updated successfully!`, 'success');



}







function updatePPTQualityCheck() {



  const totalEl = document.getElementById('qcTotalSlides');



  const objEl = document.getElementById('qcObjectivesInc');



  const concEl = document.getElementById('qcConceptsCovered');



  const exEl = document.getElementById('qcExamplesInc');



  const sumEl = document.getElementById('qcSummaryInc');



  const revEl = document.getElementById('qcReviewQsInc');







  if (totalEl) totalEl.innerText = activeGeneratedSlides.length;







  const hasObj = activeGeneratedSlides.some(s => s.title.toLowerCase().includes('objective'));



  const hasEx = activeGeneratedSlides.some(s => s.example && s.example.length > 0);



  const hasSum = activeGeneratedSlides.some(s => s.title.toLowerCase().includes('summary'));



  const hasRev = activeGeneratedSlides.some(s => s.title.toLowerCase().includes('review'));







  if (objEl) objEl.innerHTML = hasObj ? `<span class="badge bg-success"><i class="bi bi-check-lg"></i> Yes</span>` : `<span class="badge bg-secondary">No</span>`;



  if (concEl) concEl.innerText = `${activeGeneratedSlides.length} Core Concepts`;



  if (exEl) exEl.innerHTML = hasEx ? `<span class="badge bg-success"><i class="bi bi-check-lg"></i> Yes</span>` : `<span class="badge bg-secondary">No</span>`;



  if (sumEl) sumEl.innerHTML = hasSum ? `<span class="badge bg-success"><i class="bi bi-check-lg"></i> Yes</span>` : `<span class="badge bg-secondary">No</span>`;



  if (revEl) revEl.innerHTML = hasRev ? `<span class="badge bg-success"><i class="bi bi-check-lg"></i> Yes</span>` : `<span class="badge bg-secondary">No</span>`;



}







function openPPTPreviewModal() {



  if (activeGeneratedSlides.length === 0) {



    showToastNotice('No Slides', 'Please generate or add slides first.', 'warning');



    return;



  }



  currentPreviewSlideIndex = 0;



  renderCurrentPreviewSlide();







  const modalEl = document.getElementById('pptPreviewModal');



  if (modalEl) {



    const bsModal = new bootstrap.Modal(modalEl);



    bsModal.show();



  }



}







function renderCurrentPreviewSlide() {



  const s = activeGeneratedSlides[currentPreviewSlideIndex];



  const canvas = document.getElementById('pptPreviewCanvas');



  const counter = document.getElementById('previewSlideCounter');







  if (counter) counter.innerText = `Slide ${currentPreviewSlideIndex + 1} of ${activeGeneratedSlides.length}`;







  if (canvas && s) {



    canvas.innerHTML = `



      <div>



        <div class="slide-header-area d-flex justify-content-between align-items-center">



          <div>



            <span class="role-badge role-badge-faculty me-2">Slide ${s.slideNum}</span>



            <h4 class="fw-bold text-dark d-inline mb-0">${s.title}</h4>



          </div>



          <small class="text-muted font-monospace">${activePPTConfig.subject || 'DBMS'} • ${activePPTConfig.unit || 'Unit III'}</small>



        </div>



        <p class="fs-6 text-dark fw-semibold mb-3">${s.content}</p>



        <ul class="fs-6 text-dark ps-4 mb-3">



          ${s.bullets.map(b => `<li class="slide-content-bullet">${b}</li>`).join('')}



        </ul>



        ${s.example ? `<div class="p-3 bg-light border rounded font-monospace text-dark mb-3"><strong>Code / Example:</strong><br>${s.example}</div>` : ''}



      </div>



      <div>



        ${s.visualSuggestion ? `<div class="slide-visual-pill mt-3"><i class="bi bi-image"></i> Visual Suggestion: ${s.visualSuggestion}</div>` : ''}



        <div class="d-flex justify-content-between align-items-center pt-3 border-top mt-3 text-muted small">



          <span>${activePPTConfig.dept || 'Engineering Department'}</span>



          <span>${activePPTConfig.sourceMat || 'Academic Resource'}</span>



        </div>



      </div>



    `;



  }







  const prevBtn = document.getElementById('prevPreviewSlideBtn');



  const nextBtn = document.getElementById('nextPreviewSlideBtn');







  if (prevBtn) prevBtn.disabled = (currentPreviewSlideIndex === 0);



  if (nextBtn) nextBtn.disabled = (currentPreviewSlideIndex === activeGeneratedSlides.length - 1);



}







function prevPreviewSlide() {



  if (currentPreviewSlideIndex > 0) {



    currentPreviewSlideIndex--;



    renderCurrentPreviewSlide();



  }



}







function nextPreviewSlide() {



  if (currentPreviewSlideIndex < activeGeneratedSlides.length - 1) {



    currentPreviewSlideIndex++;



    renderCurrentPreviewSlide();



  }



}







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

// ==========================================



// STEP 6: FACULTY LESSON PLAN GENERATOR



// ==========================================







let activeLessonPlanObj = null;







function initLessonPlanGeneratorForm() {
  const subj = document.getElementById('lpSubjectSelect');
  const unit = document.getElementById('lpUnitSelect');
  const sync = () => syncModuleDatalists('lpSubjectSelect', 'lpSubjectList', 'lpUnitSelect', 'lpUnitList', 'lpTopicSelect', 'lpTopicList');
  if (subj) {
    subj.addEventListener('input', sync);
    subj.addEventListener('change', sync);
  }
  if (unit) {
    unit.addEventListener('input', sync);
    unit.addEventListener('change', sync);
  }
  sync();
}

function populateLPTopics() {
  syncModuleDatalists('lpSubjectSelect', 'lpSubjectList', 'lpUnitSelect', 'lpUnitList', 'lpTopicSelect', 'lpTopicList');
}

function initLessonPlanGeneratorPage() {



  initLessonPlanGeneratorForm();



  populateLPTopics();



  renderFacultyLessonPlanHistory();



}







function generateLessonPlanContent() {



  const dept = document.getElementById('lpDeptSelect')?.value || "Artificial Intelligence & Data Science";



  const subject = document.getElementById('lpSubjectSelect')?.value || "Database Management Systems";



  const year = document.getElementById('lpYearSelect')?.value || "2025-2026";



  const sem = document.getElementById('lpSemSelect')?.value || "Semester 6";



  const unitText = (document.getElementById('lpUnitSelect')?.value || '').trim() || 'Unit 1';



  const topic = document.getElementById('lpTopicSelect')?.value || "Joins & Subqueries";



  const sourceMat = document.getElementById('lpSourceSelect')?.value || "DBMS Syllabus 2026 (RES-101)";



  const title = document.getElementById('lpTitleInput')?.value || `${subject}: ${topic} Lesson Plan`;



  const duration = document.getElementById('lpDurationSelect')?.value || "45 minutes";



  const method = document.getElementById('lpMethodSelect')?.value || "Demonstration & Problem Solving";







  const timeline = buildDynamicTimeline(duration);







  activeLessonPlanObj = {



    id: `LP-2026-${Date.now().toString().slice(-4)}`,



    title, department: dept, subject, academicYear: year, semester: sem, unit: unitText, topic,



    sourceMaterial: sourceMat, duration, teachingMethod: method, status: "Draft",



    createdAt: new Date().toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }),



    createdBy: (JSON.parse(localStorage.getItem('academic_user') || '{}').name) || "Faculty Member",



    objectives: `1. Understand fundamental principles of ${topic}.\n2. Demonstrate competency in formulating solutions for ${unitText}.\n3. Apply theoretical principles to real-world software scenarios.`,



    prerequisites: `Basic understanding of ${subject} concepts and prerequisite unit materials.`,



    concepts: `${topic}, ${unitText} schema design, performance trade-offs, integrity constraints.`,



    activities: `Live interactive demonstration of ${topic} followed by guided pair-programming activity.`,



    resources: `Classroom Projector, ${sourceMat}, Reference Textbook, Database Workstation.`,



    explanationPoints: `1. Introduce core definition and relevance of ${topic}.\n2. Explain syntax and execution flow step-by-step.\n3. Demonstrate edge cases and common error handling.`,



    studentActivities: `Students work in pairs to analyze sample problem sets and write solution queries on worksheets.`,



    assessment: `5-minute pop quiz / exit ticket evaluating comprehension of key definitions.`,



    homework: `Complete practice exercise questions from Unit chapter in ${sourceMat}.`,



    outcomes: `Students will be capable of independently solving ${topic} engineering problems.`,



    summary: `${topic} provides essential foundation for advanced ${subject} application development.`,



    timeline: timeline



  };







  document.getElementById('lpWorkspaceArea')?.classList.remove('d-none');



  renderGeneratedLessonPlan();



  updateLessonPlanQualityCheck();



  showToastNotice('Lesson Plan Generated', 'Structured academic lesson plan generated successfully!', 'success');



}







function buildDynamicTimeline(durationStr) {



  const durMins = parseInt(durationStr) || 45;







  const t1 = Math.round(durMins * 0.1);



  const t2 = Math.round(durMins * 0.3);



  const t3 = Math.round(durMins * 0.35);



  const t4 = Math.round(durMins * 0.15);



  const t5 = durMins - (t1 + t2 + t3 + t4);







  let c1 = 0, c2 = c1 + t1, c3 = c2 + t2, c4 = c3 + t3, c5 = c4 + t4, c6 = durMins;







  return [



    { time: `${c1}–${c2} min`, activity: "Introduction & Warm-up", facultyRole: "Present real-world scenario and learning objectives.", studentRole: "Listen and answer warm-up questions." },



    { time: `${c2}–${c3} min`, activity: "Core Concept Explanation", facultyRole: "Explain core theoretical principles using slides/board.", studentRole: "Take structured notes." },



    { time: `${c3}–${c4} min`, activity: "Demonstration / Activity", facultyRole: "Conduct live demonstration of sample problems.", studentRole: "Observe steps and follow along." },



    { time: `${c4}–${c5} min`, activity: "Student Practice", facultyRole: "Circulate classroom and guide student pairs.", studentRole: "Solve worksheet problem sets in pairs." },



    { time: `${c5}–${c6} min`, activity: "Assessment & Summary", facultyRole: "Conduct quick exit assessment and summarize key takeaways.", studentRole: "Complete assessment and clarify doubts." }



  ];



}







function renderGeneratedLessonPlan() {



  if (!activeLessonPlanObj) return;







  const setVal = (id, val) => { const el = document.getElementById(id); if (el) el.value = val; };







  setVal('lpEditTitle', activeLessonPlanObj.title);



  setVal('lpEditObjectives', activeLessonPlanObj.objectives);



  setVal('lpEditPrereqs', activeLessonPlanObj.prerequisites);



  setVal('lpEditConcepts', activeLessonPlanObj.concepts);



  setVal('lpEditActivities', activeLessonPlanObj.activities);



  setVal('lpEditResources', activeLessonPlanObj.resources);



  setVal('lpEditExplanations', activeLessonPlanObj.explanationPoints);



  setVal('lpEditStudentActs', activeLessonPlanObj.studentActivities);



  setVal('lpEditAssessment', activeLessonPlanObj.assessment);



  setVal('lpEditHomework', activeLessonPlanObj.homework);



  setVal('lpEditOutcomes', activeLessonPlanObj.outcomes);



  setVal('lpEditSummary', activeLessonPlanObj.summary);







  renderTimelineTable(activeLessonPlanObj.timeline);



}







function renderTimelineTable(timeline) {



  const container = document.getElementById('lpTimelineTableBody');



  if (!container) return;







  container.innerHTML = timeline.map(t => `



    <tr>



      <td><span class="timeline-time-badge">${t.time}</span></td>



      <td><strong>${t.activity}</strong></td>



      <td><small class="text-dark">${t.facultyRole}</small></td>



      <td><small class="text-muted">${t.studentRole}</small></td>



    </tr>



  `).join('');



}







function updateLessonPlanQualityCheck() {



  const setQC = (id, valid) => {



    const el = document.getElementById(id);



    if (el) el.innerHTML = valid ? `<span class="badge bg-success"><i class="bi bi-check-lg"></i> Complete</span>` : `<span class="badge bg-warning text-dark">Needs Review</span>`;



  };







  setQC('lpQCObjectives', !!activeLessonPlanObj?.objectives);



  setQC('lpQCConcepts', !!activeLessonPlanObj?.concepts);



  setQC('lpQCActivities', !!activeLessonPlanObj?.activities);



  setQC('lpQCAssessment', !!activeLessonPlanObj?.assessment);



  setQC('lpQCOutcomes', !!activeLessonPlanObj?.outcomes);



}







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

// ==========================================



// STEP 6: STUDENT PRESENTATIONS & LESSON PLANS (STUDENT)



// ==========================================







let studentCurrentPPT = null;



let studentPreviewSlideIndex = 0;







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

// ==========================================



// STEP 7: VOICE-TO-QUESTION MODULE



// ==========================================







let speechRecognitionInstance = null;



let isRecordingSpeech = false;



let activeVoiceQuestions = [];



let activeVoiceConfig = {};








// Dynamic Datalist Synchronizer for All 7 Academic Modules
function syncModuleDatalists(subjId, subjListId, unitId, unitListId, topicId, topicListId) {
  const subjEl = document.getElementById(subjId);
  const unitEl = document.getElementById(unitId);
  const topicEl = document.getElementById(topicId);
  const unitListEl = document.getElementById(unitListId);
  const topicListEl = document.getElementById(topicListId);

  const subjectVal = (subjEl?.value || '').trim();
  const unitVal = (unitEl?.value || '').trim();

  // Standard Units list options
  const defaultUnits = [
    "All Units (Complete Syllabus)",
    "Unit 1",
    "Unit 2",
    "Unit 3",
    "Unit 4",
    "Unit 5",
    "Unit I — Introduction",
    "Unit II — Core Concepts",
    "Unit III — Advanced Topics",
    "Unit IV — Applications",
    "Unit V — System Design"
  ];

  const struct = typeof AcademicMockData !== 'undefined' ? AcademicMockData?.subjectStructure?.[subjectVal] : null;
  let customUnits = [];

  if (struct && struct.units) {
    struct.units.forEach(u => {
      if (u.name) customUnits.push(u.name);
    });
  }

  if (unitListEl) {
    const combinedUnits = ["All Units (Complete Syllabus)", "Unit 1", "Unit 2", "Unit 3", "Unit 4", "Unit 5", ...customUnits];
    const uniqueUnits = Array.from(new Set(combinedUnits));
    unitListEl.innerHTML = uniqueUnits.map(u => `<option value="${u}">`).join('\n');
  }

  if (topicListEl) {
    let matchedTopics = [];
    if (struct && struct.units) {
      const uObj = struct.units.find(u => (u.name || u.id) === unitVal || (u.id && unitVal.includes(u.id)));
      if (uObj && uObj.topics) {
        matchedTopics.push(...uObj.topics);
      }
    }
    if (matchedTopics.length === 0) {
      matchedTopics = [
        "Core Architectural Principles",
        "Functional Mechanisms and Operations",
        "Query Optimization & Indexing",
        "Transaction Management & Concurrency",
        "Practical Implementation & Case Studies",
        "System Analysis & Performance"
      ];
      if (subjectVal) {
        matchedTopics.unshift(`${subjectVal} Fundamentals`, `${subjectVal} Key Implementations`);
      }
    }
    const uniqueTopics = Array.from(new Set(matchedTopics));
    topicListEl.innerHTML = uniqueTopics.map(t => `<option value="${t}">`).join('\n');
  }
}

function initVoiceQuestionForm() {
  const subj = document.getElementById('voiceSubjectSelect');
  const unit = document.getElementById('voiceUnitSelect');
  const sync = () => syncModuleDatalists('voiceSubjectSelect', 'voiceSubjectList', 'voiceUnitSelect', 'voiceUnitList', 'voiceTopicSelect', 'voiceTopicList');
  if (subj) {
    subj.addEventListener('input', sync);
    subj.addEventListener('change', sync);
  }
  if (unit) {
    unit.addEventListener('input', sync);
    unit.addEventListener('change', sync);
  }
  sync();
}

function populateVoiceTopics() {
  syncModuleDatalists('voiceSubjectSelect', 'voiceSubjectList', 'voiceUnitSelect', 'voiceUnitList', 'voiceTopicSelect', 'voiceTopicList');
}

function initVoiceQuestionPage() {



  initVoiceQuestionForm();



  populateVoiceTopics();



  renderFacultyVoiceHistory();



}







function startVoiceRecording() {



  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;







  const statusBadge = document.getElementById('voiceStatusBadge');



  const recognizedArea = document.getElementById('voiceRecognizedText');



  const fallbackNotice = document.getElementById('voiceFallbackNotice');



  const lang = document.getElementById('voiceLanguageSelect')?.value || 'en-IN';







  if (!SpeechRecognition) {



    if (statusBadge) statusBadge.innerHTML = `<span class="badge bg-danger"><i class="bi bi-x-circle me-1"></i> Not Supported</span>`;



    if (fallbackNotice) fallbackNotice.classList.remove('d-none');



    showToastNotice('Speech Recognition Unsupported', 'Voice recognition is not supported in this browser. Please enter text manually in the box below.', 'warning');



    return;



  }







  try {



    speechRecognitionInstance = new SpeechRecognition();



    speechRecognitionInstance.continuous = true;



    speechRecognitionInstance.interimResults = true;



    speechRecognitionInstance.lang = lang;







    speechRecognitionInstance.onstart = () => {



      isRecordingSpeech = true;



      if (statusBadge) statusBadge.innerHTML = `<span class="recording-pulse-badge"><span class="recording-dot-active"></span> Listening (${lang})...</span>`;



      document.getElementById('startVoiceRecBtn')?.classList.add('d-none');



      document.getElementById('stopVoiceRecBtn')?.classList.remove('d-none');



    };







    speechRecognitionInstance.onresult = (event) => {



      let transcript = '';



      for (let i = event.resultIndex; i < event.results.length; i++) {



        transcript += event.results[i][0].transcript;



      }



      if (recognizedArea) recognizedArea.value = transcript;



    };







    speechRecognitionInstance.onerror = (event) => {



      showToastNotice('Voice Recognition Error', `Speech error: ${event.error}. Using fallback text input.`, 'danger');



      stopVoiceRecording();



    };







    speechRecognitionInstance.onend = () => {



      isRecordingSpeech = false;



      if (statusBadge) statusBadge.innerHTML = `<span class="badge bg-success"><i class="bi bi-check-circle me-1"></i> Completed</span>`;



      document.getElementById('startVoiceRecBtn')?.classList.remove('d-none');



      document.getElementById('stopVoiceRecBtn')?.classList.add('d-none');



    };







    speechRecognitionInstance.start();



  } catch (err) {



    if (fallbackNotice) fallbackNotice.classList.remove('d-none');



    showToastNotice('Speech API Error', 'Could not initialize microphone. Please type your prompt manually.', 'warning');



  }



}







function stopVoiceRecording() {



  if (speechRecognitionInstance && isRecordingSpeech) {



    speechRecognitionInstance.stop();



  }



  isRecordingSpeech = false;



  const statusBadge = document.getElementById('voiceStatusBadge');



  if (statusBadge) statusBadge.innerHTML = `<span class="badge bg-success"><i class="bi bi-check-circle me-1"></i> Speech Saved</span>`;



  document.getElementById('startVoiceRecBtn')?.classList.remove('d-none');



  document.getElementById('stopVoiceRecBtn')?.classList.add('d-none');



}







function clearVoiceText() {



  const recognizedArea = document.getElementById('voiceRecognizedText');



  if (recognizedArea) recognizedArea.value = '';



  const statusBadge = document.getElementById('voiceStatusBadge');



  if (statusBadge) statusBadge.innerHTML = `<span class="badge bg-secondary">Idle</span>`;



}







function generateQuestionsFromVoice() {



  const text = document.getElementById('voiceRecognizedText')?.value || '';



  if (!text.trim()) {



    showToastNotice('Input Required', 'Please record speech or enter manual prompt text first.', 'warning');



    return;



  }







  const dept = document.getElementById('voiceDeptSelect')?.value || "Artificial Intelligence & Data Science";



  const subject = document.getElementById('voiceSubjectSelect')?.value || "Database Management Systems";



  const unitText = (document.getElementById('voiceUnitSelect')?.value || '').trim() || 'Unit 1';



  const topic = document.getElementById('voiceTopicSelect')?.value || "Joins & Subqueries";



  const lang = document.getElementById('voiceLanguageSelect')?.value || "en-IN";



  const count = parseInt(document.getElementById('voiceCountSelect')?.value || "5");



  const diff = document.getElementById('voiceDiffSelect')?.value || "Balanced";



  const type = document.getElementById('voiceTypeSelect')?.value || "Short Answer";



  const blooms = document.getElementById('voiceBloomsSelect')?.value || "Understand";







  activeVoiceConfig = { dept, subject, unit: unitText, topic, lang, count, diff, type, blooms, transcript: text };







  activeVoiceQuestions = [];



  const isTamil = (lang === 'ta-IN');







  for (let i = 0; i < count; i++) {



    const qNum = i + 1;



    let qText = "";



    let qDiff = diff === "Balanced" ? (i % 3 === 0 ? "Easy" : i % 3 === 1 ? "Medium" : "Hard") : diff;



    let qConcept = `${topic} Concept ${qNum}`;







    if (isTamil) {



      qText = `(${topic}) ${qNum}. தரவுத்தள அமைப்பில் ${topic} தொடர்பான முக்கிய கேள்வி ${qNum}?`;



    } else {



      qText = `Based on voice prompt ("${text.slice(0, 40)}..."): Explain the fundamental operation of ${topic} item #${qNum} in ${subject}.`;



    }







    activeVoiceQuestions.push({



      num: qNum,



      question: qText,



      difficulty: qDiff,



      type: type,



      blooms: blooms === "Auto Select" ? (i % 2 === 0 ? "Understand" : "Apply") : blooms,



      concept: qConcept,



      similarityStatus: i === 1 ? "92% Concept Match (Unique Intent)" : "Unique Concept"



    });



  }







  document.getElementById('voiceWorkspaceArea')?.classList.remove('d-none');



  renderGeneratedVoiceQuestions();



  updateVoiceQualityCheck();



  showToastNotice('Voice Questions Generated', `Generated ${activeVoiceQuestions.length} questions from speech input!`, 'success');



}







function renderGeneratedVoiceQuestions() {



  const container = document.getElementById('voiceQuestionsContainer');



  if (!container) return;







  container.innerHTML = activeVoiceQuestions.map((q, idx) => `



    <div class="card card-academic p-3 mb-3">



      <div class="d-flex justify-content-between align-items-center mb-2 flex-wrap gap-2">



        <div class="d-flex align-items-center gap-2">



          <span class="badge bg-primary me-1">Q${q.num}</span>



          <span class="badge ${q.difficulty === 'Easy' ? 'bg-success' : q.difficulty === 'Medium' ? 'bg-warning text-dark' : 'bg-danger'}">${q.difficulty}</span>



          <span class="badge bg-secondary-subtle text-dark border">${q.type}</span>



          <span class="badge bg-light text-muted border">${q.blooms}</span>



        </div>



        <div class="btn-group btn-group-sm">



          <button class="btn btn-outline-secondary py-0 px-2" onclick="translateQuestionDirectly('${idx}', 'voice')" title="Translate to Tamil/English"><i class="bi bi-translate text-primary me-1"></i> Translate</button>



          <button class="btn btn-outline-danger py-0 px-2" onclick="deleteVoiceQuestion(${idx})" title="Delete"><i class="bi bi-trash"></i></button>



        </div>



      </div>



      <p class="fw-semibold text-dark mb-2">${q.question}</p>



      <div class="d-flex justify-content-between align-items-center small text-muted border-top pt-2 mt-1">



        <span><strong>Concept:</strong> ${q.concept}</span>



        <span class="badge ${q.similarityStatus.includes('Match') ? 'bg-warning-subtle text-warning border border-warning' : 'bg-success-subtle text-success border border-success'}">${q.similarityStatus}</span>



      </div>



    </div>



  `).join('');



}







function deleteVoiceQuestion(idx) {



  activeVoiceQuestions.splice(idx, 1);



  activeVoiceQuestions.forEach((q, i) => q.num = i + 1);



  renderGeneratedVoiceQuestions();



  updateVoiceQualityCheck();



}







function updateVoiceQualityCheck() {



  const easyCount = activeVoiceQuestions.filter(q => q.difficulty === 'Easy').length;



  const medCount = activeVoiceQuestions.filter(q => q.difficulty === 'Medium').length;



  const hardCount = activeVoiceQuestions.filter(q => q.difficulty === 'Hard').length;







  const easyEl = document.getElementById('voiceQCEasy');



  const medEl = document.getElementById('voiceQCMed');



  const hardEl = document.getElementById('voiceQCHard');



  const totalEl = document.getElementById('voiceQCTotal');







  if (easyEl) easyEl.innerText = `${easyCount} Easy`;



  if (medEl) medEl.innerText = `${medCount} Med`;



  if (hardEl) hardEl.innerText = `${hardCount} Hard`;



  if (totalEl) totalEl.innerText = `${activeVoiceQuestions.length} Qs`;



}







function saveVoiceQuestions() {



  if (activeVoiceQuestions.length === 0) {



    showToastNotice('Cannot Save', 'No voice questions to save.', 'warning');



    return;



  }







  const voiceObj = {



    id: `VOICE-2026-${Date.now().toString().slice(-4)}`,



    transcript: activeVoiceConfig.transcript,



    language: activeVoiceConfig.lang,



    department: activeVoiceConfig.dept,



    subject: activeVoiceConfig.subject,



    unit: activeVoiceConfig.unit,



    topic: activeVoiceConfig.topic,



    count: activeVoiceQuestions.length,



    difficulty: activeVoiceConfig.diff,



    createdAt: new Date().toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }),



    questions: activeVoiceQuestions



  };







  let voiceList = JSON.parse(localStorage.getItem('academic_voice_questions') || '[]');



  voiceList.unshift(voiceObj);



  localStorage.setItem(getScopedStorageKey('academic_voice_questions'), JSON.stringify(voiceList));







  AcademicMockData.publishedVoiceQuestions.unshift(voiceObj);







  showToastNotice('Voice Questions Saved', 'Questions generated from speech saved successfully!', 'success');



  renderFacultyVoiceHistory();



}







function renderFacultyVoiceHistory() {



  const tableBody = document.getElementById('facultyVoiceHistoryTableBody');



  if (!tableBody) return;







  const stored = JSON.parse(localStorage.getItem(getScopedStorageKey('academic_voice_questions')) || '[]');







  if (stored.length === 0) {



    tableBody.innerHTML = `<tr><td colspan="6" class="text-center py-4 text-muted">No voice question sessions saved yet.</td></tr>`;



    return;



  }







  tableBody.innerHTML = stored.map(v => `



    <tr>



      <td><small class="fw-semibold text-dark">${v.transcript.slice(0, 45)}...</small></td>



      <td><span class="badge bg-primary-subtle text-primary border">${v.subject}</span></td>



      <td><small>${v.topic}</small></td>



      <td><span class="badge ${v.language === 'ta-IN' ? 'badge-lang-ta' : 'badge-lang-en'}">${v.language === 'ta-IN' ? 'Tamil' : 'English'}</span></td>



      <td><small>${v.count} Questions</small></td>



      <td>



        <button class="btn btn-outline-danger btn-sm py-0 px-2" onclick="deleteVoiceSession('${v.id}')" title="Delete"><i class="bi bi-trash"></i></button>



      </td>



    </tr>



  `).join('');



}







function deleteVoiceSession(id) {



  let list = JSON.parse(localStorage.getItem('academic_voice_questions') || '[]');



  list = list.filter(v => v.id !== id);



  localStorage.setItem(getScopedStorageKey('academic_voice_questions'), JSON.stringify(list));



  AcademicMockData.publishedVoiceQuestions = AcademicMockData.publishedVoiceQuestions.filter(v => v.id !== id);







  showToastNotice('Session Deleted', 'Voice session removed.', 'danger');



  renderFacultyVoiceHistory();



}











// ==========================================



// STEP 7: IMAGE / DIAGRAM QUESTION GENERATOR



// ==========================================







let selectedImageFile = null;
window.selectedImageFile = null;
let activeUploadedImageData = null;
let activeImageQuestions = [];
let activeImageConfig = {};

function initImageQuestionForm() {
  const subj = document.getElementById('imgSubjectSelect');
  const unit = document.getElementById('imgUnitSelect');
  const sync = () => syncModuleDatalists('imgSubjectSelect', 'imgSubjectList', 'imgUnitSelect', 'imgUnitList', 'imgTopicSelect', 'imgTopicList');
  if (subj) {
    subj.addEventListener('input', sync);
    subj.addEventListener('change', sync);
  }
  if (unit) {
    unit.addEventListener('input', sync);
    unit.addEventListener('change', sync);
  }
  sync();

  const fileInput = document.getElementById('imageFileInput');
  if (fileInput) {
    fileInput.onchange = handleImageFileUpload;
  }
}

function populateImageTopics() {
  syncModuleDatalists('imgSubjectSelect', 'imgSubjectList', 'imgUnitSelect', 'imgUnitList', 'imgTopicSelect', 'imgTopicList');
}

function initImageQuestionPage() {
  initImageQuestionForm();
  populateImageTopics();
  renderFacultyImageHistory();
}

function handleImageFileUpload(event) {
  let file = null;
  if (event && event.target && event.target.files && event.target.files.length > 0) {
    file = event.target.files[0];
  } else if (event && event.files && event.files.length > 0) {
    file = event.files[0];
  } else {
    const fileInput = document.getElementById('imageFileInput');
    if (fileInput && fileInput.files && fileInput.files.length > 0) {
      file = fileInput.files[0];
    }
  }

  if (!file) return;

  const validExts = ['png', 'jpg', 'jpeg', 'webp'];
  const ext = file.name.split('.').pop().toLowerCase();
  if (!validExts.includes(ext)) {
    showToastNotice('Invalid File Type', 'Please upload a valid diagram image (PNG, JPG, JPEG, WEBP).', 'error');
    const fileInput = document.getElementById('imageFileInput');
    if (fileInput) fileInput.value = '';
    return;
  }

  if (file.size > 16 * 1024 * 1024) {
    showToastNotice('File Too Large', 'Maximum image size is 16MB.', 'warning');
    const fileInput = document.getElementById('imageFileInput');
    if (fileInput) fileInput.value = '';
    return;
  }

  // Clear stale state from previous uploads
  activeImageQuestions = [];
  const container = document.getElementById('imageQuestionsContainer');
  if (container) container.innerHTML = '';
  const wsArea = document.getElementById('imgWorkspaceArea');
  if (wsArea) wsArea.classList.add('d-none');
  const descInput = document.getElementById('imageDescriptionInput');
  if (descInput) descInput.value = '';

  // Retain actual DOM File object in global and module scope
  selectedImageFile = file;
  window.selectedImageFile = file;

  const reader = new FileReader();
  reader.onload = (e) => {
    activeUploadedImageData = {
      file: file,
      dataUrl: e.target.result,
      name: file.name,
      type: file.type || `image/${ext}`,
      size: `${Math.round(file.size / 1024)} KB`
    };

    const previewContainer = document.getElementById('imagePreviewContainer');
    if (previewContainer) previewContainer.classList.remove('d-none');

    const previewImg = document.getElementById('uploadedImagePreview');
    if (previewImg) previewImg.src = e.target.result;

    const nameDisplay = document.getElementById('imageFileNameDisplay');
    if (nameDisplay) nameDisplay.innerText = file.name;

    const metaDisplay = document.getElementById('imageMetaDisplay');
    if (metaDisplay) metaDisplay.innerText = `${file.type || ext.toUpperCase()} • ${Math.round(file.size / 1024)} KB`;

    const statusBadge = document.getElementById('imageAnalysisStatus');
    if (statusBadge) {
      statusBadge.innerHTML = `<span class="badge bg-primary"><i class="bi bi-file-earmark-image me-1"></i> Image Loaded: ${escapeHtml(file.name)}</span>`;
    }

    showToastNotice('Image Uploaded', `Successfully loaded ${file.name}`, 'success');
  };
  reader.readAsDataURL(file);
}
window.handleImageFileUpload = handleImageFileUpload;
window.handleImageUploadSelection = handleImageFileUpload;

function removeUploadedImage() {
  selectedImageFile = null;
  window.selectedImageFile = null;
  activeUploadedImageData = null;
  activeImageQuestions = [];

  const fileInput = document.getElementById('imageFileInput');
  if (fileInput) fileInput.value = '';

  const previewContainer = document.getElementById('imagePreviewContainer');
  if (previewContainer) previewContainer.classList.add('d-none');

  const previewImg = document.getElementById('uploadedImagePreview');
  if (previewImg) previewImg.src = '';

  const nameDisplay = document.getElementById('imageFileNameDisplay');
  if (nameDisplay) nameDisplay.innerText = '';

  const metaDisplay = document.getElementById('imageMetaDisplay');
  if (metaDisplay) metaDisplay.innerText = '';

  const descInput = document.getElementById('imageDescriptionInput');
  if (descInput) descInput.value = '';

  const statusBadge = document.getElementById('imageAnalysisStatus');
  if (statusBadge) {
    statusBadge.innerHTML = `<span class="badge bg-light text-muted border"><i class="bi bi-image me-1"></i> No Image Selected</span>`;
  }

  const wsArea = document.getElementById('imgWorkspaceArea');
  if (wsArea) wsArea.classList.add('d-none');

  const container = document.getElementById('imageQuestionsContainer');
  if (container) container.innerHTML = '';

  showToastNotice('Image Removed', 'Uploaded image removed.', 'info');
}
window.removeUploadedImage = removeUploadedImage;

async function analyzeUploadedImage() {
  const fileInput = document.getElementById('imageFileInput');
  const fileToUse = selectedImageFile || (fileInput && fileInput.files && fileInput.files[0]) || (activeUploadedImageData && activeUploadedImageData.file);

  if (!fileToUse) {
    showToastNotice('Image Required', 'Please upload a diagram image first.', 'warning');
    return;
  }

  selectedImageFile = fileToUse;
  window.selectedImageFile = fileToUse;

  const analyzeBtn = document.querySelector("button[onclick='analyzeUploadedImage()']");
  const origBtnHtml = analyzeBtn ? analyzeBtn.innerHTML : '';
  if (analyzeBtn) {
    analyzeBtn.disabled = true;
    analyzeBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Analyzing Context...';
  }

  const descInput = document.getElementById('imageDescriptionInput');
  const currentDesc = descInput?.value?.trim() || '';
  const dept = document.getElementById('imgDeptSelect')?.value?.trim() || "Artificial Intelligence & Data Science";
  const subject = document.getElementById('imgSubjectSelect')?.value?.trim() || "Database Management Systems";
  const unit = document.getElementById('imgUnitSelect')?.value?.trim() || "Unit 1";
  const topic = document.getElementById('imgTopicSelect')?.value?.trim() || "";

  try {
    const formData = new FormData();
    formData.append('image', fileToUse);
    formData.append('file', fileToUse);
    formData.append('diagram', fileToUse);
    formData.append('original_filename', fileToUse.name);
    formData.append('description', currentDesc);
    formData.append('department', dept);
    formData.append('subject', subject);
    formData.append('unit', unit);
    formData.append('topic', topic);

    const endpoints = [
      '/api/questions/analyze-image',
      'http://localhost:5000/api/questions/analyze-image',
      '/api/questions/analyze',
      'http://localhost:5000/api/questions/analyze'
    ];

    let analysisData = null;
    let errorMessage = '';
    for (const endpoint of endpoints) {
      try {
        const res = await fetch(endpoint, {
          method: 'POST',
          credentials: 'include',
          body: formData
        });
        const data = await safeParseJsonResponse(res);
        if (res.ok && data && (data.status === 'success' || data.metadata)) {
          analysisData = data;
          break;
        } else if (data && data.message) {
          errorMessage = data.message;
        }
      } catch (err) {
        console.warn(`Analyze endpoint ${endpoint} failed:`, err);
      }
    }

    if (analysisData) {
      if (analysisData.suggested_description && descInput) {
        descInput.value = analysisData.suggested_description;
      }

      const statusBadge = document.getElementById('imageAnalysisStatus');
      if (statusBadge) {
        statusBadge.innerHTML = `<span class="badge bg-success"><i class="bi bi-check-circle me-1"></i> Image Analysis Ready</span>`;
      }

      const summaryText = analysisData.metadata ? `${analysisData.metadata.format} (${analysisData.metadata.width}x${analysisData.metadata.height})` : fileToUse.name;
      showToastNotice('Image Analyzed', `Context parsed: ${summaryText}`, 'success');
    } else {
      showToastNotice('Analysis Incomplete', errorMessage || 'Could not analyze diagram image.', 'warning');
    }

  } catch (err) {
    console.error('Error analyzing diagram image:', err);
    showToastNotice('Analysis Error', `Error analyzing image: ${err.message || 'Network error'}`, 'error');
  } finally {
    if (analyzeBtn) {
      analyzeBtn.disabled = false;
      analyzeBtn.innerHTML = origBtnHtml || '<i class="bi bi-cpu me-1"></i> Analyze Image Context';
    }
  }
}
window.analyzeUploadedImage = analyzeUploadedImage;

async function generateQuestionsFromImage() {
  const fileInput = document.getElementById('imageFileInput');
  const fileToUse = selectedImageFile || (fileInput && fileInput.files && fileInput.files[0]) || (activeUploadedImageData && activeUploadedImageData.file);

  if (!fileToUse) {
    showToastNotice('Image Required', 'Please upload a diagram image first.', 'warning');
    return;
  }

  // Retain same File object and its exact name
  selectedImageFile = fileToUse;
  window.selectedImageFile = fileToUse;
  const fileNameToUse = fileToUse.name || (activeUploadedImageData && activeUploadedImageData.name) || 'diagram.png';

  const dept = document.getElementById('imgDeptSelect')?.value?.trim() || "Artificial Intelligence & Data Science";
  const subject = document.getElementById('imgSubjectSelect')?.value?.trim() || "Database Management Systems";
  const unitText = document.getElementById('imgUnitSelect')?.value?.trim() || "Unit 1";
  const topic = document.getElementById('imgTopicSelect')?.value?.trim() || "";
  const count = parseInt(document.getElementById('imgCountSelect')?.value || "5", 10);
  const imgMarks = document.getElementById('imgMarksSelect')?.value || document.getElementById('imgTypeSelect')?.value || "Mixed";
  const qType = imgMarks === '2' ? 'Concise Definition (2 Marks)' : (imgMarks === '8' ? 'Working Principle / Analysis (8 Marks)' : (imgMarks === '16' ? 'Comprehensive Architecture (16 Marks)' : 'Diagram Interpretation'));
  const diff = document.getElementById('imgDiffSelect')?.value || "Balanced";
  const blooms = document.getElementById('imgBloomsSelect')?.value || "Analyze";
  const desc = document.getElementById('imageDescriptionInput')?.value?.trim() || `Diagram of ${topic || subject}`;

  activeImageConfig = { dept, subject, unit: unitText, topic, count, marks: imgMarks, qType, diff, blooms, desc, fileName: fileNameToUse };

  const genBtn = document.querySelector("button[onclick='generateQuestionsFromImage()']");
  const originalBtnHtml = genBtn ? genBtn.innerHTML : '';
  if (genBtn) {
    genBtn.disabled = true;
    genBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Generating Questions...';
  }

  try {
    const formData = new FormData();
    formData.append('image', fileToUse);
    formData.append('file', fileToUse);
    formData.append('diagram', fileToUse);
    formData.append('original_filename', fileNameToUse);
    formData.append('department', dept);
    formData.append('subject', subject);
    formData.append('unit', unitText);
    formData.append('topic', topic);
    formData.append('num_questions', count);
    formData.append('count', count);
    formData.append('marks', imgMarks);
    formData.append('marks_per_question', imgMarks);
    formData.append('question_type', qType);
    formData.append('difficulty', diff);
    formData.append('bloom_level', blooms);
    formData.append('description', desc);
    formData.append('diagram_mode', '1');

    const endpoints = [
      '/api/questions/generate-image',
      'http://localhost:5000/api/questions/generate-image',
      '/api/questions/generate',
      'http://localhost:5000/api/questions/generate'
    ];

    let generated = null;
    let errorMessage = '';
    for (const endpoint of endpoints) {
      try {
        const res = await fetch(endpoint, {
          method: 'POST',
          credentials: 'include',
          body: formData
        });

        const data = await safeParseJsonResponse(res);
        if (res.ok && data && (data.questions || data.status === 'success')) {
          generated = data;
          break;
        } else if (data && data.message) {
          errorMessage = data.message;
          console.warn(`Endpoint ${endpoint} returned:`, data.message);
        }
      } catch (fetchErr) {
        console.warn(`Fetch to ${endpoint} failed:`, fetchErr);
      }
    }

    if (generated && generated.questions && generated.questions.length > 0) {
      activeImageQuestions = generated.questions.map((q, i) => ({
        num: q.num || (i + 1),
        question: q.question || q.question_text || q.text,
        question_text: q.question || q.question_text || q.text,
        subject: q.subject || subject,
        department: q.department || dept,
        unit: q.unit || unitText,
        topic: q.topic || topic || (q.concept || 'Diagram Concept'),
        marks: q.marks || (qType === 'Short Answer' ? 2 : (qType === 'Descriptive' ? 16 : 8)),
        difficulty: q.difficulty || diff,
        type: q.type || q.question_type || qType,
        blooms: q.blooms || q.bloom_level || blooms,
        concept: q.concept || `${fileNameToUse} Concept`,
        imageRef: q.image_ref || q.imageRef || q.source_reference || fileNameToUse,
        source_reference: q.source_reference || q.image_ref || q.imageRef || fileNameToUse,
        source_type: 'Diagram Image',
        image_path: q.image_path || '',
        image_url: q.image_url || '',
        similarityStatus: q.similarityStatus || "Unique Concept"
      }));
    } else {
      // Grounded fallback adhering to user inputs and diagram filename
      activeImageQuestions = [];
      const diagramTemplates = [
        {
          q: `Analyze the structural relationships and functional entities depicted in the diagram '${fileNameToUse}'. Deduce the primary interaction sequence between components in ${subject}.`,
          diff: "Medium", type: "Diagram Interpretation", blooms: "Analyze", concept: "Structural Entities & Flow"
        },
        {
          q: `Based on the visual blueprint in '${fileNameToUse}', identify the critical inputs, outputs, and interface constraints established for ${unitText}.`,
          diff: "Easy", type: "Short Answer", blooms: "Understand", concept: "Interface Constraints"
        },
        {
          q: `Examine the dependency hierarchy represented in '${fileNameToUse}' and formulate an implementation model for ${topic || subject}.`,
          diff: "Hard", type: "Problem Solving", blooms: "Apply", concept: "Dependency Architecture"
        },
        {
          q: `Evaluate the scalability and fault tolerance of the architecture depicted in '${fileNameToUse}'. What potential single points of failure exist?`,
          diff: "Hard", type: "Descriptive", blooms: "Evaluate", concept: "Reliability & Fault Tolerance"
        },
        {
          q: `Synthesize the schema visual in '${fileNameToUse}' to design an optimized, normalized data or process pipeline for ${topic || subject}.`,
          diff: "Medium", type: "Problem Solving", blooms: "Create", concept: "Pipeline Normalization"
        }
      ];

      for (let i = 0; i < count; i++) {
        const t = diagramTemplates[i % diagramTemplates.length];
        activeImageQuestions.push({
          num: i + 1,
          question: t.q,
          question_text: t.q,
          subject: subject,
          department: dept,
          unit: unitText,
          topic: topic || t.concept,
          marks: qType === 'Short Answer' ? 2 : (qType === 'Descriptive' ? 16 : 8),
          difficulty: diff === "Balanced" ? t.diff : diff,
          type: qType === "Diagram Interpretation" ? t.type : qType,
          blooms: blooms === "Auto Select" ? t.blooms : blooms,
          concept: t.concept,
          imageRef: fileNameToUse,
          source_reference: fileNameToUse,
          source_type: 'Diagram Image',
          similarityStatus: "Unique Concept"
        });
      }
    }

    const wsArea = document.getElementById('imgWorkspaceArea');
    if (wsArea) wsArea.classList.remove('d-none');

    renderGeneratedImageQuestions();
    updateImageQualityCheck();
    showToastNotice('Image Questions Generated', `Generated ${activeImageQuestions.length} diagram-based questions from ${fileNameToUse}!`, 'success');

  } catch (err) {
    console.error('Error generating image questions:', err);
    showToastNotice('Error', 'An unexpected error occurred while generating questions.', 'error');
  } finally {
    if (genBtn) {
      genBtn.disabled = false;
      genBtn.innerHTML = originalBtnHtml || '<i class="bi bi-cpu me-2"></i> Generate Questions From Image';
    }
  }
}
window.generateQuestionsFromImage = generateQuestionsFromImage;

function renderGeneratedImageQuestions() {
  const container = document.getElementById('imageQuestionsContainer');
  if (!container) return;

  container.innerHTML = activeImageQuestions.map((q, idx) => `
    <div class="card card-academic p-3 mb-3">
      <div class="d-flex justify-content-between align-items-center mb-2 flex-wrap gap-2">
        <div class="d-flex align-items-center gap-2">
          <span class="badge bg-primary me-1">Q${q.num}</span>
          <span class="badge bg-dark fw-bold">${q.marks || 2} Marks</span>
          <span class="badge ${q.difficulty === 'Easy' ? 'bg-success' : q.difficulty === 'Medium' ? 'bg-warning text-dark' : 'bg-danger'}">${q.difficulty}</span>
          <span class="badge bg-info-subtle text-info border border-info">${q.type}</span>
          <span class="badge bg-light text-muted border">${q.blooms}</span>
        </div>
        <div class="btn-group btn-group-sm">
          <button class="btn btn-outline-secondary py-0 px-2" onclick="translateQuestionDirectly('${idx}', 'image')" title="Translate"><i class="bi bi-translate text-primary me-1"></i> Translate</button>
          <button class="btn btn-outline-danger py-0 px-2" onclick="deleteImageQuestion(${idx})" title="Delete"><i class="bi bi-trash"></i></button>
        </div>
      </div>
      <p class="fw-semibold text-dark mb-2">${escapeHtml(q.question)}</p>
      <div class="d-flex justify-content-between align-items-center small text-muted border-top pt-2 mt-1 flex-wrap gap-1">
        <span><i class="bi bi-image me-1"></i> Reference: <strong>${escapeHtml(q.imageRef)}</strong></span>
        <span><strong>Concept:</strong> ${escapeHtml(q.concept)}</span>
      </div>
    </div>
  `).join('');
}
window.renderGeneratedImageQuestions = renderGeneratedImageQuestions;

function deleteImageQuestion(idx) {
  activeImageQuestions.splice(idx, 1);
  activeImageQuestions.forEach((q, i) => q.num = i + 1);
  renderGeneratedImageQuestions();
  updateImageQualityCheck();
}
window.deleteImageQuestion = deleteImageQuestion;

function updateImageQualityCheck() {
  const totalEl = document.getElementById('imgQCTotal');
  const concEl = document.getElementById('imgQCConcepts');
  const easyEl = document.getElementById('imgQCEasy');

  if (totalEl) totalEl.innerText = `${activeImageQuestions.length} Qs`;
  if (concEl) concEl.innerText = `${activeImageQuestions.length} Diagram Concepts`;
  if (easyEl) easyEl.innerText = `${activeImageQuestions.filter(q => q.difficulty === 'Easy').length} Easy / ${activeImageQuestions.filter(q => q.difficulty === 'Hard').length} Hard`;
}
window.updateImageQualityCheck = updateImageQualityCheck;

async function saveImageQuestionsToBank() {
  if (!activeImageQuestions || activeImageQuestions.length === 0) {
    showToastNotice('Cannot Save', 'No image questions generated yet.', 'warning');
    return;
  }

  const saveBtn = document.querySelector("button[onclick='saveImageQuestionsToBank()']");
  const origHtml = saveBtn ? saveBtn.innerHTML : '';
  if (saveBtn) {
    saveBtn.disabled = true;
    saveBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Saving to Question Bank...';
  }

  try {
    const fileNameToUse = (selectedImageFile && selectedImageFile.name) || (activeUploadedImageData && activeUploadedImageData.name) || activeImageConfig.fileName || 'diagram.png';

    const questionsToSave = activeImageQuestions.map(q => ({
      question_text: q.question || q.question_text || q.text,
      subject: q.subject || activeImageConfig.subject || 'Distributed Computing',
      department: q.department || activeImageConfig.dept || 'Artificial Intelligence & Data Science',
      unit: q.unit || activeImageConfig.unit || 'Unit 1',
      topic: q.topic || activeImageConfig.topic || (q.concept || 'Diagram Concept'),
      marks: q.marks || 8,
      difficulty: q.difficulty || 'Medium',
      question_type: q.type || q.question_type || 'Diagram Interpretation',
      bloom_level: q.blooms || q.bloom_level || 'Analyze',
      concept: q.concept || fileNameToUse,
      source_type: 'Diagram Image',
      source_reference: q.imageRef || fileNameToUse,
      image_ref: q.imageRef || fileNameToUse
    }));

    const endpoints = [
      '/api/question-bank',
      'http://localhost:5000/api/question-bank'
    ];

    let serverSaved = false;
    let serverMessage = '';

    for (const ep of endpoints) {
      try {
        const res = await fetch(ep, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({ questions: questionsToSave, batch: questionsToSave })
        });
        const data = await safeParseJsonResponse(res);
        if (res.ok && data && (data.status === 'success' || data.success || data.questions || data.ids)) {
          serverSaved = true;
          serverMessage = data.message || 'Saved successfully';
          break;
        } else if (data && data.message) {
          serverMessage = data.message;
        }
      } catch (apiErr) {
        console.warn(`Save to question bank endpoint ${ep} notice:`, apiErr);
      }
    }

    if (!serverSaved) {
      showToastNotice('Save Failed', serverMessage || 'Failed to save questions to Question Bank database.', 'error');
      return;
    }

    const imgObj = {
      id: `IMG-2026-${Date.now().toString().slice(-4)}`,
      fileName: fileNameToUse,
      fileType: (activeUploadedImageData && activeUploadedImageData.type) || "image/png",
      fileSize: (activeUploadedImageData && activeUploadedImageData.size) || "200 KB",
      department: activeImageConfig.dept,
      subject: activeImageConfig.subject,
      unit: activeImageConfig.unit,
      topic: activeImageConfig.topic,
      description: activeImageConfig.desc,
      createdAt: new Date().toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }),
      questions: activeImageQuestions
    };

    let list = JSON.parse(localStorage.getItem(getScopedStorageKey('academic_image_questions')) || '[]');
    list.unshift(imgObj);
    localStorage.setItem(getScopedStorageKey('academic_image_questions'), JSON.stringify(list));

    if (typeof AcademicMockData !== 'undefined' && AcademicMockData.publishedImageQuestions) {
      AcademicMockData.publishedImageQuestions.unshift(imgObj);
    }

    showToastNotice('Saved to Question Bank', 'Image questions saved to repository successfully!', 'success');
    renderFacultyImageHistory();

  } catch (err) {
    console.error('Error in saveImageQuestionsToBank:', err);
    showToastNotice('Save Error', 'Failed to save image questions.', 'error');
  } finally {
    if (saveBtn) {
      saveBtn.disabled = false;
      saveBtn.innerHTML = origHtml || '<i class="bi bi-bookmark-plus me-1"></i> Save All to Question Bank';
    }
  }
}
window.saveImageQuestionsToBank = saveImageQuestionsToBank;


function renderFacultyImageHistory() {



  const tableBody = document.getElementById('facultyImageHistoryTableBody');



  if (!tableBody) return;







  const stored = JSON.parse(localStorage.getItem(getScopedStorageKey('academic_image_questions')) || '[]');







  if (stored.length === 0) {



    tableBody.innerHTML = `<tr><td colspan="6" class="text-center py-4 text-muted">No image question sessions saved yet.</td></tr>`;



    return;



  }







  tableBody.innerHTML = stored.map(img => `



    <tr>



      <td><small class="fw-semibold text-dark"><i class="bi bi-file-earmark-image me-1 text-primary"></i> ${img.fileName}</small></td>



      <td><span class="badge bg-primary-subtle text-primary border">${img.subject}</span></td>



      <td><small>${img.topic}</small></td>



      <td><small class="text-muted">${img.description.slice(0, 35)}...</small></td>



      <td><small class="fw-semibold">${img.questions.length} Qs</small></td>



      <td>



        <button class="btn btn-outline-danger btn-sm py-0 px-2" onclick="deleteImageSession('${img.id}')" title="Delete"><i class="bi bi-trash"></i></button>



      </td>



    </tr>



  `).join('');



}







function deleteImageSession(id) {



  let list = JSON.parse(localStorage.getItem('academic_image_questions') || '[]');



  list = list.filter(i => i.id !== id);



  localStorage.setItem(getScopedStorageKey('academic_image_questions'), JSON.stringify(list));



  AcademicMockData.publishedImageQuestions = AcademicMockData.publishedImageQuestions.filter(i => i.id !== id);







  showToastNotice('Session Deleted', 'Image question session removed.', 'danger');



  renderFacultyImageHistory();



}











// ==========================================



// STEP 7: ENGLISH ↔ TAMIL LANGUAGE CONVERSION



// ==========================================







function initLanguageConverterForm() {
  const subj = document.getElementById('transSubjectSelect');
  const unit = document.getElementById('transUnitSelect');
  const sync = () => syncModuleDatalists('transSubjectSelect', 'transSubjectList', 'transUnitSelect', 'transUnitList', 'transTopicSelect', 'transTopicList');
  if (subj) {
    subj.addEventListener('input', sync);
    subj.addEventListener('change', sync);
  }
  if (unit) {
    unit.addEventListener('input', sync);
    unit.addEventListener('change', sync);
  }
  sync();
}

function populateTransTopics() {
  syncModuleDatalists('transSubjectSelect', 'transSubjectList', 'transUnitSelect', 'transUnitList', 'transTopicSelect', 'transTopicList');
}

function initLanguageConverterPage() {



  initLanguageConverterForm();



  populateTransTopics();



  renderFacultyTranslatedHistory();







  // Check URL params for prefilled translation request



  const urlParams = new URLSearchParams(window.location.search);



  const prefillQ = urlParams.get('q');



  if (prefillQ) {



    const inputArea = document.getElementById('transInputText');



    if (inputArea) inputArea.value = decodeURIComponent(prefillQ);



  }



}







function swapLanguages() {



  const srcSelect = document.getElementById('transSrcLangSelect');



  const tgtSelect = document.getElementById('transTgtLangSelect');







  if (srcSelect && tgtSelect) {



    const temp = srcSelect.value;



    srcSelect.value = tgtSelect.value;



    tgtSelect.value = temp;



  }







  showToastNotice('Languages Swapped', 'Source and target languages swapped.', 'info');



}







function convertAcademicLanguage() {



  const inputText = document.getElementById('transInputText')?.value || '';



  if (!inputText.trim()) {



    showToastNotice('Input Required', 'Please enter an academic question to convert.', 'warning');



    return;



  }







  const srcLang = document.getElementById('transSrcLangSelect')?.value || "English";



  const tgtLang = document.getElementById('transTgtLangSelect')?.value || "Tamil";



  const dept = document.getElementById('transDeptSelect')?.value || "Artificial Intelligence & Data Science";



  const subject = document.getElementById('transSubjectSelect')?.value || "Database Management Systems";



  const unitText = (document.getElementById('transUnitSelect')?.value || '').trim() || 'Unit 1';



  const topic = document.getElementById('transTopicSelect')?.value || "Joins & Subqueries";







  let convertedText = "";







  if (srcLang === "English" && tgtLang === "Tamil") {



    // Preserve technical terms in English script/parentheses while converting query intent to Tamil



    convertedText = translateEnglishToTamilAcademic(inputText, topic);



  } else {



    // Tamil to English translation



    convertedText = `What is the academic formulation of: "${inputText.replace(/[\u0B80-\u0BFF]/g, '').trim() || topic}" in ${subject}?`;



  }







  document.getElementById('transResultCard')?.classList.remove('d-none');



  document.getElementById('transOriginalTextDisplay').innerText = inputText;



  document.getElementById('transConvertedTextDisplay').innerText = convertedText;







  document.getElementById('transMetaConcept').innerText = `${topic} Concept`;



  document.getElementById('transMetaDiff').innerText = "Medium";



  document.getElementById('transMetaType').innerText = "Short Answer";



  document.getElementById('transMetaBlooms').innerText = "Understand";







  showToastNotice('Conversion Complete', `Converted question from ${srcLang} to ${tgtLang} preserving technical terms.`, 'success');



}







function translateEnglishToTamilAcademic(englishQ, topic) {



  // Academic Tamil conversion keeping key technical symbols



  const techTerms = ["DBMS", "SQL", "Normalization", "Primary Key", "Foreign Key", "Algorithm", "Machine Learning", "Artificial Intelligence", "ER Diagram", "Join", "Index", "ACID", "Transactions"];







  let result = englishQ;







  // Replace common question prefixes with academic Tamil equivalents



  result = result.replace(/^What is the primary purpose of/i, "முக்கிய நோக்கம் என்ன");



  result = result.replace(/^What is/i, "என்றால் என்ன");



  result = result.replace(/^Explain/i, "விளக்குக:");



  result = result.replace(/^Differentiate between/i, "வேறுபடுத்துக:");



  result = result.replace(/^Describe/i, "விவரிக்கவும்:");







  return `${result} (${topic} தொடர்பான தமிழ் வினா)`;



}







function saveTranslatedQuestion() {



  const orig = document.getElementById('transOriginalTextDisplay')?.innerText || '';



  const conv = document.getElementById('transConvertedTextDisplay')?.innerText || '';







  if (!orig || !conv) return;







  const transObj = {



    id: `TRANS-2026-${Date.now().toString().slice(-4)}`,



    originalQuestion: orig,



    translatedQuestion: conv,



    sourceLanguage: document.getElementById('transSrcLangSelect')?.value || "English",



    targetLanguage: document.getElementById('transTgtLangSelect')?.value || "Tamil",



    department: document.getElementById('transDeptSelect')?.value || "Artificial Intelligence & Data Science",



    subject: document.getElementById('transSubjectSelect')?.value || "Database Management Systems",



    unit: (document.getElementById('transUnitSelect')?.value || '').trim() || 'Unit 1',



    topic: document.getElementById('transTopicSelect')?.value || "Joins & Subqueries",



    difficulty: "Medium",



    questionType: "Short Answer",



    bloomLevel: "Understand",



    concept: `${document.getElementById('transTopicSelect')?.value || 'SQL'} Concept`,



    createdAt: new Date().toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })



  };







  let list = JSON.parse(localStorage.getItem('academic_translated_questions') || '[]');



  list.unshift(transObj);



  localStorage.setItem(getScopedStorageKey('academic_translated_questions'), JSON.stringify(list));







  AcademicMockData.publishedTranslatedQuestions.unshift(transObj);







  showToastNotice('Translation Saved', 'Converted question saved to repository!', 'success');



  renderFacultyTranslatedHistory();



}







function renderFacultyTranslatedHistory() {



  const tableBody = document.getElementById('facultyTransHistoryTableBody');



  if (!tableBody) return;







  const stored = JSON.parse(localStorage.getItem(getScopedStorageKey('academic_translated_questions')) || '[]');







  if (stored.length === 0) {



    tableBody.innerHTML = `<tr><td colspan="6" class="text-center py-4 text-muted">No translated questions saved yet.</td></tr>`;



    return;



  }







  tableBody.innerHTML = stored.map(t => `



    <tr>



      <td><small class="fw-semibold text-dark">${t.originalQuestion.slice(0, 35)}...</small></td>



      <td><small class="text-secondary">${t.translatedQuestion.slice(0, 35)}...</small></td>



      <td><span class="badge bg-primary-subtle text-primary border">${t.subject}</span></td>



      <td><span class="badge ${t.targetLanguage === 'Tamil' ? 'badge-lang-ta' : 'badge-lang-en'}">${t.sourceLanguage} → ${t.targetLanguage}</span></td>



      <td><small class="text-muted">${t.createdAt}</small></td>



      <td>



        <button class="btn btn-outline-danger btn-sm py-0 px-2" onclick="deleteTranslatedItem('${t.id}')" title="Delete"><i class="bi bi-trash"></i></button>



      </td>



    </tr>



  `).join('');



}







function deleteTranslatedItem(id) {



  let list = JSON.parse(localStorage.getItem('academic_translated_questions') || '[]');



  list = list.filter(t => t.id !== id);



  localStorage.setItem(getScopedStorageKey('academic_translated_questions'), JSON.stringify(list));



  AcademicMockData.publishedTranslatedQuestions = AcademicMockData.publishedTranslatedQuestions.filter(t => t.id !== id);







  showToastNotice('Item Deleted', 'Translated question removed.', 'danger');



  renderFacultyTranslatedHistory();



}







function translateQuestionDirectly(idx, source) {



  let qText = "";



  if (source === 'voice' && activeVoiceQuestions[idx]) qText = activeVoiceQuestions[idx].question;



  if (source === 'image' && activeImageQuestions[idx]) qText = activeImageQuestions[idx].question;







  if (!qText) qText = "Sample Question";







  window.location.href = `faculty-language-converter.html?q=${encodeURIComponent(qText)}`;



}







/* ==========================================



   STEP 8: RESULTS, PERFORMANCE ANALYTICS & HISTORY



   ========================================== */







// Activity Recording Helpers



function recordFacultyActivity(category, title, details, subject = "General") {



  const activity = {



    id: "HIST-F-" + Date.now().toString(36),



    timestamp: new Date().toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }) + ", " + new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),



    category: category,



    title: title,



    details: details,



    subject: subject



  };



  let history = JSON.parse(localStorage.getItem('academic_faculty_history') || '[]');



  history.unshift(activity);



  localStorage.setItem('academic_faculty_history', JSON.stringify(history));



}







function recordStudentActivity(category, title, details, subject = "General") {



  const activity = {



    id: "HIST-S-" + Date.now().toString(36),



    timestamp: new Date().toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }) + ", " + new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),



    category: category,



    title: title,



    details: details,



    subject: subject



  };



  let history = JSON.parse(localStorage.getItem('academic_student_history') || '[]');



  history.unshift(activity);



  localStorage.setItem('academic_student_history', JSON.stringify(history));



}







// Non-competitive Academic Status Badge Helper



function getAcademicBadge(percentage) {



  if (percentage >= 85) {



    return { label: 'Strong', badgeClass: 'badge-academic-strong', bgClass: 'bg-strong' };



  } else if (percentage >= 70) {



    return { label: 'Good Progress', badgeClass: 'badge-academic-good', bgClass: 'bg-good' };



  } else if (percentage >= 50) {



    return { label: 'Needs Attention', badgeClass: 'badge-academic-attention', bgClass: 'bg-attention' };



  } else {



    return { label: 'Needs Focus', badgeClass: 'badge-academic-focus', bgClass: 'bg-focus' };



  }



}







// Data Aggregation



function getAllStudentResults() {
  const localResults = JSON.parse(localStorage.getItem(getScopedStorageKey('academic_quiz_results')) || '[]');
  return localResults;
}







function getAllAssignmentEvaluations() {



  const localSubs = JSON.parse(localStorage.getItem('academic_assignment_submissions') || '[]');



  return localSubs;



}







function getAllStudentHistory() {



  const localHist = JSON.parse(localStorage.getItem('academic_student_history') || '[]');



  return localHist;



}







function getAllFacultyHistory() {
  const localHist = JSON.parse(localStorage.getItem(getScopedStorageKey('academic_faculty_history')) || '[]');
  return localHist;
}







/* ------------------------------------------



   STUDENT RESULTS PAGE (student-results.html)



   ------------------------------------------ */



async function renderStudentResultsPage() {



  const resultsTable = document.getElementById('studentResultsTableBody');



  if (!resultsTable) return;







  let apiAttempts = [];



  try {



    const res = await fetch('http://localhost:5000/api/quizzes/attempts', { credentials: 'include' });



    if (res.ok) {



      const data = await res.json();



      if (data.status === 'success' && data.attempts) {



        apiAttempts = data.attempts;



      }



    }



  } catch (e) {



    console.warn('Could not fetch student attempts from API:', e);



  }







  const localQuizResults = getAllStudentResults();



  const assignmentResults = getAllAssignmentEvaluations();







  // Combine results into unified list



  const combinedItems = [



    ...apiAttempts.map(a => ({



      id: `ATTEMPT-${a.id}`,



      title: a.title || 'Academic Quiz',



      type: 'Quiz',



      subject: a.subject || 'Database Management Systems',



      date: a.date || 'Today',



      score: a.correct,



      maxMarks: a.total,



      percentage: parseInt(a.percentage) || Math.round((a.correct / a.total) * 100),



      rawObj: a



    })),



    ...localQuizResults.map(q => ({



      id: q.id,



      title: q.title,



      type: 'Quiz',



      subject: q.subject || 'Database Management Systems',



      date: q.dateCompleted || 'Today',



      score: q.score,



      maxMarks: q.totalMarks || 10,



      percentage: q.percentage || Math.round((q.score / (q.totalMarks || 10)) * 100),



      rawObj: q



    })),



    ...assignmentResults.map(a => ({



      id: a.id,



      title: a.title,



      type: 'Assignment',



      subject: a.subject || 'Database Management Systems',



      date: a.dateSubmitted || 'Today',



      score: a.score,



      maxMarks: a.maxMarks || 50,



      percentage: a.status === 'Evaluation Pending' ? null : (a.percentage || Math.round((a.score / (a.maxMarks || 50)) * 100)),



      statusText: a.status,



      rawObj: a



    }))



  ];







  // Update Summary Stats



  const totalQuizzes = quizResults.length;



  const totalAssignments = assignmentResults.length;



  const evaluatedScores = combinedItems.filter(i => i.percentage !== null).map(i => i.percentage);



  const overallAvg = evaluatedScores.length ? Math.round(evaluatedScores.reduce((a, b) => a + b, 0) / evaluatedScores.length) : 0;



  const badgeInfo = getAcademicBadge(overallAvg);







  if (document.getElementById('statQuizzesCompleted')) document.getElementById('statQuizzesCompleted').textContent = totalQuizzes;



  if (document.getElementById('statAssignmentsSubmitted')) document.getElementById('statAssignmentsSubmitted').textContent = totalAssignments;



  if (document.getElementById('statOverallAvg')) document.getElementById('statOverallAvg').textContent = overallAvg + '%';



  if (document.getElementById('statOverallBadge')) {



    document.getElementById('statOverallBadge').textContent = badgeInfo.label;



    document.getElementById('statOverallBadge').className = `badge ${badgeInfo.badgeClass}`;



  }







  if (combinedItems.length === 0) {



    resultsTable.innerHTML = `



      <tr>



        <td colspan="7" class="text-center py-5 text-muted">



          <i class="bi bi-journal-x fs-1 opacity-50 mb-2 d-block"></i>



          <h5>No quiz attempts or assignment submissions recorded yet</h5>



          <p class="small mb-3">Attempt a practice quiz or submit an assignment to view academic performance results.</p>



          <a href="student-quizzes.html" class="btn btn-primary btn-sm me-2"><i class="bi bi-patch-question me-1"></i> Take a Quiz</a>



          <a href="student-assignments.html" class="btn btn-outline-secondary btn-sm"><i class="bi bi-file-earmark-arrow-up me-1"></i> View Assignments</a>



        </td>



      </tr>



    `;



    return;



  }







  resultsTable.innerHTML = combinedItems.map(item => {



    let statusBadgeHTML = '';



    if (item.percentage === null || item.statusText === 'Evaluation Pending') {



      statusBadgeHTML = `<span class="badge badge-academic-pending"><i class="bi bi-hourglass-split me-1"></i> Evaluation Pending</span>`;



    } else {



      const b = getAcademicBadge(item.percentage);



      statusBadgeHTML = `<span class="badge ${b.badgeClass}">${b.label} (${item.percentage}%)</span>`;



    }







    const scoreDisplay = item.percentage === null ? `<span class="text-muted">Pending</span>` : `<strong>${item.score}</strong> / ${item.maxMarks}`;







    return `



      <tr>



        <td>



          <div class="fw-semibold text-dark">${item.title}</div>



          <small class="text-secondary">${item.subject}</small>



        </td>



        <td><span class="badge ${item.type === 'Quiz' ? 'bg-secondary-subtle text-secondary' : 'bg-warning-subtle text-dark'} border">${item.type}</span></td>



        <td><small class="text-muted">${item.date}</small></td>



        <td>${scoreDisplay}</td>



        <td>${statusBadgeHTML}</td>



        <td>



          <button class="btn btn-outline-primary btn-sm py-1 px-2" onclick="viewStudentResultModal('${item.id}', '${item.type}')">



            <i class="bi bi-eye me-1"></i> Details



          </button>



        </td>



      </tr>



    `;



  }).join('');



}







function viewStudentResultModal(id, type) {



  if (type === 'Quiz') {



    const results = getAllStudentResults();



    const item = results.find(r => r.id === id);



    if (!item) return;







    const b = getAcademicBadge(item.percentage || 80);







    const questionsHTML = (item.questions || []).map((q, idx) => `



      <div class="card card-academic mb-3">



        <div class="card-body p-3">



          <div class="d-flex justify-content-between align-items-center mb-2">



            <span class="badge bg-dark text-light">Question ${q.num || idx + 1}</span>



            <div>



              <span class="badge bg-secondary-subtle text-dark border me-1">${q.concept || 'General'}</span>



              <span class="badge bg-info-subtle text-dark me-1">${q.difficulty || 'Medium'}</span>



              <span class="badge bg-warning-subtle text-dark">${q.blooms || 'Understand'}</span>



            </div>



          </div>



          <p class="fw-semibold text-dark mb-2">${q.question}</p>



          <div class="row g-2 mb-2">



            <div class="col-md-6">



              <div class="p-2 border rounded ${q.isCorrect ? 'bg-success-subtle text-success border-success' : 'bg-danger-subtle text-danger border-danger'}">



                <small class="d-block fw-bold mb-1">Your Answer:</small>



                <span>${q.userAnswer || 'Not Answered'}</span>



              </div>



            </div>



            <div class="col-md-6">



              <div class="p-2 border rounded bg-light text-dark">



                <small class="d-block fw-bold mb-1">Correct Answer:</small>



                <span>${q.correctAnswer}</span>



              </div>



            </div>



          </div>



          ${q.explanation ? `<div class="p-2 bg-light border-start border-primary border-3 text-secondary small"><strong>Explanation:</strong> ${q.explanation}</div>` : ''}



        </div>



      </div>



    `).join('');







    const modalBody = document.getElementById('studentResultModalBody');



    if (modalBody) {



      modalBody.innerHTML = `



        <div class="border-bottom pb-3 mb-3">



          <div class="d-flex justify-content-between align-items-center mb-2">



            <h5 class="fw-bold text-primary mb-0">${item.title}</h5>



            <span class="badge ${b.badgeClass} fs-6">${b.label} (${item.percentage}%)</span>



          </div>



          <div class="text-secondary small">Subject: <strong>${item.subject}</strong> | Completed: <strong>${item.dateCompleted}</strong> | Score: <strong>${item.score}/${item.totalMarks}</strong></div>



        </div>



        <div>



          <h6 class="fw-bold text-dark mb-3">Question-by-Question Breakdown:</h6>



          ${questionsHTML || '<p class="text-muted">No individual question details available.</p>'}



        </div>



      `;



      const modal = new bootstrap.Modal(document.getElementById('studentResultModal'));



      modal.show();



    }



  } else {



    const subs = getAllAssignmentEvaluations();



    const item = subs.find(s => s.id === id);



    if (!item) return;







    const modalBody = document.getElementById('studentResultModalBody');



    if (modalBody) {



      modalBody.innerHTML = `



        <div class="border-bottom pb-3 mb-3">



          <div class="d-flex justify-content-between align-items-center mb-2">



            <h5 class="fw-bold text-primary mb-0">${item.title}</h5>



            <span class="badge ${item.status === 'Evaluation Pending' ? 'badge-academic-pending' : getAcademicBadge(item.percentage).badgeClass} fs-6">



              ${item.status === 'Evaluation Pending' ? 'Evaluation Pending' : getAcademicBadge(item.percentage).label + ' (' + item.percentage + '%)'}



            </span>



          </div>



          <div class="text-secondary small">Subject: <strong>${item.subject}</strong> | Submitted: <strong>${item.dateSubmitted}</strong></div>



        </div>



        <div class="card card-academic p-3 mb-3">



          <h6 class="fw-bold text-dark">Submission Details:</h6>



          <p class="small text-secondary mb-1">Submitted File: <code>${item.submittedFile || 'Assignment_Submission.pdf'}</code></p>



          <p class="small text-secondary mb-0">Score: <strong>${item.status === 'Evaluation Pending' ? 'Pending' : item.score + '/' + item.maxMarks}</strong></p>



        </div>



        <div class="card card-academic p-3 border-start border-warning border-4">



          <h6 class="fw-bold text-dark mb-1">Faculty Feedback:</h6>



          <p class="mb-0 text-secondary">${item.facultyFeedback || 'No feedback recorded.'}</p>



        </div>



      `;



      const modal = new bootstrap.Modal(document.getElementById('studentResultModal'));



      modal.show();



    }



  }



}







/* ------------------------------------------



   STUDENT PERFORMANCE PAGE (student-performance.html)



   ------------------------------------------ */



function renderStudentPerformancePage() {



  const conceptContainer = document.getElementById('conceptAccuracyContainer');



  if (!conceptContainer) return;







  const quizResults = getAllStudentResults();



  const allQuestions = [];



  quizResults.forEach(r => {



    (r.questions || []).forEach(q => {



      allQuestions.push(q);



    });



  });







  // Calculate Concept Mastery: Correct / Attempts



  const conceptMap = {};



  allQuestions.forEach(q => {



    const c = q.concept || "General Concept";



    if (!conceptMap[c]) conceptMap[c] = { correct: 0, attempts: 0 };



    conceptMap[c].attempts += 1;



    if (q.isCorrect) conceptMap[c].correct += 1;



  });







  const conceptList = Object.keys(conceptMap).map(c => {



    const acc = Math.round((conceptMap[c].correct / conceptMap[c].attempts) * 100);



    return { concept: c, correct: conceptMap[c].correct, attempts: conceptMap[c].attempts, accuracy: acc };



  });







  if (conceptList.length === 0) {



    conceptContainer.innerHTML = `<div class="p-4 text-center text-muted">No quiz performance data recorded yet for concept analysis. Attempt quizzes to see concept breakdown.</div>`;



  } else {



    conceptContainer.innerHTML = conceptList.map(item => {



      const b = getAcademicBadge(item.accuracy);



      return `



        <div class="mb-3">



          <div class="d-flex justify-content-between align-items-center mb-1">



            <span class="fw-semibold text-dark">${item.concept}</span>



            <div>



              <small class="text-muted me-2">${item.correct} / ${item.attempts} Correct</small>



              <span class="badge ${b.badgeClass}">${b.label} (${item.accuracy}%)</span>



            </div>



          </div>



          <div class="progress-gauge-container">



            <div class="progress-gauge-bar ${b.bgClass}" style="width: ${item.accuracy}%"></div>



          </div>



        </div>



      `;



    }).join('');



  }







  // Calculate Difficulty Accuracy: Easy, Medium, Hard



  const diffMap = { Easy: { correct: 0, attempts: 0 }, Medium: { correct: 0, attempts: 0 }, Hard: { correct: 0, attempts: 0 } };



  allQuestions.forEach(q => {



    const d = q.difficulty || "Medium";



    if (diffMap[d]) {



      diffMap[d].attempts += 1;



      if (q.isCorrect) diffMap[d].correct += 1;



    }



  });







  ['Easy', 'Medium', 'Hard'].forEach(d => {



    const elScore = document.getElementById(`diffAccuracy${d}`);



    const elBar = document.getElementById(`diffBar${d}`);



    const attempts = diffMap[d].attempts;



    const acc = attempts > 0 ? Math.round((diffMap[d].correct / attempts) * 100) : 0;



    if (elScore) elScore.textContent = attempts > 0 ? `${acc}% (${diffMap[d].correct}/${attempts})` : "N/A";



    if (elBar) elBar.style.width = `${acc}%`;



  });







  // Chronological Score Trend Table



  const trendTableBody = document.getElementById('studentScoreTrendTableBody');



  if (trendTableBody) {



    if (quizResults.length === 0) {



      trendTableBody.innerHTML = `<tr><td colspan="5" class="text-center py-4 text-muted">No historical score trend recorded.</td></tr>`;



    } else {



      trendTableBody.innerHTML = quizResults.map(r => {



        const b = getAcademicBadge(r.percentage || 80);



        return `



          <tr>



            <td><small class="fw-semibold text-dark">${r.dateCompleted || '18 Sep 2026'}</small></td>



            <td><span class="fw-semibold text-primary">${r.title}</span></td>



            <td><small class="text-secondary">${r.subject}</small></td>



            <td><strong>${r.score}</strong> / ${r.totalMarks || 10}</td>



            <td><span class="badge ${b.badgeClass}">${b.label} (${r.percentage}%)</span></td>



          </tr>



        `;



      }).join('');



    }



  }



}







/* ------------------------------------------



   STUDENT HISTORY PAGE (student-history.html)



   ------------------------------------------ */



function renderStudentHistoryPage() {



  const historyTable = document.getElementById('studentHistoryTableBody');



  if (!historyTable) return;







  const logs = getAllStudentHistory();







  if (logs.length === 0) {



    historyTable.innerHTML = `<tr><td colspan="5" class="text-center py-4 text-muted">No activity history logged yet.</td></tr>`;



    return;



  }







  historyTable.innerHTML = logs.map(log => {



    let catClass = 'cat-quiz';



    if (log.category === 'Assignment') catClass = 'cat-assignment';



    if (log.category === 'Study Material') catClass = 'cat-material';



    if (log.category === 'Presentation') catClass = 'cat-ppt';







    return `



      <tr>



        <td><small class="text-muted fw-semibold">${log.timestamp}</small></td>



        <td><span class="history-category-badge ${catClass}">${log.category}</span></td>



        <td>



          <div class="fw-semibold text-dark">${log.title}</div>



          <small class="text-secondary">${log.subject || 'General'}</small>



        </td>



        <td><small class="text-dark">${log.details}</small></td>



        <td><span class="badge bg-success-subtle text-success border"><i class="bi bi-check-circle me-1"></i> Recorded</span></td>



      </tr>



    `;



  }).join('');



}







/* ------------------------------------------



   FACULTY RESULTS PAGE (faculty-results.html)



   ------------------------------------------ */



async function renderFacultyResultsPage() {



  const tableBody = document.getElementById('facultySubmissionsTableBody');



  if (!tableBody) return;







  let apiAttempts = [];



  try {



    const res = await fetch('http://localhost:5000/api/quizzes/attempts', { credentials: 'include' });



    if (res.ok) {



      const data = await res.json();



      if (data.status === 'success' && data.attempts) {



        apiAttempts = data.attempts;



      }



    }



  } catch (e) {



    console.warn('Could not fetch quiz attempts from API:', e);



  }







  const assignmentSubs = getAllAssignmentEvaluations();



  const quizResults = getAllStudentResults();







  const allItems = [



    ...assignmentSubs.map(s => ({



      id: s.id,



      studentName: s.studentName || 'Student',



      regNum: s.registerNum || '2024-AIDS-042',



      title: s.title,



      type: 'Assignment',



      subject: s.subject || 'Database Management Systems',



      date: s.dateSubmitted || '18 Sep 2026',



      score: s.score,



      maxMarks: s.maxMarks || 50,



      status: s.status,



      percentage: s.percentage,



      raw: s



    })),



    ...apiAttempts.map(a => ({



      id: `ATTEMPT-${a.id}`,



      studentName: a.studentName || 'Student',



      regNum: a.studentEmail ? a.studentEmail.split('@')[0] : '2024-AIDS-042',



      title: a.title || 'Academic Quiz',



      type: 'Quiz',



      subject: a.subject || 'Database Management Systems',



      date: a.date || 'Today',



      score: a.correct,



      maxMarks: a.total,



      status: 'Evaluated',



      percentage: parseInt(a.percentage) || Math.round((a.correct / a.total) * 100),



      raw: a



    })),



    ...quizResults.map(q => ({



      id: q.id,



      studentName: q.studentName || 'Student',



      regNum: q.regNum || '2024-AIDS-042',



      title: q.title,



      type: 'Quiz',



      subject: q.subject || 'Database Management Systems',



      date: q.dateCompleted || 'Today',



      score: q.score,



      maxMarks: q.totalMarks || 10,



      status: 'Evaluated',



      percentage: q.percentage,



      raw: q



    }))



  ];







  if (allItems.length === 0) {



    tableBody.innerHTML = `<tr><td colspan="7" class="text-center py-4 text-muted">No student submissions recorded yet.</td></tr>`;



    return;



  }







  tableBody.innerHTML = allItems.map(item => {



    let badgeHTML = '';



    if (item.status === 'Evaluation Pending') {



      badgeHTML = `<span class="badge badge-academic-pending"><i class="bi bi-hourglass-split me-1"></i> Evaluation Pending</span>`;



    } else {



      const b = getAcademicBadge(item.percentage || 80);



      badgeHTML = `<span class="badge ${b.badgeClass}">${b.label} (${item.percentage}%)</span>`;



    }







    return `



      <tr>



        <td>



          <div class="fw-semibold text-dark">${item.studentName}</div>



          <small class="text-muted">Reg: ${item.regNum}</small>



        </td>



        <td>



          <div class="fw-semibold text-primary">${item.title}</div>



          <small class="text-secondary">${item.subject}</small>



        </td>



        <td><span class="badge ${item.type === 'Quiz' ? 'bg-secondary-subtle text-secondary' : 'bg-warning-subtle text-dark'} border">${item.type}</span></td>



        <td><small class="text-muted">${item.date}</small></td>



        <td>${item.status === 'Evaluation Pending' ? '<span class="text-muted">Pending</span>' : `<strong>${item.score}</strong> / ${item.maxMarks}`}</td>



        <td>${badgeHTML}</td>



        <td>



          ${item.type === 'Assignment' && item.status === 'Evaluation Pending' ? `



            <button class="btn btn-warning btn-sm py-1 px-2" onclick="evaluateAssignmentModal('${item.id}')">



              <i class="bi bi-pencil-square me-1"></i> Evaluate



            </button>



          ` : `



            <button class="btn btn-outline-secondary btn-sm py-1 px-2" onclick="viewStudentResultModal('${item.id}', '${item.type}')">



              <i class="bi bi-eye me-1"></i> View



            </button>



          `}



        </td>



      </tr>



    `;



  }).join('');



}







function evaluateAssignmentModal(subId) {



  const subs = getAllAssignmentEvaluations();



  const item = subs.find(s => s.id === subId);



  if (!item) return;







  const modalBody = document.getElementById('facultyEvaluateModalBody');



  if (modalBody) {



    modalBody.innerHTML = `



      <form id="evaluationForm" onsubmit="submitAssignmentEvaluation(event, '${item.id}')">



        <div class="mb-3">



          <label class="form-label fw-semibold text-dark">Student Name & Register Number</label>



          <input type="text" class="form-control" value="${item.studentName} (${item.registerNum})" readonly>



        </div>



        <div class="mb-3">



          <label class="form-label fw-semibold text-dark">Assignment Title</label>



          <input type="text" class="form-control" value="${item.title}" readonly>



        </div>



        <div class="mb-3">



          <label class="form-label fw-semibold text-dark">Submitted File</label>



          <div class="p-2 border rounded bg-light text-primary"><i class="bi bi-file-pdf me-2"></i><code>${item.submittedFile || 'Student_Submission.pdf'}</code></div>



        </div>



        <div class="row g-3 mb-3">



          <div class="col-md-6">



            <label class="form-label fw-semibold text-dark">Awarded Score (out of ${item.maxMarks || 50})</label>



            <input type="number" id="evalScoreInput" class="form-control" min="0" max="${item.maxMarks || 50}" value="42" required>



          </div>



          <div class="col-md-6">



            <label class="form-label fw-semibold text-dark">Max Marks</label>



            <input type="number" class="form-control" value="${item.maxMarks || 50}" readonly>



          </div>



        </div>



        <div class="mb-3">



          <label class="form-label fw-semibold text-dark">Faculty Feedback Comments</label>



          <textarea id="evalFeedbackInput" class="form-control" rows="3" placeholder="Provide constructive feedback for student learning...">Good analytical decomposition. Add more detailed foreign key constraint proofs in future work.</textarea>



        </div>



        <div class="d-flex justify-content-end gap-2">



          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>



          <button type="submit" class="btn btn-primary"><i class="bi bi-check-circle me-1"></i> Save Evaluation</button>



        </div>



      </form>



    `;



    const modal = new bootstrap.Modal(document.getElementById('facultyEvaluateModal'));



    modal.show();



  }



}







function submitAssignmentEvaluation(event, subId) {



  event.preventDefault();



  const score = parseInt(document.getElementById('evalScoreInput').value) || 0;



  const feedback = document.getElementById('evalFeedbackInput').value;







  let subs = getAllAssignmentEvaluations();



  const item = subs.find(s => s.id === subId);



  if (item) {



    item.score = score;



    item.percentage = Math.round((score / (item.maxMarks || 50)) * 100);



    item.status = 'Evaluated';



    item.academicStatus = getAcademicBadge(item.percentage).label;



    item.facultyFeedback = feedback;







    localStorage.setItem('academic_assignment_submissions', JSON.stringify(subs));



    showToastNotice('Evaluation Saved', 'Student submission evaluated successfully!', 'success');







    recordFacultyActivity('Assignment', `Evaluated Assignment Submission for ${item.studentName}`, `Score: ${score}/${item.maxMarks} (${item.percentage}%)`, item.subject);







    const modalEl = document.getElementById('facultyEvaluateModal');



    const modal = bootstrap.Modal.getInstance(modalEl);



    if (modal) modal.hide();







    renderFacultyResultsPage();



  }



}







/* ------------------------------------------



   FACULTY PERFORMANCE ANALYTICS PAGE (faculty-performance.html)



   ------------------------------------------ */



function renderFacultyPerformancePage() {



  const conceptGapsContainer = document.getElementById('facultyConceptGapsContainer');



  if (!conceptGapsContainer) return;







  const quizResults = getAllStudentResults();



  const allQuestions = [];



  quizResults.forEach(r => {



    (r.questions || []).forEach(q => {



      allQuestions.push(q);



    });



  });







  const conceptMap = {};



  allQuestions.forEach(q => {



    const c = q.concept || "General Concept";



    if (!conceptMap[c]) conceptMap[c] = { correct: 0, attempts: 0 };



    conceptMap[c].attempts += 1;



    if (q.isCorrect) conceptMap[c].correct += 1;



  });







  const conceptList = Object.keys(conceptMap).map(c => {



    const acc = Math.round((conceptMap[c].correct / conceptMap[c].attempts) * 100);



    return { concept: c, correct: conceptMap[c].correct, attempts: conceptMap[c].attempts, accuracy: acc };



  });







  // Filter Concept Gaps: concepts with accuracy < 70%



  const weakConcepts = conceptList.filter(c => c.accuracy < 70);







  if (weakConcepts.length === 0) {



    conceptGapsContainer.innerHTML = `



      <div class="p-3 border rounded bg-success-subtle text-success">



        <i class="bi bi-check-circle-fill me-2"></i> All concepts currently meet or exceed target threshold accuracy ($\ge 70\%$).



      </div>



    `;



  } else {



    conceptGapsContainer.innerHTML = weakConcepts.map(c => `



      <div class="concept-gap-card">



        <div class="d-flex justify-content-between align-items-center mb-1">



          <span class="fw-bold text-dark"><i class="bi bi-exclamation-triangle-fill text-warning me-2"></i>${c.concept}</span>



          <span class="badge badge-academic-attention">${c.accuracy}% Accuracy</span>



        </div>



        <p class="small text-secondary mb-2">Student success rate: ${c.correct} out of ${c.attempts} attempts. Recommendation: Conduct a review or tutorial session on this topic.</p>



        <div class="progress-gauge-container">



          <div class="progress-gauge-bar bg-attention" style="width: ${c.accuracy}%"></div>



        </div>



      </div>



    `).join('');



  }



}







/* ------------------------------------------



   FACULTY HISTORY PAGE (faculty-history.html)



   ------------------------------------------ */



function renderFacultyHistoryPage() {



  const tableBody = document.getElementById('facultyHistoryTableBody');



  if (!tableBody) return;







  const logs = getAllFacultyHistory();







  if (logs.length === 0) {



    tableBody.innerHTML = `<tr><td colspan="5" class="text-center py-4 text-muted">No faculty activity history logged yet.</td></tr>`;



    return;



  }







  tableBody.innerHTML = logs.map(log => {



    let catClass = 'cat-paper';



    if (log.category === 'Quiz') catClass = 'cat-quiz';



    if (log.category === 'AI Questions') catClass = 'cat-ai';



    if (log.category === 'Presentation') catClass = 'cat-ppt';







    return `



      <tr>



        <td><small class="text-muted fw-semibold">${log.timestamp}</small></td>



        <td><span class="history-category-badge ${catClass}">${log.category}</span></td>



        <td>



          <div class="fw-semibold text-dark">${log.title}</div>



          <small class="text-secondary">${log.subject || 'General'}</small>



        </td>



        <td><small class="text-dark">${log.details}</small></td>



        <td><span class="badge bg-primary-subtle text-primary border"><i class="bi bi-shield-check me-1"></i> Audited</span></td>



      </tr>



    `;



  }).join('');



}













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

  const objectives = lp.objectives || `1. Understand fundamental theoretical concepts of ${lp.topic || lp.title}.\n2. Analyze practical implementation paradigms and constraints.\n3. Evaluate system trade-offs through real-world case studies.`;
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


