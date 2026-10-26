import re
import sys

app_js_path = r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\js\app.js"

with open(app_js_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update header helpers (safeParseJsonResponse, refreshFacultyGenResources, handleQuickUploadForGen, updateSourceMaterialDisplay)
old_top_block = """// === Faculty Study Materials & Grounded Question Generation Helpers ===

window.facultyAcademicResources = [];

async function refreshFacultyGenResources() {
  const resourceSelect = document.getElementById('genResourceSelect');
  const subjectInput = document.getElementById('genSubject');
  const subj = subjectInput?.value?.trim() || '';

  try {
    const res = await fetch('/api/resources', { credentials: 'include' });
    if (res.ok) {
      const data = await res.json();
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
}"""

new_top_block = """// === Faculty Study Materials & Grounded Question Generation Helpers ===

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
}"""

# Normalize \r\n to \n for matching then replace
content_norm = content.replace("\r\n", "\n")

if old_top_block in content_norm:
    content_norm = content_norm.replace(old_top_block, new_top_block, 1)
    print("Top block replaced successfully!")
else:
    print("Top block NOT found!")
    sys.exit(1)

# 2. Update updateSourceMaterialDisplay 'else' branch to recognize genQuickUploadFile
old_else = """  } else {
    if (statusBadge) {
      statusBadge.className = 'badge bg-warning text-dark';
      statusBadge.innerText = 'No Materials Attached';
    }
    if (verifiedDisp) {
      verifiedDisp.innerHTML = `<i class="bi bi-exclamation-triangle text-warning me-1"></i> None (Upload needed)`;
    }
    if (topicsDisp) topicsDisp.innerText = 'Please upload a Syllabus or Notes file (PDF, DOCX, TXT) or select Question Bank';
    if (conceptsDisp) conceptsDisp.innerText = 'Awaiting uploaded document or question bank selection';
  }"""

new_else = """  } else {
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
  }"""

if old_else in content_norm:
    content_norm = content_norm.replace(old_else, new_else, 1)
    print("updateSourceMaterialDisplay else branch updated successfully!")
else:
    print("updateSourceMaterialDisplay else branch NOT found!")
    sys.exit(1)

# 3. Update handleQuickUploadForGen
old_upload = """async function handleQuickUploadForGen() {
  const fileInput = document.getElementById('genQuickUploadFile');
  const typeSelect = document.getElementById('genQuickUploadType');
  const subjectInput = document.getElementById('genSubject');
  const deptInput = document.getElementById('genDept');
  const unitInput = document.getElementById('genUnit');
  const topicInput = document.getElementById('genTopic');

  if (!fileInput || !fileInput.files || fileInput.files.length === 0) {
    showToastNotice('Upload Error', 'Please select a PDF, DOCX, or TXT file to upload.', 'warning');
    return;
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

  try {
    const res = await fetch('/api/resources', {
      method: 'POST',
      credentials: 'include',
      body: formData
    });
    const data = await res.json();
    if (res.ok && data.status === 'success') {
      showToastNotice('Material Uploaded', `Successfully uploaded and registered ${file.name}!`, 'success');
      await refreshFacultyGenResources();
      if (data.resource && document.getElementById('genResourceSelect')) {
        document.getElementById('genResourceSelect').value = data.resource.id;
      }
      updateSourceMaterialDisplay();
    } else {
      showToastNotice('Upload Failed', data.message || 'Failed to upload resource.', 'danger');
    }
  } catch (err) {
    console.error('Quick upload error:', err);
    showToastNotice('Server Error', 'Failed to communicate with upload service.', 'danger');
  }
}"""

new_upload = """async function handleQuickUploadForGen() {
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
}"""

if old_upload in content_norm:
    content_norm = content_norm.replace(old_upload, new_upload, 1)
    print("handleQuickUploadForGen replaced successfully!")
else:
    print("handleQuickUploadForGen NOT found!")
    sys.exit(1)

# 4. Update Question Generator Form Submit to auto-upload selected file if needed and use safeParseJsonResponse + API_QUESTIONS_BASE
old_form_fetch = """      const payload = {
        department,
        subject,
        academic_year,
        semester,
        unit,
        topic,
        num_questions: numQuestions,
        question_type,
        bloom_level: blooms_choice,
        diff_easy: pEasy,
        diff_medium: pMedium,
        diff_hard: pHard,
        resource_id: resourceId,
        use_question_bank: useQb
      };

      try {
        const res = await fetch('/api/questions/generate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify(payload)
        });

        const data = await res.json();"""

new_form_fetch = """      let effectiveResourceId = resourceId;
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

        const data = await safeParseJsonResponse(res);"""

if old_form_fetch in content_norm:
    content_norm = content_norm.replace(old_form_fetch, new_form_fetch, 1)
    print("Question form fetch replaced successfully!")
else:
    print("Question form fetch NOT found!")
    sys.exit(1)

# 5. Also attach onchange event listener for genQuickUploadFile in initQuestionGeneratorPage
old_init_input = """  if (topicInput) {
    topicInput.addEventListener('input', () => {
      if (typeof updateSourceMaterialDisplay === 'function') updateSourceMaterialDisplay();
    });
  }"""

new_init_input = """  if (topicInput) {
    topicInput.addEventListener('input', () => {
      if (typeof updateSourceMaterialDisplay === 'function') updateSourceMaterialDisplay();
    });
  }

  const quickUploadInp = document.getElementById('genQuickUploadFile');
  if (quickUploadInp) {
    quickUploadInp.addEventListener('change', onQuickUploadFileSelected);
  }"""

if old_init_input in content_norm:
    content_norm = content_norm.replace(old_init_input, new_init_input, 1)
    print("initQuestionGeneratorPage quickUploadInp listener attached successfully!")
else:
    print("initQuestionGeneratorPage quickUploadInp listener NOT found!")
    sys.exit(1)

# 6. Update quiz generator fetch calls
old_quiz_res = """  // Fetch faculty resources to populate subject suggestions and update source panel
  try {
    fetch('/api/resources', { credentials: 'include' })
      .then(res => res.json())"""

new_quiz_res = """  // Fetch faculty resources to populate subject suggestions and update source panel
  try {
    const quizResUrl = (typeof API_RESOURCES_BASE !== 'undefined' && API_RESOURCES_BASE)
      ? API_RESOURCES_BASE
      : 'http://localhost:5000/api/resources';
    fetch(quizResUrl, { credentials: 'include' })
      .then(res => safeParseJsonResponse(res))"""

if old_quiz_res in content_norm:
    content_norm = content_norm.replace(old_quiz_res, new_quiz_res, 1)
    print("Quiz resources fetch replaced successfully!")
else:
    print("Quiz resources fetch NOT found!")
    sys.exit(1)

old_quiz_gen = """  try {
    const res = await fetch('/api/quizzes/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(payload)
    });

    const data = await res.json();"""

new_quiz_gen = """  try {
    const quizGenUrl = (typeof API_QUIZZES_BASE !== 'undefined' && API_QUIZZES_BASE)
      ? `${API_QUIZZES_BASE}/generate`
      : 'http://localhost:5000/api/quizzes/generate';

    const res = await fetch(quizGenUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(payload)
    });

    const data = await safeParseJsonResponse(res);"""

if old_quiz_gen in content_norm:
    content_norm = content_norm.replace(old_quiz_gen, new_quiz_gen, 1)
    print("Quiz generate fetch replaced successfully!")
else:
    print("Quiz generate fetch NOT found!")
    sys.exit(1)

# Save back with original \r\n line endings
with open(app_js_path, "w", encoding="utf-8", newline="\r\n") as f:
    f.write(content_norm.replace("\n", "\r\n"))

print("All app.js updates applied successfully!")
