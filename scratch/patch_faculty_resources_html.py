filepath = 'C:/Users/Nisha/.gemini/antigravity/scratch/academic-question-system/faculty-resources.html'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the Subject select dropdown with input + datalist
old_subject_block = """              <!-- Subject -->
              <div class="col-md-6">
                <label for="resourceSubject" class="form-label fw-semibold">Subject</label>
                <select class="form-select" id="resourceSubject" required>
                  <option value="Database Management Systems" selected>Database Management Systems</option>
                  <option value="Data Structures">Data Structures</option>
                  <option value="Artificial Intelligence">Artificial Intelligence</option>
                  <option value="Machine Learning">Machine Learning</option>
                  <option value="Computer Networks">Computer Networks</option>
                </select>
              </div>"""

new_subject_block = """              <!-- Subject -->
              <div class="col-md-6">
                <label for="resourceSubject" class="form-label fw-semibold">Subject</label>
                <input type="text" class="form-control" id="resourceSubject" list="resourceSubjectList" placeholder="Enter or select subject..." required autocomplete="off">
                <datalist id="resourceSubjectList">
                  <option value="Database Management Systems">
                  <option value="Data Structures">
                  <option value="Artificial Intelligence">
                  <option value="Machine Learning">
                  <option value="Computer Networks">
                  <option value="Cloud Computing">
                  <option value="Operating Systems">
                  <option value="Cyber Security">
                </datalist>
                <div class="form-text text-muted small">Choose from suggestions or type any custom subject name.</div>
              </div>"""

if old_subject_block in content:
    content = content.replace(old_subject_block, new_subject_block)
    print("Replaced Subject select with input + datalist.")
else:
    # Try normalizing newlines
    old_norm = old_subject_block.replace('\r\n', '\n')
    content_norm = content.replace('\r\n', '\n')
    if old_norm in content_norm:
        content = content_norm.replace(old_norm, new_subject_block.replace('\r\n', '\n'))
        print("Replaced Subject select (normalized newlines).")
    else:
        print("Error: Could not locate old_subject_block!")
        exit(1)

# Add Edit Resource Modal if not present
edit_modal = """  <!-- Edit Resource Modal -->
  <div class="modal fade" id="editResourceModal" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog modal-lg modal-dialog-centered">
      <div class="modal-content card-academic">
        <div class="modal-header card-academic-header">
          <h5 class="modal-title" id="editResourceTitle">
            <i class="bi bi-pencil-square text-warning me-2"></i> Edit Academic Resource
          </h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <form id="editResourceForm">
          <input type="hidden" id="editResourceId">
          <div class="modal-body p-4">
            <div class="row g-3">
              <div class="col-md-6">
                <label for="editResourceSubject" class="form-label fw-semibold">Subject</label>
                <input type="text" class="form-control" id="editResourceSubject" list="resourceSubjectList" placeholder="Enter or select subject..." required autocomplete="off">
                <div class="form-text text-muted small">Choose from suggestions or type any custom subject name.</div>
              </div>
              <div class="col-md-6">
                <label for="editResourceDept" class="form-label fw-semibold">Department</label>
                <select class="form-select" id="editResourceDept" required>
                  <option value="Artificial Intelligence & Data Science">Artificial Intelligence & Data Science</option>
                  <option value="Artificial Intelligence & Machine Learning">Artificial Intelligence & Machine Learning</option>
                  <option value="Computer and Communication Engineering">Computer and Communication Engineering</option>
                </select>
              </div>
              <div class="col-md-4">
                <label for="editResourceYear" class="form-label fw-semibold">Academic Year</label>
                <select class="form-select" id="editResourceYear" required>
                  <option value="2025-2026">2025 - 2026</option>
                  <option value="2026-2027">2026 - 2027</option>
                </select>
              </div>
              <div class="col-md-4">
                <label for="editResourceSem" class="form-label fw-semibold">Semester</label>
                <select class="form-select" id="editResourceSem" required>
                  <option value="Semester 4">Semester 4</option>
                  <option value="Semester 6">Semester 6</option>
                  <option value="Semester 8">Semester 8</option>
                </select>
              </div>
              <div class="col-md-4">
                <label for="editResourceUnit" class="form-label fw-semibold">Unit</label>
                <select class="form-select" id="editResourceUnit" required>
                  <option value="All Units">All Units (Complete Syllabus)</option>
                  <option value="Unit I">Unit I - Fundamentals</option>
                  <option value="Unit II">Unit II - Normalization & Schema Design</option>
                  <option value="Unit III">Unit III — SQL</option>
                  <option value="Unit IV">Unit IV - Transactions & Concurrency</option>
                  <option value="Unit V">Unit V - Storage & Indexing</option>
                </select>
              </div>
              <div class="col-md-6">
                <label for="editResourceTopic" class="form-label fw-semibold">Topic / Chapter Name</label>
                <input type="text" class="form-control" id="editResourceTopic" required>
              </div>
              <div class="col-md-6">
                <label for="editResourceType" class="form-label fw-semibold">Resource Type</label>
                <select class="form-select" id="editResourceType" required>
                  <option value="Syllabus">Syllabus</option>
                  <option value="Book">Book / Textbook</option>
                  <option value="Study Material">Study Material</option>
                  <option value="PDF">PDF / Document</option>
                  <option value="Image">Image / Diagram</option>
                </select>
              </div>
              <div class="col-12">
                <label for="editResourceFile" class="form-label fw-semibold">Replace File (Optional)</label>
                <input class="form-control" type="file" id="editResourceFile" accept=".pdf,.doc,.docx,.ppt,.pptx,.png,.jpg,.jpeg">
                <div id="editFileFeedback" class="small text-muted mt-1">Leave empty to keep existing file.</div>
              </div>
            </div>
          </div>
          <div class="modal-footer border-top bg-light">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button type="submit" class="btn btn-academic-primary">
              <i class="bi bi-save me-1"></i> Save Changes
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</body>"""

if 'editResourceModal' not in content:
    content = content.replace('</body>', edit_modal)
    print("Added Edit Resource Modal.")

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Successfully updated faculty-resources.html")
