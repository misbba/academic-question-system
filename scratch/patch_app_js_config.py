filepath = 'C:/Users/Nisha/.gemini/antigravity/scratch/academic-question-system/js/app.js'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update datalist population in renderFacultyResourcesTable to also populate resourceDeptList
old_datalist_block = """    // Augment subject datalist suggestions with existing subjects from user's repository
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
    }"""

new_datalist_block = """    // Augment subject and department datalist suggestions with existing user data
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
    }"""

content = content.replace(old_datalist_block.replace('\r\n', '\n'), new_datalist_block.replace('\r\n', '\n'))
content = content.replace(old_datalist_block, new_datalist_block)

# 2. Add dynamic hierarchy rendering in analyzeFacultyResource
old_analysis_modal = """    const modalEl = document.getElementById('academicAnalysisModal');

    if (modalEl) {

      const bsModal = new bootstrap.Modal(modalEl);"""

new_analysis_modal = """    const hierarchyEl = document.getElementById('conceptHierarchyContainer');
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

      const bsModal = new bootstrap.Modal(modalEl);"""

content = content.replace(old_analysis_modal.replace('\r\n', '\n'), new_analysis_modal.replace('\r\n', '\n'))
content = content.replace(old_analysis_modal, new_analysis_modal)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Successfully updated js/app.js for dynamic department and analysis hierarchy!")
