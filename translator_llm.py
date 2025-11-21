#!/usr/bin/env python3
"""
Author: Julian Dario Romero 
Independent Study: AI Agent for Mixed Reality Robotics - Flexible Manufacturing
Date: 11/20/2025

Description:
    translator_llm.py
    Converts symbolic task steps into robot-executable JSON actions.
    This is the second LLM in the 2-layer architecture.

Contributors:
    Julian Dario Romero, romerorj@purdue.edu 


Academic Integrity Statement:
    I have not used source code obtained from any unauthorized
    source, either modified or unmodified;  The project I am
    submitting is my own original work and it has GenAI assistance.
"""


import json
import sys
import requests

OLLAMA_URL = "http://localhost:11434"
MODEL = "llama3.1:8b"

SYSTEM_PROMPT = """
You translate a SINGLE symbolic task step into a low-level robot action JSON.

You must ONLY output JSON (minified or pretty OK). No text.

You never guess coordinates.
You ONLY use the pose names below that correspond to known robot waypoints.

Workspace (fixed for now):
object "box":
- "box_approach_l"
- "box_pick_l"

destination "bin_a":
- "bin_a_approach_l"
- "bin_a_drop_l"

home:
- "home_j"

Rules:
- For "pick", produce:
  {
    "action":"pick",
    "approach":"box_approach_l",
    "pick":"box_pick_l",
    "retreat":"box_approach_l",
    "speed":0.2,
    "acc":0.5
  }

- For "place", produce:
  {
    "action":"place",
    "approach":"bin_a_approach_l",
    "drop":"bin_a_drop_l",
    "retreat":"bin_a_approach_l",
    "speed":0.2,
    "acc":0.5
  }

- For "go_home":
  {
    "action": "go_home",
    "target": "home_j",
    "space": "joint",
    "speed":0.2,
    "acc":0.5
  }

Mandatory:
- Only output JSON.
- Only use keys: action, approach, pick, drop, retreat, target, space, speed, acc.
- Never invent new pose names.
- Speed and acc must always appear.
"""

def translate_step(step: dict) -> dict:
    """Call Ollama to translate a step."""
    user_msg = json.dumps(step)

    payload = {
        "model": MODEL,
        "messages": [
            {"role":"system","content": SYSTEM_PROMPT},
            {"role":"user","content": user_msg}
        ],
        "stream": False,
    }

    r = requests.post(f"{OLLAMA_URL}/api/chat", json=payload)
    r.raise_for_status()
    content = r.json()["message"]["content"].strip()

    try:
        return json.loads(content)
    except Exception:
        print("\n[ERROR] Translator LLM returned invalid JSON:")
        print(content)
        sys.exit(1)


def main():
    if len(sys.argv) < 2:
        print("Usage: python translator_llm.py '{\"step\":\"pick\",\"object\":\"box\",\"from\":\"table\"}'")
        sys.exit(1)

    step_json = json.loads(sys.argv[1])
    print("[INPUT STEP]")
    print(step_json)

    action = translate_step(step_json)

    print("\n[TRANSLATED ACTION]")
    print(json.dumps(action, indent=2))


if __name__ == "__main__":
    main()

