''' Motif: 1-Bar Bass Drop Knee-Squat & Hip Pop (full-body 113.3 BPM, 4 beats = 2.12s) '''
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

    t_grid = [0.36, 0.53, 1.06, 1.48, 1.59, 2.12]
    times = [list(t_grid) for _ in names]

    # Squat drop on Beat 1 -> HOLD Beat 2 -> hip pop Beat 3 -> bounce & settle Beat 4
    b = [0.30, 0.30, 0.30, 0.08, 0.22, 0.0]
    r = [0.10, 0.10, 0.10, -0.10, -0.10, 0.0]

    hip_p = [round(-0.44 - 0.5 * v, 4) for v in b]
    knee_p = [round(0.69 + 1.0 * v, 4) for v in b]
    ank_p = [round(-0.35 - 0.5 * v, 4) for v in b]
    hip_r = [round(v, 4) for v in r]
    ank_r = [round(-v, 4) for v in r]

    keys = [
        # HeadPitch & HeadYaw
        [6.0 * DEG, 6.0 * DEG, 6.0 * DEG, -6.0 * DEG, 4.0 * DEG, 0.0 * DEG],
        [-10.0 * DEG, -10.0 * DEG, -10.0 * DEG, 10.0 * DEG, 10.0 * DEG, 0.0 * DEG],
        # Left arm (cool/low near hips & chest)
        [62.0 * DEG, 62.0 * DEG, 62.0 * DEG, 74.0 * DEG, 66.0 * DEG, 72.0 * DEG],
        [18.0 * DEG, 18.0 * DEG, 18.0 * DEG, 14.0 * DEG, 16.0 * DEG, 14.0 * DEG],
        [-50.0 * DEG, -50.0 * DEG, -50.0 * DEG, -62.0 * DEG, -55.0 * DEG, -60.0 * DEG],
        [-65.0 * DEG, -65.0 * DEG, -65.0 * DEG, -45.0 * DEG, -60.0 * DEG, -48.0 * DEG],
        [-12.0 * DEG, -12.0 * DEG, -12.0 * DEG, 8.0 * DEG, 0.0 * DEG, 0.0 * DEG],
        [0.3, 0.3, 0.3, 0.3, 0.3, 0.3],
        # Right arm (cool/low near hips & chest)
        [62.0 * DEG, 62.0 * DEG, 62.0 * DEG, 74.0 * DEG, 66.0 * DEG, 72.0 * DEG],
        [-18.0 * DEG, -18.0 * DEG, -18.0 * DEG, -14.0 * DEG, -16.0 * DEG, -14.0 * DEG],
        [50.0 * DEG, 50.0 * DEG, 50.0 * DEG, 62.0 * DEG, 55.0 * DEG, 60.0 * DEG],
        [65.0 * DEG, 65.0 * DEG, 65.0 * DEG, 45.0 * DEG, 60.0 * DEG, 48.0 * DEG],
        [12.0 * DEG, 12.0 * DEG, 12.0 * DEG, -8.0 * DEG, 0.0 * DEG, 0.0 * DEG],
        [0.3, 0.3, 0.3, 0.3, 0.3, 0.3],
        # Left leg
        list(hip_p), list(knee_p), list(ank_p), list(hip_r), list(ank_r),
        # Right leg
        list(hip_p), list(knee_p), list(ank_p), list(hip_r), list(ank_r),
    ]

    motion.angleInterpolation(names, keys, times, True)

if __name__ == "__main__":
    main()
