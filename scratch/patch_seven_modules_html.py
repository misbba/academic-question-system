"""
Update the 7 module HTML files with editable text inputs and datalists:
1. faculty-voice-question.html
2. faculty-image-question.html
3. faculty-language-converter.html
4. faculty-question-paper.html
5. faculty-generate-assignment.html
6. faculty-generate-ppt.html
7. faculty-generate-lesson-plan.html
"""

import os
import re

BASE_DIR = r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system"

DEPT_DATALIST_OPTIONS = """
  <option value="Artificial Intelligence & Data Science">
  <option value="Artificial Intelligence & Machine Learning">
  <option value="Computer and Communication Engineering">
  <option value="Computer Science and Engineering">
  <option value="Information Technology">
  <option value="Electronics & Communication Engineering">
"""

SUBJECT_DATALIST_OPTIONS = """
  <option value="Database Management Systems">
  <option value="Artificial Intelligence">
  <option value="Machine Learning">
  <option value="Distributed Computing">
  <option value="Data Structures">
  <option value="Computer Networks">
  <option value="Operating Systems">
  <option value="Python Programming">
  <option value="Cloud Computing">
"""

UNIT_DATALIST_OPTIONS = """
  <option value="All Units (Complete Syllabus)">
  <option value="Unit 1">
  <option value="Unit 2">
  <option value="Unit 3">
  <option value="Unit 4">
  <option value="Unit 5">
  <option value="Unit I — Introduction">
  <option value="Unit II — Core Concepts">
  <option value="Unit III — Advanced Topics">
  <option value="Unit IV — Applications">
  <option value="Unit V — System Design">
"""

TOPIC_DATALIST_OPTIONS = """
  <option value="Core Architectural Principles">
  <option value="Functional Mechanisms and Operations">
  <option value="Query Optimization & Indexing">
  <option value="Transaction Management & Concurrency">
  <option value="Practical Implementation & Case Studies">
"""

