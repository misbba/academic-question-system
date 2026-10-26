import os

# 1. Update student-question-papers.html
sqp_path = r'C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\student-question-papers.html'
with open(sqp_path, 'r', encoding='utf-8') as f:
    sqp = f.read()

sqp = sqp.replace(
    '<div class="modal-dialog modal-lg modal-dialog-centered">',
    '<div class="modal-dialog modal-xl modal-dialog-centered modal-dialog-scrollable">'
)
sqp = sqp.replace(
    '<div class="modal-footer border-top d-flex justify-content-end">\n          <button type="button" class="btn btn-academic-secondary btn-sm" data-bs-dismiss="modal">Close Preview</button>\n        </div>',
    """<div class="modal-footer border-top d-flex justify-content-between">
          <button type="button" class="btn btn-academic-primary btn-sm" onclick="printStudentPaper()">
            <i class="bi bi-printer me-1"></i> Print / Download Paper
          </button>
          <button type="button" class="btn btn-academic-secondary btn-sm" data-bs-dismiss="modal">Close Preview</button>
        </div>"""
)
# Add subject filter in question papers header if not present
if 'studentPaperSubjectFilter' not in sqp:
    sqp = sqp.replace(
        '<div class="card-academic-header d-flex justify-content-between align-items-center">',
        """<div class="card-academic-header d-flex justify-content-between align-items-center flex-wrap gap-2">"""
    )
    sqp = sqp.replace(
        '<span class="badge bg-success">Verified & Published</span>',
        """<div class="d-flex align-items-center gap-2">
            <select id="studentPaperSubjectFilter" class="form-select form-select-sm" style="width: auto;" onchange="filterStudentPapers()">
              <option value="ALL">All Subjects</option>
            </select>
            <span class="badge bg-success">Verified & Published</span>
          </div>"""
    )

with open(sqp_path, 'w', encoding='utf-8') as f:
    f.write(sqp)
print("Updated student-question-papers.html")

# 2. Update student-materials.html
sm_path = r'C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\student-materials.html'
with open(sm_path, 'r', encoding='utf-8') as f:
    sm = f.read()

sm = sm.replace(
    '<select class="form-select form-select-sm" style="width: auto;">',
    '<select id="studentMaterialSubjectFilter" class="form-select form-select-sm" style="width: auto;" onchange="filterStudentMaterials()">'
)
with open(sm_path, 'w', encoding='utf-8') as f:
    f.write(sm)
print("Updated student-materials.html")

# 3. Update student-assignments.html
sa_path = r'C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\student-assignments.html'
with open(sa_path, 'r', encoding='utf-8') as f:
    sa = f.read()

if 'studentAssignmentSubjectFilter' not in sa:
    sa = sa.replace(
        '<span><i class="bi bi-journal-check me-2 text-primary"></i> Course Assignments & Submission Deadlines</span>',
        """<span><i class="bi bi-journal-check me-2 text-primary"></i> Course Assignments & Submission Deadlines</span>
          <div class="d-flex gap-2">
            <select id="studentAssignmentSubjectFilter" class="form-select form-select-sm" style="width: auto;" onchange="filterStudentAssignments()">
              <option value="ALL">All Subjects</option>
            </select>
          </div>"""
    )
with open(sa_path, 'w', encoding='utf-8') as f:
    f.write(sa)
print("Updated student-assignments.html")

# 4. Update student-quizzes.html
sq_path = r'C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\student-quizzes.html'
with open(sq_path, 'r', encoding='utf-8') as f:
    sq = f.read()

if 'studentQuizSubjectFilter' not in sq:
    sq = sq.replace(
        '<span><i class="bi bi-patch-question me-2 text-warning"></i> Available Academic Quizzes</span>',
        """<span><i class="bi bi-patch-question me-2 text-warning"></i> Available Academic Quizzes</span>
          <div class="d-flex gap-2">
            <select id="studentQuizSubjectFilter" class="form-select form-select-sm" style="width: auto;" onchange="filterStudentQuizzes()">
              <option value="ALL">All Subjects</option>
            </select>
          </div>"""
    )
with open(sq_path, 'w', encoding='utf-8') as f:
    f.write(sq)
print("Updated student-quizzes.html")
