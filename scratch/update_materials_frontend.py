import os

app_path = r'C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\js\app.js'
with open(app_path, 'r', encoding='utf-8') as f:
    text = f.read()

start_idx = text.find('async function renderStudentMaterialsTable')
end_idx = text.find('// Universal Faculty Header Profile Synchronizer')

new_materials_code = """
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
    const response = await fetch(API_RESOURCES_BASE, {
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
      const res = await fetch(`${API_RESOURCES_BASE}/${resourceId}`, { credentials: 'include' });
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

"""

text = text[:start_idx] + new_materials_code + "\n\n" + text[end_idx:]

with open(app_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated renderStudentMaterialsTable and viewStudentMaterial successfully!")
