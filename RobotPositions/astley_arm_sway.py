''' Rick Astley Arm Sway: Moving arms side-to-side in rhythm with 113 BPM '''

import sys
import motion
import almath
import math
import time
from naoqi import ALProxy

def main(robotIP="127.0.0.1", port=9559):
    try:
        motionProxy = ALProxy("ALMotion", robotIP, port)
    except Exception as e:
        print("Could not create proxy to ALMotion: %s" % e)
        return

    try:
        postureProxy = ALProxy("ALRobotPosture", robotIP, port)
    except Exception:
        postureProxy = None

    # Joint names for both arms and head
    joint_names = [
        "HeadYaw",
        "LShoulderPitch", "LShoulderRoll", "LElbowYaw", "LElbowRoll", "LWristYaw",
        "RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll", "RWristYaw"
    ]

    TO_RAD = almath.TO_RAD

    # Center starting pose (forearms bent in front of chest)
    pose_center = [
        0.0 * TO_RAD,
        75.0 * TO_RAD,  10.0 * TO_RAD, -40.0 * TO_RAD, -60.0 * TO_RAD,  0.0 * TO_RAD,
        75.0 * TO_RAD, -10.0 * TO_RAD,  40.0 * TO_RAD,  60.0 * TO_RAD,  0.0 * TO_RAD
    ]

    # Sway Left: both arms angle to the robot's left, head turns slightly left
    pose_sway_left = [
        12.0 * TO_RAD,
        72.0 * TO_RAD,  28.0 * TO_RAD, -55.0 * TO_RAD, -65.0 * TO_RAD, -20.0 * TO_RAD,
        78.0 * TO_RAD,  -4.0 * TO_RAD,  15.0 * TO_RAD,  75.0 * TO_RAD,  20.0 * TO_RAD
    ]

    # Sway Right: both arms angle to the robot's right, head turns slightly right
    pose_sway_right = [
        -12.0 * TO_RAD,
        78.0 * TO_RAD,   4.0 * TO_RAD, -15.0 * TO_RAD, -75.0 * TO_RAD, -20.0 * TO_RAD,
        72.0 * TO_RAD, -28.0 * TO_RAD,  55.0 * TO_RAD,  65.0 * TO_RAD,  20.0 * TO_RAD
    ]

    # Sequence of keyframe times matching 113.3 BPM (beat = ~0.53s, 2 beats = 1.06s)
    times = [0.8, 1.86, 2.92, 3.98, 5.04, 6.0]

    # Build angle lists transposed per joint
    trajectory = [pose_center, pose_sway_left, pose_sway_right, pose_sway_left, pose_sway_right, pose_center]
    angle_lists = []
    time_lists = []
    for j_idx in range(len(joint_names)):
        joint_angles = [trajectory[step][j_idx] for step in range(len(times))]
        angle_lists.append(joint_angles)
        time_lists.append(times)

    # Execute smooth joint interpolation
    motionProxy.angleInterpolation(joint_names, angle_lists, time_lists, True)

if __name__ == "__main__":
    ip = "127.0.0.1"
    port = 9559
    if len(sys.argv) > 1:
        ip = sys.argv[1]
    if len(sys.argv) > 2:
        port = int(sys.argv[2])
    main(ip, port)
