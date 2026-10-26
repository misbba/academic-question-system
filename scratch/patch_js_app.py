import sys

path = r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\js\app.js"

with open(path, "r", encoding="utf-8") as f:
    content = f.read().replace("\r\n", "\n")

# 1. Update toast notice in generateAcademicTemplateAction
toast_start = content.find("const noticeMsg = templateType === 'semester_exam'")
assert toast_start != -1, "toast_start not found"
toast_end = content.find("showToastNotice('Template Generated Successfully', noticeMsg, 'success');", toast_start)
assert toast_end != -1, "toast_end not found"

new_toast = """const noticeMsg = templateType === 'semester_exam'
        ? 'Semester Examination generated: 100 attempted marks (Part A: 20M, Part B: 80M with flexible Direct 16M and Split 8+8 subquestions, strictly Part A & B only)!'
        : 'Internal Examination generated: 50 attempted marks (Part A: 10M, Part B: 8M, Part C: 32M) matching inter.pdf!';
      """

content = content[:toast_start] + new_toast + content[toast_end:]

# 2. Update renderPaperSectionStructure and append renderPartBGroupManager and changeGroupAlternativeFormat
render_start = content.find("function renderPaperSectionStructure(sections) {")
assert render_start != -1, "render_start not found"
render_end = content.find("function calculatePaperMarksValidation() {", render_start)
assert render_end != -1, "render_end not found"

