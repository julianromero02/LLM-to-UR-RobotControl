#!/usr/bin/env python3
import json
import requests
import subprocess
import shlex
import sys
import os

# ----------------------------
# CONFIG
# ----------------------------
OLLAMA_URL = "http://localhost:11434"
MODEL = "llama3.1:8b"
ROBOT_IP = "192.168.1.226"     # put your real robot IP

SYSTEM_PROMPT = """
You translate natural language commands into robot actions.
Output ONLY minified JSON.

Available pose names:
- "home_j"
- "box_approach_l", "box_pick_l"
- "bin_a_approach_l", "bin_a_drop_l"

JSON schemas:
1) Go home
{"action":"go_home","speed":0.2,"acc":0.5}

2) Go to pose
{"action":"go_pose","target":"box_approach_l","speed":0.2,"acc":0.5}

3) Joint delta
{"action":"joint_move","joint":1,"delta":0.1,"speed":0.2,"acc":0.5}

4) Pick (3-step)
{"action":"pick","approach":"box_approach_l","pick":"box_pick_l","retreat":"box_approach_l","speed":0.2,"acc":0.5}

5) Place (3-step)
{"action":"place","approach":"bin_a_approach_l","drop":"bin_a_drop_l","retreat":"bin_a_approach_l","speed":0.2,"acc":0.5}

Mappings:
- "pick the box" → {"action":"pick", "approach":"box_approach_l", "pick":"box_pick_l", "retreat":"box_approach_l", ...}
- "place it in bin A" → {"action":"place", "approach":"bin_a_approach_l", "drop":"bin_a_drop_l", "retreat":"bin_a_approach_l"}

Rules:
- Output ONLY JSON.
- No extra text, no markdown.
"""



# ----------------------------
# LLM CALL
# ----------------------------
def call_llm(user_message: str) -> dict:
    payload = {
        "model": MODEL,
        "messages": [
            {"role":"system","content": SYSTEM_PROMPT},
            {"role":"user","content": user_message}
        ],
        "stream": False,
    }
    r = requests.post(f"{OLLAMA_URL}/api/chat", json=payload)
    r.raise_for_status()
    content = r.json()["message"]["content"].strip()
    try:
        return json.loads(content)
    except Exception:
        print("\n[ERROR] LLM gave invalid JSON:\n", content)
        sys.exit(1)

# ----------------------------
# EXECUTE ROBOT COMMAND
# ----------------------------
def execute_command(cmd_dict: dict):
    # Convert dict to JSON string for move_basic.py
    json_arg = json.dumps(cmd_dict)

    # Build the execution command
    command = f"python3 move_basic.py '{json_arg}'"

    print("\n[EXECUTOR] Running:")
    print(command, "\n")

    # Run and stream output
    process = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    assert process.stdout is not None
    for line in process.stdout:
        print(line, end="")
    process.wait()

# ----------------------------
# MAIN
# ----------------------------
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python agent_execute.py \"move left\"")
        sys.exit(1)

    user_text = " ".join(sys.argv[1:])
    print(f"[USER] {user_text}")

    # 1. LLM → JSON
    cmd = call_llm(user_text)
    print("\n[LLM OUTPUT]:")
    print(json.dumps(cmd, indent=2))

    # 2. JSON → Robot executor
    execute_command(cmd)
