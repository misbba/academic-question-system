filepath = 'C:/Users/Nisha/.gemini/antigravity/scratch/academic-question-system/js/app.js'
with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}")
# Find occurrences of const hierarchyEl
decl_indices = [i for i, line in enumerate(lines) if "const hierarchyEl = document.getElementById('conceptHierarchyContainer');" in line]
print(f"Declaration indices: {decl_indices}")

if len(decl_indices) == 2:
    start_second = decl_indices[1]
    # find ending of this if block (closing `;\n }`)
    end_second = start_second
    for j in range(start_second, start_second + 35):
        if lines[j].strip() == "}":
            end_second = j
            break
    print(f"Removing lines {start_second} to {end_second}:")
    for k in range(start_second, end_second + 1):
        print(f"  {lines[k]}", end="")
    
    # Remove these lines
    new_lines = lines[:start_second] + lines[end_second+1:]
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print("Successfully removed duplicate declaration.")
else:
    print("Unexpected number of declarations found:", len(decl_indices))