new_render_code = """function renderPaperSectionStructure(sections) {
  const container = document.getElementById('paperSectionsStructureContainer');
  const overallMarksDisp = document.getElementById('overallMarksDisplay');
  const validationMsg = document.getElementById('marksValidationMsg');
  const maxMarksInput = document.getElementById('paperMaxMarks');
  const targetMaxMarks = parseInt(maxMarksInput?.value || '100', 10);

  if (!container) return;

  if (!sections || !Array.isArray(sections) || sections.length === 0) {
    container.innerHTML = `
      <div class="row g-3">
        <div class="col-md-6"><div class="p-3 border rounded bg-white"><h6 class="fw-bold text-success mb-1">PART - A</h6><div class="small text-muted">10 Compulsory Questions × 2 Marks = 20 Attempted Marks</div></div></div>
        <div class="col-md-6"><div class="p-3 border rounded bg-white"><h6 class="fw-bold text-success mb-1">PART - B</h6><div class="small text-muted">5 Either/Or Groups × 16 Marks (Direct 16M or Split 8+8) = 80 Attempted Marks</div></div></div>
      </div>
    `;
    if (overallMarksDisp) {
      overallMarksDisp.textContent = `Attempted Marks: 100 / ${targetMaxMarks}`;
      overallMarksDisp.className = 100 === targetMaxMarks ? 'fw-bold text-success fs-6' : 'fw-bold text-warning fs-6';
    }
    renderPartBGroupManager(null);
    return;
  }

  let totalAttempted = 0;
  const colSize = sections.length <= 2 ? 'col-md-6' : 'col-md-4';
  let html = '<div class="row g-3">';

  sections.forEach((sec) => {
    let secAttempted = sec.attempted_marks || sec.total_marks || 0;
    let details = '';

    const groups = sec.groups || sec.either_or_groups;
    if (groups && groups.length > 0) {
      const groupCount = groups.length;
      const marksPerGroup = sec.marks_per_q || (secAttempted / groupCount);
      details = `${groupCount} Either/Or Group${groupCount > 1 ? 's' : ''} × ${marksPerGroup} Marks (Students answer only 1 alternative per group)`;
    } else {
      const qCount = (sec.questions && sec.questions.length) || sec.count || 0;
      const marksPerQ = sec.marks_per_q || 2;
      details = `${qCount} Compulsory Questions × ${marksPerQ} Marks`;
    }

    totalAttempted += secAttempted;

    html += `
      <div class="${colSize}">
        <div class="p-3 border rounded bg-white h-100 shadow-sm">
          <div class="d-flex justify-content-between align-items-center mb-1">
            <h6 class="fw-bold text-primary mb-0">${sec.name}</h6>
            <span class="badge bg-primary-subtle text-primary border">${secAttempted} Marks</span>
          </div>
          <p class="small text-muted mb-2">${details}</p>
          <div class="small text-success fw-semibold"><i class="bi bi-check2-circle me-1"></i>Attempted: ${secAttempted} Marks</div>
        </div>
      </div>
    `;
  });

  html += '</div>';
  container.innerHTML = html;

  if (overallMarksDisp) {
    overallMarksDisp.textContent = `Attempted Marks: ${totalAttempted} / ${targetMaxMarks}`;
    overallMarksDisp.className = totalAttempted === targetMaxMarks ? 'fw-bold text-success fs-6' : 'fw-bold text-danger fs-6';
  }

  if (validationMsg) {
    if (totalAttempted === targetMaxMarks) {
      validationMsg.innerHTML = `<span class="alert alert-success d-inline-block py-2 px-3 mb-0 small"><i class="bi bi-check-circle-fill me-1"></i> <strong>Official Semester Exam Structure Validated:</strong> Part A (20 Marks) + Part B (80 Marks: 5 Either/Or groups × 16 Marks) = Exactly ${totalAttempted} Attempted Marks. Strictly Part A & B only.</span>`;
    } else {
      validationMsg.innerHTML = `<span class="alert alert-warning d-inline-block py-2 px-3 mb-0 small"><i class="bi bi-exclamation-triangle-fill me-1"></i> Total attempted marks (${totalAttempted}) differ from Maximum Marks (${targetMaxMarks}). Please adjust configuration.</span>`;
    }
  }

  renderPartBGroupManager(sections);
  return totalAttempted === targetMaxMarks;
}

function renderPartBGroupManager(sections) {
  const container = document.getElementById('partBGroupManagerContainer');
  if (!container) return;

  if (!sections || !Array.isArray(sections)) {
    container.style.display = 'none';
    return;
  }

  const secB = sections.find(s => (s.name || s.title || '').toUpperCase().includes('PART - B') || (s.name || s.title || '').toUpperCase().includes('PART B'));
  const groups = secB ? (secB.groups || secB.either_or_groups || []) : [];

  if (!secB || groups.length !== 5) {
    container.style.display = 'none';
    return;
  }

  container.style.display = 'block';

  let html = `
    <div class="card border border-primary-subtle shadow-sm mb-4">
      <div class="card-header bg-primary-subtle text-primary-emphasis d-flex justify-content-between align-items-center flex-wrap gap-2">
        <div>
          <i class="bi bi-sliders2-vertical me-2"></i>
          <strong>Part B: Flexible 16-Mark Question Format Configuration</strong>
        </div>
        <span class="badge bg-primary">5 Either/Or Groups × 16 Marks = 80 Attempted Marks</span>
      </div>
      <div class="card-body p-3">
        <div class="alert alert-light border py-2 px-3 small mb-3">
          <i class="bi bi-info-circle me-1 text-primary"></i>
          Each Part B question allows choosing between <strong>Direct 16 Marks</strong> (one complete question) or <strong>Split 8 + 8</strong> (two subquestions displayed under the same main question number). Select the desired format for Alternative (a) and Alternative (b) independently.
        </div>
        <div class="row g-3">
  `;

  groups.forEach((grp, gIdx) => {
    const qNum = grp.question_number || (11 + gIdx);
    const unit = grp.unit || `Unit ${['I','II','III','IV','V'][gIdx] || (gIdx+1)}`;

    const altA = grp.alternative_a || grp.option_a || {};
    const isSplitA = Boolean(altA.format === 'split' || altA.is_subquestion || (altA.subquestions && altA.subquestions.length > 0));

    const altB = grp.alternative_b || grp.option_b || {};
    const isSplitB = Boolean(altB.format === 'split' || altB.is_subquestion || (altB.subquestions && altB.subquestions.length > 0));

    const renderAltPreview = (alt, isSplit, letter) => {
      if (isSplit && alt.subquestions && alt.subquestions.length >= 2) {
        const sq1 = alt.subquestions[0];
        const sq2 = alt.subquestions[1];
        return `
          <div class="p-2 border rounded bg-white mt-2 small">
            <div class="d-flex justify-content-between align-items-center text-muted mb-1">
              <span class="badge bg-secondary-subtle text-secondary border">Split Format: (8 + 8 = 16M)</span>
              <span class="badge bg-success-subtle text-success border">16 Marks Total</span>
            </div>
            <div class="mb-1"><span class="fw-bold text-dark">(i)</span> ${sq1.text || sq1.question_text || sq1.question || 'Subquestion 1'} <span class="badge bg-light text-dark border ms-1">8M</span></div>
            <div><span class="fw-bold text-dark">(ii)</span> ${sq2.text || sq2.question_text || sq2.question || 'Subquestion 2'} <span class="badge bg-light text-dark border ms-1">8M</span></div>
          </div>
        `;
      } else {
        const text = alt.question_text || alt.text || alt.question || 'Direct 16-Mark Question';
        const bTag = alt.bloom_tag || (alt.bloom_level ? `[${alt.bloom_level.substring(0,2).toUpperCase()}]` : '');
        return `
          <div class="p-2 border rounded bg-white mt-2 small">
            <div class="d-flex justify-content-between align-items-center text-muted mb-1">
              <span class="badge bg-primary-subtle text-primary border">Direct Format: (16M)</span>
              <span class="badge bg-success-subtle text-success border">16 Marks</span>
            </div>
            <div class="text-dark">${text} <span class="badge bg-light text-dark border ms-1">${bTag} 16M</span></div>
          </div>
        `;
      }
    };

    html += `
      <div class="col-12">
        <div class="card border rounded shadow-sm">
          <div class="card-header bg-light py-2 px-3 d-flex justify-content-between align-items-center flex-wrap gap-2">
            <span class="fw-bold text-dark">
              <span class="badge bg-primary me-2">Q${qNum}</span>
              <span>${unit} — Either / Or Choice (16 Attempted Marks)</span>
            </span>
            <span class="small text-muted font-monospace">1 Alternative Attempted</span>
          </div>
          <div class="card-body p-3">
            <div class="row g-3">
              <!-- Alternative A -->
              <div class="col-md-6 border-end">
                <div class="d-flex justify-content-between align-items-center flex-wrap gap-1 mb-1">
                  <span class="fw-bold text-primary">Alternative (a)</span>
                  <div class="btn-group btn-group-sm" role="group">
                    <input type="radio" class="btn-check" name="grp_${gIdx}_a_fmt" id="grp_${gIdx}_a_direct" autocomplete="off" ${!isSplitA ? 'checked' : ''} onchange="changeGroupAlternativeFormat(${gIdx}, 'a', 'direct')">
                    <label class="btn btn-outline-primary" for="grp_${gIdx}_a_direct">Direct 16M</label>

                    <input type="radio" class="btn-check" name="grp_${gIdx}_a_fmt" id="grp_${gIdx}_a_split" autocomplete="off" ${isSplitA ? 'checked' : ''} onchange="changeGroupAlternativeFormat(${gIdx}, 'a', 'split')">
                    <label class="btn btn-outline-primary" for="grp_${gIdx}_a_split">Split 8 + 8</label>
                  </div>
                </div>
                ${renderAltPreview(altA, isSplitA, 'a')}
              </div>

              <!-- Alternative B -->
              <div class="col-md-6">
                <div class="d-flex justify-content-between align-items-center flex-wrap gap-1 mb-1">
                  <span class="fw-bold text-primary">Alternative (b)</span>
                  <div class="btn-group btn-group-sm" role="group">
                    <input type="radio" class="btn-check" name="grp_${gIdx}_b_fmt" id="grp_${gIdx}_b_direct" autocomplete="off" ${!isSplitB ? 'checked' : ''} onchange="changeGroupAlternativeFormat(${gIdx}, 'b', 'direct')">
                    <label class="btn btn-outline-primary" for="grp_${gIdx}_b_direct">Direct 16M</label>

                    <input type="radio" class="btn-check" name="grp_${gIdx}_b_fmt" id="grp_${gIdx}_b_split" autocomplete="off" ${isSplitB ? 'checked' : ''} onchange="changeGroupAlternativeFormat(${gIdx}, 'b', 'split')">
                    <label class="btn btn-outline-primary" for="grp_${gIdx}_b_split">Split 8 + 8</label>
                  </div>
                </div>
                ${renderAltPreview(altB, isSplitB, 'b')}
              </div>
            </div>
          </div>
        </div>
      </div>
    `;
  });

  html += `
        </div>
      </div>
    </div>
  `;

  container.innerHTML = html;
}

function changeGroupAlternativeFormat(groupIndex, altLetter, newFormat) {
  if (!window.currentGeneratedTemplate || !window.currentGeneratedTemplate.sections) return;

  const secB = window.currentGeneratedTemplate.sections.find(s =>
    (s.name || s.title || '').toUpperCase().includes('PART - B') ||
    (s.name || s.title || '').toUpperCase().includes('PART B')
  );
  if (!secB) return;

  const groups = secB.groups || secB.either_or_groups || [];
  const group = groups[groupIndex];
  if (!group) return;

  const unit = group.unit || `Unit ${['I','II','III','IV','V'][groupIndex] || 'I'}`;
  const pool = window.paperQuestionBankPool || [];

  const unitPool = pool.filter(q => (q.unit || q.source_unit || '') === unit);
  const activePool = unitPool.length >= 3 ? unitPool : pool;

  const usedIds = new Set();
  window.currentGeneratedTemplate.sections.forEach(s => {
    (s.questions || []).forEach(q => usedIds.add(q.id));
    (s.groups || s.either_or_groups || []).forEach((g, idx) => {
      ['alternative_a', 'alternative_b'].forEach(altKey => {
        if (idx === groupIndex && altKey === (altLetter === 'a' ? 'alternative_a' : 'alternative_b')) {
          return;
        }
        const alt = g[altKey];
        if (!alt) return;
        if (alt.subquestions && Array.isArray(alt.subquestions)) {
          alt.subquestions.forEach(sq => usedIds.add(sq.id));
        } else if (alt.id) {
          usedIds.add(alt.id);
        }
      });
    });
  });

  const altKey = altLetter === 'a' ? 'alternative_a' : 'alternative_b';

  if (newFormat === 'direct') {
    let cand16 = activePool.filter(q => q.marks === 16 && !usedIds.has(q.id));
    if (cand16.length === 0) cand16 = pool.filter(q => q.marks === 16 && !usedIds.has(q.id));
    if (cand16.length === 0) cand16 = pool.filter(q => q.marks === 16);

    if (cand16.length > 0) {
      const q16 = JSON.parse(JSON.stringify(cand16[0]));
      q16.format = 'direct';
      q16.is_subquestion = false;
      q16.marks = 16;
      group[altKey] = q16;
    } else {
      showToastNotice('Notice', 'No 16-mark question available in Question Bank to switch to direct format.', 'warning');
      return;
    }
  } else {
    let cand8 = activePool.filter(q => q.marks === 8 && !usedIds.has(q.id));
    if (cand8.length < 2) cand8 = pool.filter(q => q.marks === 8 && !usedIds.has(q.id));
    if (cand8.length < 2) cand8 = pool.filter(q => q.marks === 8);

    if (cand8.length >= 2) {
      const q8_1 = cand8[0];
      const q8_2 = cand8[1];
      group[altKey] = {
        format: 'split',
        is_subquestion: true,
        marks: 16,
        unit: unit,
        topic: q8_1.topic || `${unit} Topics`,
        subquestions: [
          {
            part: '(i)',
            id: q8_1.id,
            text: q8_1.question_text || q8_1.text || q8_1.question,
            question_text: q8_1.question_text || q8_1.text || q8_1.question,
            marks: 8,
            bloom_tag: q8_1.bloom_tag || (q8_1.bloom_level ? `[${q8_1.bloom_level.substring(0,2).toUpperCase()}]` : '[AP]'),
            topic: q8_1.topic
          },
          {
            part: '(ii)',
            id: q8_2.id,
            text: q8_2.question_text || q8_2.text || q8_2.question,
            question_text: q8_2.question_text || q8_2.text || q8_2.question,
            marks: 8,
            bloom_tag: q8_2.bloom_tag || (q8_2.bloom_level ? `[${q8_2.bloom_level.substring(0,2).toUpperCase()}]` : '[AN]'),
            topic: q8_2.topic
          }
        ]
      };
    } else {
      showToastNotice('Notice', 'Insufficient 8-mark questions in Question Bank to switch to split format.', 'warning');
      return;
    }
  }

  const qList = [];
  window.currentGeneratedTemplate.sections.forEach(sec => {
    (sec.questions || []).forEach(q => qList.push(q));
    (sec.groups || sec.either_or_groups || []).forEach(g => {
      ['alternative_a', 'alternative_b'].forEach(k => {
        const a = g[k];
        if (!a) return;
        if (a.subquestions && Array.isArray(a.subquestions)) {
          a.subquestions.forEach(sq => qList.push(sq));
        } else {
          qList.push(a);
        }
      });
    });
  });
  window.paperSelectedQuestions = qList;

  renderPaperSelectedQuestions();
  renderPaperSectionStructure(window.currentGeneratedTemplate.sections);
  generateAcademicPaperPreview();

  const qNum = group.question_number || (11 + groupIndex);
  showToastNotice(
    'Format Updated',
    `Question ${qNum} Alternative (${altLetter}) is now set to ${newFormat === 'direct' ? 'Direct 16 Marks' : 'Split 8 + 8 Subquestions'}.`,
    'success'
  );
}

"""

content = content[:render_start] + new_render_code + content[render_end:]

# 3. Update fallback sections in saveQuestionPaperToBackend
save_start = content.find("sections = [\n      { name: \"PART - A (10 x 2 = 20 Marks)\"")
if save_start == -1:
    save_start = content.find("sections = [")
    while save_start != -1:
        snippet = content[save_start:save_start+300]
        if "PART - A (10 x 2 = 20 Marks)" in snippet and "PART - B" in snippet:
            break
        save_start = content.find("sections = [", save_start + 1)

assert save_start != -1, "save_start not found"
save_end = content.find("];", save_start) + 2

new_save_secs = """sections = [
      { name: "PART - A (10 x 2 = 20 Marks)", count: 10, marks_per_q: 2, total_marks: 20 },
      { name: "PART - B (5 x 16 = 80 Marks)", count: 5, marks_per_q: 16, total_marks: 80 }
    ];"""

content = content[:save_start] + new_save_secs + content[save_end:]

content_crlf = content.replace("\n", "\r\n")
with open(path, "w", encoding="utf-8") as f:
    f.write(content_crlf)

print("js/app.js patched successfully.")
