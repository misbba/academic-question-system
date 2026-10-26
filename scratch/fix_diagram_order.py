# Reorder diagram category matching in backend/services/question_service.py
import os

WORKSPACE = r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system"
SERVICE_PATH = os.path.join(WORKSPACE, "backend", "services", "question_service.py")

with open(SERVICE_PATH, 'r', encoding='utf-8') as f:
    code = f.read()

# Replace condition in line 1498:
old_cond = "if any(k in corpus for k in ['lamport', 'clock', 'logical clock', 'happens-before', 'vector clock', 'synchronization']) or (prominent_horiz_lines >= 3 and aspect_ratio >= 1.3 and any(k in corpus for k in ['algorithm', 'distributed', 'process', 'event', 'system', 'concurrency'])):"
new_cond = "if (any(k in corpus for k in ['lamport', 'clock', 'logical clock', 'happens-before', 'vector clock', 'synchronization']) or (prominent_horiz_lines >= 3 and aspect_ratio >= 1.3 and any(k in corpus for k in ['distributed', 'timeline', 'lifeline', 'process', 'concurrency']))) and not any(k in corpus for k in ['schema', 'entity', 'relational', 'database', 'dbms', 'sql']):"

assert old_cond in code, "old_cond not found in question_service.py!"
code = code.replace(old_cond, new_cond, 1)

with open(SERVICE_PATH, 'w', encoding='utf-8', newline='\r\n') as f:
    f.write(code)

print("Successfully updated diagram category precedence in question_service.py!")
