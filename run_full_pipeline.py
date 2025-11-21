"""
Author: Julian Dario Romero 
Independent Study: AI Agent for Mixed Reality Robotics - Flexible Manufacturing
Date: 11/20/2025

Description:
Complete 2-layer robot task execution pipeline (safe simulation only).

Pipeline:
1. Planner LLM   → symbolic plan
2. Translator LLM → robot action JSON
3. Executor (simulation) → prints actions

Robot is NOT moved yet. This is a safe dry-run.

Contributors:
    Julian Dario Romero, romerorj@purdue.edu 


Academic Integrity Statement:
    I have not used source code obtained from any unauthorized
    source, either modified or unmodified;  The project I am
    submitting is my own original work and it has GenAI assistance.
"""

import json
import sys
from planner_llm import call_planner
from translator_llm import translate_step


# -------------------------------
# Pretty print helper
# -------------------------------
def print_action(action):
    action_type = action.get("action")

    if action_type == "pick":
        print(f" → PICK")
        print(f"    approach : {action['approach']}")
        print(f"    pick     : {action['pick']}")
        print(f"    retreat  : {action['retreat']}")

    elif action_type == "place":
        print(f" → PLACE")
        print(f"    approach : {action['approach']}")
        print(f"    drop     : {action['drop']}")
        print(f"    retreat  : {action['retreat']}")

    elif action_type == "go_home":
        print(f" → GO HOME")
        print(f"    target : {action['target']}")

    else:
        print(f" → UNKNOWN ACTION: {action}")

    print(f"    speed : {action.get('speed')}")
    print(f"    acc   : {action.get('acc')}")
    print()


# -------------------------------
# Main pipeline
# -------------------------------
def run_pipeline(user_text: str):
    print("\n=======================================")
    print("           FULL PIPELINE RUN")
    print("=======================================\n")

    print(f"[USER INPUT] {user_text}\n")

    # 1) High-level plan
    print("[1] Calling PLANNER LLM…")
    plan_json = call_planner(user_text)
    task_plan = plan_json.get("task_plan", [])

    print("\n[PLANNER OUTPUT]:")
    print(json.dumps(plan_json, indent=2))

    # 2) Translate each step
    print("\n[2] Translating each step via TRANSLATOR LLM…\n")
    robot_actions = []

    for i, step in enumerate(task_plan):
        print(f"  Step {i+1}: {step}")
        action = translate_step(step)
        robot_actions.append(action)
        print(f"  → Translated to:")
        print(json.dumps(action, indent=2))
        print()

    # 3) Simulated execution
    print("\n[3] EXECUTION (simulation only)")
    print("---------------------------------------\n")

    for i, action in enumerate(robot_actions):
        print(f"[Action {i+1}]")
        print_action(action)

    print("=======================================")
    print("    END OF SIMULATION — NO ROBOT MOVED")
    print("=======================================\n")


# -------------------------------
# Entry point
# -------------------------------
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_full_pipeline.py \"Pick the box and place it in bin A\"")
        sys.exit(1)

    user_text = " ".join(sys.argv[1:])
    run_pipeline(user_text)
