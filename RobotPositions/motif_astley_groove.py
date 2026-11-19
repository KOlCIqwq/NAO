''' Motif: Rick Astley Signature Sway (full-body beat-locked 113.3 BPM, 8 beats = 4.24s) '''
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

    t_grid = [0.30, 0.53, 1.06, 1.59, 2.12, 2.65, 3.18, 3.71, 4.24]
    times = [list(t_grid) for _ in names]

    b = [0.20, 0.08, 0.24, 0.24, 0.06, 0.24, 0.24, 0.10, 0.0]
    r = [0.12, 0.12, 0.14, 0.14, 0.0, -0.14, -0.14, 0.06, 0.0]

    hip_p = [round(-0.44 - 0.5 * v, 4) for v in b]
    knee_p = [round(0.69 + 1.0 * v, 4) for v in b]
    ank_p = [round(-0.35 - 0.5 * v, 4) for v in b]
    hip_r = [round(v, 4) for v in r]
    ank_r = [round(-v, 4) for v in r]

    keys = [
        # HeadPitch (nods on every beat)
        [-6.0 * DEG, 6.0 * DEG, -10.0 * DEG, -10.0 * DEG, 8.0 * DEG, -10.0 * DEG, -10.0 * DEG, 8.0 * DEG, -4.0 * DEG],
        # HeadYaw (follows sway, holds on stops)
        [18.0 * DEG, 20.0 * DEG, 22.0 * DEG, 22.0 * DEG, 0.0 * DEG, -22.0 * DEG, -22.0 * DEG, 12.0 * DEG, 0.0 * DEG],
        # LShoulderPitch
        [56.0 * DEG, 56.0 * DEG, 50.0 * DEG, 50.0 * DEG, 72.0 * DEG, 82.0 * DEG, 82.0 * DEG, 60.0 * DEG, 68.0 * DEG],
        # LShoulderRoll
        [32.0 * DEG, 32.0 * DEG, 36.0 * DEG, 36.0 * DEG, 16.0 * DEG, 8.0 * DEG, 8.0 * DEG, 24.0 * DEG, 16.0 * DEG],
        # LElbowYaw
        [-70.0 * DEG, -70.0 * DEG, -75.0 * DEG, -75.0 * DEG, -55.0 * DEG, -35.0 * DEG, -35.0 * DEG, -65.0 * DEG, -60.0 * DEG],
        # LElbowRoll
        [-80.0 * DEG, -80.0 * DEG, -80.0 * DEG, -80.0 * DEG, -65.0 * DEG, -75.0 * DEG, -75.0 * DEG, -70.0 * DEG, -55.0 * DEG],
        # LWristYaw
        [-25.0 * DEG, -25.0 * DEG, -30.0 * DEG, -30.0 * DEG, 0.0 * DEG, 20.0 * DEG, 20.0 * DEG, -15.0 * DEG, 0.0 * DEG],
        # LHand
        [0.4, 0.3, 0.5, 0.5, 0.3, 0.4, 0.4, 0.4, 0.3],
        # RShoulderPitch
        [82.0 * DEG, 82.0 * DEG, 85.0 * DEG, 85.0 * DEG, 72.0 * DEG, 50.0 * DEG, 50.0 * DEG, 70.0 * DEG, 68.0 * DEG],
        # RShoulderRoll
        [-8.0 * DEG, -8.0 * DEG, -6.0 * DEG, -6.0 * DEG, -16.0 * DEG, -36.0 * DEG, -36.0 * DEG, -18.0 * DEG, -16.0 * DEG],
        # RElbowYaw
        [35.0 * DEG, 35.0 * DEG, 30.0 * DEG, 30.0 * DEG, 55.0 * DEG, 75.0 * DEG, 75.0 * DEG, 55.0 * DEG, 60.0 * DEG],
        # RElbowRoll
        [75.0 * DEG, 75.0 * DEG, 78.0 * DEG, 78.0 * DEG, 65.0 * DEG, 80.0 * DEG, 80.0 * DEG, 65.0 * DEG, 55.0 * DEG],
        # RWristYaw
        [-20.0 * DEG, -20.0 * DEG, -20.0 * DEG, -20.0 * DEG, 0.0 * DEG, 30.0 * DEG, 30.0 * DEG, 15.0 * DEG, 0.0 * DEG],
        # RHand
        [0.4, 0.3, 0.4, 0.4, 0.3, 0.5, 0.5, 0.4, 0.3],
        # Left leg
        list(hip_p), list(knee_p), list(ank_p), list(hip_r), list(ank_r),
        # Right leg
        list(hip_p), list(knee_p), list(ank_p), list(hip_r), list(ank_r),
    ]

    motion.angleInterpolation(names, keys, times, True)

if __name__ == "__main__":
    main()
