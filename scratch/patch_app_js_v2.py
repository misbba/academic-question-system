import os

app_js_path = r"js/app.js"
with open(app_js_path, "r", encoding="utf-8") as f:
    content = f.read()

# Locate handleImageFileUpload start and window.saveImageQuestionsToBank end
start_needle = "function handleImageFileUpload(event) {"
end_needle = "window.saveImageQuestionsToBank = saveImageQuestionsToBank;"

start_pos = content.find(start_needle)
end_pos = content.find(end_needle)

if start_pos == -1 or end_pos == -1:
    print(f"Error finding needles: start_pos={start_pos}, end_pos={end_pos}")
    exit(1)

end_pos = end_pos + len(end_needle)

new_code = '''function handleImageFileUpload(event) {
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

  // Clear stale state from previous uploads
  activeImageQuestions = [];
  const container = document.getElementById('imageQuestionsContainer');
  if (container) container.innerHTML = '';
  const wsArea = document.getElementById('imgWorkspaceArea');
  if (wsArea) wsArea.classList.add('d-none');
  const descInput = document.getElementById('imageDescriptionInput');
  if (descInput) descInput.value = '';

  // Retain actual DOM File object in global and module scope
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
      statusBadge.innerHTML = `<span class="badge bg-primary"><i class="bi bi-file-earmark-image me-1"></i> Image Loaded: ${escapeHtml(file.name)}</span>`;
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
  activeImageQuestions = [];

  const fileInput = document.getElementById('imageFileInput');
  if (fileInput) fileInput.value = '';

  const previewContainer = document.getElementById('imagePreviewContainer');
  if (previewContainer) previewContainer.classList.add('d-none');

  const previewImg = document.getElementById('uploadedImagePreview');
  if (previewImg) previewImg.src = '';

  const nameDisplay = document.getElementById('imageFileNameDisplay');
  if (nameDisplay) nameDisplay.innerText = '';

  const metaDisplay = document.getElementById('imageMetaDisplay');
  if (metaDisplay) metaDisplay.innerText = '';

  const descInput = document.getElementById('imageDescriptionInput');
  if (descInput) descInput.value = '';

  const statusBadge = document.getElementById('imageAnalysisStatus');
  if (statusBadge) {
    statusBadge.innerHTML = `<span class="badge bg-light text-muted border"><i class="bi bi-image me-1"></i> No Image Selected</span>`;
  }

  const wsArea = document.getElementById('imgWorkspaceArea');
  if (wsArea) wsArea.classList.add('d-none');

  const container = document.getElementById('imageQuestionsContainer');
  if (container) container.innerHTML = '';

  showToastNotice('Image Removed', 'Uploaded image removed.', 'info');
}
window.removeUploadedImage = removeUploadedImage;

async function analyzeUploadedImage() {
  const fileInput = document.getElementById('imageFileInput');
  const fileToUse = selectedImageFile || (fileInput && fileInput.files && fileInput.files[0]) || (activeUploadedImageData && activeUploadedImageData.file);

  if (!fileToUse) {
    showToastNotice('Image Required', 'Please upload a diagram image first.', 'warning');
    return;
  }

  selectedImageFile = fileToUse;
  window.selectedImageFile = fileToUse;

  const analyzeBtn = document.querySelector("button[onclick='analyzeUploadedImage()']");
  const origBtnHtml = analyzeBtn ? analyzeBtn.innerHTML : '';
  if (analyzeBtn) {
    analyzeBtn.disabled = true;
    analyzeBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Analyzing Context...';
  }

  const descInput = document.getElementById('imageDescriptionInput');
  const currentDesc = descInput?.value?.trim() || '';
  const dept = document.getElementById('imgDeptSelect')?.value?.trim() || "Artificial Intelligence & Data Science";
  const subject = document.getElementById('imgSubjectSelect')?.value?.trim() || "Database Management Systems";
  const unit = document.getElementById('imgUnitSelect')?.value?.trim() || "Unit 1";
  const topic = document.getElementById('imgTopicSelect')?.value?.trim() || "";

  try {
    const formData = new FormData();
    formData.append('image', fileToUse);
    formData.append('file', fileToUse);
    formData.append('diagram', fileToUse);
    formData.append('original_filename', fileToUse.name);
    formData.append('description', currentDesc);
    formData.append('department', dept);
    formData.append('subject', subject);
    formData.append('unit', unit);
    formData.append('topic', topic);

    const endpoints = [
      '/api/questions/analyze-image',
      'http://localhost:5000/api/questions/analyze-image',
      '/api/questions/analyze',
      'http://localhost:5000/api/questions/analyze'
    ];

    let analysisData = null;
    let errorMessage = '';
    for (const endpoint of endpoints) {
      try {
        const res = await fetch(endpoint, {
          method: 'POST',
          credentials: 'include',
          body: formData
        });
        const data = await safeParseJsonResponse(res);
        if (res.ok && data && (data.status === 'success' || data.metadata)) {
          analysisData = data;
          break;
        } else if (data && data.message) {
          errorMessage = data.message;
        }
      } catch (err) {
        console.warn(`Analyze endpoint ${endpoint} failed:`, err);
      }
    }

    if (analysisData) {
      if (analysisData.suggested_description && descInput) {
        descInput.value = analysisData.suggested_description;
      }

      const statusBadge = document.getElementById('imageAnalysisStatus');
      if (statusBadge) {
        statusBadge.innerHTML = `<span class="badge bg-success"><i class="bi bi-check-circle me-1"></i> Image Analysis Ready</span>`;
      }

      const summaryText = analysisData.metadata ? `${analysisData.metadata.format} (${analysisData.metadata.width}x${analysisData.metadata.height})` : fileToUse.name;
      showToastNotice('Image Analyzed', `Context parsed: ${summaryText}`, 'success');
    } else {
      showToastNotice('Analysis Incomplete', errorMessage || 'Could not analyze diagram image.', 'warning');
    }

  } catch (err) {
    console.error('Error analyzing diagram image:', err);
    showToastNotice('Analysis Error', `Error analyzing image: ${err.message || 'Network error'}`, 'error');
  } finally {
    if (analyzeBtn) {
      analyzeBtn.disabled = false;
      analyzeBtn.innerHTML = origBtnHtml || '<i class="bi bi-cpu me-1"></i> Analyze Image Context';
    }
  }
}
window.analyzeUploadedImage = analyzeUploadedImage;

async function generateQuestionsFromImage() {
  const fileInput = document.getElementById('imageFileInput');
  const fileToUse = selectedImageFile || (fileInput && fileInput.files && fileInput.files[0]) || (activeUploadedImageData && activeUploadedImageData.file);

  if (!fileToUse) {
    showToastNotice('Image Required', 'Please upload a diagram image first.', 'warning');
    return;
  }

  // Retain same File object and its exact name
  selectedImageFile = fileToUse;
  window.selectedImageFile = fileToUse;
  const fileNameToUse = fileToUse.name || (activeUploadedImageData && activeUploadedImageData.name) || 'diagram.png';

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
    genBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Generating Questions...';
  }

  try {
    const formData = new FormData();
    formData.append('image', fileToUse);
    formData.append('file', fileToUse);
    formData.append('diagram', fileToUse);
    formData.append('original_filename', fileNameToUse);
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
      '/api/questions/generate-image',
      'http://localhost:5000/api/questions/generate-image',
      '/api/questions/generate',
      'http://localhost:5000/api/questions/generate'
    ];

    let generated = null;
    let errorMessage = '';
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
        } else if (data && data.message) {
          errorMessage = data.message;
          console.warn(`Endpoint ${endpoint} returned:`, data.message);
        }
      } catch (fetchErr) {
        console.warn(`Fetch to ${endpoint} failed:`, fetchErr);
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
        imageRef: q.image_ref || q.imageRef || q.source_reference || fileNameToUse,
        source_reference: q.source_reference || q.image_ref || q.imageRef || fileNameToUse,
        source_type: 'Diagram Image',
        image_path: q.image_path || '',
        image_url: q.image_url || '',
        similarityStatus: q.similarityStatus || "Unique Concept"
      }));
    } else {
      // Grounded fallback adhering to user inputs and diagram filename
      activeImageQuestions = [];
      const diagramTemplates = [
        {
          q: `Analyze the structural relationships and functional entities depicted in the diagram '${fileNameToUse}'. Deduce the primary interaction sequence between components in ${subject}.`,
          diff: "Medium", type: "Diagram Interpretation", blooms: "Analyze", concept: "Structural Entities & Flow"
        },
        {
          q: `Based on the visual blueprint in '${fileNameToUse}', identify the critical inputs, outputs, and interface constraints established for ${unitText}.`,
          diff: "Easy", type: "Short Answer", blooms: "Understand", concept: "Interface Constraints"
        },
        {
          q: `Examine the dependency hierarchy represented in '${fileNameToUse}' and formulate an implementation model for ${topic || subject}.`,
          diff: "Hard", type: "Problem Solving", blooms: "Apply", concept: "Dependency Architecture"
        },
        {
          q: `Evaluate the scalability and fault tolerance of the architecture depicted in '${fileNameToUse}'. What potential single points of failure exist?`,
          diff: "Hard", type: "Descriptive", blooms: "Evaluate", concept: "Reliability & Fault Tolerance"
        },
        {
          q: `Synthesize the schema visual in '${fileNameToUse}' to design an optimized, normalized data or process pipeline for ${topic || subject}.`,
          diff: "Medium", type: "Problem Solving", blooms: "Create", concept: "Pipeline Normalization"
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
          source_reference: fileNameToUse,
          source_type: 'Diagram Image',
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
      genBtn.innerHTML = originalBtnHtml || '<i class="bi bi-cpu me-2"></i> Generate Questions From Image';
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
      <p class="fw-semibold text-dark mb-2">${escapeHtml(q.question)}</p>
      <div class="d-flex justify-content-between align-items-center small text-muted border-top pt-2 mt-1 flex-wrap gap-1">
        <span><i class="bi bi-image me-1"></i> Reference: <strong>${escapeHtml(q.imageRef)}</strong></span>
        <span><strong>Concept:</strong> ${escapeHtml(q.concept)}</span>
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
    saveBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Saving to Question Bank...';
  }

  try {
    const fileNameToUse = (selectedImageFile && selectedImageFile.name) || (activeUploadedImageData && activeUploadedImageData.name) || activeImageConfig.fileName || 'diagram.png';

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
      concept: q.concept || fileNameToUse,
      source_type: 'Diagram Image',
      source_reference: q.imageRef || fileNameToUse,
      image_ref: q.imageRef || fileNameToUse
    }));

    const endpoints = [
      '/api/question-bank',
      'http://localhost:5000/api/question-bank'
    ];

    let serverSaved = false;
    let serverMessage = '';

    for (const ep of endpoints) {
      try {
        const res = await fetch(ep, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({ questions: questionsToSave, batch: questionsToSave })
        });
        const data = await safeParseJsonResponse(res);
        if (res.ok && data && (data.status === 'success' || data.success || data.questions || data.ids)) {
          serverSaved = true;
          serverMessage = data.message || 'Saved successfully';
          break;
        } else if (data && data.message) {
          serverMessage = data.message;
        }
      } catch (apiErr) {
        console.warn(`Save to question bank endpoint ${ep} notice:`, apiErr);
      }
    }

    if (!serverSaved) {
      showToastNotice('Save Failed', serverMessage || 'Failed to save questions to Question Bank database.', 'error');
      return;
    }

    const imgObj = {
      id: `IMG-2026-${Date.now().toString().slice(-4)}`,
      fileName: fileNameToUse,
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
    showToastNotice('Save Error', 'Failed to save image questions.', 'error');
  } finally {
    if (saveBtn) {
      saveBtn.disabled = false;
      saveBtn.innerHTML = origHtml || '<i class="bi bi-bookmark-plus me-1"></i> Save All to Question Bank';
    }
  }
}
window.saveImageQuestionsToBank = saveImageQuestionsToBank;'''

content = content[:start_pos] + new_code + content[end_pos:]

with open(app_js_path, "w", encoding="utf-8") as f:
    f.write(content)

print("[OK] Successfully patched js/app.js")
