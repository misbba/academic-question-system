import sys

path = r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\faculty-question-paper.html"

with open(path, "r", encoding="utf-8") as f:
    content = f.read().replace("\r\n", "\n")

old_card = """                  <ul class="small text-secondary ps-3 mb-3">
                    <li><strong>PART - A (10 x 2 = 20 Marks):</strong> 10 compulsory questions with Bloom's taxonomy tags [RE], [UN], [AP], [AN].</li>
                    <li><strong>PART - B (5 x 13 = 65 Marks):</strong> Questions 11 to 15 with Either/Or choice (a) vs (b). Accurately supports <strong>(8 + 5 = 13 marks) subquestions</strong> and 13m single questions.</li>
                    <li><strong>PART - C (1 x 15 = 15 Marks):</strong> Question 16 with Either/Or choice (a) vs (b) for comprehensive analytical/case study assessment.</li>
                  </ul>"""

new_card = """                  <ul class="small text-secondary ps-3 mb-3">
                    <li><strong>PART - A (10 x 2 = 20 Marks):</strong> 10 compulsory questions carrying 2 marks each with Bloom's taxonomy tags [RE], [UN], [AP], [AN].</li>
                    <li><strong>PART - B (5 x 16 = 80 Marks):</strong> Questions 11 to 15 (Units I to V) with Either/Or choice (a) vs (b). Supports flexible <strong>Direct 16-Mark Question</strong> or <strong>Split 16-Mark Question (8 + 8 subquestions)</strong> for each alternative.</li>
                    <li><strong>Structure:</strong> Strictly Part A and Part B only (Total Attempted Marks = 100). No Part C.</li>
                  </ul>"""

assert old_card in content, "old_card not found in faculty-question-paper.html"
content = content.replace(old_card, new_card)

old_sec_container = """          <div id="paperSectionsStructureContainer" class="mb-3">
            <!-- Rendered dynamically based on current template -->
          </div>"""

new_sec_container = """          <div id="paperSectionsStructureContainer" class="mb-3">
            <!-- Rendered dynamically based on current template -->
          </div>

          <!-- Interactive Part B 16-Mark Group Format Selector & Manager -->
          <div id="partBGroupManagerContainer" class="mt-4" style="display: none;"></div>"""

assert old_sec_container in content, "old_sec_container not found in faculty-question-paper.html"
content = content.replace(old_sec_container, new_sec_container)

content_crlf = content.replace("\n", "\r\n")
with open(path, "w", encoding="utf-8") as f:
    f.write(content_crlf)

print("faculty-question-paper.html patched successfully.")
