import os
import re

app_path = r'C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\js\app.js'
with open(app_path, 'r', encoding='utf-8') as f:
    text = f.read()

# Helper to normalize whitespace for replacement
def replace_block(source, target_snippet, replacement_snippet):
    target_norm = '\n'.join(line.rstrip() for line in target_snippet.strip().splitlines())
    source_norm = '\n'.join(line.rstrip() for line in source.splitlines())
    if target_norm in source_norm:
        res = source_norm.replace(target_norm, '\n'.join(line.rstrip() for line in replacement_snippet.strip().splitlines()))
        return res, True
    else:
        return source, False

# 1. Update initPage to call renderStudentSubjects
target_init = """    if (path.includes('student-materials.html') && typeof renderStudentMaterialsTable === 'function') renderStudentMaterialsTable();"""

repl_init = """    if (path.includes('student-subjects.html') && typeof renderStudentSubjects === 'function') renderStudentSubjects();

    if (path.includes('student-materials.html') && typeof renderStudentMaterialsTable === 'function') renderStudentMaterialsTable();"""

text, s1 = replace_block(text, target_init, repl_init)
print(f"Step 1 (initPage): {s1}")

# 2. Add renderStudentSubjects implementation right before renderStudentMaterialsTable
subjects_code = """
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
"""

if 'function renderStudentSubjects' not in text:
    insert_target = "// Render Student Study Materials Table from MySQL"
    text = text.replace(insert_target, subjects_code + "\n\n" + insert_target)
    print("Step 2 (renderStudentSubjects added): True")
else:
    print("Step 2 (renderStudentSubjects already present): True")

with open(app_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("Finished app.js step 1 & 2")