def update_file(filename, replacements):
    filepath = os.path.join(BASE_DIR, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Normalize CRLF to LF for reliable regex matching
    content_norm = content.replace("\r\n", "\n")
    orig_norm = content_norm

    for pattern, replacement in replacements:
        if isinstance(pattern, re.Pattern):
            content_norm, count = pattern.subn(replacement, content_norm)
            if count == 0:
                print(f"WARN: Pattern not found in {filename}: {pattern.pattern[:60]}...")
            else:
                print(f"MATCH: Applied {count} substitution(s) in {filename}")
        else:
            if pattern in content_norm:
                content_norm = content_norm.replace(pattern, replacement)
                print(f"MATCH: Literal replaced in {filename}")
            else:
                print(f"WARN: Literal not found in {filename}: {pattern[:60]}...")

    with open(filepath, "w", encoding="utf-8", newline="\r\n") as f:
        f.write(content_norm.replace("\n", "\r\n"))
    print(f"Done updating {filename}\n")


# 1. Voice
voice_reps = [
    (
        re.compile(r'<div class="mb-3">\s*<label class="form-label small fw-bold">Department</label>\s*<select class="form-select form-select-sm" id="voiceDeptSelect">[\s\S]*?</select>\s*</div>', re.MULTILINE),
        f'''<div class="mb-3">
                <label class="form-label small fw-bold">Department</label>
                <input type="text" class="form-control form-control-sm" id="voiceDeptSelect" list="voiceDeptList" placeholder="Type or select department" value="Artificial Intelligence & Data Science" required>
                <datalist id="voiceDeptList">
                {DEPT_DATALIST_OPTIONS}
                </datalist>
              </div>'''
    ),
    (
        re.compile(r'<div class="col-6">\s*<label class="form-label small fw-bold">Subject</label>\s*<select class="form-select form-select-sm" id="voiceSubjectSelect">[\s\S]*?</select>\s*</div>', re.MULTILINE),
        f'''<div class="col-6">
                  <label class="form-label small fw-bold">Subject</label>
                  <input type="text" class="form-control form-control-sm" id="voiceSubjectSelect" list="voiceSubjectList" placeholder="Type or select subject" value="Database Management Systems" required>
                  <datalist id="voiceSubjectList">
                  {SUBJECT_DATALIST_OPTIONS}
                  </datalist>
                </div>'''
    ),
    (
        re.compile(r'<div class="col-6">\s*<label class="form-label small fw-bold">Unit</label>\s*<select class="form-select form-select-sm" id="voiceUnitSelect">[\s\S]*?</select>\s*</div>', re.MULTILINE),
        f'''<div class="col-6">
                  <label class="form-label small fw-bold">Unit</label>
                  <input type="text" class="form-control form-control-sm" id="voiceUnitSelect" list="voiceUnitList" placeholder="e.g. Unit 1 or All Units" value="All Units (Complete Syllabus)">
                  <datalist id="voiceUnitList">
                  {UNIT_DATALIST_OPTIONS}
                  </datalist>
                </div>'''
    ),
    (
        re.compile(r'<div class="col-6">\s*<label class="form-label small fw-bold">Topic</label>\s*<select class="form-select form-select-sm" id="voiceTopicSelect">[\s\S]*?</select>\s*</div>', re.MULTILINE),
        f'''<div class="col-6">
                  <label class="form-label small fw-bold">Topic</label>
                  <input type="text" class="form-control form-control-sm" id="voiceTopicSelect" list="voiceTopicList" placeholder="Optional topic (leave blank for syllabus)" value="">
                  <datalist id="voiceTopicList">
                  {TOPIC_DATALIST_OPTIONS}
                  </datalist>
                </div>'''
    )
]
update_file("faculty-voice-question.html", voice_reps)

# 2. Image
image_reps = [
    (
        re.compile(r'<div class="mb-3">\s*<label class="form-label small fw-bold">Department</label>\s*<select class="form-select form-select-sm" id="imgDeptSelect">[\s\S]*?</select>\s*</div>', re.MULTILINE),
        f'''<div class="mb-3">
                <label class="form-label small fw-bold">Department</label>
                <input type="text" class="form-control form-control-sm" id="imgDeptSelect" list="imgDeptList" placeholder="Type or select department" value="Artificial Intelligence & Data Science" required>
                <datalist id="imgDeptList">
                {DEPT_DATALIST_OPTIONS}
                </datalist>
              </div>'''
    ),
    (
        re.compile(r'<div class="col-6">\s*<label class="form-label small fw-bold">Subject</label>\s*<select class="form-select form-select-sm" id="imgSubjectSelect">[\s\S]*?</select>\s*</div>', re.MULTILINE),
        f'''<div class="col-6">
                  <label class="form-label small fw-bold">Subject</label>
                  <input type="text" class="form-control form-control-sm" id="imgSubjectSelect" list="imgSubjectList" placeholder="Type or select subject" value="Database Management Systems" required>
                  <datalist id="imgSubjectList">
                  {SUBJECT_DATALIST_OPTIONS}
                  </datalist>
                </div>'''
    ),
    (
        re.compile(r'<div class="col-6">\s*<label class="form-label small fw-bold">Unit</label>\s*<select class="form-select form-select-sm" id="imgUnitSelect">[\s\S]*?</select>\s*</div>', re.MULTILINE),
        f'''<div class="col-6">
                  <label class="form-label small fw-bold">Unit</label>
                  <input type="text" class="form-control form-control-sm" id="imgUnitSelect" list="imgUnitList" placeholder="e.g. Unit 1 or All Units" value="All Units (Complete Syllabus)">
                  <datalist id="imgUnitList">
                  {UNIT_DATALIST_OPTIONS}
                  </datalist>
                </div>'''
    ),
    (
        re.compile(r'<div class="mb-3">\s*<label class="form-label small fw-bold">Topic</label>\s*<select class="form-select form-select-sm" id="imgTopicSelect">[\s\S]*?</select>\s*</div>', re.MULTILINE),
        f'''<div class="mb-3">
                <label class="form-label small fw-bold">Topic</label>
                <input type="text" class="form-control form-control-sm" id="imgTopicSelect" list="imgTopicList" placeholder="Optional topic (leave blank for syllabus)" value="">
                <datalist id="imgTopicList">
                {TOPIC_DATALIST_OPTIONS}
                </datalist>
              </div>'''
    )
]
update_file("faculty-image-question.html", image_reps)

# 3. Language Converter
trans_reps = [
    (
        re.compile(r'<div class="col-6">\s*<label class="form-label small fw-bold">Department</label>\s*<select class="form-select form-select-sm" id="transDeptSelect">[\s\S]*?</select>\s*</div>', re.MULTILINE),
        f'''<div class="col-6">
                  <label class="form-label small fw-bold">Department</label>
                  <input type="text" class="form-control form-control-sm" id="transDeptSelect" list="transDeptList" placeholder="Type or select department" value="Artificial Intelligence & Data Science" required>
                  <datalist id="transDeptList">
                  {DEPT_DATALIST_OPTIONS}
                  </datalist>
                </div>'''
    ),
    (
        re.compile(r'<div class="col-6">\s*<label class="form-label small fw-bold">Subject</label>\s*<select class="form-select form-select-sm" id="transSubjectSelect">[\s\S]*?</select>\s*</div>', re.MULTILINE),
        f'''<div class="col-6">
                  <label class="form-label small fw-bold">Subject</label>
                  <input type="text" class="form-control form-control-sm" id="transSubjectSelect" list="transSubjectList" placeholder="Type or select subject" value="Database Management Systems" required>
                  <datalist id="transSubjectList">
                  {SUBJECT_DATALIST_OPTIONS}
                  </datalist>
                </div>'''
    ),
    (
        re.compile(r'<div class="col-6">\s*<label class="form-label small fw-bold">Unit</label>\s*<select class="form-select form-select-sm" id="transUnitSelect">[\s\S]*?</select>\s*</div>', re.MULTILINE),
        f'''<div class="col-6">
                  <label class="form-label small fw-bold">Unit</label>
                  <input type="text" class="form-control form-control-sm" id="transUnitSelect" list="transUnitList" placeholder="e.g. Unit 1 or All Units" value="All Units (Complete Syllabus)">
                  <datalist id="transUnitList">
                  {UNIT_DATALIST_OPTIONS}
                  </datalist>
                </div>'''
    ),
    (
        re.compile(r'<div class="col-6">\s*<label class="form-label small fw-bold">Topic</label>\s*<select class="form-select form-select-sm" id="transTopicSelect">[\s\S]*?</select>\s*</div>', re.MULTILINE),
        f'''<div class="col-6">
                  <label class="form-label small fw-bold">Topic</label>
                  <input type="text" class="form-control form-control-sm" id="transTopicSelect" list="transTopicList" placeholder="Optional topic (leave blank for syllabus)" value="">
                  <datalist id="transTopicList">
                  {TOPIC_DATALIST_OPTIONS}
                  </datalist>
                </div>'''
    )
]
update_file("faculty-language-converter.html", trans_reps)

# 4. Question Paper Builder
paper_reps = [
    (
        re.compile(r'<div class="col-md-6">\s*<label for="paperDept" class="form-label fw-semibold">Department</label>\s*<select class="form-select" id="paperDept" required onchange="onPaperSpecificationChanged\(\)">[\s\S]*?</select>\s*</div>', re.MULTILINE),
        f'''<div class="col-md-6">
              <label for="paperDept" class="form-label fw-semibold">Department</label>
              <input type="text" class="form-control" id="paperDept" list="paperDeptList" placeholder="Type or select department" value="Artificial Intelligence & Data Science" required onchange="onPaperSpecificationChanged()" oninput="onPaperSpecificationChanged()">
              <datalist id="paperDeptList">
              {DEPT_DATALIST_OPTIONS}
              </datalist>
            </div>'''
    ),
    (
        re.compile(r'<div class="col-md-6">\s*<label for="paperSubject" class="form-label fw-semibold">Subject</label>\s*<select class="form-select" id="paperSubject" required onchange="onPaperSpecificationChanged\(\)">[\s\S]*?</select>\s*</div>', re.MULTILINE),
        f'''<div class="col-md-6">
              <label for="paperSubject" class="form-label fw-semibold">Subject</label>
              <input type="text" class="form-control" id="paperSubject" list="paperSubjectList" placeholder="Type or select subject" value="Database Management Systems" required onchange="onPaperSpecificationChanged()" oninput="onPaperSpecificationChanged()">
              <datalist id="paperSubjectList">
              {SUBJECT_DATALIST_OPTIONS}
              </datalist>
            </div>'''
    ),
    (
        re.compile(r'<div class="col-md-6">\s*<label class="form-label fw-semibold">Department</label>\s*<select class="form-select" id="addQDept" required>[\s\S]*?</select>\s*</div>', re.MULTILINE),
        f'''<div class="col-md-6">
                <label class="form-label fw-semibold">Department</label>
                <input type="text" class="form-control" id="addQDept" list="paperDeptList" placeholder="Department" value="Artificial Intelligence & Data Science" required>
              </div>'''
    ),
    (
        re.compile(r'<div class="col-md-6">\s*<label class="form-label fw-semibold">Subject</label>\s*<select class="form-select" id="addQSubject" required>[\s\S]*?</select>\s*</div>', re.MULTILINE),
        f'''<div class="col-md-6">
                <label class="form-label fw-semibold">Subject</label>
                <input type="text" class="form-control" id="addQSubject" list="paperSubjectList" placeholder="Subject" value="Database Management Systems" required>
              </div>'''
    )
]
update_file("faculty-question-paper.html", paper_reps)

# 5. Assignment
asn_reps = [
    (
        re.compile(r'<div class="col-md-6">\s*<label for="asnDept" class="form-label fw-semibold">Department</label>\s*<select class="form-select" id="asnDept" required>[\s\S]*?</select>\s*</div>', re.MULTILINE),
        f'''<div class="col-md-6">
                <label for="asnDept" class="form-label fw-semibold">Department</label>
                <input type="text" class="form-control" id="asnDept" list="asnDeptList" placeholder="Type or select department" value="Artificial Intelligence & Data Science" required>
                <datalist id="asnDeptList">
                {DEPT_DATALIST_OPTIONS}
                </datalist>
              </div>'''
    ),
    (
        re.compile(r'<div class="col-md-6">\s*<label for="asnSubject" class="form-label fw-semibold">Subject</label>\s*<select class="form-select" id="asnSubject" required>[\s\S]*?</select>\s*</div>', re.MULTILINE),
        f'''<div class="col-md-6">
                <label for="asnSubject" class="form-label fw-semibold">Subject</label>
                <input type="text" class="form-control" id="asnSubject" list="asnSubjectList" placeholder="Type or select subject" value="Database Management Systems" required>
                <datalist id="asnSubjectList">
                {SUBJECT_DATALIST_OPTIONS}
                </datalist>
              </div>'''
    ),
    (
        re.compile(r'<div class="col-md-3">\s*<label for="asnUnit" class="form-label fw-semibold">Unit</label>\s*<select class="form-select" id="asnUnit" required>[\s\S]*?</select>\s*</div>', re.MULTILINE),
        f'''<div class="col-md-3">
                <label for="asnUnit" class="form-label fw-semibold">Unit</label>
                <input type="text" class="form-control" id="asnUnit" list="asnUnitList" placeholder="e.g. Unit 1 or All Units" value="All Units (Complete Syllabus)" required>
                <datalist id="asnUnitList">
                {UNIT_DATALIST_OPTIONS}
                </datalist>
              </div>'''
    ),
    (
        re.compile(r'<div class="col-md-3">\s*<label for="asnTopic" class="form-label fw-semibold">Topic</label>\s*<select class="form-select" id="asnTopic" required>[\s\S]*?</select>\s*</div>', re.MULTILINE),
        f'''<div class="col-md-3">
                <label for="asnTopic" class="form-label fw-semibold">Topic</label>
                <input type="text" class="form-control" id="asnTopic" list="asnTopicList" placeholder="Optional topic (leave blank for syllabus)" value="">
                <datalist id="asnTopicList">
                {TOPIC_DATALIST_OPTIONS}
                </datalist>
              </div>'''
    ),
    (
        re.compile(r'<div class="col-md-3">\s*<label for="asnNumQuestions" class="form-label fw-semibold">Number of Questions</label>\s*<select class="form-select" id="asnNumQuestions">[\s\S]*?</select>\s*</div>', re.MULTILINE),
        '''<div class="col-md-3">
                <label for="asnNumQuestions" class="form-label fw-semibold">Number of Questions</label>
                <input type="number" class="form-control" id="asnNumQuestions" min="1" max="50" value="5" placeholder="Number of Questions" required>
              </div>'''
    )
]
update_file("faculty-generate-assignment.html", asn_reps)

# 6. PPT
ppt_reps = [
    (
        re.compile(r'<div class="mb-3">\s*<label class="form-label small fw-bold">Department</label>\s*<select class="form-select form-select-sm" id="pptDeptSelect">[\s\S]*?</select>\s*</div>', re.MULTILINE),
        f'''<div class="mb-3">
                <label class="form-label small fw-bold">Department</label>
                <input type="text" class="form-control form-control-sm" id="pptDeptSelect" list="pptDeptList" placeholder="Type or select department" value="Artificial Intelligence & Data Science" required>
                <datalist id="pptDeptList">
                {DEPT_DATALIST_OPTIONS}
                </datalist>
              </div>'''
    ),
    (
        re.compile(r'<div class="col-6">\s*<label class="form-label small fw-bold">Subject</label>\s*<select class="form-select form-select-sm" id="pptSubjectSelect">[\s\S]*?</select>\s*</div>', re.MULTILINE),
        f'''<div class="col-6">
                  <label class="form-label small fw-bold">Subject</label>
                  <input type="text" class="form-control form-control-sm" id="pptSubjectSelect" list="pptSubjectList" placeholder="Type or select subject" value="Database Management Systems" required>
                  <datalist id="pptSubjectList">
                  {SUBJECT_DATALIST_OPTIONS}
                  </datalist>
                </div>'''
    ),
    (
        re.compile(r'<div class="col-6">\s*<label class="form-label small fw-bold">Unit</label>\s*<select class="form-select form-select-sm" id="pptUnitSelect">[\s\S]*?</select>\s*</div>', re.MULTILINE),
        f'''<div class="col-6">
                  <label class="form-label small fw-bold">Unit</label>
                  <input type="text" class="form-control form-control-sm" id="pptUnitSelect" list="pptUnitList" placeholder="e.g. Unit 1 or All Units" value="All Units (Complete Syllabus)">
                  <datalist id="pptUnitList">
                  {UNIT_DATALIST_OPTIONS}
                  </datalist>
                </div>'''
    ),
    (
        re.compile(r'<div class="mb-3">\s*<label class="form-label small fw-bold">Topic</label>\s*<select class="form-select form-select-sm" id="pptTopicSelect">[\s\S]*?</select>\s*</div>', re.MULTILINE),
        f'''<div class="mb-3">
                <label class="form-label small fw-bold">Topic</label>
                <input type="text" class="form-control form-control-sm" id="pptTopicSelect" list="pptTopicList" placeholder="Optional topic (leave blank for syllabus)" value="">
                <datalist id="pptTopicList">
                {TOPIC_DATALIST_OPTIONS}
                </datalist>
              </div>'''
    )
]
update_file("faculty-generate-ppt.html", ppt_reps)

# 7. Lesson Plan
lp_reps = [
    (
        re.compile(r'<div class="mb-3">\s*<label class="form-label small fw-bold">Department</label>\s*<select class="form-select form-select-sm" id="lpDeptSelect">[\s\S]*?</select>\s*</div>', re.MULTILINE),
        f'''<div class="mb-3">
                <label class="form-label small fw-bold">Department</label>
                <input type="text" class="form-control form-control-sm" id="lpDeptSelect" list="lpDeptList" placeholder="Type or select department" value="Artificial Intelligence & Data Science" required>
                <datalist id="lpDeptList">
                {DEPT_DATALIST_OPTIONS}
                </datalist>
              </div>'''
    ),
    (
        re.compile(r'<div class="col-6">\s*<label class="form-label small fw-bold">Subject</label>\s*<select class="form-select form-select-sm" id="lpSubjectSelect">[\s\S]*?</select>\s*</div>', re.MULTILINE),
        f'''<div class="col-6">
                  <label class="form-label small fw-bold">Subject</label>
                  <input type="text" class="form-control form-control-sm" id="lpSubjectSelect" list="lpSubjectList" placeholder="Type or select subject" value="Database Management Systems" required>
                  <datalist id="lpSubjectList">
                  {SUBJECT_DATALIST_OPTIONS}
                  </datalist>
                </div>'''
    ),
    (
        re.compile(r'<div class="col-6">\s*<label class="form-label small fw-bold">Unit</label>\s*<select class="form-select form-select-sm" id="lpUnitSelect">[\s\S]*?</select>\s*</div>', re.MULTILINE),
        f'''<div class="col-6">
                  <label class="form-label small fw-bold">Unit</label>
                  <input type="text" class="form-control form-control-sm" id="lpUnitSelect" list="lpUnitList" placeholder="e.g. Unit 1 or All Units" value="All Units (Complete Syllabus)">
                  <datalist id="lpUnitList">
                  {UNIT_DATALIST_OPTIONS}
                  </datalist>
                </div>'''
    ),
    (
        re.compile(r'<div class="mb-3">\s*<label class="form-label small fw-bold">Topic</label>\s*<select class="form-select form-select-sm" id="lpTopicSelect">[\s\S]*?</select>\s*</div>', re.MULTILINE),
        f'''<div class="mb-3">
                <label class="form-label small fw-bold">Topic</label>
                <input type="text" class="form-control form-control-sm" id="lpTopicSelect" list="lpTopicList" placeholder="Optional topic (leave blank for syllabus)" value="">
                <datalist id="lpTopicList">
                {TOPIC_DATALIST_OPTIONS}
                </datalist>
              </div>'''
    )
]
update_file("faculty-generate-lesson-plan.html", lp_reps)

print("All 7 module HTML files have been processed!")
