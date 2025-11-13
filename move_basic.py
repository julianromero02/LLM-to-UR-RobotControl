#!/usr/bin/env python3
import sys, time, json
from rtde_control import RTDEControlInterface

ROBOT_IP = "192.168.1.226"  # adjust to your real one
HOME = [0, -1.57, 1.57, 0, 1.57, 0]
VEL, ACC = 0.2, 0.5

def main(cmd: dict):
    # connect to the robot controller
    rtde_c = RTDEControlInterface(ROBOT_IP)

    if cmd["action"] == "go_home":
        # simple moveJ to home
        rtde_c.moveJ(HOME, speed=cmd.get("speed",VEL), acceleration=cmd.get("acc",ACC))

    elif cmd["action"] == "joint_move":
        # read current joint angles
        q = rtde_c.getActualQ()
        # choose joint index
        j = cmd["joint"]
        # apply delta to the chosen joint
        q[j] += cmd["delta"]
        # perform the move
        rtde_c.moveJ(q, speed=cmd.get("speed",VEL), acceleration=cmd.get("acc",ACC))

    else:
        print("Unknown action:", cmd)

    time.sleep(0.5)
    # emergency stop
    rtde_c.stopJ(acceleration=cmd.get("acc",ACC))
    # disconnect safely
    rtde_c.disconnect()
    
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python move_basic.py '<json_string>'")
        sys.exit(1)
    cmd = json.loads(sys.argv[1])
    main(cmd)
