import os, json

transcript_path = r"C:\Users\Nisha\.gemini\antigravity\brain\b8abb139-122a-4e36-a310-69e5f6798bcd\.system_generated\logs\transcript.jsonl"
with open(transcript_path, "r", encoding="utf-8") as f:
    for line in f:
        if "test_e2e_proxy_and_generation.py" in line:
            obj = json.loads(line)
            tool_calls = obj.get("tool_calls", [])
            for tc in tool_calls:
                print(tc.get("name"), tc.get("args"))
