#!/usr/bin/env python3
import json, sys, requests, subprocess

OLLAMA_URL = "http://localhost:11434"
MODEL = "llama3.1:8b"

SYSTEM_PROMPT = """You are a translator from natural language to robot joint moves.
Output only minified JSON with keys: action, joint, delta, speed, acc.
Examples:
"move left" -> {"action":"joint_move","joint":1,"delta":-0.1,"speed":0.2,"acc":0.5}
"move right" -> {"action":"joint_move","joint":1,"delta":0.1,"speed":0.2,"acc":0.5}
"move up" -> {"action":"joint_move","joint":2,"delta":-0.1,"speed":0.2,"acc":0.5}
"move down" -> {"action":"joint_move","joint":2,"delta":0.1,"speed":0.2,"acc":0.5}
"go home" -> {"action":"go_home","speed":0.2,"acc":0.5}
Return only JSON—no explanations, no markdown.
"""

def chat(msg: str):
    r = requests.post(f"{OLLAMA_URL}/api/chat", json={
        "model": MODEL,
        "messages": [
            {"role":"system","content": SYSTEM_PROMPT},
            {"role":"user","content": msg}
        ],
        "stream": False
    })
    r.raise_for_status()
    txt = r.json()["message"]["content"]
    try:
        return json.loads(txt)
    except Exception:
        print("Invalid JSON from model:", txt)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python agent_basic.py 'move left'")
        sys.exit(1)
    result = chat(" ".join(sys.argv[1:]))
    print(json.dumps(result, indent=2))
