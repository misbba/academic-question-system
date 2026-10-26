import os
import re

app_js_path = r'C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\js\app.js'
with open(app_js_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update populateQuestionDropdowns and updateTopicDropdown to support datalists
old_populate = '''function populateQuestionDropdowns() {

  const subjectSelect = document.getElementById('genSubject');

  const unitSelect = document.getElementById('genUnit');

  const topicSelect = document.getElementById('genTopic');



  if (!subjectSelect || !unitSelect || !topicSelect) return;



  const subject = subjectSelect.value || "Database Management Systems";

  const struct = (typeof AcademicMockData !== 'undefined' && AcademicMockData.subjectStructure)

    ? AcademicMockData.subjectStructure[subject]

    : null;



  unitSelect.innerHTML = '';

  if (struct && struct.units && struct.units.length > 0) {

    struct.units.forEach(u => {

      const opt = document.createElement('option');

      opt.value = u.name;

      opt.textContent = u.name;

      unitSelect.appendChild(opt);

    });

  } else {

    const defaultUnits = [

      "Unit I — Introduction",

      "Unit II — Core Concepts",

      "Unit III — Advanced Topics",

      "Unit IV — Applications",

      "Unit V — System Design"

    ];

    defaultUnits.forEach(u => {

      const opt = document.createElement('option');

      opt.value = u;

      opt.textContent = u;

      unitSelect.appendChild(opt);

    });

  }



  updateTopicDropdown();

}'''

new_populate = '''function populateQuestionDropdowns() {
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
}'''

if old_populate in content:
    content = content.replace(old_populate, new_populate, 1)
    print("populateQuestionDropdowns replaced successfully.")
else:
    print("Warning: old_populate not matched exactly.")


# 2. Update updateTopicDropdown to support datalist
old_update_topic = '''function updateTopicDropdown() {

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

}'''

new_update_topic = '''function updateTopicDropdown() {
  const subjectInput = document.getElementById('genSubject');
  const unitInput = document.getElementById('genUnit');
  const topicInput = document.getElementById('genTopic');

  if (!subjectInput || !unitInput || !topicInput) return;

  const subject = subjectInput.value;
  const selectedUnitName = unitInput.value;
  const struct = (typeof AcademicMockData !== 'undefined' && AcademicMockData.subjectStructure)
    ? AcademicMockData.subjectStructure[subject]
    : null;

  let topics = [];
  if (struct && struct.units) {
    const matchedUnit = struct.units.find(u => u.name === selectedUnitName);
    if (matchedUnit && matchedUnit.topics) {
      topics = matchedUnit.topics;
    }
  }

  if (topics.length === 0) {
    topics = ["All Topics", "Fundamental Architecture", "Core Implementation Patterns", "Practical Problem Solving", "Advanced Analytical Models"];
  }

  const topicDatalist = document.getElementById('genTopicList');
  if (topicDatalist) {
    topicDatalist.innerHTML = topics.map(t => `<option value="${t}">`).join('');
  }
  if (topicInput.tagName === 'SELECT') {
    topicInput.innerHTML = topics.map(t => `<option value="${t}">${t}</option>`).join('');
  }
}'''

if old_update_topic in content:
    content = content.replace(old_update_topic, new_update_topic, 1)
    print("updateTopicDropdown replaced successfully.")
else:
    print("Warning: old_update_topic not matched exactly.")


# 3. Add refreshFacultyGenResources, updateSourceMaterialDisplay, handleQuickUploadForGen, edit/regenerate/delete functions
helpers_code = '''

// === Faculty Study Materials & Grounded Question Generation Helpers ===

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

async function handleQuickUploadForGen() {
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
  formData.append('topic', topicInput?.value?.trim() || file.name.replace(/\\.[^/.]+$/, ''));
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
'''

if "function handleQuickUploadForGen" not in content:
    content = helpers_code + '\n' + content
    print("helpers_code prepended successfully.")

with open(app_js_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("scratch/patch_app_js_features.py completed.")
