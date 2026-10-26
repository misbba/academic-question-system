import os

app_js_path = r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\js\app.js"
with open(app_js_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

start_idx = None
end_idx = None

for i, l in enumerate(lines):
    if "let activeUploadedImageData = null;" in l and start_idx is None:
        start_idx = i
    if "function renderFacultyImageHistory() {" in l and end_idx is None:
        end_idx = i

print(f"start_idx: {start_idx}, end_idx: {end_idx}")

new_code = """let selectedImageFile = null;
window.selectedImageFile = null;
let activeUploadedImageData = null;
let activeImageQuestions = [];
let activeImageConfig = {};

function initImageQuestionForm() {
  const subj = document.getElementById('imgSubjectSelect');
  const unit = document.getElementById('imgUnitSelect');
  const sync = () => syncModuleDatalists('imgSubjectSelect', 'imgSubjectList', 'imgUnitSelect', 'imgUnitList', 'imgTopicSelect', 'imgTopicList');
  if (subj) {
    subj.addEventListener('input', sync);
    subj.addEventListener('change', sync);
  }
  if (unit) {
    unit.addEventListener('input', sync);
    unit.addEventListener('change', sync);
  }
  sync();

  const fileInput = document.getElementById('imageFileInput');
  if (fileInput) {
    fileInput.removeEventListener('change', handleImageFileUpload);
    fileInput.addEventListener('change', handleImageFileUpload);
  }
}

function populateImageTopics() {
  syncModuleDatalists('imgSubjectSelect', 'imgSubjectList', 'imgUnitSelect', 'imgUnitList', 'imgTopicSelect', 'imgTopicList');
}

function initImageQuestionPage() {
  initImageQuestionForm();
  populateImageTopics();
  renderFacultyImageHistory();
}

function handleImageFileUpload(event) {
  let file = null;
  if (event && event.target && event.target.files && event.target.files.length > 0) {
    file = event.target.files[0];
  } else if (event && event.files && event.files.length > 0) {
    file = event.files[0];
  } else {
    const fileInput = document.getElementById('imageFileInput');
    if (fileInput && fileInput.files && fileInput.files.length > 0) {
      file = fileInput.files[0];
    }
  }

  if (!file) return;

  const validExts = ['png', 'jpg', 'jpeg', 'webp'];
  const ext = file.name.split('.').pop().toLowerCase();
  if (!validExts.includes(ext)) {
    showToastNotice('Invalid File Type', 'Please upload a valid diagram image (PNG, JPG, JPEG, WEBP).', 'error');
    const fileInput = document.getElementById('imageFileInput');
    if (fileInput) fileInput.value = '';
    return;
  }

  if (file.size > 16 * 1024 * 1024) {
    showToastNotice('File Too Large', 'Maximum image size is 16MB.', 'warning');
    const fileInput = document.getElementById('imageFileInput');
    if (fileInput) fileInput.value = '';
    return;
  }

  // Preserve DOM File object
  selectedImageFile = file;
  window.selectedImageFile = file;

  const reader = new FileReader();
  reader.onload = (e) => {
    activeUploadedImageData = {
      file: file,
      dataUrl: e.target.result,
      name: file.name,
      type: file.type || `image/${ext}`,
      size: `${Math.round(file.size / 1024)} KB`
    };

    const previewContainer = document.getElementById('imagePreviewContainer');
    if (previewContainer) previewContainer.classList.remove('d-none');

    const previewImg = document.getElementById('uploadedImagePreview');
    if (previewImg) previewImg.src = e.target.result;

    const nameDisplay = document.getElementById('imageFileNameDisplay');
    if (nameDisplay) nameDisplay.innerText = file.name;

    const metaDisplay = document.getElementById('imageMetaDisplay');
    if (metaDisplay) metaDisplay.innerText = `${file.type || ext.toUpperCase()} • ${Math.round(file.size / 1024)} KB`;

    const statusBadge = document.getElementById('imageAnalysisStatus');
    if (statusBadge) {
      statusBadge.innerHTML = `<span class=\"badge bg-primary\"><i class=\"bi bi-file-earmark-image me-1\"></i> Image Loaded: ${file.name}</span>`;
    }

    showToastNotice('Image Uploaded', `Successfully loaded ${file.name}`, 'success');
  };
  reader.readAsDataURL(file);
}
window.handleImageFileUpload = handleImageFileUpload;
window.handleImageUploadSelection = handleImageFileUpload;

function removeUploadedImage() {
  selectedImageFile = null;
  window.selectedImageFile = null;
  activeUploadedImageData = null;

  const fileInput = document.getElementById('imageFileInput');
  if (fileInput) fileInput.value = '';

  const previewContainer = document.getElementById('imagePreviewContainer');
  if (previewContainer) previewContainer.classList.add('d-none');

  const previewImg = document.getElementById('uploadedImagePreview');
  if (previewImg) previewImg.src = '';

  const statusBadge = document.getElementById('imageAnalysisStatus');
  if (statusBadge) {
    statusBadge.innerHTML = `<span class=\"badge bg-light text-muted border\"><i class=\"bi bi-image me-1\"></i> No Image Selected</span>`;
  }

  showToastNotice('Image Removed', 'Uploaded image removed.', 'info');
}
window.removeUploadedImage = removeUploadedImage;

function analyzeUploadedImage() {
  const fileInput = document.getElementById('imageFileInput');
  const currentFile = selectedImageFile || (fileInput && fileInput.files && fileInput.files[0]);

  if (!currentFile && !activeUploadedImageData) {
    showToastNotice('Image Required', 'Please upload a diagram image first.', 'warning');
    return;
  }

  if (currentFile && !selectedImageFile) {
    selectedImageFile = currentFile;
    window.selectedImageFile = currentFile;
  }

  const desc = document.getElementById('imageDescriptionInput')?.value?.trim() || "Diagram depicting structural relationships.";

  const statusBadge = document.getElementById('imageAnalysisStatus');
  if (statusBadge) {
    statusBadge.innerHTML = `<span class=\"badge bg-success\"><i class=\"bi bi-check-circle me-1\"></i> Image Analysis Ready</span>`;
  }

  showToastNotice('Image Analyzed', `Context parsed: "${desc.slice(0, 30)}${desc.length > 30 ? '...' : ''}"`, 'success');
}
window.analyzeUploadedImage = analyzeUploadedImage;

async function generateQuestionsFromImage() {
  const fileInput = document.getElementById('imageFileInput');
  const currentFile = selectedImageFile || (fileInput && fileInput.files && fileInput.files[0]);

  if (!currentFile && !activeUploadedImageData) {
    showToastNotice('Image Required', 'Please upload a diagram image first.', 'warning');
    return;
  }

  const fileToUse = currentFile || (activeUploadedImageData && activeUploadedImageData.file);
  const fileNameToUse = (fileToUse && fileToUse.name) || (activeUploadedImageData && activeUploadedImageData.name) || 'diagram.png';

  const dept = document.getElementById('imgDeptSelect')?.value?.trim() || "Artificial Intelligence & Data Science";
  const subject = document.getElementById('imgSubjectSelect')?.value?.trim() || "Database Management Systems";
  const unitText = document.getElementById('imgUnitSelect')?.value?.trim() || "Unit 1";
  const topic = document.getElementById('imgTopicSelect')?.value?.trim() || "";
  const count = parseInt(document.getElementById('imgCountSelect')?.value || "5", 10);
  const qType = document.getElementById('imgTypeSelect')?.value || "Diagram Interpretation";
  const diff = document.getElementById('imgDiffSelect')?.value || "Balanced";
  const blooms = document.getElementById('imgBloomsSelect')?.value || "Analyze";
  const desc = document.getElementById('imageDescriptionInput')?.value?.trim() || `Diagram of ${topic || subject}`;

  activeImageConfig = { dept, subject, unit: unitText, topic, count, qType, diff, blooms, desc, fileName: fileNameToUse };

  const genBtn = document.querySelector("button[onclick='generateQuestionsFromImage()']");
  const originalBtnHtml = genBtn ? genBtn.innerHTML : '';
  if (genBtn) {
    genBtn.disabled = true;
    genBtn.innerHTML = '<span class=\"spinner-border spinner-border-sm me-2\"></span>Generating Questions...';
  }

  try {
    let generated = null;

    if (fileToUse) {
      const formData = new FormData();
      formData.append('image', fileToUse);
      formData.append('file', fileToUse);
      formData.append('department', dept);
      formData.append('subject', subject);
      formData.append('unit', unitText);
      formData.append('topic', topic);
      formData.append('num_questions', count);
      formData.append('count', count);
      formData.append('question_type', qType);
      formData.append('difficulty', diff);
      formData.append('bloom_level', blooms);
      formData.append('description', desc);
      formData.append('diagram_mode', '1');

      const endpoints = [
        'http://localhost:5000/api/questions/generate-image',
        'http://localhost:5000/api/questions/generate'
      ];

      for (const endpoint of endpoints) {
        try {
          const res = await fetch(endpoint, {
            method: 'POST',
            credentials: 'include',
            body: formData
          });

          const data = await safeParseJsonResponse(res);
          if (res.ok && data && (data.questions || data.status === 'success')) {
            generated = data;
            break;
          } else if (data && data.message && !endpoint.includes('generate-image')) {
            console.warn(`Endpoint ${endpoint} returned:`, data.message);
          }
        } catch (fetchErr) {
          console.warn(`Fetch to ${endpoint} failed:`, fetchErr);
        }
      }
    }

    if (generated && generated.questions && generated.questions.length > 0) {
      activeImageQuestions = generated.questions.map((q, i) => ({
        num: q.num || (i + 1),
        question: q.question || q.question_text || q.text,
        question_text: q.question || q.question_text || q.text,
        subject: q.subject || subject,
        department: q.department || dept,
        unit: q.unit || unitText,
        topic: q.topic || topic || (q.concept || 'Diagram Concept'),
        marks: q.marks || (qType === 'Short Answer' ? 2 : (qType === 'Descriptive' ? 16 : 8)),
        difficulty: q.difficulty || diff,
        type: q.type || q.question_type || qType,
        blooms: q.blooms || q.bloom_level || blooms,
        concept: q.concept || `${fileNameToUse} Concept`,
        imageRef: q.image_ref || q.imageRef || fileNameToUse,
        image_path: q.image_path || '',
        image_url: q.image_url || '',
        similarityStatus: q.similarityStatus || "Unique Concept"
      }));
    } else {
      activeImageQuestions = [];
      const diagramTemplates = [
        {
          q: `Based on the uploaded diagram (${fileNameToUse}), identify the primary entity types, notation symbols, and their relationship cardinality.`,
          diff: "Medium", type: "Diagram Interpretation", blooms: "Analyze", concept: "Structural Entities & Cardinality"
        },
        {
          q: `Analyze the interconnected components in '${fileNameToUse}' and deduce the primary data flow sequence for ${subject}.`,
          diff: "Hard", type: "Problem Solving", blooms: "Apply", concept: "Interaction Flow & Execution Model"
        },
        {
          q: `Identify the critical boundary constraints and dependency hierarchies established in '${fileNameToUse}' for ${unitText}.`,
          diff: "Easy", type: "Short Answer", blooms: "Remember", concept: "Interface & Dependency Constraints"
        },
        {
          q: `Evaluate the potential failure modes and architectural bottlenecks in the structure depicted in '${fileNameToUse}'.`,
          diff: "Hard", type: "Descriptive", blooms: "Evaluate", concept: "Reliability & Bottleneck Analysis"
        },
        {
          q: `Synthesize the visual blueprint in '${fileNameToUse}' to formulate an optimized implementation schema for ${topic || subject}.`,
          diff: "Medium", type: "Problem Solving", blooms: "Create", concept: "Schema Optimization & Implementation"
        }
      ];

      for (let i = 0; i < count; i++) {
        const t = diagramTemplates[i % diagramTemplates.length];
        activeImageQuestions.push({
          num: i + 1,
          question: t.q,
          question_text: t.q,
          subject: subject,
          department: dept,
          unit: unitText,
          topic: topic || t.concept,
          marks: qType === 'Short Answer' ? 2 : (qType === 'Descriptive' ? 16 : 8),
          difficulty: diff === "Balanced" ? t.diff : diff,
          type: qType === "Diagram Interpretation" ? t.type : qType,
          blooms: blooms === "Auto Select" ? t.blooms : blooms,
          concept: t.concept,
          imageRef: fileNameToUse,
          similarityStatus: "Unique Concept"
        });
      }
    }

    const wsArea = document.getElementById('imgWorkspaceArea');
    if (wsArea) wsArea.classList.remove('d-none');

    renderGeneratedImageQuestions();
    updateImageQualityCheck();
    showToastNotice('Image Questions Generated', `Generated ${activeImageQuestions.length} diagram-based questions from ${fileNameToUse}!`, 'success');

  } catch (err) {
    console.error('Error generating image questions:', err);
    showToastNotice('Error', 'An unexpected error occurred while generating questions.', 'error');
  } finally {
    if (genBtn) {
      genBtn.disabled = false;
      genBtn.innerHTML = originalBtnHtml || '<i class=\"bi bi-cpu me-2\"></i> Generate Questions From Image';
    }
  }
}
window.generateQuestionsFromImage = generateQuestionsFromImage;

function renderGeneratedImageQuestions() {
  const container = document.getElementById('imageQuestionsContainer');
  if (!container) return;

  container.innerHTML = activeImageQuestions.map((q, idx) => `
    <div class="card card-academic p-3 mb-3">
      <div class="d-flex justify-content-between align-items-center mb-2 flex-wrap gap-2">
        <div class="d-flex align-items-center gap-2">
          <span class="badge bg-primary me-1">Q${q.num}</span>
          <span class="badge ${q.difficulty === 'Easy' ? 'bg-success' : q.difficulty === 'Medium' ? 'bg-warning text-dark' : 'bg-danger'}">${q.difficulty}</span>
          <span class="badge bg-info-subtle text-info border border-info">${q.type}</span>
          <span class="badge bg-light text-muted border">${q.blooms}</span>
        </div>
        <div class="btn-group btn-group-sm">
          <button class="btn btn-outline-secondary py-0 px-2" onclick="translateQuestionDirectly('${idx}', 'image')" title="Translate"><i class="bi bi-translate text-primary me-1"></i> Translate</button>
          <button class="btn btn-outline-danger py-0 px-2" onclick="deleteImageQuestion(${idx})" title="Delete"><i class="bi bi-trash"></i></button>
        </div>
      </div>
      <p class="fw-semibold text-dark mb-2">${q.question}</p>
      <div class="d-flex justify-content-between align-items-center small text-muted border-top pt-2 mt-1">
        <span><i class="bi bi-image me-1"></i> Reference: <strong>${q.imageRef}</strong></span>
        <span><strong>Concept:</strong> ${q.concept}</span>
      </div>
    </div>
  `).join('');
}
window.renderGeneratedImageQuestions = renderGeneratedImageQuestions;

function deleteImageQuestion(idx) {
  activeImageQuestions.splice(idx, 1);
  activeImageQuestions.forEach((q, i) => q.num = i + 1);
  renderGeneratedImageQuestions();
  updateImageQualityCheck();
}
window.deleteImageQuestion = deleteImageQuestion;

function updateImageQualityCheck() {
  const totalEl = document.getElementById('imgQCTotal');
  const concEl = document.getElementById('imgQCConcepts');
  const easyEl = document.getElementById('imgQCEasy');

  if (totalEl) totalEl.innerText = `${activeImageQuestions.length} Qs`;
  if (concEl) concEl.innerText = `${activeImageQuestions.length} Diagram Concepts`;
  if (easyEl) easyEl.innerText = `${activeImageQuestions.filter(q => q.difficulty === 'Easy').length} Easy / ${activeImageQuestions.filter(q => q.difficulty === 'Hard').length} Hard`;
}
window.updateImageQualityCheck = updateImageQualityCheck;

async function saveImageQuestionsToBank() {
  if (!activeImageQuestions || activeImageQuestions.length === 0) {
    showToastNotice('Cannot Save', 'No image questions generated yet.', 'warning');
    return;
  }

  const saveBtn = document.querySelector("button[onclick='saveImageQuestionsToBank()']");
  const origHtml = saveBtn ? saveBtn.innerHTML : '';
  if (saveBtn) {
    saveBtn.disabled = true;
    saveBtn.innerHTML = '<span class=\"spinner-border spinner-border-sm me-2\"></span>Saving to Question Bank...';
  }

  try {
    const questionsToSave = activeImageQuestions.map(q => ({
      question_text: q.question || q.question_text || q.text,
      subject: q.subject || activeImageConfig.subject || 'Distributed Computing',
      department: q.department || activeImageConfig.dept || 'Artificial Intelligence & Data Science',
      unit: q.unit || activeImageConfig.unit || 'Unit 1',
      topic: q.topic || activeImageConfig.topic || (q.concept || 'Diagram Concept'),
      marks: q.marks || 8,
      difficulty: q.difficulty || 'Medium',
      question_type: q.type || q.question_type || 'Diagram Interpretation',
      bloom_level: q.blooms || q.bloom_level || 'Analyze',
      concept: q.concept || (activeUploadedImageData ? activeUploadedImageData.name : ''),
      image_ref: q.imageRef || (activeUploadedImageData ? activeUploadedImageData.name : '')
    }));

    try {
      const res = await fetch(API_QUESTION_BANK_BASE, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ batch: questionsToSave })
      });
      const data = await safeParseJsonResponse(res);
      if (res.ok) {
        console.log('Saved to backend question bank:', data);
      }
    } catch (apiErr) {
      console.warn('Backend save to question bank notice:', apiErr);
    }

    const imgObj = {
      id: `IMG-2026-${Date.now().toString().slice(-4)}`,
      fileName: (activeUploadedImageData && activeUploadedImageData.name) || activeImageConfig.fileName || "diagram.png",
      fileType: (activeUploadedImageData && activeUploadedImageData.type) || "image/png",
      fileSize: (activeUploadedImageData && activeUploadedImageData.size) || "200 KB",
      department: activeImageConfig.dept,
      subject: activeImageConfig.subject,
      unit: activeImageConfig.unit,
      topic: activeImageConfig.topic,
      description: activeImageConfig.desc,
      createdAt: new Date().toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }),
      questions: activeImageQuestions
    };

    let list = JSON.parse(localStorage.getItem(getScopedStorageKey('academic_image_questions')) || '[]');
    list.unshift(imgObj);
    localStorage.setItem(getScopedStorageKey('academic_image_questions'), JSON.stringify(list));

    if (typeof AcademicMockData !== 'undefined' && AcademicMockData.publishedImageQuestions) {
      AcademicMockData.publishedImageQuestions.unshift(imgObj);
    }

    showToastNotice('Saved to Question Bank', 'Image questions saved to repository successfully!', 'success');
    renderFacultyImageHistory();

  } catch (err) {
    console.error('Error in saveImageQuestionsToBank:', err);
    showToastNotice('Save Error', 'Failed to save all image questions.', 'error');
  } finally {
    if (saveBtn) {
      saveBtn.disabled = false;
      saveBtn.innerHTML = origHtml || '<i class=\"bi bi-bookmark-plus me-1\"></i> Save All to Question Bank';
    }
  }
}
window.saveImageQuestionsToBank = saveImageQuestionsToBank;

"""

new_lines = lines[:start_idx] + [new_code + "\n"] + lines[end_idx:]

with open(app_js_path, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("Updated js/app.js successfully!")
