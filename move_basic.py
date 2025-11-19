#!/usr/bin/env python3
import sys, time, json, pathlib
from rtde_control import RTDEControlInterface

ROBOT_IP = "192.168.1.226"
VEL, ACC = 0.2, 0.5

def load_poses():
    p = pathlib.Path("poses.json")
    if not p.exists():
        print("[ERROR] poses.json not found.")
        return {}
    return json.loads(p.read_text())

def move_pose(rtde_c, pose, speed, acc):
    if isinstance(pose, str):
        raise ValueError("Pose should be list of 6 floats, not string.")
    if len(pose) != 6:
        raise ValueError("Pose must have length 6.")
    rtde_c.moveL(pose, speed=speed, acceleration=acc)

def move_joint(rtde_c, joints, speed, acc):
    rtde_c.moveJ(joints, speed=speed, acceleration=acc)

def main(cmd: dict):
    rtde_c = RTDEControlInterface(ROBOT_IP)
    poses = load_poses()

    action = cmd["action"]
    speed = cmd.get("speed", VEL)
    acc   = cmd.get("acc",   ACC)

    # ------------------------------------------------------------------
    # BASIC ACTIONS
    # ------------------------------------------------------------------
    if action == "go_home":
        home = poses["home_j"]
        move_joint(rtde_c, home, speed, acc)

    elif action == "go_pose":
        pose_name = cmd["target"]
        pose = poses[pose_name]
        if pose_name.endswith("_j"):
            move_joint(rtde_c, pose, speed, acc)
        else:
            move_pose(rtde_c, pose, speed, acc)

    elif action == "joint_move":
        q = rtde_c.getActualQ()
        j = cmd["joint"]
        q[j] += cmd["delta"]
        move_joint(rtde_c, q, speed, acc)

    # ------------------------------------------------------------------
    # PICK ACTION: approach → pick → retreat
    # ------------------------------------------------------------------
    elif action == "pick":
        approach = poses[cmd["approach"]]
        pick     = poses[cmd["pick"]]
        retreat  = poses[cmd["retreat"]]

        move_pose(rtde_c, approach, speed, acc)
        move_pose(rtde_c, pick, speed, acc)
        # TODO later: close gripper
        move_pose(rtde_c, retreat, speed, acc)

    # ------------------------------------------------------------------
    # PLACE ACTION: approach → drop → retreat
    # ------------------------------------------------------------------
    elif action == "place":
        approach = poses[cmd["approach"]]
        drop     = poses[cmd["drop"]]
        retreat  = poses[cmd["retreat"]]

        move_pose(rtde_c, approach, speed, acc)
        move_pose(rtde_c, drop, speed, acc)
        # TODO later: open gripper
        move_pose(rtde_c, retreat, speed, acc)

    else:
        print("[ERROR] Unknown action:", cmd)

    time.sleep(0.5)
    rtde_c.stopJ(acc)

    #rtde_c.stopJ(acceleration=acc)
    rtde_c.disconnect()

if __name__ == "__main__":
    cmd = json.loads(sys.argv[1])
    main(cmd)
