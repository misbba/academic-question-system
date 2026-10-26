filepath = 'C:/Users/Nisha/.gemini/antigravity/scratch/academic-question-system/faculty-resources.html'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update Department field in upload form
old_dept = """              <!-- Department -->
              <div class="col-md-6">
                <label for="resourceDept" class="form-label fw-semibold">Department</label>
                <select class="form-select" id="resourceDept" required>
                  <option value="Artificial Intelligence & Data Science" selected>Artificial Intelligence & Data Science</option>
                  <option value="Artificial Intelligence & Machine Learning">Artificial Intelligence & Machine Learning</option>
                  <option value="Computer and Communication Engineering">Computer and Communication Engineering</option>
                </select>
              </div>"""

new_dept = """              <!-- Department -->
              <div class="col-md-6">
                <label for="resourceDept" class="form-label fw-semibold">Department</label>
                <input type="text" class="form-control" id="resourceDept" list="resourceDeptList" placeholder="Enter or select department..." required autocomplete="off">
                <datalist id="resourceDeptList">
                  <option value="Artificial Intelligence & Data Science">
                  <option value="Artificial Intelligence & Machine Learning">
                  <option value="Computer Science & Engineering">
                  <option value="Information Technology">
                  <option value="Computer and Communication Engineering">
                  <option value="Electronics & Communication Engineering">
                  <option value="Electrical & Electronics Engineering">
                  <option value="Mechanical Engineering">
                  <option value="Civil Engineering">
                </datalist>
                <div class="form-text text-muted small">Choose from suggestions or enter any department name.</div>
              </div>"""

content = content.replace(old_dept.replace('\r\n', '\n'), new_dept.replace('\r\n', '\n'))
content = content.replace(old_dept, new_dept)

# 2. Update Unit field in upload form to generic units
old_unit = """              <!-- Unit -->
              <div class="col-md-4">
                <label for="resourceUnit" class="form-label fw-semibold">Unit</label>
                <select class="form-select" id="resourceUnit" required>
                  <option value="All Units">All Units (Complete Syllabus)</option>
                  <option value="Unit I">Unit I - Fundamentals</option>
                  <option value="Unit II">Unit II - Normalization & Schema Design</option>
                  <option value="Unit III" selected>Unit III — SQL</option>
                  <option value="Unit IV">Unit IV - Transactions & Concurrency</option>
                  <option value="Unit V">Unit V - Storage & Indexing</option>
                </select>
              </div>"""

new_unit = """              <!-- Unit -->
              <div class="col-md-4">
                <label for="resourceUnit" class="form-label fw-semibold">Unit</label>
                <select class="form-select" id="resourceUnit" required>
                  <option value="All Units (Complete Syllabus)" selected>All Units (Complete Syllabus)</option>
                  <option value="Unit I">Unit I</option>
                  <option value="Unit II">Unit II</option>
                  <option value="Unit III">Unit III</option>
                  <option value="Unit IV">Unit IV</option>
                  <option value="Unit V">Unit V</option>
                </select>
              </div>"""

content = content.replace(old_unit.replace('\r\n', '\n'), new_unit.replace('\r\n', '\n'))
content = content.replace(old_unit, new_unit)

# 3. Update Topic placeholder
old_topic = 'placeholder="e.g. SQL Queries & Aggregations"'
new_topic = 'placeholder="e.g. Chapter 1: Introduction or Topic Name"'
content = content.replace(old_topic, new_topic)

# 4. Update Edit Modal Department & Unit
old_edit_dept = """              <div class="col-md-6">
                <label for="editResourceDept" class="form-label fw-semibold">Department</label>
                <select class="form-select" id="editResourceDept" required>
                  <option value="Artificial Intelligence & Data Science">Artificial Intelligence & Data Science</option>
                  <option value="Artificial Intelligence & Machine Learning">Artificial Intelligence & Machine Learning</option>
                  <option value="Computer and Communication Engineering">Computer and Communication Engineering</option>
                </select>
              </div>"""

