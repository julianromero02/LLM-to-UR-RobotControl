#!/usr/bin/env python3
"""
run_plan.py
Step 2 of the 2-layer architecture.
- Calls the high-level task planner LLM
- Retrieves the symbolic plan
- Iterates through the steps
- For now: prints the symbolic steps (no robot execution)
"""

import json
import sys
from planner_llm import call_planner   # re-use your planner

def pretty_step(step):
    """Generate a human-friendly description."""
    if step["step"] == "pick":
        return f"→ PICK object '{step['object']}' from '{step['from']}'"

    if step["step"] == "place":
        return f"→ PLACE object '{step['object']}' into '{step['to']}'"

    if step["step"] == "go_home":
        return f"→ MOVE robot to home position"

    return f"→ UNKNOWN STEP: {step}"

def run_plan(task_plan: list):
    print("\n==============================")
    print("   SYMBOLIC TASK PLAN")
    print("==============================\n")

    for i, step in enumerate(task_plan):
        desc = pretty_step(step)
        print(f"Step {i+1}: {desc}")

    print("\n(✔ simulation only — no robot movements yet)")
    print("==============================\n")


def main():
    if len(sys.argv) < 2:
        print("Usage: python run_plan.py \"Pick the box and place it in bin A\"")
        sys.exit(1)

    user_text = " ".join(sys.argv[1:])
    print(f"[USER] {user_text}")

    plan_json = call_planner(user_text)
    print("\n[PLANNER RAW OUTPUT]")
    print(json.dumps(plan_json, indent=2))

    task_plan = plan_json.get("task_plan", [])
    run_plan(task_plan)


if __name__ == "__main__":
    main()
