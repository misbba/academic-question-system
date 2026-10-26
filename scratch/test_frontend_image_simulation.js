const fs = require('fs');
const path = require('path');

// Read faculty-image-question.html
const htmlContent = fs.readFileSync(path.join(__dirname, '..', 'faculty-image-question.html'), 'utf-8');

console.log("--- Test 1: Verify Initial Badge in HTML ---");
if (htmlContent.includes('<div id="imageAnalysisStatus"><span class="badge bg-light text-muted border"><i class="bi bi-image me-1"></i> No Image Selected</span></div>')) {
  console.log("[PASS] HTML initial badge correctly displays 'No Image Selected'");
} else {
  console.error("[FAIL] HTML still contains old/incorrect badge");
  process.exit(1);
}

console.log("--- Test 2: Verify File Input has accept and onchange ---");
if (htmlContent.includes('id="imageFileInput"') && htmlContent.includes('onchange="handleImageFileUpload(event)"')) {
  console.log("[PASS] File input properly specifies onchange='handleImageFileUpload(event)'");
} else {
  console.error("[FAIL] File input does not have expected onchange handler");
  process.exit(1);
}

// Read js/app.js
const appJsContent = fs.readFileSync(path.join(__dirname, '..', 'js', 'app.js'), 'utf-8');

console.log("--- Test 3: Verify JS Handlers and Global Bindings ---");
const checks = [
  'selectedImageFile',
  'function handleImageFileUpload',
  'function analyzeUploadedImage',
  'function generateQuestionsFromImage',
  'function removeUploadedImage',
  'function saveImageQuestionsToBank',
  'window.handleImageUploadSelection = handleImageFileUpload',
  'window.selectedImageFile',
  '/api/questions/generate-image'
];

for (const check of checks) {
  if (appJsContent.includes(check)) {
    console.log(`[PASS] Found in app.js: '${check}'`);
  } else {
    console.error(`[FAIL] Missing in app.js: '${check}'`);
    process.exit(1);
  }
}

console.log("\n=======================================================");
console.log("ALL FRONTEND STATIC & BINDING CHECKS PASSED!");
console.log("=======================================================");
