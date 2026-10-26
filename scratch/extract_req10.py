import json

transcript_path = r"C:\Users\Nisha\.gemini\antigravity\brain\b8abb139-122a-4e36-a310-69e5f6798bcd\.system_generated\logs\transcript_full.jsonl"
with open(transcript_path, 'r', encoding='utf-8') as f:
    for line in f:
        if 'COMPLETE FIX REQUEST' in line:
            obj = json.loads(line)
            content = obj.get('content', '')
            out_path = r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\scratch\user_request_10.txt"
            with open(out_path, 'w', encoding='utf-8') as out_f:
                out_f.write(content)
            print(f"Wrote {len(content)} chars to scratch/user_request_10.txt")
            break
