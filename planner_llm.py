#!/usr/bin/env python3
"""
planner_llm.py
High-level task planner LLM.
Input: natural language instruction (e.g., "Pick the box and place it in bin A, then go home")
Output: symbolic JSON plan (no robot details).
"""

import sys
import json
import requests

OLLAMA_URL = "http://localhost:11434"
MODEL = "llama3.1:8b"

SYSTEM_PROMPT = """
You are a high-level task planner for a robot.
You DO NOT output robot coordinates or joint angles.
You ONLY output a symbolic task plan in JSON.

The workspace:
- One box on a table: object "box", location "table"
- One bin: "bin_a"
- The robot has a "home" position.

Valid steps in the plan:
- {"step":"pick","object":"box","from":"table"}
- {"step":"place","object":"box","to":"bin_a"}
- {"step":"go_home"}

Output format (always):
{
  "task_plan": [
    { ...step 1... },
    { ...step 2... },
    ...
  ]
}

Examples:
User: "Pick the box and put it in bin A, then go home"
Plan:
{
  "task_plan": [
    {"step":"pick","object":"box","from":"table"},
    {"step":"place","object":"box","to":"bin_a"},
    {"step":"go_home"}
  ]
}

User: "Just go home"
Plan:
{
  "task_plan": [
    {"step":"go_home"}
  ]
}

User: "Move the box to the bin"
Plan:
{
  "task_plan": [
    {"step":"pick","object":"box","from":"table"},
    {"step":"place","object":"box","to":"bin_a"}
  ]
}

Rules:
- Always respond with a SINGLE JSON object.
- The top-level key MUST be "task_plan".
- Use only the allowed fields: step, object, from, to.
- Do NOT include any explanation, comments, or markdown. JSON only.
"""

def call_planner(user_text: str) -> dict:
    """Call Ollama and return the parsed JSON task plan."""
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text}
        ],
        "stream": False,
    }
    resp = requests.post(f"{OLLAMA_URL}/api/chat", json=payload, timeout=120)
    resp.raise_for_status()
    content = resp.json()["message"]["content"].strip()
    try:
        return json.loads(content)
    except Exception:
        print("[ERROR] LLM returned invalid JSON:")
        print(content)
        sys.exit(1)

def main():
    if len(sys.argv) < 2:
        print("Usage: python planner_llm.py \"pick the box and place it in bin A\"")
        sys.exit(1)

    user_text = " ".join(sys.argv[1:])
    print(f"[USER] {user_text}")

    plan = call_planner(user_text)
    print("\n[PLANNER OUTPUT]:")
    print(json.dumps(plan, indent=2))

if __name__ == "__main__":
    main()
