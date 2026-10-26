import glob
import os
import re

project_dir = r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system"
html_files = glob.glob(os.path.join(project_dir, "*.html"))

print(f"Updating script tags in {len(html_files)} HTML files...")

for fpath in html_files:
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()

    orig = content
    # Replace auth.js, mock-data.js, app.js references with cache buster ?v=20261025
    content = re.sub(r'src="js/auth\.js(\?v=[^"]*)?"', 'src="js/auth.js?v=20261025"', content)
    content = re.sub(r'src="js/mock-data\.js(\?v=[^"]*)?"', 'src="js/mock-data.js?v=20261025"', content)
    content = re.sub(r'src="js/app\.js(\?v=[^"]*)?"', 'src="js/app.js?v=20261025"', content)

    if content != orig:
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated: {os.path.basename(fpath)}")

print("All HTML files updated with cache buster!")