new_edit_dept = """              <div class="col-md-6">
                <label for="editResourceDept" class="form-label fw-semibold">Department</label>
                <input type="text" class="form-control" id="editResourceDept" list="resourceDeptList" placeholder="Enter or select department..." required autocomplete="off">
                <div class="form-text text-muted small">Choose from suggestions or enter any department name.</div>
              </div>"""

content = content.replace(old_edit_dept.replace('\r\n', '\n'), new_edit_dept.replace('\r\n', '\n'))
content = content.replace(old_edit_dept, new_edit_dept)

old_edit_unit = """              <div class="col-md-4">
                <label for="editResourceUnit" class="form-label fw-semibold">Unit</label>
                <select class="form-select" id="editResourceUnit" required>
                  <option value="All Units">All Units (Complete Syllabus)</option>
                  <option value="Unit I">Unit I - Fundamentals</option>
                  <option value="Unit II">Unit II - Normalization & Schema Design</option>
                  <option value="Unit III">Unit III — SQL</option>
                  <option value="Unit IV">Unit IV - Transactions & Concurrency</option>
                  <option value="Unit V">Unit V - Storage & Indexing</option>
                </select>
              </div>"""

new_edit_unit = """              <div class="col-md-4">
                <label for="editResourceUnit" class="form-label fw-semibold">Unit</label>
                <select class="form-select" id="editResourceUnit" required>
                  <option value="All Units (Complete Syllabus)">All Units (Complete Syllabus)</option>
                  <option value="Unit I">Unit I</option>
                  <option value="Unit II">Unit II</option>
                  <option value="Unit III">Unit III</option>
                  <option value="Unit IV">Unit IV</option>
                  <option value="Unit V">Unit V</option>
                </select>
              </div>"""

content = content.replace(old_edit_unit.replace('\r\n', '\n'), new_edit_unit.replace('\r\n', '\n'))
content = content.replace(old_edit_unit, new_edit_unit)

# 5. Make concept hierarchy in analysis modal dynamic
old_hierarchy = """          <div class="concept-hierarchy">
            <div class="hierarchy-node hierarchy-level-subject">
              <i class="bi bi-journal-album me-2"></i> Subject: Database Management Systems (CS402)
            </div>
            <div class="hierarchy-arrow"><i class="bi bi-arrow-down"></i></div>
            
            <div class="hierarchy-node hierarchy-level-unit">
              <i class="bi bi-collection me-2"></i> Unit III: SQL & Relational Queries
            </div>
            <div class="hierarchy-arrow"><i class="bi bi-arrow-down"></i></div>
            
            <div class="hierarchy-node hierarchy-level-topic">
              <i class="bi bi-bookmark-star me-2"></i> Topic: SQL Joins & Subqueries
            </div>
            <div class="hierarchy-arrow"><i class="bi bi-arrow-down"></i></div>
            
            <div class="hierarchy-node hierarchy-level-subtopic">
              <i class="bi bi-hash me-2"></i> Subtopic: INNER JOIN, LEFT JOIN, Aggregations (GROUP BY)
            </div>
            <div class="hierarchy-arrow"><i class="bi bi-arrow-down"></i></div>
            
            <div class="hierarchy-node hierarchy-level-concept">
              <i class="bi bi-lightbulb-fill me-2 text-warning"></i> Key Concepts: DDL, DML, TCL, Aggregate Functions, Complex Joins
            </div>
          </div>"""

new_hierarchy = """          <div class="concept-hierarchy" id="conceptHierarchyContainer">
            <!-- Dynamically populated by app.js based on analyzed resource -->
          </div>"""

content = content.replace(old_hierarchy.replace('\r\n', '\n'), new_hierarchy.replace('\r\n', '\n'))
content = content.replace(old_hierarchy, new_hierarchy)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Successfully updated faculty-resources.html for full configurability!")
