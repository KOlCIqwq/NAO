''' Motif: 1-Bar Verse Groove & Stylized Pause (beat-locked 113.3 BPM, 4 beats = 2.12s) '''
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
        "RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll", "RWristYaw", "RHand"
    ]

    # 4 beats:
    # 0.35s -> 0.53s -> 1.59s: Shoulder lean + head tilt on Beat 1, stylized FREEZE/PAUSE through Beat 3
    # 1.88s -> 2.12s: Crisp wrist flick + head snap back to groove-ready on Beat 4
    t_grid = [0.35, 0.53, 1.59, 1.88, 2.12]
    times = [list(t_grid) for _ in names]

    keys = [
        # HeadPitch
        [-8.0 * DEG, -8.0 * DEG, -8.0 * DEG, 9.0 * DEG, 0.0 * DEG],
        # HeadYaw
        [20.0 * DEG, 20.0 * DEG, 20.0 * DEG, -10.0 * DEG, 0.0 * DEG],
        # LShoulderPitch
        [40.0 * DEG, 40.0 * DEG, 40.0 * DEG, 60.0 * DEG, 68.0 * DEG],
        # LShoulderRoll
        [30.0 * DEG, 30.0 * DEG, 30.0 * DEG, 20.0 * DEG, 16.0 * DEG],
        # LElbowYaw
        [-45.0 * DEG, -45.0 * DEG, -45.0 * DEG, -70.0 * DEG, -60.0 * DEG],
        # LElbowRoll
        [-80.0 * DEG, -80.0 * DEG, -80.0 * DEG, -40.0 * DEG, -50.0 * DEG],
        # LWristYaw
        [-30.0 * DEG, -30.0 * DEG, -30.0 * DEG, 30.0 * DEG, 0.0 * DEG],
        # LHand
        [0.7, 0.7, 0.7, 0.2, 0.4],
        # RShoulderPitch
        [78.0 * DEG, 78.0 * DEG, 78.0 * DEG, 56.0 * DEG, 68.0 * DEG],
        # RShoulderRoll
        [-10.0 * DEG, -10.0 * DEG, -10.0 * DEG, -24.0 * DEG, -16.0 * DEG],
        # RElbowYaw
        [65.0 * DEG, 65.0 * DEG, 65.0 * DEG, 45.0 * DEG, 60.0 * DEG],
        # RElbowRoll
        [45.0 * DEG, 45.0 * DEG, 45.0 * DEG, 70.0 * DEG, 50.0 * DEG],
        # RWristYaw
        [0.0 * DEG, 0.0 * DEG, 0.0 * DEG, -35.0 * DEG, 0.0 * DEG],
        # RHand
        [0.3, 0.3, 0.3, 0.85, 0.4],
    ]

    motion.angleInterpolation(names, keys, times, True)

if __name__ == "__main__":
    main()
