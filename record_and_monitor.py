"""
NAO Live Visualizer & Pose Monitor
Connects to NAO on 127.0.0.1:9559 and prints real-time ASCII posture indicators
and limb coordinates for visual debugging.
Compatible with Python 2.7 (Choregraphe SDK) and Python 3.
"""

import sys
import time
import os

def monitor_robot(ip="127.0.0.1", port=9559, duration=10):
    try:
        from naoqi import ALProxy
    except ImportError:
        print("naoqi not found. Please run via run_sim.bat.")
        return

    print("Connecting to NAO on {}:{}...".format(ip, port))
    try:
        motion = ALProxy("ALMotion", ip, port)
        posture = ALProxy("ALRobotPosture", ip, port)
    except Exception as e:
        print("Failed to connect: {}".format(e))
        return

    print("Monitor active for {} seconds. Press Ctrl+C to stop.".format(duration))
    print("=" * 65)
    print("{:<8} | {:<12} | {:<12} | {:<12} | {:<10}".format("Time", "Head Z (m)", "LArm Z (m)", "RArm Z (m)", "Posture"))
    print("-" * 65)

    start = time.time()
    try:
        while time.time() - start < duration:
            t_curr = time.time() - start
            post = posture.getPostureFamily()
            pos_head = motion.getPosition("Head", 1, True)
            pos_larm = motion.getPosition("LArm", 1, True)
            pos_rarm = motion.getPosition("RArm", 1, True)

            print("{:6.1f}s  | {:10.3f}   | {:10.3f}   | {:10.3f}   | {:<10}".format(
                t_curr, pos_head[2], pos_larm[2], pos_rarm[2], post
            ))
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass
    print("=" * 65)
    print("Monitoring ended.")

if __name__ == "__main__":
    dur = 10
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        dur = int(sys.argv[1])
    monitor_robot("127.0.0.1", 9559, dur)

