import os, re

routes_dir = r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\backend\routes"
for fname in os.listdir(routes_dir):
    if fname.endswith(".py"):
        fpath = os.path.join(routes_dir, fname)
        print(f"\n==================== {fname} ====================")
        with open(fpath, "r", encoding="utf-8") as f:
            lines = f.readlines()
        for i, l in enumerate(lines):
            if "@" in l and (".route(" in l or "bp.route" in l):
                print(f"Line {i+1}: {l.strip()}")
                # Also print the def line following it
                for j in range(i+1, min(len(lines), i+6)):
                    if lines[j].strip().startswith("def "):
                        print(f"         {lines[j].strip()}")
                        break
