import os
from pathlib import Path

env_file = Path(r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\.env")
print(".env exists?", env_file.exists())
if env_file.exists():
    with open(env_file, 'r', encoding='utf-8') as f:
        for line in f:
            if any(k in line.lower() for k in ['api', 'key', 'model', 'ai', 'secret', 'gemini', 'openai']):
                print("Line:", line.split('=')[0])

print("\nEnvironment variables related to AI:")
for k, v in os.environ.items():
    if any(term in k.lower() for term in ['gemini', 'openai', 'anthropic', 'api_key', 'tesseract']):
        print(f"{k} is set (len: {len(v)})")
