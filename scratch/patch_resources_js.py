filepath = 'C:/Users/Nisha/.gemini/antigravity/scratch/academic-question-system/js/app.js'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update renderFacultyResourcesTable to populate datalist and add Edit button
old_row_render = """              <button class="btn btn-outline-primary py-0 px-2" onclick="viewFacultyResource(${r.id})" title="View Details">

                <i class="bi bi-eye"></i>

              </button>

              <button class="btn btn-outline-success py-0 px-2" onclick="analyzeFacultyResource(${r.id})" title="Analyze Content">"""

new_row_render = """              <button class="btn btn-outline-primary py-0 px-2" onclick="viewFacultyResource(${r.id})" title="View Details">

                <i class="bi bi-eye"></i>

              </button>

              <button class="btn btn-outline-warning py-0 px-2" onclick="openEditResourceModal(${r.id})" title="Edit Resource">

                <i class="bi bi-pencil"></i>

              </button>

              <button class="btn btn-outline-success py-0 px-2" onclick="analyzeFacultyResource(${r.id})" title="Analyze Content">"""

if old_row_render in content:
    content = content.replace(old_row_render, new_row_render)
    print("Added Edit button to resource actions.")
else:
    print("Warning: old_row_render not matched directly, checking normalized...")
    old_row_norm = old_row_render.replace('\r\n', '\n')
    content_norm = content.replace('\r\n', '\n')
    if old_row_norm in content_norm:
        content = content_norm.replace(old_row_norm, new_row_render.replace('\r\n', '\n'))
        print("Added Edit button (normalized).")
    else:
        print("Error: Could not locate old_row_render!")
        exit(1)

# 2. Add datalist population inside renderFacultyResourcesTable
old_map_start = """    tableBody.innerHTML = resources.map(r => {"""
new_map_start = """    // Augment subject datalist suggestions with existing subjects from user's repository
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

    tableBody.innerHTML = resources.map(r => {"""

if old_map_start in content:
    content = content.replace(old_map_start, new_map_start)
    print("Added datalist population.")
else:
    old_map_norm = old_map_start.replace('\r\n', '\n')
    content_norm = content.replace('\r\n', '\n')
    if old_map_norm in content_norm:
        content = content_norm.replace(old_map_norm, new_map_start.replace('\r\n', '\n'))
        print("Added datalist population (normalized).")
    else:
        print("Error: Could not locate old_map_start!")
        exit(1)

# 3. Add openEditResourceModal and edit form handler right after deleteFacultyResource
old_del_end = """    console.error('Delete resource error:', err);

    showToastNotice('Error', 'Failed to delete resource.', 'danger');

  }

}"""

new_edit_funcs = """    console.error('Delete resource error:', err);

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

}"""

if old_del_end in content:
    content = content.replace(old_del_end, new_edit_funcs)
    print("Added openEditResourceModal and initEditResourceForm.")
else:
    old_del_norm = old_del_end.replace('\r\n', '\n')
    content_norm = content.replace('\r\n', '\n')
    if old_del_norm in content_norm:
        content = content_norm.replace(old_del_norm, new_edit_funcs.replace('\r\n', '\n'))
        print("Added openEditResourceModal (normalized).")
    else:
        print("Error: Could not locate old_del_end!")
        exit(1)

# 4. Call initEditResourceForm inside bindFormHandlers or DOMContentLoaded
bind_handlers_str = "function bindFormHandlers() {"
if bind_handlers_str in content:
    content = content.replace(bind_handlers_str, bind_handlers_str + "\n  initEditResourceForm();")
    print("Added initEditResourceForm() to bindFormHandlers.")

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Successfully updated js/app.js")
