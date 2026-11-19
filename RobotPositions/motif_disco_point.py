''' Motif: 80s Disco Point Dance (full-body beat-locked 113.3 BPM, 8 beats = 4.24s) '''
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

    t_grid = [0.42, 1.06, 1.56, 2.12, 2.60, 3.18, 3.68, 4.24]
    times = [list(t_grid) for _ in names]

    # Hips lean opposite the high disco point + knee bounce
    b = [0.22, 0.22, 0.06, 0.16, 0.22, 0.22, 0.08, 0.0]
    r = [0.12, 0.12, 0.0, 0.0, -0.12, -0.12, 0.0, 0.0]

    hip_p = [round(-0.44 - 0.5 * v, 4) for v in b]
    knee_p = [round(0.69 + 1.0 * v, 4) for v in b]
    ank_p = [round(-0.35 - 0.5 * v, 4) for v in b]
    hip_r = [round(v, 4) for v in r]
    ank_r = [round(-v, 4) for v in r]

    keys = [
        # HeadPitch
        [-16.0 * DEG, -16.0 * DEG, 8.0 * DEG, 6.0 * DEG, -16.0 * DEG, -16.0 * DEG, 8.0 * DEG, 0.0 * DEG],
        # HeadYaw
        [-28.0 * DEG, -28.0 * DEG, 0.0 * DEG, 0.0 * DEG, 28.0 * DEG, 28.0 * DEG, 0.0 * DEG, 0.0 * DEG],
        # LShoulderPitch
        [72.0 * DEG, 72.0 * DEG, 70.0 * DEG, 70.0 * DEG, -38.0 * DEG, -38.0 * DEG, 68.0 * DEG, 68.0 * DEG],
        # LShoulderRoll
        [18.0 * DEG, 18.0 * DEG, 22.0 * DEG, 22.0 * DEG, 42.0 * DEG, 42.0 * DEG, 18.0 * DEG, 16.0 * DEG],
        # LElbowYaw
        [-60.0 * DEG, -60.0 * DEG, -60.0 * DEG, -60.0 * DEG, -30.0 * DEG, -30.0 * DEG, -65.0 * DEG, -60.0 * DEG],
        # LElbowRoll
        [-70.0 * DEG, -70.0 * DEG, -82.0 * DEG, -82.0 * DEG, -8.0 * DEG, -8.0 * DEG, -60.0 * DEG, -50.0 * DEG],
        # LWristYaw
        [0.0 * DEG, 0.0 * DEG, 0.0 * DEG, 0.0 * DEG, -45.0 * DEG, -45.0 * DEG, 0.0 * DEG, 0.0 * DEG],
        # LHand
        [0.2, 0.2, 0.2, 0.2, 0.85, 0.85, 0.3, 0.3],
        # RShoulderPitch
        [-38.0 * DEG, -38.0 * DEG, 70.0 * DEG, 70.0 * DEG, 72.0 * DEG, 72.0 * DEG, 70.0 * DEG, 68.0 * DEG],
        # RShoulderRoll
        [-42.0 * DEG, -42.0 * DEG, -22.0 * DEG, -22.0 * DEG, -18.0 * DEG, -18.0 * DEG, -18.0 * DEG, -16.0 * DEG],
        # RElbowYaw
        [30.0 * DEG, 30.0 * DEG, 60.0 * DEG, 60.0 * DEG, 60.0 * DEG, 60.0 * DEG, 65.0 * DEG, 60.0 * DEG],
        # RElbowRoll
        [8.0 * DEG, 8.0 * DEG, 82.0 * DEG, 82.0 * DEG, 70.0 * DEG, 70.0 * DEG, 60.0 * DEG, 50.0 * DEG],
        # RWristYaw
        [45.0 * DEG, 45.0 * DEG, 0.0 * DEG, 0.0 * DEG, 0.0 * DEG, 0.0 * DEG, 0.0 * DEG, 0.0 * DEG],
        # RHand
        [0.85, 0.85, 0.2, 0.2, 0.2, 0.2, 0.3, 0.3],
        # Left leg
        list(hip_p), list(knee_p), list(ank_p), list(hip_r), list(ank_r),
        # Right leg
        list(hip_p), list(knee_p), list(ank_p), list(hip_r), list(ank_r),
    ]

    motion.angleInterpolation(names, keys, times, True)

if __name__ == "__main__":
    main()
