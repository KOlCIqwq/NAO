''' Motif: 1-Bar High-Energy Drop & Freeze (full-body beat-locked 113.3 BPM, 4 beats = 2.12s) '''
import sys
import math
from naoqi import ALProxy

DEG = math.pi / 180.0

def main(robotIP="127.0.0.1", port=9559):
    try:
        motion = ALProxy("ALMotion", robotIP, port)
    except Exception as e:
        print("ALMotion error: %s" % e)
        return

    names = [
        "HeadPitch", "HeadYaw",
        "LShoulderPitch", "LShoulderRoll", "LElbowYaw", "LElbowRoll", "LWristYaw", "LHand",
        "RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll", "RWristYaw", "RHand",
        "LHipPitch", "LKneePitch", "LAnklePitch", "LHipRoll", "LAnkleRoll",
        "RHipPitch", "RKneePitch", "RAnklePitch", "RHipRoll", "RAnkleRoll"
    ]

    t_grid = [0.30, 0.53, 1.06, 1.38, 1.59, 2.12]
    times = [list(t_grid) for _ in names]

    # Squat drop on Beat 1 + freeze hold -> rise & hip accent Beat 3 -> settle Beat 4
    b = [0.28, 0.28, 0.28, 0.10, 0.18, 0.0]
    r = [0.0, 0.0, 0.0, 0.10, 0.10, 0.0]

    hip_p = [round(-0.44 - 0.5 * v, 4) for v in b]
    knee_p = [round(0.69 + 1.0 * v, 4) for v in b]
    ank_p = [round(-0.35 - 0.5 * v, 4) for v in b]
    hip_r = [round(v, 4) for v in r]
    ank_r = [round(-v, 4) for v in r]

    keys = [
        # HeadPitch
        [-10.0 * DEG, -10.0 * DEG, -10.0 * DEG, 10.0 * DEG, 10.0 * DEG, 0.0 * DEG],
        # HeadYaw
        [0.0 * DEG, 0.0 * DEG, 0.0 * DEG, 12.0 * DEG, 12.0 * DEG, 0.0 * DEG],
        # LShoulderPitch (from ~68 deg -> 22 deg punch -> 50 deg chest -> 68 deg)
        [22.0 * DEG, 22.0 * DEG, 22.0 * DEG, 50.0 * DEG, 50.0 * DEG, 68.0 * DEG],
        # LShoulderRoll
        [38.0 * DEG, 38.0 * DEG, 38.0 * DEG, 14.0 * DEG, 14.0 * DEG, 16.0 * DEG],
        # LElbowYaw
        [-45.0 * DEG, -45.0 * DEG, -45.0 * DEG, -38.0 * DEG, -38.0 * DEG, -60.0 * DEG],
        # LElbowRoll
        [-25.0 * DEG, -25.0 * DEG, -25.0 * DEG, -75.0 * DEG, -75.0 * DEG, -50.0 * DEG],
        # LWristYaw
        [-25.0 * DEG, -25.0 * DEG, -25.0 * DEG, 10.0 * DEG, 10.0 * DEG, 0.0 * DEG],
        # LHand
        [0.7, 0.7, 0.7, 0.2, 0.2, 0.3],
        # RShoulderPitch
        [22.0 * DEG, 22.0 * DEG, 22.0 * DEG, 50.0 * DEG, 50.0 * DEG, 68.0 * DEG],
        # RShoulderRoll
        [-38.0 * DEG, -38.0 * DEG, -38.0 * DEG, -14.0 * DEG, -14.0 * DEG, -16.0 * DEG],
        # RElbowYaw
        [45.0 * DEG, 45.0 * DEG, 45.0 * DEG, 38.0 * DEG, 38.0 * DEG, 60.0 * DEG],
        # RElbowRoll
        [25.0 * DEG, 25.0 * DEG, 25.0 * DEG, 75.0 * DEG, 75.0 * DEG, 50.0 * DEG],
        # RWristYaw
        [25.0 * DEG, 25.0 * DEG, 25.0 * DEG, -10.0 * DEG, -10.0 * DEG, 0.0 * DEG],
        # RHand
        [0.7, 0.7, 0.7, 0.2, 0.2, 0.3],
        # Left leg
        list(hip_p), list(knee_p), list(ank_p), list(hip_r), list(ank_r),
        # Right leg
        list(hip_p), list(knee_p), list(ank_p), list(hip_r), list(ank_r),
    ]

    motion.angleInterpolation(names, keys, times, True)

if __name__ == "__main__":
    main()
